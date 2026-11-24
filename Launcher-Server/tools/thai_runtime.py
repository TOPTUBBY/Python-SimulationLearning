"""Optional Thai UI overlay for eight SimulationLearning frontends.

The original mirrored HTML/JS/CSS stays on disk unchanged. The local server
injects a small independent accessibility/localization layer into HTML responses.
No upstream website sources are republished with this package.
"""
from __future__ import annotations

import argparse
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote
import webbrowser

from clone_runtime import (HOST, VERSION, check_site, existing_server, load_config,
                           local_url, make_handler, port_in_use, update_site)
from moon_runtime import TranslationService

LOCALE_ROOT = Path(__file__).resolve().parents[1] / 'localization'
ROUTE = '/__thai__/'
SCRIPT_URL = ROUTE + 'overlay.js'
STYLE_URL = ROUTE + 'overlay.css'
DICTIONARY_URL = ROUTE + 'dictionary.json'
TRANSLATE_URL = ROUTE + 'translate'
MAX_ITEMS, MAX_PER_ITEM, MAX_TOTAL = 20, 2200, 18000


def inject_overlay(document, site_id, thai_default=False, online_default=False):
    """Insert same-origin overlay references before closing HEAD, once only."""
    if SCRIPT_URL in document:
        return document
    import html
    attrs = ' data-site="%s" data-default="%s" data-online="%s"' % (
        html.escape(site_id, quote=True), 'th' if thai_default else 'original',
        'true' if online_default else 'false')
    markup = ('<link rel="stylesheet" href="%s">' % STYLE_URL +
              '<script src="%s"%s defer></script>' % (SCRIPT_URL, attrs))
    match = re.search(r'</head\s*>', document, re.I)
    if not match:
        match = re.search(r'</body\s*>', document, re.I)
    if match:
        return document[:match.start()] + markup + document[match.start():]
    return document + markup


def load_dictionary(config):
    """Merge curated phrase translations (common + site-specific)."""
    common = json.loads((LOCALE_ROOT / 'common_th.json').read_text(encoding='utf-8'))
    site = json.loads((LOCALE_ROOT / 'sites' / (config['id'] + '.json')).read_text(encoding='utf-8'))
    if not isinstance(common, dict) or not isinstance(site, dict):
        raise ValueError('Localization dictionaries must be JSON objects')
    common.update(site)
    return common


def make_thai_handler(config, site, project_dir, translator=None):
    """Wrap base mirror/SPA server. All file, asset and health requests stay intact."""
    base = make_handler(config, site)
    site = Path(site).resolve()
    project_dir = Path(project_dir).resolve()
    dictionary = json.dumps(load_dictionary(config), ensure_ascii=False).encode('utf-8')
    js = (LOCALE_ROOT / 'thai_overlay.js').read_bytes()
    css = (LOCALE_ROOT / 'thai_overlay.css').read_bytes()
    service = translator or TranslationService(project_dir)

    class ThaiHandler(base):
        def _send_bytes(self, body, mime, head=False):
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            if not head:
                self.wfile.write(body)

        def _index_route(self, path):
            if path == '/' or path == '/index.html':
                return True
            if path.startswith(ROUTE) or path == '/__clone_health__':
                return False
            if '\\' in path or '\0' in path or '..' in path.split('/'):
                return False
            return not Path(path).suffix and not (site / path.lstrip('/')).is_file() and not (site / path.lstrip('/')).is_dir()

        def _local(self, head=False):
            path = unquote(urlsplit(self.path).path)
            if path == SCRIPT_URL:
                self._send_bytes(js, 'text/javascript; charset=utf-8', head)
                return True
            if path == STYLE_URL:
                self._send_bytes(css, 'text/css; charset=utf-8', head)
                return True
            if path == DICTIONARY_URL:
                self._send_bytes(dictionary, 'application/json; charset=utf-8', head)
                return True
            if path.startswith(ROUTE):
                self.send_error(404)
                return True
            if self._index_route(path):
                index = site / 'index.html'
                if not index.is_file():
                    self.send_error(404, 'Local cache not available; run Update_Clone.bat first')
                    return True
                original = index.read_text(encoding='utf-8-sig')
                translated = inject_overlay(original, config['id'],
                                            config.get('thai_default', False),
                                            config.get('online_translation_default', False))
                self._send_bytes(translated.encode('utf-8'), 'text/html; charset=utf-8', head)
                return True
            return False

        def do_GET(self):
            if not self._local():
                super().do_GET()

        def do_HEAD(self):
            if not self._local(head=True):
                super().do_HEAD()

        def do_POST(self):
            if urlsplit(self.path).path != TRANSLATE_URL:
                self.send_error(404)
                return
            origin = self.headers.get('Origin', '')
            allowed = ('http://%s:%s' % (HOST, self.server.server_port),
                       'http://localhost:%s' % self.server.server_port)
            if origin and origin not in allowed:
                self.send_error(403, 'Same-origin requests only')
                return
            try:
                if not self.headers.get('Content-Type', '').lower().startswith('application/json'):
                    raise ValueError('Expected application/json')
                length = int(self.headers.get('Content-Length', '0'))
                if not (1 <= length <= 60000):
                    raise ValueError('Invalid request size')
                payload = json.loads(self.rfile.read(length).decode('utf-8'))
                items = payload['texts']
                online = payload.get('online', False) is True
                if (not isinstance(items, list) or len(items) > MAX_ITEMS or
                    any(not isinstance(x, str) or len(x) > MAX_PER_ITEM for x in items) or
                    sum(len(x) for x in items) > MAX_TOTAL):
                    raise ValueError('Invalid translation items')
            except (ValueError, KeyError, UnicodeDecodeError, TypeError) as error:
                self.send_error(400, str(error))
                return
            result = service.translate_many(items, online=online)
            body = json.dumps({'results': result, 'online': online}, ensure_ascii=False).encode('utf-8')
            self._send_bytes(body, 'application/json; charset=utf-8')

    return ThaiHandler


def serve(config, project_dir, port=None, no_browser=False, update=False):
    project_dir = Path(project_dir)
    port = int(port or config['port'])
    url = local_url(config, port)
    if existing_server(config, port):
        print('Already running:', url)
        if not no_browser:
            webbrowser.open(url)
        return 0
    if port_in_use(port):
        print('ERROR: Port %s already in use.' % port)
        return 2
    cache = project_dir / 'site'
    if update or not check_site(cache, verbose=False)[0]:
        print('Downloading original website assets; first run needs Internet...', flush=True)
        try:
            ok = update_site(config, project_dir)
        except Exception as error:
            print('Mirror error:', error)
            ok = False
        if not ok and not check_site(cache, verbose=False)[0]:
            print('ERROR: No valid local copy. Browser not opened.')
            return 1
        if not ok:
            print('WARNING: Using last known good cache')
    try:
        server = ThreadingHTTPServer((HOST, port), make_thai_handler(config, cache, project_dir))
    except OSError as error:
        print('Bind error:', error)
        return 2
    print('Project:', config['name'])
    print('Local URL:', url)
    print('Local Thai UI overlay: TH / Original')
    print('Optional online translation: text is sent to Google Translate only when enabled')
    print('Press Ctrl+C or close CMD to stop.', flush=True)
    if not no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def main(command, project_dir):
    config = load_config(project_dir)
    parser = argparse.ArgumentParser(description='Thai-enabled Local Clone: ' + command)
    if command == 'serve':
        parser.add_argument('--port', type=int)
        parser.add_argument('--no-browser', action='store_true')
        parser.add_argument('--update', action='store_true')
    elif command == 'mirror':
        parser.add_argument('--jobs', type=int, default=12)
    args = parser.parse_args()
    if command == 'serve':
        return serve(config, project_dir, args.port, args.no_browser, args.update)
    if command == 'mirror':
        return 0 if update_site(config, project_dir, args.jobs) else 1
    if command == 'check':
        try:
            entries = load_dictionary(config)
            ok = bool(entries) and (LOCALE_ROOT / 'thai_overlay.js').is_file() and (LOCALE_ROOT / 'thai_overlay.css').is_file()
        except (OSError, ValueError) as error:
            print('[Thai] File error:', error)
            ok = False
        print('TH translation resources:', 'PASS' if ok else 'FAIL')
        local_ok = check_site(Path(project_dir) / 'site')[0]
        return 0 if ok and local_ok else 1
    raise ValueError('Unknown command: ' + command)
