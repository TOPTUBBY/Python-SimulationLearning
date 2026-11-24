"""Shared local frontend mirror, integrity checker, and HTTP server.

Python standard library only. Website assets remain in each project's ignored
`site/` directory and are not distributed with this repository.
"""
from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import posixpath
import queue
import re
import shutil
import socket
import sys
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import Request, urlopen
import webbrowser

VERSION = "1.6.0"
HOST = "127.0.0.1"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
EXTENSIONS = {".js", ".mjs", ".css", ".json", ".svg", ".png", ".jpg", ".jpeg",
              ".webp", ".avif", ".gif", ".ico", ".webmanifest", ".wasm", ".txt",
              ".woff", ".woff2", ".ttf", ".otf", ".eot", ".glb", ".gltf", ".bin",
              ".ktx2", ".basis", ".hdr", ".obj", ".mtl", ".stl", ".mp4", ".webm",
              ".mp3", ".ogg", ".wav", ".pdf", ".map"}
EXT_PATTERN = "|".join(re.escape(x[1:]) for x in sorted(EXTENSIONS, key=len, reverse=True))
QUOTED_ASSET = re.compile(r'''["'`]((?:https?://|//|/|\.\.?/)?[a-zA-Z0-9_@%+.,~:/=-]+\.(?:'''
                          + EXT_PATTERN + r''')(?:\?[^"'`\s]*)?)["'`]''', re.I)
CSS_URL = re.compile(r'''url\(\s*["']?([^"')]+)["']?\s*\)''', re.I)
CSS_IMPORT = re.compile(r'''@import\s+["']([^"']+)["']''', re.I)
ROOT_ASSET = re.compile(r'''(?<![\w])(?:/|\.\.?/)?assets/[a-zA-Z0-9_./@%+~-]+\.(?:'''
                        + EXT_PATTERN + r''')''', re.I)
FONT_HOSTS = {"fonts.googleapis.com", "fonts.gstatic.com"}
MAX_ASSETS = 4000


def load_config(project_dir):
    root = Path(project_dir).resolve()
    data = json.loads((root / "config.json").read_text(encoding="utf-8"))
    for key in ("id", "name", "source", "launch_path", "port"):
        if key not in data:
            raise ValueError("Missing config field: " + key)
    parsed = urlsplit(data["source"])
    if parsed.scheme != "https" or not parsed.hostname or parsed.path not in ("", "/"):
        raise ValueError("source must be an HTTPS site origin (ending with /)")
    if not str(data["launch_path"]).startswith("/"):
        raise ValueError("launch_path must begin with /")
    port = int(data["port"])
    if not 1024 <= port <= 65535:
        raise ValueError("port must be between 1024 and 65535")
    return data


def origin_url(config):
    return config["source"].rstrip("/") + "/"


def asset_path(url, origin_host):
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return None
    host = parsed.hostname.lower()
    if host != origin_host and host not in FONT_HOSTS:
        return None
    raw = unquote(parsed.path or "/")
    if "\\" in raw or "\0" in raw or any(part == ".." for part in raw.split("/")):
        return None
    name = posixpath.normpath(raw).lstrip("/")
    if host == origin_host:
        if not name or name == ".":
            name = "index.html"
    else:
        if not name or name == ".":
            name = "index"
        if not Path(name).suffix:
            name += ".css" if host == "fonts.googleapis.com" else ".bin"
        if parsed.query:
            stem, ext = posixpath.splitext(name)
            name = stem + "__" + hashlib.sha1(parsed.query.encode()).hexdigest()[:12] + ext
        name = "_external/" + host + "/" + name
    if ":" in name or name.startswith("../"):
        return None
    return Path(name)


class HTMLAssets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attributes):
        d = dict(attributes)
        if tag in ("script", "img", "source", "video", "audio", "embed", "iframe"):
            for key in ("src", "poster", "data-src"):
                if d.get(key):
                    self.refs.append(d[key])
        if tag == "link" and d.get("href"):
            rel = d.get("rel", "").lower()
            if any(t in rel for t in ("stylesheet", "preload", "icon", "manifest", "modulepreload")):
                self.refs.append(d["href"])
        for key in ("srcset", "imagesrcset"):
            if d.get(key):
                self.refs += [piece.strip().split(" ")[0] for piece in d[key].split(",")]


def check_site(site, verbose=True):
    site = Path(site)
    index = site / "index.html"
    if not index.is_file():
        if verbose:
            print("FAIL: site/index.html is missing. Run Update_Clone.bat while online.")
        return False, ["index.html"]
    try:
        parser = HTMLAssets()
        parser.feed(index.read_text(encoding="utf-8-sig"))
    except (UnicodeError, OSError) as exc:
        if verbose:
            print("FAIL: invalid index.html:", exc)
        return False, ["index.html invalid"]
    missing = []
    for ref in parser.refs:
        p = urlsplit(ref)
        if p.scheme or p.netloc or ref.startswith("//"):
            continue  # External fonts are optional for the root entrypoint.
        path = unquote(p.path)
        if not path or not Path(path).suffix:
            continue
        candidate = site / path.lstrip("/")
        if not candidate.is_file():
            missing.append(ref)
    js_files = list(site.rglob("*.js")) + list(site.rglob("*.mjs"))
    if not js_files:
        missing.append("at least one JavaScript bundle")
    manifest_path = site / ".clone-manifest.json"
    manifest = {}
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            missing.append("valid manifest")
    else:
        missing.append("download manifest")
    if verbose:
        print("Cached files:", sum(x.is_file() for x in site.rglob("*")))
        print("Entry assets checked:", len(parser.refs))
        print("Mirror warnings:", len(manifest.get("errors", [])))
        for item in missing[:20]:
            print("MISSING:", item)
        print("PASS: Local entrypoint is present." if not missing else "FAIL: Refresh with Update_Clone.bat.")
        print("NOTE: This does not verify every 3D model, lesson, network request, or animation.")
    return not missing, missing


class Mirror:
    def __init__(self, config, directory, jobs=12):
        self.base = origin_url(config)
        self.host = urlsplit(self.base).hostname.lower()
        self.directory = Path(directory)
        self.jobs = max(1, min(24, jobs))
        self.queue = queue.Queue()
        self.seen = set()
        self.errors = []
        self.replacements = {}
        self.lock = threading.Lock()
        self.saved = 0
        self.total_bytes = 0

    def enqueue(self, raw, parent=None):
        raw = html.unescape(str(raw).strip())
        if not raw or raw.startswith(("#", "data:", "blob:", "javascript:", "mailto:", "tel:")):
            return
        if raw.startswith("//"):
            raw = "https:" + raw
        resolved = urljoin(parent or self.base, raw)
        mapped = asset_path(resolved, self.host)
        if mapped is None or (mapped.suffix.lower() not in EXTENSIONS and str(mapped) != "index.html"):
            return
        with self.lock:
            if len(self.seen) >= MAX_ASSETS or resolved in self.seen:
                return
            self.seen.add(resolved)
            if urlsplit(resolved).hostname.lower() in FONT_HOSTS:
                self.replacements[resolved] = "/" + mapped.as_posix()
        self.queue.put((resolved, mapped))

    def download(self, url):
        headers = {"User-Agent": UA, "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"}
        for i in range(3):
            try:
                with urlopen(Request(url, headers=headers), timeout=25) as response:
                    data = response.read()
                    mimetype = response.headers.get("Content-Type", "").lower()
                    if "text/html" in mimetype and Path(urlsplit(url).path).suffix.lower() not in ("", ".html"):
                        raise ValueError("HTML fallback returned for an asset")
                    return data
            except (HTTPError, URLError, TimeoutError, OSError) as error:
                if i == 2 or (isinstance(error, HTTPError) and 400 <= error.code < 500):
                    raise
                time.sleep(0.5 * (i + 1))

    def discover(self, url, rel, content):
        if rel.suffix.lower() not in (".html", ".js", ".mjs", ".json", ".css", ".svg", ".webmanifest"):
            return
        try:
            src = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            return
        if rel.suffix.lower() == ".html":
            parser = HTMLAssets()
            parser.feed(src)
            for href in parser.refs:
                self.enqueue(href, url)
        if rel.suffix.lower() in (".html", ".css", ".svg"):
            for found in CSS_URL.findall(src) + CSS_IMPORT.findall(src):
                self.enqueue(found, url)
        for match in QUOTED_ASSET.finditer(src):
            raw = match.group(1)
            # Compiled Vite bundles contain root-relative paths as 'assets/foo.js'.
            if raw.startswith("assets/") or raw.startswith("./assets/"):
                raw = "/" + raw.lstrip("./")
            self.enqueue(raw, url)
        for match in ROOT_ASSET.finditer(src):
            raw = match.group(0)
            if raw.startswith("assets/") or raw.startswith("./assets/"):
                raw = "/" + raw.lstrip("./")
            self.enqueue(raw, url)

    def worker(self):
        while True:
            job = self.queue.get()
            if job is None:
                self.queue.task_done()
                break
            url, rel = job
            try:
                body = self.download(url)
                target = self.directory / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                temporary = target.with_name(target.name + ".part")
                temporary.write_bytes(body)
                temporary.replace(target)
                with self.lock:
                    self.saved += 1
                    self.total_bytes += len(body)
                    if self.saved <= 5 or self.saved % 50 == 0:
                        print("  [asset %d] %s" % (self.saved, rel.as_posix()), flush=True)
                self.discover(url, rel, body)
            except Exception as exc:
                with self.lock:
                    self.errors.append({"url": url, "error": str(exc)})
                    if len(self.errors) <= 8:
                        print("  [WARN] %s: %s" % (url, exc), flush=True)
            finally:
                self.queue.task_done()

    def rewrite_fonts(self):
        if not self.replacements:
            return
        for p in self.directory.rglob("*"):
            if p.suffix.lower() not in (".html", ".css") or not p.is_file():
                continue
            try:
                source = p.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                continue
            changed = source
            for external, local in self.replacements.items():
                changed = changed.replace(external, local).replace(html.escape(external, quote=True), html.escape(local, quote=True))
            if source != changed:
                p.write_text(changed, encoding="utf-8")

    def run(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        print("Source:", self.base, flush=True)
        print("Cache:", self.directory, flush=True)
        self.enqueue(self.base)
        threads = [threading.Thread(target=self.worker, daemon=True) for _ in range(self.jobs)]
        for thread in threads:
            thread.start()
        self.queue.join()
        for _ in threads:
            self.queue.put(None)
        for thread in threads:
            thread.join(timeout=2)
        self.rewrite_fonts()
        manifest = {"mirror_version": VERSION, "source": self.base,
                    "downloaded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "asset_count": self.saved, "total_bytes": self.total_bytes,
                    "errors": self.errors}
        (self.directory / ".clone-manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        passed, missing = check_site(self.directory, verbose=False)
        print("Downloaded %d files (%.1f MB), %d warnings." % (
            self.saved, self.total_bytes / 1048576, len(self.errors)), flush=True)
        if not passed:
            print("Missing required files:", ", ".join(missing[:10]), flush=True)
        return passed


def update_site(config, directory, jobs=12):
    directory = Path(directory).resolve()
    target = directory / "site"
    stage = directory / "site.__staging__"
    backup = directory / "site.__backup__"
    if stage.exists():
        shutil.rmtree(stage)
    if not Mirror(config, stage, jobs).run():
        shutil.rmtree(stage, ignore_errors=True)
        print("Mirror update rejected: prior cache was preserved.")
        return False
    if backup.exists():
        shutil.rmtree(backup)
    if target.exists():
        target.rename(backup)
    try:
        stage.rename(target)
    except Exception:
        if backup.exists() and not target.exists():
            backup.rename(target)
        raise
    shutil.rmtree(backup, ignore_errors=True)
    print("Mirror update installed at:", target)
    return True


def local_url(config, port=None):
    return "http://%s:%d%s" % (HOST, port or int(config["port"]), config["launch_path"])


def existing_server(config, port):
    try:
        with urlopen("http://%s:%d/__clone_health__" % (HOST, port), timeout=1) as response:
            data = json.loads(response.read().decode())
            return data.get("clone_id") == config["id"]
    except (OSError, ValueError, KeyError):
        return False


def port_in_use(port):
    with socket.socket() as sock:
        sock.settimeout(1)
        return sock.connect_ex((HOST, port)) == 0


def make_handler(config, site):
    base = origin_url(config)
    site = Path(site).resolve()

    class Handler(SimpleHTTPRequestHandler):
        server_version = "SimulationLearning/" + VERSION

        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(site), **kwargs)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("X-Content-Type-Options", "nosniff")
            super().end_headers()

        def guess_type(self, path):
            types = {".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css",
                     ".json": "application/json", ".wasm": "application/wasm",
                     ".glb": "model/gltf-binary", ".gltf": "model/gltf+json",
                     ".svg": "image/svg+xml", ".webmanifest": "application/manifest+json"}
            return types.get(Path(path).suffix.lower(), super().guess_type(path))

        def do_GET(self):
            path = unquote(urlsplit(self.path).path)
            if path == "/__clone_health__":
                self.health()
                return
            if not path.startswith("/") or "\\" in path or "\0" in path:
                self.send_error(400)
                return
            rel = path.lstrip("/")
            if path != "/" and not (site / rel).is_file():
                if Path(rel).suffix.lower() in EXTENSIONS:
                    self.fetch_asset(path, rel)
                elif not Path(rel).suffix and not (site / rel).is_dir():
                    # SPA history route; hash routes never reach the server.
                    self.path = "/index.html"
            super().do_GET()

        def do_HEAD(self):
            if urlsplit(self.path).path == "/__clone_health__":
                self.health(head_only=True)
                return
            if urlsplit(self.path).path != "/" and not Path(urlsplit(self.path).path).suffix:
                self.path = "/index.html"
            super().do_HEAD()

        def health(self, head_only=False):
            data = json.dumps({"clone_id": config["id"], "port": self.server.server_port,
                               "version": VERSION}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            if not head_only:
                self.wfile.write(data)

        def fetch_asset(self, path, rel):
            target = (site / rel).resolve()
            try:
                target.relative_to(site)
            except ValueError:
                return
            try:
                url = urljoin(base, path.lstrip("/"))
                with urlopen(Request(url, headers={"User-Agent": UA}), timeout=8) as response:
                    mime = response.headers.get("Content-Type", "").lower()
                    if "text/html" in mime:
                        return
                    body = response.read()
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(body)
                print("[On demand] %s (%d bytes)" % (rel, len(body)), flush=True)
            except (OSError, HTTPError, URLError, TimeoutError, ValueError) as exc:
                print("[Offline/missing] %s: %s" % (path, exc), flush=True)

    return Handler


def serve(config, directory, port=None, no_browser=False, update=False):
    directory = Path(directory)
    port = port or int(config["port"])
    url = local_url(config, port)
    if existing_server(config, port):
        print("Already running:", url)
        if not no_browser:
            webbrowser.open(url)
        return 0
    if port_in_use(port):
        print("ERROR: Port %d is used by another service." % port)
        return 2
    site = directory / "site"
    if update or not check_site(site, verbose=False)[0]:
        print("Downloading public frontend assets (internet required on first launch)...", flush=True)
        try:
            success = update_site(config, directory)
        except Exception as exc:
            print("ERROR: Mirror download failed:", exc)
            success = False
        if not success and not check_site(site, verbose=False)[0]:
            print("ERROR: No usable local cache. Browser will not open a blank page.")
            return 1
        if not success:
            print("WARNING: Using previously cached site.")
    try:
        httpd = ThreadingHTTPServer((HOST, port), make_handler(config, site))
    except OSError as exc:
        print("ERROR: Could not bind port:", exc)
        return 2
    print("=" * 60)
    print(config["name"], "| v" + VERSION)
    print("URL:", url)
    print("Press Ctrl+C or close this window to stop the server.")
    print("=" * 60, flush=True)
    if not no_browser:
        webbrowser.open(url)
    try:
        httpd.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print("Stopping server...")
    finally:
        httpd.server_close()
    return 0


def main(command, project_dir):
    config = load_config(project_dir)
    parser = argparse.ArgumentParser(description="SimulationLearning " + command)
    if command == "serve":
        parser.add_argument("--port", type=int)
        parser.add_argument("--no-browser", action="store_true")
        parser.add_argument("--update", action="store_true")
    elif command == "mirror":
        parser.add_argument("--jobs", type=int, default=12)
    args = parser.parse_args()
    print("%s | SimulationLearning v%s" % (config["name"], VERSION), flush=True)
    if command == "serve":
        return serve(config, project_dir, args.port, args.no_browser, args.update)
    if command == "mirror":
        return 0 if update_site(config, project_dir, args.jobs) else 1
    if command == "check":
        return 0 if check_site(Path(project_dir) / "site")[0] else 1
    raise ValueError("Unknown command: " + command)
