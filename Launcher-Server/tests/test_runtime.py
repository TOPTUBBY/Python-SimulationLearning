"""Offline regression tests; no internet or third-party assets required."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import socket
import sys
import tempfile
import threading
import unittest
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from clone_runtime import asset_path, check_site, load_config, make_handler, Mirror

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ["ESP32", "Arduino", "RoverKit", "Multimeter", "Protocol", "DesignedToScale", "RoboticsLab", "ByteSizedAlgorithms", "MoonLife", "ESP32Labs"]


class RuntimeTests(unittest.TestCase):
    def test_config_ports_and_routes(self):
        ports = set()
        for project in PROJECTS:
            config = load_config(ROOT / project)
            self.assertNotIn(config["port"], ports)
            self.assertEqual(config["port"], 8121 + PROJECTS.index(project))
            ports.add(config["port"])
        self.assertEqual(load_config(ROOT / "Multimeter")["launch_path"], "/multimeter")
        self.assertEqual(load_config(ROOT / "RoboticsLab")["launch_path"], "/#uno")
        self.assertEqual(load_config(ROOT / "ByteSizedAlgorithms")["launch_path"], "/#/big-o/1")
        self.assertEqual(load_config(ROOT / "MoonLife")["launch_path"], "/")

    def test_paths_block_traversal_and_other_hosts(self):
        self.assertEqual(str(asset_path("https://example.com/assets/a.js", "example.com")), "assets/a.js")
        self.assertIsNone(asset_path("https://example.com/../../bad.js", "example.com"))
        self.assertIsNone(asset_path("https://other.com/a.js", "example.com"))

    def test_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertFalse(check_site(root, verbose=False)[0])
            (root / "index.html").write_text('<script src="/assets/app.js"></script>', encoding="utf-8")
            self.assertFalse(check_site(root, verbose=False)[0])
            (root / "assets").mkdir()
            (root / "assets/app.js").write_text("console.log(1)", encoding="utf-8")
            (root / ".clone-manifest.json").write_text("{}", encoding="utf-8")
            self.assertTrue(check_site(root, verbose=False)[0])

    def test_local_serve_health_and_history_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text("<!doctype html><title>Offline Test</title>", encoding="utf-8")
            config = load_config(ROOT / "Multimeter")
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(config, root))
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                base = "http://127.0.0.1:%s" % server.server_port
                self.assertIn(b"Offline Test", urlopen(base + "/multimeter").read())
                state = json.loads(urlopen(base + "/__clone_health__").read())
                self.assertEqual(state["clone_id"], "multimeter")
                self.assertEqual(state["port"], server.server_port)
            finally:
                server.shutdown()
                server.server_close()
                worker.join(timeout=3)

    def test_mirror_on_local_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            src = path / "source"
            src.mkdir()
            (src / "index.html").write_text('<script type="module" src="/assets/main.js"></script><link rel="stylesheet" href="/assets/main.css">', encoding="utf-8")
            (src / "assets").mkdir()
            (src / "assets/main.js").write_text('const asset="/assets/chunk.js";', encoding="utf-8")
            (src / "assets/main.css").write_text('body { color: red; }', encoding="utf-8")
            (src / "assets/chunk.js").write_text("console.log('ok')", encoding="utf-8")
            handler = functools.partial(SimpleHTTPRequestHandler, directory=str(src))
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                # A local HTTP fixture avoids dependence on external HTTPS websites.
                c = {"source": "http://127.0.0.1:%d/" % server.server_port}
                mirror = Mirror(c, path / "cache", jobs=2)
                self.assertTrue(mirror.run())
                self.assertTrue((path / "cache/assets/chunk.js").exists())
            finally:
                server.shutdown()
                server.server_close()
                worker.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
