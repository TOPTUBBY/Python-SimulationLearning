"""Cross-platform fixture tests for portable EXE runtime and packaging.

These tests do not produce Windows binaries. Windows PyInstaller CI does that.
"""
from __future__ import annotations

from contextlib import contextmanager
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import portable_launcher as app
import build_portable as build
from clone_runtime import load_config


@contextmanager
def serve(handler):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


def create_dummy_site(root, project, slot="site"):
    """A complete local mirror fixture with only HTML + one JS bundle."""
    cfg = load_config(ROOT / project)
    site = root / project / slot
    if project == "ESP32Labs":
        (site / "esp-labs/assets").mkdir(parents=True)
        (site / "esp-labs/index.html").write_text(
            '<!doctype html><title>ESP Labs</title><script src="./assets/main.js"></script>',
            encoding="utf-8")
        (site / "esp-labs/assets/main.js").write_text('console.log("esp")', encoding="utf-8")
        source = "https://ionloft.com/esp-labs/"
    else:
        (site / "assets").mkdir(parents=True)
        (site / "index.html").write_text(
            '<!doctype html><title>Test</title><script src="/assets/main.js"></script>',
            encoding="utf-8")
        (site / "assets/main.js").write_text('console.log("ok")', encoding="utf-8")
        source = cfg["source"]
    (site / ".clone-manifest.json").write_text(
        json.dumps({"source": source, "errors": []}), encoding="utf-8")
    return site


class PortableExeTests(unittest.TestCase):
    def test_all_10_projects_have_distinct_ports_and_configs(self):
        self.assertEqual(len(app.SITES), 10)
        for offset, project in enumerate(app.SITES):
            cfg = load_config(ROOT / project)
            self.assertEqual(cfg["port"], 8121 + offset)
            self.assertTrue((ROOT / project / "Launcher.bat").is_file())
        self.assertEqual(load_config(ROOT / "MoonLife")["port"], 8129)
        self.assertEqual(load_config(ROOT / "ESP32Labs")["launch_path"], "/esp-labs/#/?lang=en")

    def test_app_data_localappdata_no_other_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.dict(os.environ, {"LOCALAPPDATA": folder}):
                self.assertEqual(app.app_data("ESP32"),
                                 Path(folder) / "SimulationLearning" / "ESP32")
        with self.assertRaises(ValueError):
            app.app_data("../../other")

    def test_embedded_missing_assets_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            cfg = ROOT / "ESP32/config.json"
            (root / "ESP32").mkdir()
            (root / "ESP32/config.json").write_bytes(cfg.read_bytes())
            with self.assertRaises(FileNotFoundError):
                app.prepare_site(root, "ESP32", root / "data", mode="embedded")

    def test_existing_bootstrap_cache_is_reused_without_network(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            for project in app.SITES:
                (base / project).mkdir(exist_ok=True)
                (base / project / "config.json").write_bytes(
                    (ROOT / project / "config.json").read_bytes())
                state = base / "cache" / project
                state.mkdir(parents=True)
                if project == "ESP32Labs":
                    cache = create_dummy_site(base / "cache", project, "site.__staging__")
                else:
                    cache = create_dummy_site(base / "cache", project, "site.__staging__")
                self.assertEqual(app.prepare_site(base, project, state), cache)

    def test_server_assets_health_thai_and_subpath(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            # Translation and overlays must be available in packed bundle.
            import shutil
            import thai_runtime
            old_locale_root = thai_runtime.LOCALE_ROOT
            self.addCleanup(setattr, thai_runtime, "LOCALE_ROOT", old_locale_root)
            shutil.copytree(ROOT / "localization", root / "localization")
            for project in app.SITES:
                project_dir = root / project
                project_dir.mkdir()
                (project_dir / "config.json").write_bytes((ROOT / project / "config.json").read_bytes())
                if project == "MoonLife":
                    shutil.copytree(ROOT / "MoonLife" / "translation", project_dir / "translation")
                site = create_dummy_site(root, project)
                cfg, handler = app.create_handler(root, project, state_dir=root / "appdata" / project,
                                                   site=site, offline=True)
                with serve(handler) as server:
                    base = "http://127.0.0.1:%d" % server.server_port
                    health = json.load(urlopen(base + "/__clone_health__"))
                    self.assertEqual(health["clone_id"], cfg["id"])
                    if project == "ESP32Labs":
                        html = urlopen(base + "/esp-labs/").read().decode()
                        asset = "/esp-labs/assets/main.js"
                    else:
                        html = urlopen(base + "/").read().decode()
                        asset = "/assets/main.js"
                    self.assertIn("script", html)
                    self.assertIn(b"console.log", urlopen(base + asset).read())
                    if project == "MoonLife":
                        self.assertIn("__moonlife__", html)
                        self.assertGreater(len(urlopen(base + "/__moonlife__/thai_overlay.js").read()), 200)
                    else:
                        self.assertIn("__thai__/overlay.js", html)
                        self.assertGreater(len(urlopen(base + "/__thai__/overlay.js").read()), 200)
                    try:
                        urlopen(base + "/assets/absent.js")
                    except HTTPError as error:
                        self.assertEqual(error.code, 404)
                    else:
                        self.fail("Absent bundled JS must return 404 (offline): " + project)

    def test_build_inputs_bootstrap_vs_embedded(self):
        with tempfile.TemporaryDirectory() as folder:
            temp = Path(folder)
            for project in app.SITES:
                selection = temp / (project + ".json")
                selection.write_text(json.dumps({"project": project, "mode": "bootstrap"}))
                command, name = build.build_command(project, None, selection, temp)
                self.assertIn("--onefile", command)
                self.assertIn("--windowed", command)
                self.assertIn("--add-data", command)
                self.assertIn("--paths", command)
                self.assertIn(str(ROOT / project / "config.json"), " ".join(command))
                self.assertNotIn(project + os.sep + "site", " ".join(command))
                self.assertTrue(name.endswith("-" + str(load_config(ROOT / project)["port"])))
                dummy = temp / "site"
                dummy.mkdir(exist_ok=True)
                cmd2, name2 = build.build_command(project, dummy, selection, temp, mode="embedded")
                self.assertIn(str(dummy), " ".join(cmd2))
                self.assertTrue(name2.endswith("-Offline"))

    def test_bootstrap_cache_check_does_not_require_download(self):
        self.assertEqual(build.cli(["--all", "--mode", "bootstrap", "--check"]), 0)
        self.assertEqual(build.cli(["--all", "--mode", "embedded", "--check"]), 1)


if __name__ == "__main__":
    unittest.main()
