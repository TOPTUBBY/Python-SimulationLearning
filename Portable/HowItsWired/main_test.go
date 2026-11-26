package main

import (
	"bytes"
	"encoding/json"
	"io"
	"log"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestMirrorPreviewAndThai(t *testing.T) {
	origin := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/":
			w.Header().Set("Content-Type", "text/html")
			io.WriteString(w, `<!doctype html><html><head><script type="module" src="/assets/main.js"></script><link rel="stylesheet" href="/assets/main.css"></head><body><h1>How It's Wired</h1></body></html>`)
		case "/assets/main.js":
			w.Header().Set("Content-Type", "text/javascript")
			io.WriteString(w, `const image="/assets/lamp.svg";console.log("works")`)
		case "/assets/main.css":
			w.Header().Set("Content-Type", "text/css")
			io.WriteString(w, `body{color:white}`)
		case "/assets/lamp.svg":
			w.Header().Set("Content-Type", "image/svg+xml")
			io.WriteString(w, `<svg xmlns="http://www.w3.org/2000/svg"></svg>`)
		case "/assets/dynamic.svg":
			w.Header().Set("Content-Type", "image/svg+xml")
			io.WriteString(w, `<svg>dynamic</svg>`)
		default:
			http.NotFound(w, r)
		}
	}))
	defer origin.Close()
	dir := t.TempDir()
	a, err := newApp(dir, origin.URL, log.New(io.Discard, "", 0))
	if err != nil {
		t.Fatal(err)
	}
	if a.ready {
		t.Fatal("unexpected cache ready")
	}
	a.prepare()
	if !a.ready {
		t.Fatal("mirror did not initialize:", a.failure)
	}
	for _, p := range []string{"site/index.html", "site/assets/main.js", "site/assets/main.css", "site/assets/lamp.svg"} {
		if _, err := os.Stat(filepath.Join(dir, p)); err != nil {
			t.Fatal(err)
		}
	}
	local := httptest.NewServer(http.HandlerFunc(a.handler))
	defer local.Close()
	response, err := http.Get(local.URL + "/lead-load")
	if err != nil {
		t.Fatal(err)
	}
	body, _ := io.ReadAll(response.Body)
	response.Body.Close()
	if !bytes.Contains(body, []byte("__thai__/overlay.js")) {
		t.Fatal("Thai injection missing")
	}
	response, err = http.Get(local.URL + "/assets/main.js")
	if err != nil {
		t.Fatal(err)
	}
	body, _ = io.ReadAll(response.Body)
	response.Body.Close()
	if !bytes.Contains(body, []byte("console.log")) {
		t.Fatal("JS missing")
	}
	response, err = http.Get(local.URL + "/assets/dynamic.svg")
	if err != nil {
		t.Fatal(err)
	}
	body, _ = io.ReadAll(response.Body)
	response.Body.Close()
	if !bytes.Contains(body, []byte("dynamic")) {
		t.Fatal("lazy asset missing")
	}
	response, err = http.Get(local.URL + "/__thai__/dictionary.json")
	if err != nil {
		t.Fatal(err)
	}
	var dict map[string]string
	err = json.NewDecoder(response.Body).Decode(&dict)
	response.Body.Close()
	if err != nil {
		t.Fatal(err)
	}
	if dict["Will the lead take it?"] == "" {
		t.Fatal("Lead Load Thai translation missing")
	}
	post, err := http.Post(local.URL+"/__thai__/translate", "application/json", strings.NewReader(`{"texts":["Will the lead take it?"],"online":false}`))
	if err != nil {
		t.Fatal(err)
	}
	var result struct {
		Results []string `json:"results"`
	}
	err = json.NewDecoder(post.Body).Decode(&result)
	post.Body.Close()
	if err != nil {
		t.Fatal(err)
	}
	if len(result.Results) != 1 || result.Results[0] != dict["Will the lead take it?"] {
		t.Fatalf("wrong translation %+v", result)
	}
	a2, e := newApp(dir, origin.URL, log.New(io.Discard, "", 0))
	if e != nil || !a2.ready {
		t.Fatal("offline reload of cache failed", e)
	}
}

func TestTraversalBlocked(t *testing.T) {
	a, _ := newApp(t.TempDir(), "https://how-its-wired.vercel.app", log.New(io.Discard, "", 0))
	for _, p := range []string{"/../secret", "/%2e%2e/secret", "/assets/../../x.js", "/assets\\foo.js"} {
		if file, ok := a.safeFile(p); ok {
			t.Errorf("Unsafe path accepted %q -> %q", p, file)
		}
	}
}

func TestInputAndLanguageResources(t *testing.T) {
	for _, name := range []string{"assets/overlay.js", "assets/overlay.css", "assets/dictionary.json"} {
		if b, e := bundled.ReadFile(name); e != nil || len(b) < 100 {
			t.Errorf("Missing %s: %v", name, e)
		}
	}
	html := injectHTML([]byte("<html><head></head><body>Test</body></html>"))
	if !bytes.Contains(html, []byte("__thai__/overlay.js")) {
		t.Fatal("Thai UI not embedded")
	}
}

func TestSelfTestWritesIdentity(t *testing.T) {
	output := filepath.Join(t.TempDir(), "smoke.json")
	yes, err := runSelfTest([]string{"--self-test-output", output})
	if err != nil || !yes {
		t.Fatal("Self-test failed", err)
	}
	var result struct {
		OK      bool     `json:"ok"`
		Port    int      `json:"port"`
		Project string   `json:"project"`
		Missing []string `json:"missing"`
	}
	content, err := os.ReadFile(output)
	if err != nil {
		t.Fatal(err)
	}
	if err := json.Unmarshal(content, &result); err != nil {
		t.Fatal(err)
	}
	if !result.OK || result.Port != 8131 || result.Project != "HowItsWired" || len(result.Missing) > 0 {
		t.Fatalf("invalid result %+v", result)
	}
}
