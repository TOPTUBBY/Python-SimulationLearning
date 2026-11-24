"""Thai UI release regression tests. Works without network or browser libraries."""
from __future__ import annotations

from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from clone_runtime import check_site, existing_server, load_config
from moon_runtime import TranslationService
from thai_runtime import (LOCALE_ROOT, inject_overlay, load_dictionary,
                          make_thai_handler, TRANSLATE_URL)

SITES = ["ESP32", "Arduino", "RoverKit", "Multimeter", "Protocol",
         "DesignedToScale", "RoboticsLab", "ByteSizedAlgorithms"]


def run_server(handler):
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def stop_server(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)


class ThaiUiTests(unittest.TestCase):
    def test_01_eight_projects_unique_ports_and_opt_in_online(self):
        for i, name in enumerate(SITES):
            cfg = load_config(ROOT / name)
            self.assertEqual(cfg['port'], 8121 + i)
            self.assertTrue(cfg['thai_enabled'])
            self.assertFalse(cfg['online_translation_default'])
            self.assertFalse(cfg['thai_default'])

    def test_02_standard_server_and_check_entrypoints(self):
        for name in SITES:
            for filename in ('Launcher.bat','Update_Clone.bat','Check_Clone.bat',
                             'server.py','mirror.py','verify_clone.py','config.json','README.md'):
                self.assertTrue((ROOT / name / filename).is_file(), (name,filename))
            self.assertIn('from thai_runtime import main', (ROOT / name / 'server.py').read_text())
            self.assertIn('from thai_runtime import main', (ROOT / name / 'verify_clone.py').read_text())
            self.assertIn('from clone_runtime import main', (ROOT / name / 'mirror.py').read_text())

    def test_03_common_dictionary_coverage(self):
        data=json.loads((LOCALE_ROOT / 'common_th.json').read_text(encoding='utf-8'))
        self.assertGreaterEqual(len(data), 250)
        for key in ('Home','Next','Back','Search','Pause','Reset','Code','Quiz','Language','Controls','Current','Voltage'):
            self.assertIn(key,data)
            self.assertTrue(data[key])

    def test_04_site_dictionaries_and_technical_labels(self):
        required = {'ESP32':'Meet the ESP32','Arduino':'Blink an LED',
                    'RoverKit':'Drive','Multimeter':'Using a multimeter',
                    'Protocol':'Packet','DesignedToScale':'How a Request Travels',
                    'RoboticsLab':'Find the part','ByteSizedAlgorithms':'Big-O Notation'}
        for name, phrase in required.items():
            values=load_dictionary(load_config(ROOT / name))
            self.assertIn(phrase,values)
            self.assertGreaterEqual(len(values),285)

    def test_05_html_injection_idempotent_and_preserves_original(self):
        doc='<html><head><script type="module" src="/assets/app.js"></script></head><body>Demo</body></html>'
        x=inject_overlay(doc,'esp32')
        self.assertIn('src="/assets/app.js"',x)
        self.assertIn('src="/__thai__/overlay.js"',x)
        self.assertIn('data-site="esp32"',x)
        self.assertIn('data-default="original"',x)
        self.assertEqual(inject_overlay(x,'esp32'),x)

    def test_06_html_injection_with_no_head(self):
        doc='<html><body>Start</body></html>'
        self.assertIn('/__thai__/overlay.js',inject_overlay(doc,'arduino'))

    def test_07_local_server_serves_ui_and_spa_routes_eight_sites(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'assets').mkdir()
            (root/'index.html').write_text('<!doctype html><html><head><script type="module" src="/assets/main.js"></script></head><body><button>Next</button></body></html>')
            (root/'assets/main.js').write_text('window.appReady=true')
            for name in SITES:
                cfg=load_config(ROOT/name)
                server,worker=run_server(make_thai_handler(cfg,root,ROOT/name))
                addr='http://127.0.0.1:%d'%server.server_port
                try:
                    self.assertTrue(existing_server(cfg,server.server_port))
                    html=urlopen(addr+'/').read().decode()
                    self.assertIn('src="/__thai__/overlay.js"',html)
                    route=urlopen(addr+'/multimeter' if name=='Multimeter' else addr+'/lessons/intro').read().decode()
                    self.assertIn('src="/__thai__/overlay.js"',route)
                    self.assertIn(b'window.appReady',urlopen(addr+'/assets/main.js').read())
                    dict_data=json.load(urlopen(addr+'/__thai__/dictionary.json'))
                    self.assertIn('Next',dict_data)
                    self.assertIn(b'__simthaiOverlayActive',urlopen(addr+'/__thai__/overlay.js').read())
                    self.assertIn(b'simthai-language-ui',urlopen(addr+'/__thai__/overlay.css').read())
                    h=json.load(urlopen(addr+'/__clone_health__'))
                    self.assertEqual(h['clone_id'],cfg['id'])
                    self.assertEqual(h['port'],server.server_port)
                    head=Request(addr+'/index.html',method='HEAD')
                    self.assertEqual(urlopen(head).status,200)
                finally:
                    stop_server(server,worker)

    def test_08_online_translation_optional_cache_persists(self):
        cfg=load_config(ROOT/'ESP32')
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'index.html').write_text('<html><head></head><body>Hello</body></html>')
            called=[]
            translator=TranslationService(d,translator=lambda x: called.append(x) or 'ภาษาไทย '+x)
            server,worker=run_server(make_thai_handler(cfg,root,ROOT/'ESP32',translator=translator))
            base='http://127.0.0.1:%d'%server.server_port
            try:
                def post(value,online=False,origin=None):
                    data=json.dumps({'texts':[value],'online':online}).encode()
                    headers={'Content-Type':'application/json'}
                    if origin:headers['Origin']=origin
                    return Request(base+TRANSLATE_URL,data=data,headers=headers,method='POST')
                self.assertEqual(json.load(urlopen(post('Unseen lesson')))['results'],[None])
                self.assertEqual(called,[])
                self.assertEqual(json.load(urlopen(post('Unseen lesson',True)))['results'],['ภาษาไทย Unseen lesson'])
                self.assertEqual(json.load(urlopen(post('Unseen lesson')))['results'],['ภาษาไทย Unseen lesson'])
                self.assertEqual(called,['Unseen lesson'])
                self.assertIn('Unseen lesson',json.loads((Path(d)/'translation_cache.json').read_text()))
                with self.assertRaises(HTTPError) as exc:
                    urlopen(post('Caution',True,'https://evil.example'))
                self.assertEqual(exc.exception.code,403)
            finally:
                stop_server(server,worker)

    def test_09_invalid_payload_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'index.html').write_text('<html>ok</html>')
            cfg=load_config(ROOT/'Arduino')
            server,worker=run_server(make_thai_handler(cfg,root,ROOT/'Arduino'))
            try:
                uri='http://127.0.0.1:%s'%server.server_port
                req=Request(uri+TRANSLATE_URL,data=b'{bad json',headers={'Content-Type':'application/json'},method='POST')
                with self.assertRaises(HTTPError) as exc:urlopen(req)
                self.assertEqual(exc.exception.code,400)
            finally:stop_server(server,worker)

    def test_10_release_version_and_stable_moonlife(self):
        self.assertEqual((ROOT/'VERSION').read_text().strip(),'1.4.0')
        self.assertIn('moon_runtime', (ROOT/'MoonLife/server.py').read_text())
        self.assertFalse((ROOT/'ESP32/site').exists())
        self.assertFalse((ROOT/'MoonLife/site').exists())

    def test_11_checker_requires_valid_cache(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(check_site(d,verbose=False)[0])

    def test_12_root_launchers_list_nine_sites(self):
        for target in ('Launch_All.bat','Update_All.bat','Check_All.bat'):
            text=(ROOT/target).read_text(encoding='utf-8')
            for name in SITES+['MoonLife']:
                self.assertIn(name,text)

if __name__=='__main__':unittest.main()
