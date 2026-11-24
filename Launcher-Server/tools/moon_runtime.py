"""Moon Life local mirror with optional Thai translation overlay.

Original website files are downloaded only to the user's own cache. No game
logic is rewritten. Thai localization is served through a separate same-origin
script, CSS and an opt-out-able network translation endpoint.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import ThreadingHTTPServer
import argparse
import json
import os
from pathlib import Path
import re
import threading
import time
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, urlopen
import webbrowser

from clone_runtime import (HOST, VERSION, UA, check_site, existing_server,
                           load_config, local_url, make_handler, port_in_use,
                           update_site)

MAX_TEXTS = 20
MAX_TEXT_LENGTH = 2200
MAX_TOTAL_LENGTH = 18000
SCRIPT_URL = '/__moonlife__/thai_overlay.js'
STYLE_URL = '/__moonlife__/thai_overlay.css'
DICTIONARY_URL = '/__moonlife__/thai_dictionary.json'
TRANSLATION_URL = '/__moonlife__/translate'
PANEL_MARKUP = ('<link rel="stylesheet" href="' + STYLE_URL + '">'
                '<script src="' + SCRIPT_URL + '" defer></script>')


def inject_overlay(document):
    """Inject local overlay into HTML, preserving original application files."""
    if SCRIPT_URL in document:
        return document
    match = re.search(r'</head\s*>', document, re.I)
    if match:
        return document[:match.start()] + PANEL_MARKUP + document[match.start():]
    match = re.search(r'</body\s*>', document, re.I)
    if match:
        return document[:match.start()] + PANEL_MARKUP + document[match.start():]
    return document + PANEL_MARKUP


def _is_translatable(value):
    if not isinstance(value, str) or not (1 <= len(value) <= MAX_TEXT_LENGTH):
        return False
    return bool(re.search(r'[A-Za-z\u3130-\u318f\uac00-\ud7af\u3040-\u30ff\u4e00-\u9fff]', value))


def translate_google(text):
    """Unofficial public endpoint, best-effort; network availability not guaranteed."""
    query = urlencode({'client': 'gtx', 'sl': 'auto', 'tl': 'th', 'dt': 't', 'q': text})
    url = 'https://translate.googleapis.com/translate_a/single?' + query
    request = Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
    with urlopen(request, timeout=12) as response:
        payload = json.loads(response.read().decode('utf-8'))
    segments = payload[0] if payload and isinstance(payload, list) else []
    result = ''.join(segment[0] for segment in segments if isinstance(segment, list)
                     and segment and isinstance(segment[0], str))
    if not result.strip():
        raise ValueError('Translation service returned no text')
    return result


class TranslationService:
    def __init__(self, project_dir, translator=translate_google):
        self.store = Path(project_dir) / 'translation_cache.json'
        self.cache = {}
        self.lock = threading.RLock()
        self.translator = translator
        if self.store.is_file():
            try:
                existing = json.loads(self.store.read_text(encoding='utf-8'))
                if isinstance(existing, dict):
                    self.cache = {str(k): str(v) for k, v in existing.items()
                                  if isinstance(v, str)}
            except (ValueError, OSError) as error:
                print('Warning: Could not load translation cache:', error)

    def translate(self, text, online=True):
        if not _is_translatable(text):
            return None
        with self.lock:
            if text in self.cache:
                return self.cache[text]
        if not online:
            return None
        try:
            result = self.translator(text)
        except Exception as error:
            print('[Thai] Online translation unavailable: %s' % type(error).__name__, flush=True)
            return None
        with self.lock:
            self.cache[text] = result
        return result

    def translate_many(self, items, online=True):
        items = items[:MAX_TEXTS]
        results = [None] * len(items)
        if not online:
            for idx, item in enumerate(items):
                results[idx] = self.translate(item, online=False)
            return results
        with ThreadPoolExecutor(max_workers=4) as pool:
            work = {pool.submit(self.translate, item, True): idx
                    for idx, item in enumerate(items)}
            for future in as_completed(work):
                idx = work[future]
                try:
                    results[idx] = future.result()
                except Exception:
                    pass
        self.save()
        return results

    def save(self):
        with self.lock:
            self.store.parent.mkdir(parents=True, exist_ok=True)
            out = self.store.with_name(self.store.name + '.part')
            out.write_text(json.dumps(self.cache, ensure_ascii=False, indent=1), encoding='utf-8')
            out.replace(self.store)


def make_moon_handler(config, site, project_dir, translator=None):
    original = make_handler(config, site)
    script = Path(project_dir) / 'translation' / 'thai_overlay.js'
    stylesheet = Path(project_dir) / 'translation' / 'thai_overlay.css'
    dictionary = Path(project_dir) / 'translation' / 'thai_dictionary.json'
    translations = translator or TranslationService(project_dir)
    site = Path(site)

    class MoonHandler(original):
        server_version = 'SimulationLearningMoon/' + VERSION

        def _send_blob(self, body, mime, head=False):
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            if not head:
                self.wfile.write(body)

        def _is_document_request(self, path):
            if path in ('/', '/index.html'):
                return True
            if path.startswith('/__moonlife__/') or path.startswith('/__clone_health__'):
                return False
            # Fallback history-based application routes, if ever used upstream.
            return (not Path(path).suffix and not (site / path.lstrip('/')).exists())

        def _handle_local(self, head=False):
            path = urlsplit(self.path).path
            if path == SCRIPT_URL:
                self._send_blob(script.read_bytes(), 'text/javascript; charset=utf-8', head)
                return True
            if path == STYLE_URL:
                self._send_blob(stylesheet.read_bytes(), 'text/css; charset=utf-8', head)
                return True
            if path == DICTIONARY_URL:
                self._send_blob(dictionary.read_bytes(), 'application/json; charset=utf-8', head)
                return True
            if self._is_document_request(path):
                html_file = site / 'index.html'
                if not html_file.is_file():
                    self.send_error(404, 'Local web assets are not downloaded yet')
                    return True
                original_html = html_file.read_text(encoding='utf-8-sig')
                # Preserve document content exactly, only add references to our local overlay.
                body = inject_overlay(original_html).encode('utf-8')
                self._send_blob(body, 'text/html; charset=utf-8', head)
                return True
            return False

        def do_GET(self):
            if self._handle_local():
                return
            super().do_GET()

        def do_HEAD(self):
            if self._handle_local(head=True):
                return
            super().do_HEAD()

        def do_POST(self):
            if urlsplit(self.path).path != TRANSLATION_URL:
                self.send_error(404)
                return
            origin = self.headers.get('Origin', '')
            expected = 'http://127.0.0.1:%d' % self.server.server_port
            expected_localhost = 'http://localhost:%d' % self.server.server_port
            if origin and origin not in (expected, expected_localhost):
                self.send_error(403, 'Only same-origin local translation requests are allowed')
                return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not (1 <= length <= 60000):
                    raise ValueError('Invalid request size')
                data = json.loads(self.rfile.read(length).decode('utf-8'))
                texts = data['texts']
                online = data.get('online', True) is True
                if (not isinstance(texts, list) or len(texts) > MAX_TEXTS or
                    any(not isinstance(s, str) or len(s) > MAX_TEXT_LENGTH for s in texts) or
                    sum(len(s) for s in texts) > MAX_TOTAL_LENGTH):
                    raise ValueError('Too many or overlong translation inputs')
            except (ValueError, TypeError, KeyError, UnicodeDecodeError) as exc:
                self.send_error(400, str(exc))
                return
            results = translations.translate_many(texts, online=online)
            payload = json.dumps({'results': results, 'online': online}, ensure_ascii=False).encode('utf-8')
            self._send_blob(payload, 'application/json; charset=utf-8')

    return MoonHandler


def serve_moon(config, directory, port=None, no_browser=False, update=False):
    directory = Path(directory)
    port = port or int(config['port'])
    url = local_url(config, port)
    if existing_server(config, port):
        print('Already running:', url)
        if not no_browser:
            webbrowser.open(url)
        return 0
    if port_in_use(port):
        print('ERROR: Port %d is used by another program.' % port)
        return 2
    site = directory / 'site'
    if update or not check_site(site, verbose=False)[0]:
        print('Downloading public original site to local cache (first run needs internet)...', flush=True)
        try:
            success = update_site(config, directory)
        except Exception as exc:
            print('ERROR: Could not mirror:', exc)
            success = False
        if not success and not check_site(site, verbose=False)[0]:
            print('ERROR: No working cached site. Browser will NOT open a blank page.')
            return 1
        if not success:
            print('WARNING: Reusing previous working cache.')
    try:
        server = ThreadingHTTPServer((HOST, port), make_moon_handler(config, site, directory))
    except OSError as error:
        print('ERROR: Could not bind port:', error)
        return 2
    print('=' * 65)
    print('%s | Local toolkit v%s' % (config['name'], VERSION))
    print('URL:', url)
    print('TH is on by default. Switch TH / EN in the overlay.')
    print('Online translation sends displayed text to Google Translate; disable via overlay.')
    print('Cached translations:', directory / 'translation_cache.json')
    print('Press Ctrl+C / close this window to stop the local server.')
    print('=' * 65, flush=True)
    if not no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print('Stopping Moon Life...')
    finally:
        server.server_close()
    return 0


def main(command, project_dir):
    config = load_config(project_dir)
    parser = argparse.ArgumentParser(description='Project Moon Life ' + command)
    if command == 'serve':
        parser.add_argument('--port', type=int)
        parser.add_argument('--no-browser', action='store_true')
        parser.add_argument('--update', action='store_true')
    elif command == 'mirror':
        parser.add_argument('--jobs', type=int, default=12)
    args = parser.parse_args()
    print('%s | SimulationLearning %s' % (config['name'], VERSION), flush=True)
    if command == 'serve':
        return serve_moon(config, project_dir, args.port, args.no_browser, args.update)
    if command == 'mirror':
        return 0 if update_site(config, project_dir, args.jobs) else 1
    if command == 'check':
        valid = all((Path(project_dir) / 'translation' / f).is_file()
                    for f in ('thai_overlay.js', 'thai_overlay.css', 'thai_dictionary.json'))
        print('Thai translation overlay:', 'PASS' if valid else 'FAIL')
        return 0 if valid and check_site(Path(project_dir) / 'site')[0] else 1
    raise ValueError('Invalid command')
