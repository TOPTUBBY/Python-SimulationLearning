// How It's Wired - self-contained native Windows portable launcher.
// Only the independently authored launcher and Thai UI assets are embedded.
// Public frontend assets are downloaded by the end user at first launch.
package main

import (
	"context"
	"embed"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"net/url"
	"os"
	"path"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"sync"
	"time"
)

const (
	port          = "8131"
	projectID     = "how-its-wired"
	appName       = "How It's Wired"
	startRoute    = "/lead-load"
	remoteOrigin  = "https://how-its-wired.vercel.app"
	maxAssetCount = 2400
	maxFileBytes  = 35 << 20
)

//go:embed assets/*
var bundled embed.FS

var attrRE = regexp.MustCompile(`(?i)\b(?:src|href|poster|data-src)\s*=\s*["']([^"']+)["']`)
var cssRE = regexp.MustCompile(`(?i)url\(\s*["']?([^"')\s]+)`)
var quoteRE = regexp.MustCompile(`["'\x60]([^"'\x60\s<>]{3,230}\.(?:js|mjs|css|json|svg|png|jpe?g|webp|avif|gif|ico|woff2?|ttf|otf|glb|gltf|bin|wasm|mp4|webm|mp3|ogg|wav|webmanifest)(?:\?[^"'\x60\s<>]*)?)["'\x60]`)
var assetRE = regexp.MustCompile(`(?:^|[\s"'\x60(/])((?:\.?/?|/)?assets/[\w./@%+~\-]+\.(?:js|mjs|css|json|svg|png|jpe?g|webp|avif|gif|ico|woff2?|ttf|otf|glb|gltf|bin|wasm|mp4|webm|mp3|ogg|wav))`)

var allowedExt = map[string]bool{
	".js": true, ".mjs": true, ".css": true, ".json": true, ".svg": true, ".png": true, ".jpg": true, ".jpeg": true,
	".webp": true, ".avif": true, ".gif": true, ".ico": true, ".woff": true, ".woff2": true, ".ttf": true, ".otf": true,
	".glb": true, ".gltf": true, ".bin": true, ".wasm": true, ".mp4": true, ".webm": true, ".mp3": true, ".ogg": true,
	".wav": true, ".pdf": true, ".webmanifest": true, ".txt": true, ".map": true,
}

type app struct {
	dir                string
	base               *url.URL
	httpClient         *http.Client
	mu                 sync.RWMutex
	ready, downloading bool
	failure, status    string
	fetched            int
	warnings           []string
	dict               map[string]string
	translation        map[string]string
	trMu               sync.Mutex
	logger             *log.Logger
}

func newApp(dir string, source string, logger *log.Logger) (*app, error) {
	u, err := url.Parse(source)
	if err != nil {
		return nil, err
	}
	if u.Scheme != "https" && !(u.Scheme == "http" && u.Hostname() == "127.0.0.1") {
		return nil, errors.New("invalid upstream source")
	}
	var dict map[string]string
	raw, err := bundled.ReadFile("assets/dictionary.json")
	if err != nil {
		return nil, err
	}
	if err = json.Unmarshal(raw, &dict); err != nil {
		return nil, err
	}
	a := &app{dir: dir, base: u, httpClient: &http.Client{Timeout: 35 * time.Second}, dict: dict, logger: logger, status: "Checking offline cache", translation: map[string]string{}}
	if b, err := os.ReadFile(filepath.Join(dir, "translation_cache.json")); err == nil {
		_ = json.Unmarshal(b, &a.translation)
	}
	a.ready = a.validCache()
	return a, nil
}

func (a *app) safeFile(urlPath string) (string, bool) {
	if strings.ContainsAny(urlPath, "\\\x00") || strings.Contains(urlPath, "//") {
		return "", false
	}
	decoded, err := url.PathUnescape(urlPath)
	if err != nil {
		return "", false
	}
	for _, v := range strings.Split(decoded, "/") {
		if v == ".." || v == "." || strings.Contains(v, ":") {
			return "", false
		}
	}
	clean := path.Clean("/" + decoded)
	if clean == "/" {
		clean = "/index.html"
	}
	if strings.HasSuffix(clean, "/") {
		clean += "index.html"
	}
	return filepath.Join(a.dir, "site", filepath.FromSlash(strings.TrimPrefix(clean, "/"))), true
}

func (a *app) validCache() bool {
	index := filepath.Join(a.dir, "site", "index.html")
	data, err := os.ReadFile(index)
	if err != nil || len(data) < 50 {
		return false
	}
	lower := strings.ToLower(string(data))
	if !strings.Contains(lower, "<html") && !strings.Contains(lower, "<script") {
		return false
	}
	refs := a.discover(a.base.String()+"/", data, ".html")
	// The root entry's local JS/CSS are mandatory; late assets are recovered on demand.
	count := 0
	for _, p := range refs {
		ext := path.Ext(strings.Split(p, "?")[0])
		if ext == ".js" || ext == ".mjs" || ext == ".css" {
			abs, err := url.Parse(p)
			if err != nil {
				continue
			}
			if abs.Hostname() != a.base.Hostname() {
				continue
			}
			target, ok := a.safeFile(abs.EscapedPath())
			if !ok {
				continue
			}
			if st, e := os.Stat(target); e != nil || st.Size() == 0 {
				return false
			}
			count++
		}
	}
	return count > 0
}

func (a *app) downloadOnce(target string, rawURL string) ([]byte, error) {
	if body, err := os.ReadFile(target); err == nil && len(body) > 0 {
		return body, nil
	}
	req, err := http.NewRequest("GET", rawURL, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36")
	resp, err := a.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("HTTP %d for %s", resp.StatusCode, rawURL)
	}
	if resp.ContentLength > maxFileBytes {
		return nil, fmt.Errorf("asset too large: %s", rawURL)
	}
	body, err := io.ReadAll(io.LimitReader(resp.Body, maxFileBytes+1))
	if err != nil {
		return nil, err
	}
	if len(body) == 0 || len(body) > maxFileBytes {
		return nil, errors.New("asset response empty or too large")
	}
	suffix := strings.ToLower(filepath.Ext(target))
	contentType := strings.ToLower(resp.Header.Get("Content-Type"))
	if suffix != ".html" && suffix != ".txt" && strings.Contains(contentType, "text/html") {
		return nil, fmt.Errorf("invalid HTML fallback for %s", target)
	}
	if err := os.MkdirAll(filepath.Dir(target), 0755); err != nil {
		return nil, err
	}
	tmp := target + ".part"
	if err = os.WriteFile(tmp, body, 0644); err != nil {
		return nil, err
	}
	if err = os.Rename(tmp, target); err != nil {
		// Windows anti-virus can prevent atomic rename. No big directory move.
		if _, existingErr := os.Stat(target); existingErr == nil {
			return os.ReadFile(target)
		}
		if e := os.WriteFile(target, body, 0644); e != nil {
			return nil, e
		}
		_ = os.Remove(tmp)
	}
	a.mu.Lock()
	a.fetched++
	a.status = fmt.Sprintf("Downloaded %d assets", a.fetched)
	a.mu.Unlock()
	return body, nil
}

func (a *app) normalURL(ref string, parent string) (string, bool) {
	if len(ref) == 0 || len(ref) > 512 || strings.HasPrefix(ref, "#") || strings.HasPrefix(ref, "data:") || strings.HasPrefix(ref, "blob:") {
		return "", false
	}
	if strings.HasPrefix(ref, "//") {
		ref = "https:" + ref
	}
	if strings.HasPrefix(ref, "assets/") || strings.HasPrefix(ref, "./assets/") {
		ref = "/" + strings.TrimPrefix(strings.TrimPrefix(ref, "./"), "/")
	}
	u, e := url.Parse(ref)
	if e != nil {
		return "", false
	}
	base, _ := url.Parse(parent)
	resolved := base.ResolveReference(u)
	if resolved.Hostname() != a.base.Hostname() {
		return "", false
	}
	if !allowedExt[strings.ToLower(path.Ext(resolved.Path))] {
		return "", false
	}
	if _, ok := a.safeFile(resolved.EscapedPath()); !ok {
		return "", false
	}
	resolved.Fragment = ""
	return resolved.String(), true
}

func (a *app) discover(parent string, body []byte, ext string) []string {
	if !(ext == ".html" || ext == ".css" || ext == ".js" || ext == ".mjs" || ext == ".json" || ext == ".svg" || ext == ".webmanifest") {
		return nil
	}
	if len(body) > 4<<20 {
		return nil
	}
	text := string(body)
	found := map[string]bool{}
	push := func(s string) {
		if link, ok := a.normalURL(strings.Trim(s, " \t\r\n\"'"), parent); ok {
			found[link] = true
		}
	}
	for _, m := range attrRE.FindAllStringSubmatch(text, 1500) {
		push(m[1])
	}
	for _, m := range cssRE.FindAllStringSubmatch(text, 1500) {
		push(m[1])
	}
	for _, m := range quoteRE.FindAllStringSubmatch(text, 2600) {
		push(m[1])
	}
	for _, m := range assetRE.FindAllStringSubmatch(text, 2600) {
		push(m[1])
	}
	result := make([]string, 0, len(found))
	for k := range found {
		result = append(result, k)
	}
	sort.Strings(result)
	return result
}

func (a *app) prepare() {
	a.mu.Lock()
	if a.downloading || a.ready {
		a.mu.Unlock()
		return
	}
	a.downloading = true
	a.failure = ""
	a.status = "Downloading original website for first launch..."
	a.mu.Unlock()
	defer func() { a.mu.Lock(); a.downloading = false; a.mu.Unlock() }()
	target := filepath.Join(a.dir, "site", "index.html")
	rootURL := a.base.String() + "/"
	html, err := a.downloadOnce(target, rootURL)
	if err != nil {
		a.setError(err)
		return
	}
	pending := a.discover(rootURL, html, ".html")
	seen := map[string]bool{}
	steps := 0
	// Crawl public JS/CSS references, including dynamically named chunk/assets.
	for len(pending) > 0 && steps < maxAssetCount {
		batch := pending
		pending = nil
		ch := make(chan string, len(batch))
		for _, u := range batch {
			if !seen[u] && len(seen) < maxAssetCount {
				seen[u] = true
				ch <- u
			}
		}
		close(ch)
		type result struct {
			refs []string
			err  error
		}
		results := make(chan result, len(ch))
		var wg sync.WaitGroup
		for i := 0; i < 8; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				for u := range ch {
					p, _ := url.Parse(u)
					dest, ok := a.safeFile(p.EscapedPath())
					if !ok {
						continue
					}
					body, e := a.downloadOnce(dest, u)
					if e != nil {
						results <- result{err: e}
						continue
					}
					results <- result{refs: a.discover(u, body, strings.ToLower(path.Ext(p.Path)))}
				}
			}()
		}
		wg.Wait()
		close(results)
		for it := range results {
			if it.err != nil {
				a.mu.Lock()
				if len(a.warnings) < 60 {
					a.warnings = append(a.warnings, it.err.Error())
				}
				a.mu.Unlock()
			}
			for _, u := range it.refs {
				if !seen[u] && len(seen) < maxAssetCount {
					pending = append(pending, u)
				}
			}
		}
		steps += len(batch)
	}
	valid := a.validCache()
	a.mu.Lock()
	a.ready = valid
	if valid {
		a.status = fmt.Sprintf("Website ready: %d assets cached", a.fetched)
	} else {
		a.failure = "Missing main JavaScript/CSS assets; check internet and retry"
		a.status = "Download incomplete"
	}
	a.mu.Unlock()
	if !valid {
		a.logger.Println("Preparation failed", a.failure)
	}
	if valid {
		a.logger.Printf("Site cache ready, downloaded=%d warnings=%d", a.fetched, len(a.warnings))
	}
}

func (a *app) setError(e error) {
	a.mu.Lock()
	a.failure = e.Error()
	a.status = "Download error"
	a.mu.Unlock()
	a.logger.Println(e)
}

func (a *app) serveAsset(w http.ResponseWriter, r *http.Request, pathString string) {
	target, ok := a.safeFile(pathString)
	if !ok {
		http.Error(w, "Invalid path", 400)
		return
	}
	if _, err := os.Stat(target); os.IsNotExist(err) {
		requestURL := a.base.String() + pathString
		if _, e := a.downloadOnce(target, requestURL); e != nil {
			http.NotFound(w, r)
			return
		}
	}
	w.Header().Set("Cache-Control", "no-cache")
	http.ServeFile(w, r, target)
}

func injectHTML(data []byte) []byte {
	script := `<link rel="stylesheet" href="/__thai__/overlay.css"><script src="/__thai__/overlay.js" data-site="how-its-wired" data-default="th" data-online="false" defer></script>`
	raw := string(data)
	lower := strings.ToLower(raw)
	if i := strings.Index(lower, "</head>"); i >= 0 {
		return []byte(raw[:i] + script + raw[i:])
	}
	if i := strings.Index(lower, "</body>"); i >= 0 {
		return []byte(raw[:i] + script + raw[i:])
	}
	return append(data, []byte(script)...)
}

func (a *app) servePage(w http.ResponseWriter, r *http.Request) {
	a.mu.RLock()
	ready := a.ready
	msg := a.status
	errText := a.failure
	a.mu.RUnlock()
	if !ready {
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.Header().Set("Cache-Control", "no-store")
		// No user text inserted unescaped into this page: progress is polled via JSON.
		io.WriteString(w, `<!doctype html><html lang="th"><meta charset="utf-8"><title>Preparing How It's Wired</title><style>body{font:16px 'Segoe UI',sans-serif;max-width:600px;margin:12vh auto;padding:24px;line-height:1.6;background:#111923;color:#fff}.box{padding:30px;border:1px solid #3d536c;border-radius:16px}button{padding:10px 15px;cursor:pointer}</style><div class="box"><h2>กำลังเตรียมเว็บไซต์ How It’s Wired</h2><p id="status">Downloading website assets...</p><p id="detail">ครั้งแรกต้องเชื่อมต่ออินเทอร์เน็ต ข้อมูลจะเก็บในเครื่องเพื่อเปิดครั้งต่อไป</p><button id="retry" style="display:none">ลองดาวน์โหลดอีกครั้ง</button></div><script>async function poll(){try{let s=await (await fetch('/__portable__/status',{cache:'no-store'})).json();document.getElementById('status').textContent=s.status;if(s.ready){location.reload();return;}if(s.error){document.getElementById('detail').textContent=s.error;document.getElementById('retry').style.display='inline-block';}}catch(e){}}setInterval(poll,800);poll();document.getElementById('retry').onclick=async()=>{await fetch('/__portable__/retry',{method:'POST'});document.getElementById('retry').style.display='none';};</script></html>`)
		_ = msg
		_ = errText
		return
	}
	data, err := os.ReadFile(filepath.Join(a.dir, "site", "index.html"))
	if err != nil {
		http.Error(w, "Cached entrypoint missing", 500)
		return
	}
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	w.Header().Set("Cache-Control", "no-cache")
	_, _ = w.Write(injectHTML(data))
}

func (a *app) translate(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Method not allowed", 405)
		return
	}
	origin := r.Header.Get("Origin")
	if origin != "" && origin != "http://127.0.0.1:"+port && origin != "http://localhost:"+port {
		http.Error(w, "Origin denied", 403)
		return
	}
	if !strings.HasPrefix(strings.ToLower(r.Header.Get("Content-Type")), "application/json") {
		http.Error(w, "Expected JSON", 400)
		return
	}
	r.Body = http.MaxBytesReader(w, r.Body, 60000)
	var req struct {
		Texts  []string `json:"texts"`
		Online bool     `json:"online"`
	}
	if json.NewDecoder(r.Body).Decode(&req) != nil || len(req.Texts) > 20 {
		http.Error(w, "Invalid request", 400)
		return
	}
	res := make([]string, len(req.Texts))
	total := 0
	for i, text := range req.Texts {
		total += len(text)
		if len(text) > 4000 || total > 18000 {
			http.Error(w, "Too much text", 400)
			return
		}
		if known, ok := a.dict[strings.TrimSpace(text)]; ok {
			res[i] = known
			continue
		}
		a.trMu.Lock()
		cached := a.translation[text]
		a.trMu.Unlock()
		if cached != "" {
			res[i] = cached
			continue
		}
		if !req.Online {
			res[i] = text
			continue
		}
		res[i] = a.translateOnline(text)
	}
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	_ = json.NewEncoder(w).Encode(map[string]interface{}{"results": res, "online": req.Online})
}

func (a *app) translateOnline(text string) string {
	u := "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=th&dt=t&q=" + url.QueryEscape(text)
	req, _ := http.NewRequest("GET", u, nil)
	response, err := a.httpClient.Do(req)
	if err != nil {
		return text
	}
	defer response.Body.Close()
	if response.StatusCode != 200 {
		return text
	}
	body, e := io.ReadAll(io.LimitReader(response.Body, 32000))
	if e != nil {
		return text
	}
	var payload []json.RawMessage
	if json.Unmarshal(body, &payload) != nil || len(payload) < 1 {
		return text
	}
	var phrases [][]json.RawMessage
	if json.Unmarshal(payload[0], &phrases) != nil {
		return text
	}
	var b strings.Builder
	for _, phrase := range phrases {
		if len(phrase) > 0 {
			var s string
			if json.Unmarshal(phrase[0], &s) == nil {
				b.WriteString(s)
			}
		}
	}
	translated := strings.TrimSpace(b.String())
	if translated == "" {
		return text
	}
	a.trMu.Lock()
	a.translation[text] = translated
	serialized, _ := json.MarshalIndent(a.translation, "", "  ")
	_ = os.WriteFile(filepath.Join(a.dir, "translation_cache.json"), serialized, 0600)
	a.trMu.Unlock()
	return translated
}

func (a *app) handler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "GET" && r.Method != "HEAD" && r.Method != "POST" {
		http.Error(w, "Method not allowed", 405)
		return
	}
	p := r.URL.EscapedPath()
	switch p {
	case "/__thai__/overlay.js", "/__thai__/overlay.css", "/__thai__/dictionary.json":
		name := map[string]string{"/__thai__/overlay.js": "assets/overlay.js", "/__thai__/overlay.css": "assets/overlay.css", "/__thai__/dictionary.json": "assets/dictionary.json"}[p]
		data, e := bundled.ReadFile(name)
		if e != nil {
			http.Error(w, "Resource missing", 500)
			return
		}
		ctype := "application/json; charset=utf-8"
		if strings.HasSuffix(name, ".js") {
			ctype = "text/javascript; charset=utf-8"
		}
		if strings.HasSuffix(name, ".css") {
			ctype = "text/css; charset=utf-8"
		}
		w.Header().Set("Content-Type", ctype)
		w.Header().Set("Cache-Control", "no-store")
		w.Write(data)
		return
	case "/__thai__/translate":
		a.translate(w, r)
		return
	case "/__portable__/status", "/__clone_health__":
		a.mu.RLock()
		response := map[string]interface{}{"clone_id": projectID, "port": 8131, "ready": a.ready, "status": a.status, "error": a.failure, "files_downloaded": a.fetched, "warnings": len(a.warnings)}
		a.mu.RUnlock()
		w.Header().Set("Content-Type", "application/json")
		w.Header().Set("Cache-Control", "no-store")
		_ = json.NewEncoder(w).Encode(response)
		return
	case "/__portable__/retry":
		if r.Method != "POST" {
			http.Error(w, "POST only", 405)
			return
		}
		a.mu.RLock()
		running := a.downloading
		a.mu.RUnlock()
		if !running {
			go a.prepare()
		}
		w.WriteHeader(202)
		return
	}
	if strings.HasPrefix(p, "/__") {
		http.NotFound(w, r)
		return
	}
	ext := strings.ToLower(path.Ext(p))
	if allowedExt[ext] {
		if r.Method == "POST" {
			http.Error(w, "method not allowed", 405)
			return
		}
		a.serveAsset(w, r, p)
		return
	}
	if r.Method == "POST" {
		http.Error(w, "method not allowed", 405)
		return
	}
	a.servePage(w, r)
}

// Self-test is intended for CI: verify the actual compiled EXE startup and
// embedded resources on Windows without downloading the upstream website.
func runSelfTest(args []string) (bool, error) {
	if len(args) < 2 || args[0] != "--self-test-output" {
		return false, nil
	}
	if len(args) != 2 || strings.TrimSpace(args[1]) == "" {
		return true, errors.New("usage: --self-test-output PATH")
	}
	status := struct {
		OK      bool     `json:"ok"`
		Frozen  bool     `json:"frozen"`
		Project string   `json:"project"`
		Port    int      `json:"port"`
		Mode    string   `json:"mode"`
		Missing []string `json:"missing"`
	}{OK: true, Frozen: true, Project: "HowItsWired", Port: 8131, Mode: "bootstrap", Missing: []string{}}
	for _, name := range []string{"assets/overlay.js", "assets/overlay.css", "assets/dictionary.json"} {
		value, e := bundled.ReadFile(name)
		if e != nil || len(value) < 100 {
			status.OK = false
			status.Missing = append(status.Missing, name)
		}
	}
	out, e := json.MarshalIndent(status, "", "  ")
	if e != nil {
		return true, e
	}
	e = os.WriteFile(args[1], out, 0644)
	return true, e
}

func main() {
	if tested, err := runSelfTest(os.Args[1:]); tested {
		if err != nil {
			showMessage("EXE Self-test failed: " + err.Error())
			os.Exit(2)
		}
		return
	}
	dataDir := os.Getenv("LOCALAPPDATA")
	if dataDir == "" {
		home, _ := os.UserHomeDir()
		dataDir = filepath.Join(home, "AppData", "Local")
	}
	root := filepath.Join(dataDir, "SimulationLearning", "HowItsWired")
	_ = os.MkdirAll(root, 0755)
	logFile, err := os.OpenFile(filepath.Join(root, "portable.log"), os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		showMessage("Cannot create log file: " + err.Error())
		return
	}
	defer logFile.Close()
	logger := log.New(logFile, "[HowItsWired] ", log.LstdFlags)
	a, err := newApp(root, remoteOrigin, logger)
	if err != nil {
		showMessage(err.Error())
		return
	}
	ln, err := net.Listen("tcp", "127.0.0.1:"+port)
	if err != nil {
		r, e := a.httpClient.Get("http://127.0.0.1:" + port + "/__clone_health__")
		if e == nil {
			var v struct {
				CloneID string `json:"clone_id"`
			}
			_ = json.NewDecoder(r.Body).Decode(&v)
			r.Body.Close()
			if v.CloneID == projectID {
				openBrowser("http://127.0.0.1:" + port + startRoute)
				return
			}
		}
		showMessage("Port 8131 is already in use.\n" + err.Error())
		return
	}
	server := &http.Server{Handler: http.HandlerFunc(a.handler), ReadHeaderTimeout: 8 * time.Second}
	go func() {
		err := server.Serve(ln)
		if err != nil && err != http.ErrServerClosed {
			logger.Println(err)
		}
	}()
	if !a.ready {
		go a.prepare()
	}
	localURL := "http://127.0.0.1:" + port + startRoute
	if err = openBrowser(localURL); err != nil {
		logger.Println("Could not open browser:", err)
	}
	showMessage("How It's Wired is running at:\n" + localURL + "\n\nClick OK to STOP the local server.\n\nFirst launch requires internet to download original site assets.\nCached data and Thai translations are saved under:\n" + root)
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_ = server.Shutdown(ctx)
}
