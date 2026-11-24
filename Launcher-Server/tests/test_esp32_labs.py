"""Fixture-based checks of the ESP32 Labs port 8130 preview.
These do NOT prove parity with the actual external website.
"""
from __future__ import annotations

import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
import shutil
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from clone_runtime import load_config, local_url, existing_server
from esp_labs_runtime import SubpathMirror, check_site, update_site, make_handler, SUBPATH
from thai_runtime import load_dictionary

CONFIG = load_config(ROOT / 'ESP32Labs')


def start_server(handler):
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    return server, worker


def stop_server(server, worker):
    server.shutdown()
    server.server_close()
    worker.join(timeout=3)


class DummyTranslator:
    def translate_many(self, texts, online=False):
        return ['ไทย: ' + x if online else x for x in texts]


class ESP32LabsTests(unittest.TestCase):
    def test_01_port_route_and_origin(self):
        self.assertEqual(CONFIG['port'], 8130)
        self.assertEqual(CONFIG['id'], 'esp32-labs')
        self.assertEqual(CONFIG['source'], 'https://ionloft.com/')
        self.assertEqual(CONFIG['source_subpath'], '/esp-labs/')
        self.assertEqual(local_url(CONFIG), 'http://127.0.0.1:8130/esp-labs/#/?lang=en')

    def test_02_expected_standard_files(self):
        for name in ('Launcher.bat', 'Update_Clone.bat', 'Check_Clone.bat',
                     'server.py', 'mirror.py', 'verify_clone.py', 'config.json', 'README.md'):
            self.assertTrue((ROOT / 'ESP32Labs' / name).is_file(), name)
        for name in ('clone_runtime.py', 'thai_runtime.py', 'moon_runtime.py', 'esp_labs_runtime.py'):
            self.assertTrue((ROOT / 'tools' / name).is_file(), name)

    def test_03_bat_launcher_controls(self):
        for name in ('Launcher.bat', 'Update_Clone.bat', 'Check_Clone.bat'):
            src = (ROOT / 'ESP32Labs' / name).read_text(encoding='utf-8')
            self.assertIn('Port 8130', src)
            self.assertIn('py -3', src)
            self.assertIn('python', src)

    def test_04_thai_dictionary(self):
        d = load_dictionary(CONFIG)
        self.assertGreaterEqual(len(d), 400)
        self.assertEqual(d['Meet the board'], 'ทำความรู้จักบอร์ด')
        self.assertEqual(d['All labs'], 'แล็บทั้งหมด')
        self.assertEqual(d['GPIO matrix'], 'เมทริกซ์ GPIO')

    def test_05_localization_assets(self):
        for p in ('localization/thai_overlay.js', 'localization/thai_overlay.css',
                  'localization/common_th.json', 'localization/sites/esp32-labs.json'):
            self.assertTrue((ROOT/p).is_file(), p)
        text = (ROOT/'localization/thai_overlay.js').read_text(encoding='utf-8')
        self.assertIn('/__thai__/translate', text)
        self.assertIn('data-lang="th"', text)
        self.assertIn('data-lang="original"', text)

    def test_06_missing_cache_does_not_validate(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(check_site(Path(tmp), verbose=False)[0])

    def prepare_fixture(self, root):
        src = root / 'origin'
        (src / 'esp-labs/assets').mkdir(parents=True)
        (src / 'esp-labs/firmware').mkdir(parents=True)
        (src / 'esp-labs/index.html').write_text('''<!doctype html><html><head><title>ESP32 Labs</title>
<link rel="stylesheet" href="./assets/main.css">
<script type="module" src="./assets/main.js"></script></head>
<body><div id="root"><h1>ESP32 Labs</h1><button>Meet the board</button>
<button id="dynamic">All labs</button><code>digitalWrite(GPIO4, HIGH);</code>
<input placeholder="Search the parts"></div></body></html>''', encoding='utf-8')
        (src / 'esp-labs/assets/main.js').write_text('''window.appStarted = true;
const load = "./extra.js";
const firmware = "../firmware/intro.json";''', encoding='utf-8')
        (src / 'esp-labs/assets/main.css').write_text('body{font-family:Arial}', encoding='utf-8')
        (src / 'esp-labs/assets/extra.js').write_text('window.extra = true;', encoding='utf-8')
        (src / 'esp-labs/assets/lazy.js').write_text('window.lazy = true;', encoding='utf-8')
        (src / 'esp-labs/firmware/intro.json').write_text('{"lab":"setup"}', encoding='utf-8')
        handler = functools.partial(SimpleHTTPRequestHandler, directory=str(src))
        server, worker = start_server(handler)
        config = dict(CONFIG)
        config['source'] = 'http://127.0.0.1:%s/' % server.server_port
        return server, worker, config

    def test_07_mirror_downloads_correct_subfolder_and_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, thread, config = self.prepare_fixture(root)
            try:
                self.assertTrue(SubpathMirror(config, root / 'site', jobs=3).run())
                self.assertTrue(check_site(root / 'site', verbose=False)[0])
                for p in ('index.html','esp-labs/index.html',
                          'esp-labs/assets/main.css','esp-labs/assets/main.js'):
                    self.assertTrue((root/'site'/p).is_file(), p)
                self.assertFalse((root/'site/assets/main.js').exists())
            finally:
                stop_server(source, thread)

    def test_08_local_http_thai_ui_assets_and_redirect(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src, src_t, config = self.prepare_fixture(root)
            try:
                self.assertTrue(update_site(config, root, jobs=2))
            finally:
                stop_server(src, src_t)
            # Verify local serving uses no network and honours original subfolder.
            translator = DummyTranslator()
            from thai_runtime import make_thai_handler
            from esp_labs_runtime import make_handler
            server, thread = start_server(make_handler(config, root/'site', root, translator=translator))
            try:
                base = 'http://127.0.0.1:%d' % server.server_port
                with urlopen(base+'/') as res:
                    self.assertEqual(res.geturl(), base+'/esp-labs/#/?lang=en')
                with urlopen(base+'/esp-labs/') as res:
                    html = res.read().decode()
                    self.assertIn('/__thai__/overlay.js', html)
                    self.assertIn('data-default="th"', html)
                    self.assertIn('ESP32 Labs', html)
                with urlopen(base+'/esp-labs/imaginary/spa-route') as res:
                    self.assertIn(b'ESP32 Labs', res.read())
                with urlopen(base+'/esp-labs/assets/main.js') as res:
                    self.assertIn(b'appStarted', res.read())
                with urlopen(base+'/__thai__/dictionary.json') as res:
                    d=json.load(res)
                    self.assertIn('Meet the board', d)
                with urlopen(base+'/__clone_health__') as res:
                    health=json.load(res)
                    self.assertEqual(health['clone_id'], 'esp32-labs')
                self.assertFalse(existing_server(config, server.server_port) is False)
            finally:
                stop_server(server, thread)

    def test_09_failed_update_keeps_prior_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            src, src_t, config=self.prepare_fixture(root)
            try:
                self.assertTrue(update_site(config, root, jobs=3))
            finally:
                stop_server(src, src_t)
            before=(root/'site/esp-labs/index.html').read_bytes()
            self.assertFalse(update_site(config, root, jobs=2))
            self.assertEqual(before,(root/'site/esp-labs/index.html').read_bytes())
            self.assertTrue(check_site(root/'site', verbose=False)[0])
            self.assertFalse((root/'site.__staging__').exists())

    def test_10_on_demand_asset_recovers_late_js(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src, src_t, config = self.prepare_fixture(root)
            try:
                self.assertTrue(update_site(config, root, jobs=2))
                self.assertFalse((root/'site/esp-labs/assets/lazy.js').exists())
                server, thread = start_server(make_handler(config, root/'site', root, translator=DummyTranslator()))
                try:
                    base = 'http://127.0.0.1:%d' % server.server_port
                    with urlopen(base+'/esp-labs/assets/lazy.js') as res:
                        self.assertIn(b'window.lazy', res.read())
                    self.assertTrue((root/'site/esp-labs/assets/lazy.js').exists())
                finally:
                    stop_server(server, thread)
            finally:
                stop_server(src, src_t)

    def test_11_translation_endpoint_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            src, src_t, config=self.prepare_fixture(root)
            try:
                self.assertTrue(update_site(config, root, jobs=2))
            finally:
                stop_server(src, src_t)
            from esp_labs_runtime import make_handler
            server, thread=start_server(make_handler(config, root/'site', root, translator=DummyTranslator()))
            try:
                endpoint='http://127.0.0.1:%d/__thai__/translate' % server.server_port
                def post(online):
                    data=json.dumps({'texts':['Your progress'], 'online':online}).encode()
                    req=Request(endpoint,data=data,headers={'Content-Type':'application/json'},method='POST')
                    return json.load(urlopen(req))
                self.assertEqual(post(False)['results'],['Your progress'])
                self.assertEqual(post(True)['results'],['ไทย: Your progress'])
            finally:
                stop_server(server,thread)


    def test_12_first_install_works_when_directory_rename_is_denied(self):
        """Reproduce the user's WinError 5 on staging.rename(site)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src, worker, config = self.prepare_fixture(root)
            try:
                with patch.object(Path, 'rename', side_effect=PermissionError(13, 'Access denied')):
                    self.assertTrue(update_site(config, root, jobs=2))
                self.assertTrue(check_site(root / 'site', verbose=False)[0])
                self.assertFalse((root / 'site.__staging__').exists())
            finally:
                stop_server(src, worker)

    def test_13_retry_uses_staging_after_copy_error_without_redownloading(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src, worker, config = self.prepare_fixture(root)
            actual_copy = shutil.copy2
            blocked = {'attempts': 0}
            def copy_with_transient_error(from_path, to_path, *args, **kwargs):
                if Path(from_path).name == 'main.js' and blocked['attempts'] < 2:
                    blocked['attempts'] += 1
                    raise PermissionError(13, 'Access denied by file scanner')
                return actual_copy(from_path, to_path, *args, **kwargs)
            try:
                with patch('esp_labs_runtime.shutil.copy2', side_effect=copy_with_transient_error):
                    self.assertTrue(update_site(config, root, jobs=2))
                self.assertEqual(blocked['attempts'], 2)
                self.assertTrue(check_site(root / 'site', verbose=False)[0])
            finally:
                stop_server(src, worker)

    def test_14_permanent_copy_lock_keeps_stage_and_recovers_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src, worker, config = self.prepare_fixture(root)
            actual_copy = shutil.copy2
            try:
                def blocked(from_path, to_path, *args, **kwargs):
                    if Path(from_path).name == 'main.js':
                        raise PermissionError(13, 'Access denied by antivirus')
                    return actual_copy(from_path, to_path, *args, **kwargs)
                with patch('esp_labs_runtime.shutil.copy2', side_effect=blocked):
                    self.assertFalse(update_site(config, root, jobs=2))
                self.assertTrue(check_site(root / 'site.__staging__', verbose=False)[0])
            finally:
                stop_server(src, worker)
            # Internet is now unavailable: retry must reuse staged files.
            with patch('esp_labs_runtime.SubpathMirror.run', side_effect=AssertionError('redownload forbidden')):
                self.assertTrue(update_site(config, root, jobs=2))
            self.assertTrue(check_site(root / 'site', verbose=False)[0])
            self.assertFalse((root / 'site.__staging__').exists())

    def test_15_existing_valid_cache_stays_when_windows_denies_update_rename(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src, worker, config = self.prepare_fixture(root)
            try:
                self.assertTrue(update_site(config, root, jobs=2))
                original = (root / 'site/esp-labs/index.html').read_bytes()
                with patch.object(Path, 'rename', side_effect=PermissionError(13, 'Access denied')):
                    self.assertFalse(update_site(config, root, jobs=2))
                self.assertEqual((root / 'site/esp-labs/index.html').read_bytes(), original)
                self.assertTrue(check_site(root / 'site', verbose=False)[0])
                self.assertTrue(check_site(root / 'site.__staging__', verbose=False)[0])
                # When handle lock disappears, next attempt activates stage.
                with patch('esp_labs_runtime.SubpathMirror.run', side_effect=AssertionError('redownload forbidden')):
                    self.assertTrue(update_site(config, root, jobs=2))
                self.assertTrue(check_site(root / 'site', verbose=False)[0])
            finally:
                stop_server(src, worker)


    def test_16_install_works_with_preexisting_partial_site_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src, worker, config = self.prepare_fixture(root)
            try:
                (root / 'site').mkdir()
                (root / 'site/unrelated.txt').write_text('previous interrupted installation')
                with patch.object(Path, 'rename', side_effect=PermissionError(13, 'Access denied')):
                    self.assertTrue(update_site(config, root, jobs=2))
                self.assertTrue(check_site(root / 'site', verbose=False)[0])
            finally:
                stop_server(src, worker)

    def test_17_if_both_move_and_copy_fail_server_can_use_verified_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src, worker, config = self.prepare_fixture(root)
            try:
                staging = root / 'site.__staging__'
                self.assertTrue(SubpathMirror(config, staging, jobs=2).run())
            finally:
                stop_server(src, worker)
            import esp_labs_runtime as rt
            handler_paths = []
            original_handler = rt.make_handler
            def tracking_handler(config, cache, project_dir, translator=None):
                handler_paths.append(Path(cache))
                return original_handler(config, cache, project_dir, translator)
            class FakeHTTPServer:
                def __init__(self, host_port, handler):
                    self.server_port = host_port[1]
                def serve_forever(self, poll_interval=0.2):
                    pass
                def server_close(self):
                    pass
            with patch('esp_labs_runtime.update_site', return_value=False), \
                 patch('esp_labs_runtime.make_handler', side_effect=tracking_handler), \
                 patch('esp_labs_runtime.ThreadedHTTPServer', FakeHTTPServer, create=True), \
                 patch('esp_labs_runtime.ThreadingHTTPServer', FakeHTTPServer), \
                 patch('esp_labs_runtime.existing_server', return_value=False), \
                 patch('esp_labs_runtime.port_in_use', return_value=False):
                self.assertEqual(rt.serve(config, root, port=8130, no_browser=True), 0)
            self.assertEqual(handler_paths, [staging])



    def test_18_existing_verified_stage_bypasses_bulk_copy_and_mirror(self):
        import esp_labs_runtime as rt
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, worker, config = self.prepare_fixture(root)
            try:
                stage = root / 'site.__staging__'
                self.assertTrue(SubpathMirror(config, stage, jobs=2).run())
                (root / 'site').mkdir()
                (root / 'site' / 'incomplete.txt').write_text('partial copy from rc2')
            finally:
                stop_server(source, worker)
            with patch('esp_labs_runtime.SubpathMirror.run', side_effect=AssertionError('redownload prohibited')), \
                 patch('esp_labs_runtime.shutil.copy2', side_effect=AssertionError('bulk copying prohibited')), \
                 patch.object(Path, 'rename', side_effect=PermissionError(13,'rename prohibited')):
                selected, ok = rt.prepare_cache(config, root, refresh=False)
            self.assertTrue(ok)
            self.assertEqual(selected, stage)
            self.assertFalse((root / 'site' / 'esp-labs' / 'index.html').exists())

    def test_19_first_install_serves_stage_without_copy_or_rename(self):
        import esp_labs_runtime as rt
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, worker, config = self.prepare_fixture(root)
            try:
                with patch('esp_labs_runtime.shutil.copy2', side_effect=AssertionError('bulk copying prohibited')), \
                     patch.object(Path, 'rename', side_effect=PermissionError(13, 'rename prohibited')):
                    selected, success = rt.prepare_cache(config, root, refresh=False, jobs=2)
                self.assertTrue(success)
                self.assertEqual(selected, root / 'site.__staging__')
                self.assertFalse((root / 'site').exists())
                self.assertTrue(check_site(selected, verbose=False)[0])
            finally:
                stop_server(source, worker)

    def test_20_update_rotates_verified_slots_via_pointer_no_bulk_file_moves(self):
        import esp_labs_runtime as rt
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, worker, config = self.prepare_fixture(root)
            try:
                one, ok1 = rt.prepare_cache(config, root, refresh=False, jobs=2)
                self.assertTrue(ok1)
                self.assertEqual(one.name, 'site.__staging__')
                old_content = (one / 'esp-labs/assets/main.js').read_text()
                origin_file = root / 'origin/esp-labs/assets/main.js'
                origin_file.write_text('window.appStarted = "new version";')
                with patch('esp_labs_runtime.shutil.copy2', side_effect=AssertionError('bulk copying prohibited')), \
                     patch.object(Path, 'rename', side_effect=PermissionError(13, 'rename prohibited')):
                    two, ok2 = rt.prepare_cache(config, root, refresh=True, jobs=2)
                self.assertTrue(ok2)
                self.assertEqual(two.name, 'site.__next__')
                self.assertIn('new version', (two / 'esp-labs/assets/main.js').read_text())
                self.assertEqual((one / 'esp-labs/assets/main.js').read_text(), old_content)
                self.assertEqual(rt.active_cache(root), two)
                self.assertEqual(json.loads((root / rt.ACTIVE_MARKER).read_text())['active'], two.name)
                origin_file.write_text('window.appStarted = "third version";')
                three, ok3 = rt.prepare_cache(config, root, refresh=True, jobs=2)
                self.assertTrue(ok3)
                self.assertEqual(three.name, 'site.__staging__')
                self.assertIn('third version', (three / 'esp-labs/assets/main.js').read_text())
                self.assertEqual(rt.active_cache(root), three)
            finally:
                stop_server(source, worker)

    def test_21_failed_refresh_retains_verified_cache(self):
        import esp_labs_runtime as rt
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src, worker, config = self.prepare_fixture(root)
            try:
                previous, good = rt.prepare_cache(config, root, jobs=2)
                self.assertTrue(good)
                with patch('esp_labs_runtime.SubpathMirror.run', return_value=False):
                    still_active, refreshed = rt.prepare_cache(config, root, refresh=True, jobs=2)
                self.assertFalse(refreshed)
                self.assertEqual(still_active, previous)
                self.assertEqual(rt.active_cache(root), previous)
                self.assertTrue(check_site(previous, verbose=False)[0])
            finally:
                stop_server(src, worker)

    def test_22_check_command_accepts_live_staging_slot(self):
        import esp_labs_runtime as rt
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, worker, config = self.prepare_fixture(root)
            try:
                self.assertTrue(SubpathMirror(config, root / 'site.__staging__', jobs=2).run())
            finally:
                stop_server(source, worker)
            # The CLI loads config from the project directory, so use the
            # real project directory for localization but a temporary cache
            # by mocking its cache selector.
            with patch('sys.argv', ['verify_clone.py']), \
                 patch('esp_labs_runtime.active_cache', return_value=root/'site.__staging__'):
                self.assertEqual(rt.main('check', ROOT/'ESP32Labs'), 0)

    def test_23_verified_staging_can_serve_html_css_js_and_health(self):
        import esp_labs_runtime as rt
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            origin, origin_worker, config = self.prepare_fixture(root)
            try:
                site, success = rt.prepare_cache(config, root, jobs=2)
                self.assertTrue(success)
                web, worker = start_server(rt.make_handler(config, site, ROOT/'ESP32Labs', translator=DummyTranslator()))
                try:
                    prefix = 'http://127.0.0.1:%d' % web.server_port
                    self.assertIn(b'ESP32 Labs', urlopen(prefix+'/esp-labs/').read())
                    self.assertIn(b'font-family', urlopen(prefix+'/esp-labs/assets/main.css').read())
                    self.assertIn(b'appStarted', urlopen(prefix+'/esp-labs/assets/main.js').read())
                    self.assertEqual(json.load(urlopen(prefix+'/__clone_health__'))['clone_id'], 'esp32-labs')
                finally:
                    stop_server(web, worker)
            finally:
                stop_server(origin, origin_worker)

    def test_24_denied_pointer_update_preserves_previous_active_slot(self):
        import esp_labs_runtime as rt
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, worker, config = self.prepare_fixture(root)
            try:
                first, ok = rt.prepare_cache(config, root, jobs=2)
                self.assertTrue(ok)
                with patch('esp_labs_runtime._write_active_pointer', side_effect=PermissionError(13,'pointer locked')):
                    active, updated = rt.prepare_cache(config, root, refresh=True, jobs=2)
                self.assertFalse(updated)
                self.assertEqual(active, first)
                self.assertEqual(rt.active_cache(root), first)
                self.assertTrue(check_site(first, verbose=False)[0])
            finally:
                stop_server(source, worker)

    def test_25_rerun_verified_stage_requires_no_network(self):
        import esp_labs_runtime as rt
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            origin, worker, config = self.prepare_fixture(root)
            try:
                stage, ok = rt.prepare_cache(config, root, jobs=2)
                self.assertTrue(ok)
            finally:
                stop_server(origin, worker)
            with patch('esp_labs_runtime.SubpathMirror.run', side_effect=AssertionError('offline test forbids download')):
                cache, success = rt.prepare_cache(config, root, refresh=False)
            self.assertTrue(success)
            self.assertEqual(cache, stage)


    def test_26_real_size_stage_with_583_files_starts_without_copy(self):
        """Regression for the screenshot: 583 staged assets, stalled on Copying."""
        import esp_labs_runtime as rt
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src, worker, config = self.prepare_fixture(root)
            try:
                stage = root / 'site.__staging__'
                self.assertTrue(SubpathMirror(config, stage, jobs=2).run())
                extra = stage / 'esp-labs/assets'
                for i in range(576):
                    (extra / ('dummy%04d.js' % i)).write_text('const a = 1;')
                self.assertEqual(rt._file_count(stage), 583)
            finally:
                stop_server(src, worker)
            with patch('esp_labs_runtime.shutil.copy2', side_effect=AssertionError('no bulk file copying')), \
                 patch.object(Path, 'rename', side_effect=PermissionError(13,'rename forbidden')), \
                 patch('esp_labs_runtime.SubpathMirror.run', side_effect=AssertionError('no download')):
                path, ok = rt.prepare_cache(config, root, refresh=False)
            self.assertTrue(ok)
            self.assertEqual(path, stage)
            self.assertEqual(rt._file_count(path), 583)

if __name__ == '__main__':
    unittest.main()
