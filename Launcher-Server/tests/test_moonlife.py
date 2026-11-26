"""Self-contained offline tests for Moon Life 8129 clone and Thai overlay."""
from __future__ import annotations
import functools
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'MoonLife'
sys.path.insert(0, str(ROOT / 'tools'))
from clone_runtime import Mirror, check_site, existing_server, load_config, local_url, port_in_use, update_site
from moon_runtime import TranslationService, inject_overlay, make_moon_handler, serve_moon

CONFIG = load_config(PROJECT)


def start(handler):
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def stop(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


class MoonLifePreviewTests(unittest.TestCase):
    def test_01_config_fixed_port_8129(self):
        self.assertEqual(CONFIG['id'], 'moonlife')
        self.assertEqual(CONFIG['port'], 8129)
        self.assertEqual(CONFIG['launch_path'], '/')
        self.assertEqual(CONFIG['source'], 'https://project-moon-life.vercel.app/')
        self.assertEqual(local_url(CONFIG), 'http://127.0.0.1:8129/')

    def test_02_file_structure(self):
        needed = ('Launcher.bat', 'Update_Clone.bat', 'Check_Clone.bat', 'server.py',
                  'mirror.py', 'verify_clone.py', 'config.json', 'README.md')
        for filename in needed:
            self.assertTrue((PROJECT / filename).is_file(), filename)
        for filename in ('thai_overlay.js', 'thai_overlay.css', 'thai_dictionary.json'):
            self.assertTrue((PROJECT / 'translation' / filename).is_file())
        self.assertTrue((ROOT / 'tools/clone_runtime.py').is_file())
        self.assertTrue((ROOT / 'tools/moon_runtime.py').is_file())

    def test_03_bat_launcher_python_compat_and_port(self):
        for filename in ('Launcher.bat','Update_Clone.bat','Check_Clone.bat'):
            s = (PROJECT / filename).read_text(encoding='utf-8')
            self.assertIn('Port 8129', s)
            self.assertIn('py -3', s)
            self.assertIn('python', s)
        self.assertIn('server.py', (PROJECT/'Launcher.bat').read_text())

    def test_04_dictionary_verified_ui_and_state_words(self):
        terms = json.loads((PROJECT/'translation/thai_dictionary.json').read_text(encoding='utf-8'))
        self.assertGreaterEqual(len(terms), 180)
        for phrase in ('Be born', 'Gender', 'Male', 'Female', 'Pause', 'Resume',
                       'Life log', 'Health', 'Sanity', 'Wealth', 'Network', 'Reputation',
                       'The City', 'Set a seed (optional)', 'Continue', 'Archive'):
            self.assertTrue(terms.get(phrase), phrase)
        self.assertTrue(any('Every moment' in k for k in terms))
        self.assertTrue(any('Shortcuts' in k for k in terms))

    def test_05_html_injection_preserves_game_code(self):
        original = '<!doctype html><html><head><meta charset="utf-8"><script src="/assets/main.js"></script></head><body><div id="root"></div></body></html>'
        converted = inject_overlay(original)
        self.assertIn('<script src="/assets/main.js"></script>', converted)
        self.assertIn('<div id="root"></div>', converted)
        self.assertIn('/__moonlife__/thai_overlay.js', converted)
        self.assertIn('/__moonlife__/thai_overlay.css', converted)
        self.assertEqual(inject_overlay(converted), converted)

    def test_06_empty_cache_is_detected_no_blank_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(check_site(tmp, verbose=False)[0])

    def test_07_public_asset_mirror_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/'source'
            (source/'assets').mkdir(parents=True)
            (source/'index.html').write_text('<html><head><link rel="stylesheet" href="/assets/game.css"><script type="module" src="/assets/game.js"></script></head><body><main>Start</main></body></html>')
            (source/'assets/game.css').write_text('body{background:url("/assets/paper.svg")}')
            (source/'assets/game.js').write_text('import("/assets/choices.js");const pic="/assets/portrait.webp";')
            (source/'assets/choices.js').write_text('window.engine=true;')
            (source/'assets/paper.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>')
            (source/'assets/portrait.webp').write_bytes(b'RIFFxxxxWEBP')
            origin, worker = start(functools.partial(SimpleHTTPRequestHandler, directory=str(source)))
            try:
                cache = Path(tmp)/'site'
                self.assertTrue(Mirror({'source': 'http://127.0.0.1:%d/' % origin.server_port},cache, jobs=2).run())
                self.assertTrue(check_site(cache, verbose=False)[0])
                for file in ('index.html','assets/game.css','assets/game.js',
                             'assets/choices.js','assets/paper.svg','assets/portrait.webp'):
                    self.assertTrue((cache/file).is_file(), file)
            finally:
                stop(origin, worker)

    def test_08_server_asset_delivery_thai_and_health_on_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)/'site'
            (site/'assets').mkdir(parents=True)
            (site/'index.html').write_text('<html><head><script src="/assets/main.js"></script></head><body><h1>Be born</h1></body></html>')
            (site/'assets/main.js').write_text('window.game=true')
            for _ in range(2):
                fake = TranslationService(tmp, translator=lambda s: 'แปล: '+s)
                server, worker = start(make_moon_handler(CONFIG, site, PROJECT, translator=fake))
                base = 'http://127.0.0.1:%d' % server.server_port
                try:
                    self.assertTrue(port_in_use(server.server_port))
                    self.assertTrue(existing_server(CONFIG, server.server_port))
                    self.assertIn(b'__moonlife__/thai_overlay.js',urlopen(base+'/').read())
                    self.assertIn(b'__moonlife__/thai_overlay.js',urlopen(base+'/route').read())
                    self.assertIn(b'window.game',urlopen(base+'/assets/main.js').read())
                    self.assertIn(b'moonlifeThaiOverlayLoaded',urlopen(base+'/__moonlife__/thai_overlay.js').read())
                    self.assertIn('"Be born"',urlopen(base+'/__moonlife__/thai_dictionary.json').read().decode())
                    self.assertEqual(urlopen(base+'/__moonlife__/thai_overlay.css').status,200)
                    health = json.load(urlopen(base+'/__clone_health__'))
                    self.assertEqual(health['clone_id'],'moonlife')
                finally:
                    stop(server, worker)

    def test_09_online_translation_is_optional_cache_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls = []
            service = TranslationService(tmp, translator=lambda s: calls.append(s) or 'ไทย '+s)
            self.assertEqual(service.translate_many(['Important event'], online=False),[None])
            self.assertEqual(calls, [])
            self.assertEqual(service.translate_many(['Important event'], online=True),['ไทย Important event'])
            self.assertEqual(calls,['Important event'])
            again = TranslationService(tmp,translator=lambda _: self.fail('Unexpected remote lookup'))
            self.assertEqual(again.translate_many(['Important event'], online=False), ['ไทย Important event'])

    def test_10_translation_endpoint_and_cross_site_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)/'site'
            site.mkdir()
            (site/'index.html').write_text('<html></html>')
            service = TranslationService(tmp, translator=lambda s: 'ไทย '+s)
            server,worker = start(make_moon_handler(CONFIG,site,PROJECT,translator=service))
            base = 'http://127.0.0.1:%d' % server.server_port
            try:
                data = json.dumps({'texts':['Moon story'], 'online':True}).encode()
                req = Request(base+'/__moonlife__/translate',data=data,headers={'Content-Type':'application/json'},method='POST')
                self.assertEqual(json.load(urlopen(req))['results'],['ไทย Moon story'])
                req2 = Request(base+'/__moonlife__/translate',data=data,headers={'Content-Type':'application/json','Origin':'https://evil.example'},method='POST')
                with self.assertRaises(HTTPError) as failure:
                    urlopen(req2)
                self.assertEqual(failure.exception.code,403)
                req3 = Request(base+'/__moonlife__/translate',data=json.dumps({'texts':['Moon story'],'online':False}).encode(),method='POST')
                self.assertEqual(json.load(urlopen(req3))['results'],['ไทย Moon story'])
            finally:
                stop(server,worker)

    def test_11_failed_update_keeps_existing_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'site').mkdir()
            (root/'site/index.html').write_text('KEEP ME')
            self.assertFalse(update_site({'source':'http://127.0.0.1:1/'},root,jobs=1))
            self.assertIn('KEEP ME',(root/'site/index.html').read_text())

    def test_12_version_and_local_cache_not_git(self):
        self.assertRegex((ROOT.parent / 'VERSION').read_text().strip(), r'^\d+\.\d+\.\d+(?:-[\w.]+)?$')
        self.assertFalse((PROJECT/'site').exists())
        self.assertTrue((PROJECT/'README.md').is_file())


if __name__ == '__main__':
    unittest.main()
