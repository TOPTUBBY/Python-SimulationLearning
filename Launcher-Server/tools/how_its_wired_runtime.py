"""How It's Wired launcher with Windows-safe, no-directory-rename cache slots.

Only this project uses this optional wrapper. The ten existing websites and
shared clone_runtime / thai_runtime are not changed.
"""
from __future__ import annotations

import argparse
import json
from http.server import ThreadingHTTPServer
from pathlib import Path
import webbrowser

from clone_runtime import (
    HOST, Mirror, check_site, existing_server, load_config,
    local_url, port_in_use,
)
from thai_runtime import LOCALE_ROOT, load_dictionary, make_thai_handler

SLOTS = ("site", "site.__staging__", "site.__next__")
ACTIVE = ".active-cache.json"


def active_cache(project):
    project = Path(project).resolve()
    selector = project / ACTIVE
    try:
        slot = json.loads(selector.read_text(encoding="utf-8"))["slot"]
    except (OSError, ValueError, TypeError, KeyError):
        slot = None
    choices = ([slot] if slot in SLOTS else []) + [s for s in SLOTS if s != slot]
    for folder in choices:
        cache = project / folder
        if check_site(cache, verbose=False)[0]:
            return cache
    return None


def _activate(project, target):
    # Only a tiny selector is replaced; never rename/copy hundreds of assets.
    project = Path(project).resolve()
    name = Path(target).name
    if name not in SLOTS:
        raise ValueError("Unsafe cache slot")
    tmp = project / (ACTIVE + ".tmp")
    tmp.write_text(json.dumps({"slot": name}, indent=2) + "\n", encoding="utf-8")
    try:
        tmp.replace(project / ACTIVE)
    except PermissionError:
        # The prepared slot is still usable on this launch if Windows locks
        # the tiny selector; no expensive recovery copy is attempted.
        print("[WARN] Cache selector is locked; using verified slot directly", flush=True)
    return project / name


def prepare_cache(config, project, jobs=12, refresh=False):
    project = Path(project).resolve()
    current = active_cache(project)
    if current is not None and not refresh:
        print("[Cache] Reusing verified cache:", current.name, flush=True)
        return current
    available = [s for s in SLOTS if current is None or s != current.name]
    # Reuse a partial directory when no verified cache is present; otherwise
    # use the alternate slot and leave the currently working cache intact.
    target = project / ("site.__staging__" if current is None else available[-1])
    print("[Mirror] Downloading original assets into:", target.name, flush=True)
    try:
        ok = Mirror(config, target, jobs=jobs).run()
    except (OSError, ValueError) as exc:
        print("[Mirror] Error:", exc, flush=True)
        ok = False
    if ok and check_site(target, verbose=False)[0]:
        _activate(project, target)
        print("[Cache] Ready: no directory copy/rename", flush=True)
        return target
    if current is not None:
        print("[Cache] Refresh failed; keeping previous verified cache", flush=True)
        return current
    return None


def serve(config, project, port=None, no_browser=False, update=False):
    port = int(port or config["port"])
    launch_url = local_url(config, port)
    if existing_server(config, port):
        print("[Server] Already running:", launch_url, flush=True)
        if not no_browser:
            webbrowser.open(launch_url)
        return 0
    if port_in_use(port):
        print("[ERROR] Port %s already in use" % port, flush=True)
        return 2
    cache = prepare_cache(config, project, refresh=update)
    if cache is None:
        print("[ERROR] No verified cache. First run requires internet.", flush=True)
        return 1
    handler = make_thai_handler(config, cache, project)
    try:
        server = ThreadingHTTPServer((HOST, port), handler)
    except OSError as exc:
        print("[ERROR] Cannot bind local server:", exc)
        return 2
    print("[Server] How It's Wired at", launch_url, flush=True)
    print("[Thai] TH / Original; online translation disabled by default", flush=True)
    print("[Cache]", cache, flush=True)
    print("Close this CMD or press Ctrl+C to stop", flush=True)
    if not no_browser:
        webbrowser.open(launch_url)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def check(config, project):
    cache = active_cache(project)
    try:
        dictionary = load_dictionary(config)
        lang_ok = bool(dictionary) and (LOCALE_ROOT / "thai_overlay.js").is_file() and (LOCALE_ROOT / "thai_overlay.css").is_file()
    except (OSError, ValueError) as exc:
        print("[Thai]", exc)
        lang_ok = False
    print("[Thai]", "PASS" if lang_ok else "FAIL")
    if cache is not None:
        print("[Cache]", cache.name)
        passed, _ = check_site(cache)
    else:
        print("[Cache] NOT READY - run Launcher.bat while online")
        passed = False
    return 0 if passed and lang_ok else 1


def main(command, project):
    project = Path(project).resolve()
    config = load_config(project)
    parser = argparse.ArgumentParser(description="How It's Wired local clone")
    if command == "serve":
        parser.add_argument("--port", type=int)
        parser.add_argument("--no-browser", action="store_true")
        parser.add_argument("--update", action="store_true")
    if command == "mirror":
        parser.add_argument("--jobs", type=int, default=12)
    args = parser.parse_args()
    if command == "serve":
        return serve(config, project, args.port, args.no_browser, args.update)
    if command == "mirror":
        prior = active_cache(project)
        refreshed = prepare_cache(config, project, args.jobs, refresh=True)
        if refreshed is None or (prior is not None and refreshed == prior):
            print("[Mirror] Update failed or did not install new cache", flush=True)
            return 1
        return 0
    if command == "check":
        return check(config, project)
    raise ValueError("Unknown command: " + command)
