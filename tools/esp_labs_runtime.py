"""ESP32 Labs subfolder-aware mirror and Thai UI server.

The published app lives at https://ionloft.com/esp-labs/ (not at /).
Its relative Vite assets must keep their /esp-labs/ prefix. We preserve
those paths in site/ and inject only the independently authored Thai overlay.
Standard-library-only, Python >=3.8, no third-party site assets distributed.
"""
from __future__ import annotations

import argparse
from http.server import ThreadingHTTPServer
from pathlib import Path
import json
import os
import shutil
import time
from urllib.parse import urljoin, urlsplit, unquote
import webbrowser

from clone_runtime import (Mirror, HTMLAssets, EXTENSIONS, HOST, VERSION,
                           QUOTED_ASSET, ROOT_ASSET, CSS_URL, CSS_IMPORT,
                           load_config, origin_url, local_url,
                           existing_server, port_in_use)
from thai_runtime import (make_thai_handler, inject_overlay, load_dictionary,
                          LOCALE_ROOT)

SUBPATH = "/esp-labs/"
REDIRECT = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta http-equiv="refresh" content="0;url=/esp-labs/#/?lang=en">
<title>ESP32 Labs</title><a href="/esp-labs/#/?lang=en">Open ESP32 Labs</a></html>"""


def check_site(site, verbose=True):
    """Validate the actual entrypoint in the subfolder, not just redirect HTML."""
    site = Path(site)
    entry = site / "esp-labs" / "index.html"
    missing = []
    if not entry.is_file():
        missing.append("esp-labs/index.html")
    else:
        try:
            source = entry.read_text(encoding="utf-8-sig")
            parser = HTMLAssets()
            parser.feed(source)
            for raw in parser.refs:
                url = urlsplit(raw)
                if url.scheme or url.netloc or raw.startswith("//"):
                    continue
                p = unquote(url.path)
                if not p or not Path(p).suffix:
                    continue
                if "\\" in p or ".." in p.split("/"):
                    missing.append("unsafe reference " + raw)
                    continue
                target = (site / (p.lstrip("/") if p.startswith("/") else "esp-labs/" + p)).resolve()
                if not (target == site.resolve() or site.resolve() in target.parents) or not target.is_file():
                    missing.append(raw)
        except (OSError, UnicodeError, ValueError) as exc:
            missing.append("invalid entrypoint: " + str(exc))
    if not list((site / "esp-labs").rglob("*.js")) and not list((site / "esp-labs").rglob("*.mjs")):
        missing.append("JavaScript bundle")
    manifest_file = site / ".clone-manifest.json"
    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        if not manifest.get("source", "").endswith(SUBPATH):
            missing.append("manifest source path")
    except (OSError, ValueError):
        missing.append("download manifest")
    if verbose:
        print("ESP32 Labs path:", SUBPATH)
        print("Files:", sum(p.is_file() for p in site.rglob("*")))
        for item in missing[:20]:
            print("MISSING:", item)
        print("PASS: ESP32 Labs entrypoint and assets validated" if not missing else
              "FAIL: missing files. Run Update_Clone.bat while online")
        print("NOTE: Validation cannot prove all labs, graphics or offline features work.")
    return not missing, missing


class SubpathMirror(Mirror):
    """Reuse shared Mirror while retaining subfolder relative asset URLs."""
    def __init__(self, config, directory, jobs=12):
        super().__init__(config, directory, jobs=jobs)
        self.base = urljoin(origin_url(config), SUBPATH)
        self.entry = self.base

    def enqueue(self, raw, parent=None):
        raw = str(raw).strip()
        resolved = urljoin(parent or self.base, raw)
        if resolved == self.entry:
            with self.lock:
                if resolved in self.seen:
                    return
                self.seen.add(resolved)
            self.queue.put((resolved, Path("esp-labs/index.html")))
        else:
            super().enqueue(raw, parent)

    def discover(self, url, rel, content):
        """Resolve Vite asset names against the original /esp-labs/ base."""
        if rel.suffix.lower() not in ('.html', '.js', '.mjs', '.json', '.css', '.svg', '.webmanifest'):
            return
        try:
            source = content.decode('utf-8-sig')
        except UnicodeDecodeError:
            return
        if rel.suffix.lower() == '.html':
            parser = HTMLAssets()
            parser.feed(source)
            for value in parser.refs:
                self.enqueue(value, url)
        if rel.suffix.lower() in ('.html', '.css', '.svg'):
            for value in CSS_URL.findall(source) + CSS_IMPORT.findall(source):
                self.enqueue(value, url)
        for match in QUOTED_ASSET.finditer(source):
            raw = match.group(1)
            if rel.suffix.lower() in ('.js','.mjs','.json') and raw.lstrip('./').startswith('assets/'):
                raw = '/esp-labs/' + raw.lstrip('./')
            self.enqueue(raw, url)
        for match in ROOT_ASSET.finditer(source):
            raw = match.group(0).lstrip('./')
            self.enqueue('/esp-labs/' + raw, url)

    def run(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        (self.directory / "index.html").write_text(REDIRECT, encoding="utf-8")
        preliminary = super().run()
        valid, missing = check_site(self.directory, verbose=False)
        if not valid:
            print("[ESP32 Labs] Missing:", ", ".join(missing[:12]))
        return preliminary and valid


def _copy_verified_stage(staging, target):
    """Install a new cache without renaming a directory (Windows-safe).

    On Windows, real-time antivirus scanners, Explorer or other open handles
    may prevent a directory rename for a short period, even though regular
    file copies are possible. Never remove the already downloaded staging
    copy before validating the installed cache.
    """
    if target.exists() and not target.is_dir():
        print('[ERROR] Cache destination exists and is not a folder:', target)
        return False
    files = sorted(p for p in staging.rglob('*') if p.is_file())
    if not files:
        print('[ERROR] No downloaded files in staging.')
        return False
    print('[Install] Copying %d downloaded files into site/ (Windows-safe).' % len(files), flush=True)
    count = 0
    for original in files:
        dest = target / original.relative_to(staging)
        for attempt in range(5):
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(original, dest)
                count += 1
                break
            except OSError as exc:
                if attempt == 4:
                    print('[ERROR] Cannot copy %s: %s' % (dest, exc), flush=True)
                    print('The completed staging cache is still intact. Close Explorer/antivirus locks '
                          'and rerun Launcher.bat; it will reuse the download.', flush=True)
                    return False
                time.sleep(0.35 * (attempt + 1))
    verified, missing = check_site(target, verbose=False)
    if not verified:
        print('[ERROR] Installed cache did not pass validation:', ', '.join(missing[:10]))
        print('Staging was preserved for a retry.', flush=True)
        return False
    try:
        shutil.rmtree(staging)
    except OSError as exc:
        print('[WARN] Cache installed, but staging could not be cleaned up:', exc)
    print('[Install] OK: %d files installed and verified in %s' % (count, target), flush=True)
    return True


def update_site(config, directory, jobs=12):
    """Download and install safely, preserving valid caches and staging.

    Initial installation is copy-based to work around WinError 5 on Windows.
    Existing valid caches are swapped transactionally if possible; when
    Windows holds a directory lock, keep the old cache and downloaded stage
    rather than crash, and allow the next run to finish the update.
    """
    directory = Path(directory).resolve()
    target = directory / 'site'
    staging = directory / 'site.__staging__'
    backup = directory / 'site.__backup__'

    stage_ready = check_site(staging, verbose=False)[0]
    if stage_ready:
        print('[Recovery] Reusing existing verified staging download; no redownload needed.', flush=True)
    else:
        if staging.exists():
            try:
                shutil.rmtree(staging)
            except OSError as exc:
                print('[ERROR] Cannot clean invalid staging folder:', exc)
                print('Close programs using files in site.__staging__ and retry.')
                return False
        try:
            stage_ready = SubpathMirror(config, staging, jobs=jobs).run()
        except Exception as exc:
            print('[ERROR] Mirror failed:', exc)
            stage_ready = False
        if not stage_ready:
            print('[ERROR] Download incomplete; existing site/ cache is unchanged.')
            # A partially downloaded stage cannot be used for offline recovery.
            # Keep only fully verified staging caches after install/rename failures.
            try:
                shutil.rmtree(staging)
            except OSError as exc:
                print('[WARN] Could not remove incomplete staging:', exc)
            print('Try Update_Clone.bat again while online.')
            return False

    old_valid = check_site(target, verbose=False)[0]
    if not old_valid:
        # Do not rename site.__staging__: Windows may block the rename even
        # though all ~hundreds of source files have downloaded successfully.
        return _copy_verified_stage(staging, target)

    # A working cache already exists. Avoid changing a potentially serving
    # cache on disk unless both directory moves can complete.
    if backup.exists():
        try:
            shutil.rmtree(backup)
        except OSError as exc:
            print('[WARN] Cannot remove old backup:', exc)
            print('Current cache and downloaded staging are preserved for retry.')
            return False
    moved_old = False
    try:
        target.rename(backup)
        moved_old = True
        staging.rename(target)
    except OSError as exc:
        print('[WARN] Windows prevented the cache folder switch:', exc)
        if moved_old and not target.exists():
            try:
                backup.rename(target)
            except OSError as restore_error:
                print('[WARN] Cannot rename old cache back:', restore_error)
                print('[Recovery] Copying old cache back into site/...')
                if not _copy_verified_stage(backup, target):
                    print('[ERROR] Old cache remains in site.__backup__. Do not delete it.')
        print('Old cache remains available where possible; staging download is kept.')
        print('Close Explorer/browser/server access to cache files, then rerun Update_Clone.bat.')
        return False
    except Exception:
        # Unexpected errors should still attempt restoration, without
        # deleting a valid backup.
        if moved_old and not target.exists():
            try:
                backup.rename(target)
            except OSError:
                _copy_verified_stage(backup, target)
        raise

    try:
        shutil.rmtree(backup)
    except OSError as exc:
        print('[WARN] New cache active but old backup could not be deleted:', exc)
    print('Updated offline cache:', target)
    return True


# Cache slots: no directory move or bulk copy is needed on Windows.
# A verified previous download in site.__staging__ remains a valid site cache.
CACHE_NAMES = ("site", "site.__staging__", "site.__next__")
ACTIVE_MARKER = "site.__active__.json"


def _file_count(path):
    return sum(1 for p in path.rglob("*") if p.is_file())


def active_cache(project_dir):
    """Select a verified cache without altering any files.

    Prefer an explicitly activated slot. For old rc.2 installations with a
    partially copied `site/`, choose the more complete verified staging cache.
    """
    root = Path(project_dir).resolve()
    marker = root / ACTIVE_MARKER
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
        slot = data.get("active")
        if slot in CACHE_NAMES and check_site(root / slot, verbose=False)[0]:
            return root / slot
    except (OSError, ValueError, TypeError):
        pass

    main = root / "site"
    stage = root / "site.__staging__"
    next_slot = root / "site.__next__"
    main_ok = check_site(main, verbose=False)[0]
    stage_ok = check_site(stage, verbose=False)[0]
    next_ok = check_site(next_slot, verbose=False)[0]
    if stage_ok and (not main_ok or _file_count(stage) > _file_count(main)):
        return stage
    if main_ok:
        return main
    if next_ok:
        return next_slot
    if stage_ok:
        return stage
    return None


def _write_active_pointer(project_dir, slot):
    """Atomically choose one of the two verified slots without moving assets."""
    root = Path(project_dir)
    marker = root / ACTIVE_MARKER
    temp_marker = root / (ACTIVE_MARKER + '.tmp')
    try:
        temp_marker.write_text(json.dumps({'active': slot}, indent=2) + '\n',
                               encoding='utf-8')
        os.replace(str(temp_marker), str(marker))
    finally:
        try:
            temp_marker.unlink()
        except OSError:
            pass


def prepare_cache(config, project_dir, refresh=False, jobs=12):
    """Return (active-cache-path, did_succeed) without copying ~600 files.

    The first launch serves a verified `site.__staging__` directly. For an
    explicit update, download into the inactive staging slot and switch a
    *small JSON marker*, preserving the previous cache if anything fails.
    No rename/copy of the site folder occurs in either case.
    """
    root = Path(project_dir).resolve()
    current = active_cache(root)
    if current is not None and not refresh:
        print('[Cache] Reusing verified assets: %s (%d files)' %
              (current.name, _file_count(current)), flush=True)
        print('[Cache] No copy or rename required.', flush=True)
        return current, True

    inactive = root / ('site.__next__' if current is not None and
                       current.name == 'site.__staging__' else 'site.__staging__')
    if current is not None and inactive == current:
        raise RuntimeError('Refusing to overwrite the active cache')

    # Explicit updates always re-fetch: an old inactive slot is not a new
    # version merely because it passes the HTML/asset entrypoint check.
    if inactive.exists():
        print('[Cache] Cleaning previous inactive cache: %s' % inactive.name, flush=True)
        try:
            shutil.rmtree(inactive)
        except OSError as exc:
            print('[ERROR] Cannot clear inactive cache:', exc, flush=True)
            return current, False
    print('[Mirror] Downloading to %s; active cache will stay unchanged.' %
          inactive.name, flush=True)
    try:
        success = SubpathMirror(config, inactive, jobs=jobs).run()
    except Exception as exc:
        print('[ERROR] Mirror failed:', exc, flush=True)
        success = False
    if not success or not check_site(inactive, verbose=False)[0]:
        print('[ERROR] Download incomplete; previous cache is preserved.', flush=True)
        return current, False

    # The first launch does not even need a marker. If the marker is blocked,
    # serving the validated cache remains possible, unlike a directory rename.
    try:
        _write_active_pointer(root, inactive.name)
    except OSError as exc:
        print('[WARN] Cannot save active-cache pointer:', exc, flush=True)
        if current is not None:
            return current, False
        # On a first install, there is no previous cache to preserve.
        # The verified candidate is safe to serve for this session.
    print('[Cache] ACTIVE: %s (%d files). No copy required.' %
          (inactive.name, _file_count(inactive)), flush=True)
    return inactive, True


def make_handler(config, site, project_dir, translator=None):
    parent = make_thai_handler(config, site, project_dir, translator=translator)
    site = Path(site).resolve()

    class Handler(parent):
        def _redirect(self, head=False):
            self.send_response(302)
            self.send_header("Location", config['launch_path'])
            self.send_header("Content-Length", "0")
            self.end_headers()

        def _local(self, head=False):
            path = unquote(urlsplit(self.path).path)
            if path in ('/', '/index.html', '/esp-labs'):
                self._redirect(head)
                return True
            if path.startswith(SUBPATH):
                rel = path.lstrip('/')
                entry_route = (path in (SUBPATH, SUBPATH + 'index.html') or
                               (not Path(path).suffix and not (site / rel).is_dir() and
                                not (site / rel).is_file()))
                if entry_route:
                    entry = site / 'esp-labs/index.html'
                    if not entry.is_file():
                        self.send_error(404, 'Site cache unavailable. Run Update_Clone.bat')
                        return True
                    html = inject_overlay(entry.read_text(encoding='utf-8-sig'), config['id'],
                                          config.get('thai_default', False),
                                          config.get('online_translation_default', False))
                    self._send_bytes(html.encode('utf-8'), 'text/html; charset=utf-8', head)
                    return True
            return super()._local(head=head)

    return Handler


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
        print('ERROR: Port %d is in use by another service.' % port)
        return 2
    if not active_cache(project_dir):
        print('First launch downloads the public original site (Internet required).', flush=True)
    cache, updated = prepare_cache(config, project_dir, refresh=update)
    if cache is None:
        print('ERROR: No verified cache. Browser will NOT open a blank page.', flush=True)
        return 1
    if update and not updated:
        print('[WARN] Update failed; using the previous verified cache.', flush=True)
    try:
        server = ThreadingHTTPServer((HOST, port), make_handler(config, cache, project_dir))
    except OSError as exc:
        print('Cannot open port:', exc)
        return 2
    print('ESP32 Labs | Thai UI Preview |', VERSION)
    print('Source:', config['original_url'])
    print('Cache directory:', cache, flush=True)
    print('Local:', url)
    print('Thai UI: default TH / switch to Original; online translation opt-in')
    print('Ctrl+C or close CMD to stop.', flush=True)
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
    if config.get('source_subpath') != SUBPATH:
        raise ValueError('Wrong ESP32 Labs source_subpath')
    parser = argparse.ArgumentParser(description='ESP32 Labs - ' + command)
    if command == 'serve':
        parser.add_argument('--port', type=int)
        parser.add_argument('--no-browser', action='store_true')
        parser.add_argument('--update', action='store_true')
    if command == 'mirror':
        parser.add_argument('--jobs', type=int, default=12)
    args = parser.parse_args()
    if command == 'serve':
        return serve(config, project_dir, args.port, args.no_browser, args.update)
    if command == 'mirror':
        return 0 if prepare_cache(config, project_dir, refresh=True, jobs=args.jobs)[1] else 1
    if command == 'check':
        try:
            dictionary = load_dictionary(config)
            resource_ok = (bool(dictionary) and (LOCALE_ROOT / 'thai_overlay.js').is_file() and
                           (LOCALE_ROOT / 'thai_overlay.css').is_file())
        except (OSError, ValueError) as exc:
            print('Thai resources invalid:', exc)
            resource_ok = False
        print('Thai resources:', 'PASS' if resource_ok else 'FAIL')
        cache = active_cache(project_dir)
        valid, _ = check_site(cache or project_dir / 'site')
        print('Active cache:', cache if cache else 'None')
        return 0 if valid and resource_ok else 1
    raise ValueError('Invalid command')
