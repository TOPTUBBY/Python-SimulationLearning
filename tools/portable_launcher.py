"""Run a fully packaged SimulationLearning site from a single Windows EXE.

No Python runtime or manually opened CMD is needed on the end-user PC.
Original web assets are supplied by the person building the executable; the
repository and this module do not distribute them. No executable is built or
published automatically from unlicensed third-party assets.
"""
from __future__ import annotations

import argparse
from http.server import ThreadingHTTPServer
import json
import os
import time
from pathlib import Path
import sys
import threading
from urllib.parse import unquote, urlsplit
import webbrowser

from clone_runtime import (EXTENSIONS, HOST, existing_server, load_config,
                           local_url, port_in_use, check_site, Mirror)
from thai_runtime import make_thai_handler
from moon_runtime import TranslationService, make_moon_handler
from esp_labs_runtime import (make_handler as make_esp_labs_handler,
                              check_site as check_esp_cache,
                              active_cache as active_esp_cache,
                              prepare_cache as prepare_esp_cache)

SITES = ("ESP32", "Arduino", "RoverKit", "Multimeter", "Protocol",
         "DesignedToScale", "RoboticsLab", "ByteSizedAlgorithms", "MoonLife",
         "ESP32Labs")


def app_data(project):
    """Writable per-user state, separate from temporary PyInstaller _MEIPASS."""
    base = os.environ.get("LOCALAPPDATA")
    root = Path(base) if base else Path.home() / ".local" / "share"
    # project is one of the hard-coded names in SITES, never untrusted paths.
    if project not in SITES:
        raise ValueError("Unknown site: " + str(project))
    return root / "SimulationLearning" / project


def packed_site(bundle_root, project):
    """Return the read-only bundled cache path, failing closed when absent."""
    if project not in SITES:
        raise ValueError("Unknown site: " + str(project))
    root = Path(bundle_root).resolve()
    result = root / project / "site"
    index = result / ("esp-labs/index.html" if project == "ESP32Labs" else "index.html")
    if not index.is_file():
        raise FileNotFoundError("Website bundle missing: " + str(index))
    if not (root / project / "config.json").is_file():
        raise FileNotFoundError("Website config missing: " + project)
    return result


def _valid_cache(project, cache):
    if not cache or not Path(cache).is_dir():
        return False
    check = check_esp_cache if project == "ESP32Labs" else check_site
    try:
        return check(cache, verbose=False)[0]
    except (OSError, ValueError):
        return False


def prepare_site(bundle_root, project, state_dir, mode="bootstrap", progress=None):
    """Choose packaged assets or a verified per-user cache; never rename/copy big dirs.

    bootstrap: first run downloads directly into a user data cache slot.
    embedded: web files are required inside the PyInstaller executable.
    """
    root = Path(bundle_root).resolve()
    state = Path(state_dir).resolve()
    config = load_config(root / project)
    embedded = root / project / "site"
    if _valid_cache(project, embedded):
        return embedded
    if mode == "embedded":
        raise FileNotFoundError("Embedded assets missing or invalid for " + project)
    if mode != "bootstrap":
        raise ValueError("Unknown package mode: " + mode)
    if progress:
        progress("Checking local cache for " + project + "...")
    if project == "ESP32Labs":
        cache = active_esp_cache(state)
        if cache is not None:
            return cache
        if progress:
            progress("Downloading ESP32 Labs assets. First launch needs internet...")
        cache, _ = prepare_esp_cache(config, state, refresh=False)
        if cache is None or not _valid_cache(project, cache):
            raise RuntimeError("ESP32 Labs download incomplete. Check internet, then reopen EXE.")
        return cache
    for slot in ("site", "site.__staging__", "site.__next__"):
        cache = state / slot
        if _valid_cache(project, cache):
            return cache
    if progress:
        progress("Downloading " + project + " assets. First launch needs internet...")
    cache = state / "site.__staging__"
    # Existing verified cache is never replaced: failed downloads retain the
    # partial staging cache, and next launch can retry without a directory move.
    success = Mirror(config, cache, jobs=12).run()
    if not success or not _valid_cache(project, cache):
        raise RuntimeError("Mirror incomplete. No site will be opened. Retry when online.")
    return cache


def create_handler(bundle_root, project, state_dir=None, site=None, offline=False):
    """Use the original site-specific server and per-user translation cache."""
    root = Path(bundle_root).resolve()
    if project not in SITES:
        raise ValueError("Unknown site: " + str(project))
    state = Path(state_dir) if state_dir is not None else app_data(project)
    state.mkdir(parents=True, exist_ok=True)
    site = Path(site) if site is not None else packed_site(root, project)
    cfg = load_config(root / project)
    import thai_runtime
    thai_runtime.LOCALE_ROOT = root / "localization"
    translator = TranslationService(state)
    if project == "MoonLife":
        base = make_moon_handler(cfg, site, root / project, translator=translator)
    elif project == "ESP32Labs":
        base = make_esp_labs_handler(cfg, site, root / project, translator=translator)
    else:
        base = make_thai_handler(cfg, site, root / project, translator=translator)

    class PackagedHandler(base):
        def _missing_file(self):
            # Embedded mode is true offline; no network fetch into PyInstaller
            # temporary extraction. Bootstrap mode keeps the clone's normal
            # on-demand asset recovery in persistent user-data storage.
            if not offline:
                return False
            path = unquote(urlsplit(self.path).path)
            if path.startswith(("/__thai__/", "/__moonlife__/", "/__clone_health__")):
                return False
            rel = path.lstrip("/")
            if (Path(rel).suffix.lower() in EXTENSIONS and
                    not (site / rel).is_file()):
                self.send_error(404, "Asset not included in portable bundle")
                return True
            return False

        def do_GET(self):
            if not self._missing_file():
                super().do_GET()

        def do_HEAD(self):
            if not self._missing_file():
                super().do_HEAD()

    return cfg, PackagedHandler


def _prepare_with_ui(bundle_root, project, state_dir, mode, gui):
    """Show a responsive progress window during first-run network downloads."""
    if not gui:
        return prepare_site(bundle_root, project, state_dir, mode=mode)
    import tkinter as tk
    from tkinter import ttk
    window = tk.Tk()
    window.title("Preparing " + project + " | SimulationLearning")
    window.geometry("480x155")
    window.resizable(False, False)
    outer = ttk.Frame(window, padding=19)
    outer.pack(expand=True, fill="both")
    ttk.Label(outer, text="Preparing " + project, font=("Segoe UI", 12, "bold")).pack(anchor="w")
    status = tk.StringVar(value="Checking website assets...")
    ttk.Label(outer, textvariable=status, wraplength=435).pack(anchor="w", pady=(10, 6))
    progress_bar = ttk.Progressbar(outer, mode="indeterminate")
    progress_bar.pack(fill="x")
    progress_bar.start(12)
    # Cancelling a web download mid-write can damage partial files; minimize
    # until it safely completes instead of killing the worker thread.
    window.protocol("WM_DELETE_WINDOW", window.iconify)
    result, errors = [], []

    def report(value):
        status_messages.append(value)

    status_messages = []

    def worker():
        try:
            result.append(prepare_site(bundle_root, project, state_dir,
                                       mode=mode, progress=report))
        except Exception as exc:
            errors.append(exc)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    try:
        while thread.is_alive():
            if status_messages:
                status.set(status_messages[-1])
                status_messages.clear()
            window.update()
            time.sleep(0.08)
    finally:
        progress_bar.stop()
        window.destroy()
    if errors:
        raise errors[0]
    return result[0]


def show_error(message):
    """Windows message box: works even when PyInstaller has no console."""
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, str(message),
                                               "SimulationLearning Portable", 0x10)
            return
        except Exception:
            pass
    print("ERROR:", message, file=sys.stderr)


def open_control_window(config, url, stop_server, state_dir):
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("SimulationLearning | " + config["name"])
    root.geometry("530x220")
    root.minsize(460, 210)
    outer = ttk.Frame(root, padding=20)
    outer.pack(expand=True, fill="both")
    ttk.Label(outer, text=config["name"], font=("Segoe UI", 14, "bold")).pack(anchor="w")
    ttk.Label(outer, text="Portable web server running locally on port %d" % config["port"]).pack(anchor="w", pady=(8, 4))
    address = ttk.Entry(outer)
    address.insert(0, url)
    address.configure(state="readonly")
    address.pack(fill="x", pady=5)
    row = ttk.Frame(outer)
    row.pack(anchor="w", pady=12)
    ttk.Button(row, text="Open Website", command=lambda: webbrowser.open(url)).pack(side="left", padx=(0, 9))

    def close():
        stop_server()
        root.destroy()

    ttk.Button(row, text="Stop Server / Exit", command=close).pack(side="left")
    ttk.Label(outer, text="Close this window to stop the local website. Data: " + str(state_dir),
              wraplength=485, foreground="#666666").pack(anchor="w")
    root.protocol("WM_DELETE_WINDOW", close)
    root.mainloop()


def run(bundle_root, project, gui=True, browser=True, state_dir=None,
        port=None, ready=None, mode="bootstrap"):
    """Start bundled local server; `ready(url)` is used by headless tests."""
    if project not in SITES:
        raise ValueError("Unsupported site: " + str(project))
    root = Path(bundle_root).resolve()
    state = Path(state_dir) if state_dir else app_data(project)
    state.mkdir(parents=True, exist_ok=True)
    cfg = load_config(root / project)
    port = int(port or cfg["port"])
    url = local_url(cfg, port)
    if existing_server(cfg, port):
        if browser:
            webbrowser.open(url)
        return 0
    if port_in_use(port):
        raise OSError("Port %d is already being used by another application." % port)
    cache = _prepare_with_ui(root, project, state, mode=mode, gui=gui)
    cfg, handler = create_handler(root, project, state, site=cache,
                                  offline=(mode == "embedded"))
    httpd = ThreadingHTTPServer((HOST, port), handler)
    httpd.daemon_threads = True
    thread = threading.Thread(target=httpd.serve_forever, kwargs={"poll_interval": 0.2}, daemon=True)
    thread.start()
    stopped = False

    def stop():
        nonlocal stopped
        if not stopped:
            stopped = True
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=4)

    try:
        if ready:
            ready(url)
        if browser:
            webbrowser.open(url)
        if gui:
            open_control_window(cfg, url, stop, state)
        else:
            try:
                thread.join()
            except KeyboardInterrupt:
                pass
    finally:
        stop()
    return 0


def main(argv=None, bundle_root=None):
    parser = argparse.ArgumentParser(description="SimulationLearning Portable EXE")
    parser.add_argument("--site", choices=SITES, help="Development-only site override")
    parser.add_argument("--no-gui", action="store_true", help="Run server without Tk window")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--port", type=int, help="Port override for diagnostics")
    args = parser.parse_args(argv)
    root = Path(bundle_root or getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    selection = root / "portable_selection.json"
    if selection.is_file():
        selected = json.loads(selection.read_text(encoding="utf-8"))
        project = selected["project"]
        mode = selected.get("mode", "bootstrap")
        if args.site is not None and args.site != project:
            raise ValueError("This EXE is bound to %s, not %s" % (project, args.site))
    elif args.site:
        project = args.site
        mode = "bootstrap"
    else:
        raise FileNotFoundError("No portable_selection.json in packaged application")
    state = app_data(project)
    state.mkdir(parents=True, exist_ok=True)
    if getattr(sys, "frozen", False) and (sys.stdout is None or sys.stderr is None):
        # --windowed applications do not have a Windows console; avoid crashes
        # from print() in existing runtime modules, and retain diagnostics.
        logfile = (state / "portable.log").open("a", encoding="utf-8", buffering=1)
        if sys.stdout is None:
            sys.stdout = logfile
        if sys.stderr is None:
            sys.stderr = logfile
    try:
        return run(root, project, gui=not args.no_gui,
                   browser=not args.no_browser, port=args.port, state_dir=state,
                   mode=mode)
    except Exception as exc:
        print("Portable app failed:", repr(exc), file=sys.stderr)
        show_error("Cannot launch %s.\n\n%s\n\nLogs: %s" % (project, exc, state / "portable.log"))
        return 1
