# Robotics Lab — Local Clone (Port 8127)

**Source:** https://robotics-lab-app.vercel.app/#uno  
**Local URL:** http://127.0.0.1:8127/#uno  
**Project release:** v1.1.0 (approved; included in main repository)  
**Shared runtime:** SimulationLearning v1.1.0, Python standard library only.

## Quick start / วิธีติดตั้ง

1. Extract the ZIP. Keep `RoboticsLab/` and `tools/` as sibling folders.
2. Install **Python 3.8+** with `py -3` or `python` available on PATH.
3. Connect to the internet on your first run. Double-click `RoboticsLab/Launcher.bat`.
4. Wait for the `Mirror update installed` message. The browser launches automatically at `http://127.0.0.1:8127/#uno`.
5. Close CMD to stop the local server. Double-click `Launcher.bat` again to reuse the local copy without another full download.

## Files

| File | Purpose |
| --- | --- |
| `Launcher.bat` | Start local HTTP server / open browser automatically |
| `Update_Clone.bat` | Download a fresh website snapshot to staging, validate and swap |
| `Check_Clone.bat` | Verify entrypoint JS, CSS and manifest |
| `mirror.py` | Python mirror entrypoint; uses shared runtime |
| `server.py` | Python local server entrypoint; port 8127 |
| `verify_clone.py` | Python integrity checker entrypoint |
| `config.json` | Original URL, route, port, ID |
| `site/` | Original assets downloaded **locally** at first launch; ignored by Git |

## Testing checklist / ตรวจสอบการทำงาน

Please compare **original site and local mirror in the same browser**:

- [ ] Landing view: Arduino Uno R3 appears, models and labels render (not a black screen)
- [ ] Select all eight boards: Uno, Nano, Mega, ESP32, ESP8266, Pico, STM32 Blue Pill, Raspberry Pi 4
- [ ] Mouse rotates/zooms 3D board; Top, Bottom, Front, 3/4 and Rotate behave as expected
- [ ] Toggle Labels; click each highlighted component and view part description
- [ ] Workbench opens; test mission, wiring pins and Run if available upstream
- [ ] Lesson text, specs, pins, copy-first-code work
- [ ] Find-the-part quiz, hints, score, and assembly sequence work
- [ ] Comparison table shows all eight boards and switches board on click
- [ ] Restart test: close CMD; open Launcher again; hard refresh Ctrl+Shift+R; no blank page
- [ ] Offline test: after successful first download and visiting all tabs online, disconnect internet, reload and check required features

**Important:** An identical 100% experience is not yet verified. Runtime assets/API requests fetched from other hosts and content loaded only on demand may need an internet connection; the upstream website can also change. This package downloads the original site's public front-end assets only when run on your own device; it does not include or claim rights to third-party source code or media.

## Troubleshooting

- Blank / black page: run `Check_Clone.bat` then `Update_Clone.bat` while online; close and reopen Launcher, then Ctrl+Shift+R.
- If the first download cannot connect, test the original site in the same PC/browser (corporate proxy and filtering may differ between browser and Python).
- If port 8127 is occupied: use `netstat -ano | findstr :8127` and stop the conflicting process; the launcher won't kill other applications.
- If 3D is black: verify WebGL/hardware acceleration enabled in Chrome/Edge; compare the original page on the same PC.
- If you see `Workbench is still being set up`, also check the original site; this behavior may come from the upstream site.
- For debug logs and direct invocation: `py -3 RoboticsLab\server.py --no-browser`, `py -3 RoboticsLab\mirror.py`, `py -3 RoboticsLab\verify_clone.py` from the package root.

## Repository integration

Included in [`Python-SimulationLearning`](https://github.com/TOPTUBBY/Python-SimulationLearning) as the seventh site. Use the shared `../tools/clone_runtime.py`. Original site bundles in `site/` are always excluded from Git.

---

## Thai UI — v1.4.0

- Website: **RoboticsLab** (Eight 3D boards / quiz / workbench)
- Local address: **http://127.0.0.1:8127/#uno**
- Language panel: `TH · ไทย` / `Original` at the bottom-right (collapsible).
- **Original is the default** to avoid unexpected changes. Click `TH · ไทย` to enable Thai, and `Original` to restore the source language.
- Each site's language and online-translation setting is remembered in browser localStorage.
- Offline: curated Thai UI dictionary (shared + site-specific) and previously cached translations.
- Optional online: click **แปลข้อความใหม่ผ่านออนไลน์** to translate unseen, dynamically loaded sentences. **Displayed text** may be transmitted to Google Translate, then cached in the current project folder in `translation_cache.json`.
- Code examples, editable fields, numeric readouts and canvas/WebGL pixels are intentionally excluded; not all dynamic text can be translated offline or guaranteed exact.

### How to test / วิธีทดสอบ

1. Download/extract the entire Repository ZIP from GitHub. Do not move `RoboticsLab/` away from the shared `tools/` and `localization/` folders.
2. Open `RoboticsLab/Launcher.bat` while online for the first download; the browser opens automatically at port 8127.
3. Click `TH · ไทย`. Verify menus, lesson headings, buttons, descriptions and new panels as you navigate the website.
4. Enable online translation if a long explanation remains in English. Check whether it changes to Thai and remains translated after reloading.
5. Select `Original`: all displayed text should return to the original site language; compare interactions with the source website.
6. Close CMD; reopen Launcher. Check no blank screen and selected language persists.
7. Run `Check_Clone.bat` to verify cached website entrypoint and localization resource files.

**Status:** Included in the approved v1.4.0 release. Source website bundles are not packaged and still download into ignored `site/` on the user's device.
