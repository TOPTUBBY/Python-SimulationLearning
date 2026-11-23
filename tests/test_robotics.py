"""Offline fixture tests for the Robotics Lab local clone."""
from pathlib import Path
import functools
import json
import sys
import tempfile
import threading
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from clone_runtime import Mirror, check_site, load_config, local_url, make_handler


class RoboticsLabTests(unittest.TestCase):
    def test_config_route(self):
        cfg = load_config(ROOT / "RoboticsLab")
        self.assertEqual(cfg["port"], 8127)
        self.assertEqual(cfg["launch_path"], "/#uno")
        self.assertEqual(cfg["id"], "robotics-lab")
        self.assertEqual(local_url(cfg), "http://127.0.0.1:8127/#uno")

    def test_scripts_are_present(self):
        for name in ("Launcher.bat", "Update_Clone.bat", "Check_Clone.bat", "server.py", "mirror.py", "verify_clone.py"):
            self.assertTrue((ROOT / "RoboticsLab" / name).is_file(), name)

    def test_local_mirror_and_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "source"
            (src / "assets").mkdir(parents=True)
            (src / "index.html").write_text('<link rel="stylesheet" href="/assets/main.css"><script type="module" src="/assets/main.js"></script>')
            (src / "assets/main.css").write_text("body{background:#111}")
            (src / "assets/main.js").write_text('const chunk="/assets/chunk.js";const board="/assets/uno.glb";')
            (src / "assets/chunk.js").write_text("console.log('robotics')")
            (src / "assets/uno.glb").write_bytes(b"glTF")
            origin = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(SimpleHTTPRequestHandler, directory=str(src)))
            thread = threading.Thread(target=origin.serve_forever, daemon=True)
            thread.start()
            try:
                cache = root / "site"
                self.assertTrue(Mirror({"source": "http://127.0.0.1:%d/" % origin.server_port}, cache, jobs=2).run())
                self.assertTrue(check_site(cache, verbose=False)[0])
                self.assertTrue((cache / "assets/uno.glb").exists())
            finally:
                origin.shutdown()
                origin.server_close()
                thread.join(3)
            for _ in range(2):
                server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(load_config(ROOT / "RoboticsLab"), cache))
                worker = threading.Thread(target=server.serve_forever, daemon=True)
                worker.start()
                try:
                    url = "http://127.0.0.1:%d" % server.server_port
                    self.assertIn(b"assets/main.js", urlopen(url + "/").read())
                    self.assertIn(b"glTF", urlopen(url + "/assets/uno.glb").read())
                    health = json.load(urlopen(url + "/__clone_health__"))
                    self.assertEqual(health["clone_id"], "robotics-lab")
                    self.assertEqual(health["port"], server.server_port)
                finally:
                    server.shutdown()
                    server.server_close()
                    worker.join(3)


if __name__ == "__main__":
    unittest.main()
