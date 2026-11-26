"""Offline fixture tests for new How It's Wired (port 8131), no original assets required."""
from pathlib import Path
import functools
import json
from http.server import ThreadingHTTPServer
import sys
import tempfile
import threading
import unittest
from urllib.request import urlopen
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from clone_runtime import load_config, check_site
import how_its_wired_runtime as wire
from thai_runtime import make_thai_handler, load_dictionary

PROJECT = ROOT / "HowItsWired"
CFG = load_config(PROJECT)


def create_cache(folder):
    folder = Path(folder)
    (folder / "assets").mkdir(parents=True, exist_ok=True)
    (folder / "index.html").write_text('<!doctype html><html><head><script src="/assets/app.js"></script></head><body>Will the lead take it?</body></html>', encoding="utf-8")
    (folder / "assets" / "app.js").write_text("console.log('ok')", encoding="utf-8")
    (folder / ".clone-manifest.json").write_text(json.dumps({"source": CFG["source"], "errors": []}), encoding="utf-8")
    assert check_site(folder, verbose=False)[0]
    return folder


class WiringPreviewTests(unittest.TestCase):
    def test_01_port_and_route(self):
        self.assertEqual(CFG["port"], 8131)
        self.assertEqual(CFG["id"], "how-its-wired")
        self.assertEqual(CFG["launch_path"], "/lead-load")
        self.assertEqual(CFG["source"], "https://how-its-wired.vercel.app/")

    def test_02_standard_files(self):
        for name in ("Launcher.bat", "Update_Clone.bat", "Check_Clone.bat", "server.py", "mirror.py", "verify_clone.py", "config.json", "README.md"):
            self.assertTrue((PROJECT / name).is_file(), name)
            if name.endswith(".bat"):
                self.assertIn("Port 8131", (PROJECT / name).read_text(encoding="utf-8"))

    def test_03_thai_dictionary_37_lessons(self):
        entries = load_dictionary(CFG)
        self.assertGreater(len(entries), 400)
        self.assertEqual(entries["Will the lead take it?"], "ปลั๊กพ่วงรับโหลดไหวไหม?")
        for label in ("First circuits", "Around the house", "The distribution board", "Lights & switches", "Motors & transformers", "Heat & thermostats", "Alternative power"):
            self.assertIn(label, entries)

    def test_04_no_rename_or_copy_of_cache_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            stage = create_cache(project / "site.__staging__")
            with patch.object(wire, "Mirror", side_effect=AssertionError("Unexpected download")):
                self.assertEqual(wire.prepare_cache(CFG, project), stage)
            self.assertFalse((project / "site").exists())
            self.assertFalse((project / "site.__next__").exists())

    def test_05_verified_refresh_switches_slots_without_renaming(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            stage = create_cache(project / "site.__staging__")
            class MirrorFixture:
                def __init__(self, cfg, dst, jobs=12):
                    self.dst = dst
                def run(self):
                    create_cache(self.dst)
                    return True
            with patch.object(wire, "Mirror", MirrorFixture):
                updated = wire.prepare_cache(CFG, project, refresh=True)
            self.assertEqual(updated, project / "site.__next__")
            self.assertEqual(wire.active_cache(project), updated)
            self.assertTrue(stage.is_dir())

    def test_06_failing_refresh_keeps_last_good_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            stable = create_cache(project / "site")
            class MirrorFailure:
                def __init__(self, cfg, dst, jobs=12):
                    pass
                def run(self):
                    return False
            with patch.object(wire, "Mirror", MirrorFailure):
                self.assertEqual(wire.prepare_cache(CFG, project, refresh=True), stable)
            self.assertEqual(wire.active_cache(project), stable)

    def test_07_local_server_route_assets_thai_health(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            cache = create_cache(project / "site")
            handler = make_thai_handler(CFG, cache, project)
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                url = "http://127.0.0.1:%s" % server.server_port
                html = urlopen(url + "/lead-load").read().decode("utf-8")
                self.assertIn("/__thai__/overlay.js", html)
                self.assertIn('data-default="th"', html)
                self.assertIn('assets/app.js', html)
                self.assertIn(b"console.log", urlopen(url + "/assets/app.js").read())
                words = json.load(urlopen(url + "/__thai__/dictionary.json"))
                self.assertIn("Will the lead take it?", words)
                health = json.load(urlopen(url + "/__clone_health__"))
                self.assertEqual(health["clone_id"], CFG["id"])
            finally:
                server.shutdown()
                server.server_close()
                worker.join(timeout=3)

if __name__ == "__main__":
    unittest.main()
