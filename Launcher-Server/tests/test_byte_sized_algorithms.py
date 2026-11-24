"""Offline tests for port 8128 frontend cloning infrastructure.

No internet, third-party site content, or Windows installation needed.
"""
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
sys.path.insert(0, str(ROOT / 'tools'))
from clone_runtime import (
    load_config, local_url, Mirror, check_site, make_handler,
    update_site, existing_server, port_in_use,
)

CFG = load_config(ROOT / 'ByteSizedAlgorithms')

def run_server(handler):
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread

def stop_server(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)

class ByteSizedAlgorithmsTests(unittest.TestCase):
    def test_01_config_port_and_hash_route(self):
        self.assertEqual(CFG['id'], 'byte-sized-algorithms')
        self.assertEqual(CFG['port'], 8128)
        self.assertEqual(CFG['source'], 'https://byte-sized-algorithms.vercel.app/')
        self.assertEqual(CFG['launch_path'], '/#/big-o/1')
        self.assertEqual(local_url(CFG), 'http://127.0.0.1:8128/#/big-o/1')

    def test_02_complete_standard_file_layout(self):
        required = ('Launcher.bat','Update_Clone.bat','Check_Clone.bat','server.py',
                    'mirror.py','verify_clone.py','config.json','README.md')
        for name in required:
            self.assertTrue((ROOT / 'ByteSizedAlgorithms' / name).is_file(), name)
        self.assertTrue((ROOT / 'tools/clone_runtime.py').is_file())

    def test_03_launcher_text_uses_correct_port_and_python_fallback(self):
        for filename in ('Launcher.bat','Update_Clone.bat','Check_Clone.bat'):
            s = (ROOT / 'ByteSizedAlgorithms' / filename).read_text(encoding='utf-8')
            self.assertIn('Port 8128', s)
            self.assertIn('py -3', s)
            self.assertIn('python', s)
        launch = (ROOT / 'ByteSizedAlgorithms/Launcher.bat').read_text(encoding='utf-8')
        self.assertIn('server.py', launch)
        self.assertNotIn('8127', launch)

    def test_04_empty_cache_fails_without_starting_blank_site(self):
        with tempfile.TemporaryDirectory() as tmp:
            passed, missing = check_site(Path(tmp), verbose=False)
            self.assertFalse(passed)
            self.assertIn('index.html', missing)

    def test_05_mirror_fetches_html_js_css_dynamic_chunks_and_svg(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/'upstream'
            (source/'assets').mkdir(parents=True)
            (source/'index.html').write_text('<!doctype html><html><head>\n<link rel="stylesheet" href="/assets/main.css"/>\n<script type="module" src="/assets/main.js"></script>\n</head><body><div id="root"></div></body></html>', encoding='utf-8')
            (source/'assets/main.css').write_text('body{background-image:url("/assets/grid.svg")}', encoding='utf-8')
            (source/'assets/main.js').write_text('import("/assets/lesson-a.js");const logo="/assets/robot.png";', encoding='utf-8')
            (source/'assets/lesson-a.js').write_text('window.lessonLoaded=true;', encoding='utf-8')
            (source/'assets/grid.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>', encoding='utf-8')
            (source/'assets/robot.png').write_bytes(b"\x89PNG\r\n\x1a\nEXAMPLE")
            origin, th = run_server(functools.partial(SimpleHTTPRequestHandler, directory=str(source)))
            try:
                cache = Path(tmp)/'cached'
                test_cfg={'source': 'http://127.0.0.1:%d/' % origin.server_port}
                self.assertTrue(Mirror(test_cfg, cache, jobs=2).run())
                self.assertTrue(check_site(cache, verbose=False)[0])
                for required in ('index.html', 'assets/main.css', 'assets/main.js',
                                 'assets/lesson-a.js', 'assets/grid.svg', 'assets/robot.png',
                                 '.clone-manifest.json'):
                    self.assertTrue((cache/required).is_file(), required)
            finally:
                stop_server(origin, th)

    def test_06_server_restarts_without_upstream_and_serves_hash_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            site=Path(tmp)
            (site/'index.html').write_text('<!doctype html><script type="module" src="/assets/main.js"></script>', encoding='utf-8')
            (site/'assets').mkdir()
            (site/'assets/main.js').write_text('window.demo=1', encoding='utf-8')
            for round_number in range(2):
                server, th = run_server(make_handler(CFG, site))
                try:
                    uri='http://127.0.0.1:%d' % server.server_port
                    self.assertTrue(port_in_use(server.server_port))
                    self.assertTrue(existing_server(CFG, server.server_port))
                    self.assertIn(b'main.js', urlopen(uri+'/#/big-o/1').read())
                    self.assertIn(b'main.js', urlopen(uri+'/big-o/1').read())
                    self.assertEqual(urlopen(uri+'/assets/main.js').status, 200)
                    health=json.load(urlopen(uri+'/__clone_health__'))
                    self.assertEqual(health['clone_id'], 'byte-sized-algorithms')
                    self.assertEqual(health['port'], server.server_port)
                finally:
                    stop_server(server, th)

    def test_07_bad_stage_preserves_previous_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            good=root/'site'
            good.mkdir()
            (good/'index.html').write_text('<html>OLD WORKING CACHE</html>', encoding='utf-8')
            bad={'source':'http://127.0.0.1:1/'}
            self.assertFalse(update_site(bad, root, jobs=1))
            self.assertIn('OLD WORKING CACHE', (good/'index.html').read_text(encoding='utf-8'))
            self.assertFalse((root/'site.__staging__').exists())

    def test_08_version_and_localization(self):
        self.assertEqual((ROOT.parent / 'VERSION').read_text().strip(), '1.6.0')
        self.assertIn('Thai UI — v1.4.0', (ROOT/'ByteSizedAlgorithms/README.md').read_text(encoding='utf-8'))
        self.assertFalse((ROOT/'ByteSizedAlgorithms/site').exists())

if __name__=='__main__':
    unittest.main()
