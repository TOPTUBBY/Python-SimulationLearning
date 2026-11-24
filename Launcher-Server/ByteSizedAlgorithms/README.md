# Byte-Sized Algorithms / Algo Lab — Local Clone (Port 8128)

**Original:** https://byte-sized-algorithms.vercel.app/#/big-o/1  
**Local:** http://127.0.0.1:8128/#/big-o/1  
**Toolkit preview:** `v1.2.0-rc.1` — **Pending User Approval / ยังไม่ขึ้น GitHub**.

## How it works / วิธีการทำงาน

This is a **local mirror launcher**, not a rewritten/replicated UI. On first run, a Python 3.8+ tool downloads the publicly available website's HTML, JS, CSS, fonts and referenced static assets into `site/`. The local HTTP server then serves those files on port **8128** and automatically opens your browser. Existing downloaded assets are reused after you close and reopen the launcher.

เครื่องมือนี้ใช้การดาวน์โหลดไฟล์หน้าเว็บต้นฉบับ (ไม่ใช่เขียนหน้า UI เลียนแบบ) โดยบันทึกไว้ใน `site/` และรัน Local Server ด้วย Python ที่พอร์ต **8128** เมื่อดับเบิลคลิก Launcher จะเปิด Browser ให้อัตโนมัติ โดยครั้งแรกต้องมีอินเทอร์เน็ต

### Requirements / สิ่งที่ต้องมี
- Windows 10/11
- Python 3.8+ installed and available as `py -3` or `python` in CMD; **no pip packages required**
- Internet connectivity on the first launch (and when refreshing assets)
- Chrome or Microsoft Edge with JavaScript enabled

### Quick Start / เริ่มใช้งาน
1. Extract the **entire ZIP**. Keep `ByteSizedAlgorithms/` and `tools/` as sibling directories. **Do not extract only the .bat file.**
2. Double-click **`ByteSizedAlgorithms/Launcher.bat`**.
3. On first use, let the mirror fetch the public website assets. This can take longer on a slow connection.
4. The default browser opens `http://127.0.0.1:8128/#/big-o/1`.
5. Close the CMD window or press `Ctrl+C` to stop. Reopen `Launcher.bat` to start again using the local cache.

### Common scripts / คำสั่ง

| File | Purpose |
|---|---|
| `Launcher.bat` | Start the local server and open the default browser on port **8128** |
| `Update_Clone.bat` | Re-download the original public site into a temporary staging directory; replace the old cache only when core checks pass |
| `Check_Clone.bat` | Verify local `index.html`, main JS/CSS references and download manifest |
| `server.py` | Entrypoint for local Python HTTP server |
| `mirror.py` | Entrypoint for website mirror updater |
| `verify_clone.py` | Entrypoint for offline cache integrity check |
| `config.json` | Source origin, launch hash route and port settings |
| `../tools/clone_runtime.py` | Shared download/serve/check engine |
| `site/` | Local cache of downloaded third-party assets, **not bundled** into ZIP or tracked by Git |

Command line alternatives from the project root:

```bat
py -3 ByteSizedAlgorithms\server.py
py -3 ByteSizedAlgorithms\verify_clone.py
py -3 ByteSizedAlgorithms\mirror.py
py -3 -m unittest discover -s tests -v
```

## Verify before approval / ทดสอบก่อน Approve

Compare both tabs side by side with the same browser, display scaling and zoom:

- [ ] Page opens on **Big-O Notation, Step 1** at `/#/big-o/1` without a blank screen.
- [ ] Top navigation: **Learn, Practice, Cheatsheets, Challenges, Progress**.
- [ ] Course sidebar contains **86 lessons grouped into 14 chapters**.
- [ ] Big-O animated blocks and step counter appear and change as expected.
- [ ] **Next / Back**, step selector and keyboard `←` / `→` navigate through all **7 steps**.
- [ ] Pseudocode and **Steps taken** panel update to match the animation.
- [ ] Select lessons in multiple sections (Arrays, Linked Lists, Graphs, Sorting, Dynamic Programming).
- [ ] Search (`Ctrl+K`) opens, finds a lesson and navigates correctly.
- [ ] **Practice** and **Challenges** render and respond.
- [ ] **Cheatsheets** load and content is readable.
- [ ] **Progress** can be updated and persists after browser refresh.
- [ ] Language selector and Dark/Light theme toggle work.
- [ ] Browser Refresh (`F5`) and hard refresh (`Ctrl+Shift+R`) do not show a black page.
- [ ] Close CMD, reopen `Launcher.bat`, check cached startup works without re-downloading everything.
- [ ] Optionally disable the internet after a successful mirror and check which sections truly function offline.

**Important:** A 100% functional/visual match cannot be guaranteed from a static downloader alone. The source's JavaScript may dynamically load assets or contact external services. `Check_Clone.bat` checks the entrypoint and cached files, not all 86 lessons or animations. Full browser comparison is required for approval.

## Troubleshooting / วิธีแก้ปัญหา

**Black screen / หน้าจอดำ**  
Run `Check_Clone.bat`. If it finds missing files, reconnect to the internet and run `Update_Clone.bat`. Restart the launcher. Inspect the browser's Developer Tools > Console / Network for failed JS requests.

**Browser never opens**  
Check that CMD displays `URL: http://127.0.0.1:8128/#/big-o/1`, and open that address manually. If the terminal shows an error, fix it before retrying. Check Python with `py -3 --version`.

**Port already used / พอร์ตชน**  
Run `netstat -ano | findstr :8128` in CMD. The launcher reuses an existing matching clone server, but does not hijack another program's port.

**Failed update / อัปเดตไม่สำเร็จ**  
Check your network, firewall, proxy and the original website. The updater preserves the previously working cache if a staged download does not pass the basic validation.

**Offline limits**  
Server can retrieve missing same-origin assets on demand **while online**, but external API endpoints, dynamically assembled URLs and third-party services may be unavailable offline.

## Ownership and distribution

Source site and course content remain the property of their respective rights holders. This preview ZIP includes **only our locally authored launcher/mirror/server tooling**, not a distributed copy of the website's original proprietary bundles or 86 lessons. The user runs the downloader for personal local review.

**Repository:** https://github.com/TOPTUBBY/Python-SimulationLearning  
**Publication status:** **Released in repository v1.2.0**; wait for explicit user approval before adding the folder, updating root README/version history, or pushing to GitHub.

---

## Thai UI — v1.4.0

- Website: **ByteSizedAlgorithms** (Algo Lab / 86 lessons)
- Local address: **http://127.0.0.1:8128/#/big-o/1**
- Language panel: `TH · ไทย` / `Original` at the bottom-right (collapsible).
- **Original is the default** to avoid unexpected changes. Click `TH · ไทย` to enable Thai, and `Original` to restore the source language.
- Each site's language and online-translation setting is remembered in browser localStorage.
- Offline: curated Thai UI dictionary (shared + site-specific) and previously cached translations.
- Optional online: click **แปลข้อความใหม่ผ่านออนไลน์** to translate unseen, dynamically loaded sentences. **Displayed text** may be transmitted to Google Translate, then cached in the current project folder in `translation_cache.json`.
- Code examples, editable fields, numeric readouts and canvas/WebGL pixels are intentionally excluded; not all dynamic text can be translated offline or guaranteed exact.

### How to test / วิธีทดสอบ

1. Download/extract the entire Repository ZIP from GitHub. Do not move `ByteSizedAlgorithms/` away from the shared `tools/` and `localization/` folders.
2. Open `ByteSizedAlgorithms/Launcher.bat` while online for the first download; the browser opens automatically at port 8128.
3. Click `TH · ไทย`. Verify menus, lesson headings, buttons, descriptions and new panels as you navigate the website.
4. Enable online translation if a long explanation remains in English. Check whether it changes to Thai and remains translated after reloading.
5. Select `Original`: all displayed text should return to the original site language; compare interactions with the source website.
6. Close CMD; reopen Launcher. Check no blank screen and selected language persists.
7. Run `Check_Clone.bat` to verify cached website entrypoint and localization resource files.

**Status:** Included in the approved v1.4.0 release. Source website bundles are not packaged and still download into ignored `site/` on the user's device.
