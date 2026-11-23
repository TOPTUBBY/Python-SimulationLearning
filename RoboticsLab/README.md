# Robotics Lab — Local Clone (Port 8127)

**Source:** https://robotics-lab-app.vercel.app/#uno  
**Local URL:** http://127.0.0.1:8127/#uno  
**Toolkit release:** v1.1.0 (approved for repository integration)  
**Requirements:** Windows and Python 3.8+ (standard library only).

## Quick start / วิธีใช้งาน

1. Clone or download the full Python-SimulationLearning repository. Keep the shared `tools/` directory next to `RoboticsLab/`.
2. Install Python 3.8+ and ensure `py -3` or `python` can run from CMD.
3. Connect to the internet for the **first run** and double-click `RoboticsLab/Launcher.bat`.
4. The first run downloads the original website's public front-end assets to `RoboticsLab/site/`. Once the entrypoint is checked, your browser opens automatically at `http://127.0.0.1:8127/#uno`.
5. Keep CMD open while using the page. Close it to stop; double-click the launcher again to reuse the cache.

**ภาษาไทย:** ติดตั้ง Python 3.8+ ดาวน์โหลดทั้ง Repository แล้วดับเบิลคลิก `RoboticsLab/Launcher.bat` เพื่อเปิดเว็บที่พอร์ต 8127 การเปิดครั้งแรกต้องใช้อินเทอร์เน็ตเพื่อดาวน์โหลดไฟล์เว็บต้นฉบับ หลังจากนั้นจะใช้ไฟล์แคชภายในเครื่อง โดยบางฟังก์ชันอาจยังต้องต่ออินเทอร์เน็ต

## Files

| File | Purpose |
|---|---|
| `Launcher.bat` | Start local HTTP server and open the web browser |
| `Update_Clone.bat` | Refresh original public assets, validating the download before replacing cache |
| `Check_Clone.bat` | Check local index, CSS, JS and downloaded manifest |
| `server.py` | Local server on port 8127 |
| `mirror.py` | Website downloader |
| `verify_clone.py` | Cache integrity validation |
| `config.json` | Original URL, port and launch route |
| `site/` | Locally downloaded third-party files; deliberately excluded from Git |

Shared implementation: `../tools/clone_runtime.py`. For the full setup and release policy see [the main README](../README.md).

## Functional checklist / รายการตรวจสอบ

Compare against the original website using the same computer/browser:

- [ ] Arduino Uno R3 loads in 3D and labels render instead of a black screen.
- [ ] Switch all 8 boards: Uno, Nano, Mega, ESP32, ESP8266, Pico, STM32 Blue Pill, Raspberry Pi 4.
- [ ] Rotate/zoom; Top, Bottom, Front, 3/4, Rotate and Labels work.
- [ ] Click labelled 3D components and inspect descriptions.
- [ ] Workbench opens; test wiring, missions and Run where supported upstream.
- [ ] Lessons, specification tables, pin explanations and Copy code work.
- [ ] Find-the-part quiz, hints, scoring and 3D assembly work.
- [ ] Comparison table switches the selected board correctly.
- [ ] Close CMD and restart the launcher; refresh without a blank screen.
- [ ] Test offline after the first successful download; record any external dependencies.

Automated tests validate **the local launcher/mirror/server infrastructure**, not full 3D/WebGL parity. Exact visual and functional equivalence is not guaranteed.

## Troubleshooting

- Black page: run `Check_Clone.bat`, then `Update_Clone.bat` while online; reopen and hard-refresh with Ctrl+Shift+R.
- WebGL not visible: check browser hardware acceleration and compare the original site on the same machine.
- Port 8127 already in use: `netstat -ano | findstr :8127`; do not terminate unrelated processes.
- First-run download fails: test the source site in the same network. Browser and Python may use different proxy settings.
- Workbench appears unavailable: compare the same section on the source website before concluding the clone is broken.

The original website, content and 3D assets belong to their respective owners. This repository contains independently authored local tooling, not the third-party site bundles.
