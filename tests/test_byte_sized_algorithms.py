"""Offline fixture and configuration tests for website #8 (port 8128)."""
from __future__ import annotations

import functools
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from clone_runtime import (
    load_config, local_url, Mirror, check_site, make_handler,
    update_site, existing_server, port_in_use,
)

CFG = load_config(ROOT / "ByteSizedAlgorithms")

def run_server(handler):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    return server, worker

def stop_server(server, worker):
    server.shutdown()
    server.server_close()
    worker.join(timeout=5)

class ByteSizedAlgorithmsTests(unittest.TestCase):
    def test_01_config_port_and_hash_route(self):
        self.assertEqual(CFG["id"], "byte-sized-algorithms")
        self.assertEqual(CFG["port"], 8128)
        self.assertEqual(CFG["source"], "https://byte-sized-algorithms.vercel.app/")
        self.assertEqual(CFG["launch_path"], "/#/big-o/1")
        self.assertEqual(local_url(CFG), "http://127.0.0.1:8128/#/big-o/1")

    def test_02_standard_file_layout(self):
        names = ("Launcher.bat", "Update_Clone.bat", "Check_Clone.bat",
                 "server.py", "mirror.py", "verify_clone.py", "config.json", "README.md")
        for name in names:
            self.assertTrue((ROOT / "ByteSizedAlgorithms" / name).is_file(), name)
        self.assertTrue((ROOT / "tools/clone_runtime.py").is_file())

    def test_03_launcher_text(self):
        for file in ("Launcher.bat", "Update_Clone.bat", "Check_Clone.bat"):
            body = (ROOT / "ByteSizedAlgorithms" / file).read_text(encoding="utf-8")
            self.assertIn("Port 8128", body)
            self.assertIn("py -3", body)
            self.assertIn("python", body)
            self.assertNotIn("8127", body)

    def test_04_no_cache_is_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            ok, missing = check_site(Path(tmp), verbose=False)
            self.assertFalse(ok)
            self.assertIn("index.html", missing)

    def test_05_mirror_html_js_css_lazy_chunk_and_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            origin_dir = Path(tmp) / "source"
            assets = origin_dir / "assets"
            assets.mkdir(parents=True)
            (origin_dir / "index.html").write_text(
                '<link rel="stylesheet" href="/assets/main.css">'
                '<script type="module" src="/assets/main.js"></script>', encoding="utf-8")
            (assets / "main.js").write_text('import("/assets/lesson-a.js");'
                                            'const icon="/assets/robot.png";', encoding="utf-8")
            (assets / "main.css").write_text('body{background:url("/assets/grid.svg")}', encoding="utf-8")
            (assets / "lesson-a.js").write_text("window.lessonLoaded=true", encoding="utf-8")
            (assets / "robot.png").write_bytes(b"fakePNG")
            (assets / "grid.svg").write_text("<svg></svg>", encoding="utf-8")
            server, worker = run_server(functools.partial(SimpleHTTPRequestHandler, directory=str(origin_dir)))
            try:
                cache = Path(tmp) / "site"
                self.assertTrue(Mirror({"source": "http://127.0.0.1:%d/" % server.server_port},cache,jobs=2).run())
                self.assertTrue(check_site(cache, verbose=False)[0])
                for name in ("index.html","assets/main.js","assets/main.css","assets/lesson-a.js",
                             "assets/robot.png","assets/grid.svg",".clone-manifest.json"):
                    self.assertTrue((cache / name).is_file(), name)
            finally:
                stop_server(server, worker)

    def test_06_restart_and_spa_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "assets").mkdir()
            (root / "index.html").write_text('<script src="/assets/main.js"></script>', encoding="utf-8")
            (root / "assets/main.js").write_text("window.ready=true", encoding="utf-8")
            for _ in range(2):
                server, worker = run_server(make_handler(CFG, root))
                try:
                    address = "http://127.0.0.1:%d" % server.server_port
                    self.assertTrue(port_in_use(server.server_port))
                    self.assertTrue(existing_server(CFG, server.server_port))
                    self.assertIn(b"main.js", urlopen(address+"/#/big-o/1").read())
                    self.assertIn(b"main.js", urlopen(address+"/big-o/1").read())
                    self.assertEqual(urlopen(address+"/assets/main.js").status, 200)
                    status = json.load(urlopen(address+"/__clone_health__"))
                    self.assertEqual(status["clone_id"], "byte-sized-algorithms")
                    self.assertEqual(status["port"], server.server_port)
                finally:
                    stop_server(server, worker)

    def test_07_failed_update_keeps_working_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            cache = base / "site"
            cache.mkdir()
            (cache / "index.html").write_text("<html>OLD CACHE</html>", encoding="utf-8")
            self.assertFalse(update_site({"source": "http://127.0.0.1:1/"}, base, jobs=1))
            self.assertIn("OLD CACHE", (cache/"index.html").read_text(encoding="utf-8"))
            self.assertFalse((base/"site.__staging__").exists())

    def test_08_release_metadata(self):
        from clone_runtime import VERSION as TOOL_VERSION
        self.assertEqual((ROOT / "VERSION").read_text().strip(), TOOL_VERSION)
        self.assertIn("Approved", (ROOT / "ByteSizedAlgorithms/README.md").read_text(encoding="utf-8"))
        self.assertFalse((ROOT / "ByteSizedAlgorithms/site").exists())

if __name__ == "__main__":
    unittest.main()
