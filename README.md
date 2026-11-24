# SimulationLearning

A Windows-friendly collection of ten local-launch learning/simulation frontends. Each website is mirrored *from its original public site to your own PC on first launch*, then served from `127.0.0.1` at a fixed port. This repository contains **our own launcher, Python web server, mirror utility, validator, config, tests and documentation**. It does **not** contain the third-party frontends themselves.

> **Status:** Local infrastructure and regression tests have been implemented. Actual online download, visual fidelity, interactive 3D simulations, multi-language lessons, and offline coverage must still be checked on a networked Windows PC. "100% identical" is not guaranteed.

## Sites & fixed ports

| Project | Original website | Local address | Folder |
|---|---|---|---|
| ESP32 | [Learn ESP32](https://learn-esp32.vercel.app/#board) | http://127.0.0.1:8121/#board | `ESP32/` |
| Arduino | [Learn Arduino](https://learn-arduino-red.vercel.app/#board) | http://127.0.0.1:8122/#board | `Arduino/` |
| RoverKit | [RoverKit](https://roverkit.vercel.app/#drive) | http://127.0.0.1:8123/#drive | `RoverKit/` |
| Multimeter | [Electronics 101](https://electronics-101-six.vercel.app/multimeter) | http://127.0.0.1:8124/multimeter | `Multimeter/` |
| Protocol | [Protocol Explorer](https://protocol-explorer-alpha.vercel.app/) | http://127.0.0.1:8125/ | `Protocol/` |
| DesignedToScale | [Designed to Scale](https://designed-to-scale.vercel.app/#/) | http://127.0.0.1:8126/#/ | `DesignedToScale/` |
| RoboticsLab | [Robotics Lab](https://robotics-lab-app.vercel.app/#uno) | http://127.0.0.1:8127/#uno | `RoboticsLab/` |
| ByteSizedAlgorithms | [Byte-Sized Algorithms](https://byte-sized-algorithms.vercel.app/#/big-o/1) | http://127.0.0.1:8128/#/big-o/1 | `ByteSizedAlgorithms/` |
| MoonLife | [Moon Life](https://project-moon-life.vercel.app/) | http://127.0.0.1:8129/ | `MoonLife/` |
| ESP32Labs | [ESP32-S3 Bench Guide](https://ionloft.com/esp-labs/#/?lang=en) | http://127.0.0.1:8130/esp-labs/#/?lang=en | `ESP32Labs/` |

## Thai UI — v1.5.0

**New:** Thai / Original language picker for the first eight websites (ports 8121–8128). Moon Life (8129) already has its own Thai overlay. ESP32 Labs (8130) now offers a Thai / Original picker with Thai shown by default; the first nine sites retain their earlier behavior. The picker is independent of upstream site code and does not modify downloaded assets.

Choose `TH · ไทย` at the bottom-right. Local dictionaries cover common controls and site-specific topics. The optional **online translation switch is OFF by default** to avoid sending displayed text to an external service without your choice. When enabled, unseen text is translated via Google Translate and cached locally. Switching back to `Original` restores the displayed source language. No translation applies to code, editable inputs, numeric readouts or text rendered directly inside Canvas/WebGL.

**Validation:** see [`THAI_TEST_CHECKLIST.md`](THAI_TEST_CHECKLIST.md). The local fixture tests pass; complete visual/function parity and translation of every sentence cannot be guaranteed without browser testing against original sites.

## Quick start (Windows)

1. Install **Python 3.8+** from [python.org](https://www.python.org/downloads/windows/) and select **Add Python to PATH**. No pip packages or Node.js are required.
2. Clone the repository or download its ZIP from GitHub, then extract it while retaining the shared `tools/` and `localization/` folders.
3. Double-click `ESP32/Launcher.bat` (or another project's `Launcher.bat`). On its **first launch**, it downloads that site's public JavaScript, CSS, models and other referenced assets to that project's local ignored `site/` directory. Internet access is required.
4. After the download passes the entrypoint check, the browser opens automatically at the assigned port. **Leave the CMD window running** while using the site. Close it or press Ctrl+C to stop the server.
5. On later launches the cached site is served without re-downloading. Use `Update_Clone.bat` when you want to refresh to the latest original version; use `Check_Clone.bat` to check local entrypoint integrity.

To start all ten servers at once, double-click `Launch_All.bat`. The ten servers use different ports. Expect ten CMD windows/browser tabs; downloading every site may take time the first time.

### ภาษาไทย — เริ่มใช้งาน

1. ติดตั้ง **Python 3.8 ขึ้นไป** โดยเลือก `Add Python to PATH` (ไม่ต้องติดตั้งไลบรารีเสริม)
2. ดาวน์โหลด ZIP รุ่นล่าสุดจาก GitHub หรือใช้ `git clone` แล้วแตกไฟล์โดย **คงโครงสร้างทุกโฟลเดอร์ไว้** เพราะ `tools/` และ `localization/` เป็นส่วนกลาง
3. ดับเบิลคลิก `Launcher.bat` ในโฟลเดอร์เว็บที่ต้องการ เช่น `ESP32/Launcher.bat` ระบบจะดาวน์โหลดไฟล์ต้นฉบับเข้ามาใน `site/` เมื่อใช้งานครั้งแรก (ต้องมีอินเทอร์เน็ต)
4. หลังดาวน์โหลดเสร็จ เว็บจะเปิดเองที่พอร์ตของโครงการนั้น เปิดหน้าต่าง CMD ทิ้งไว้ระหว่างใช้งาน และปิดหน้าต่างเพื่อหยุด Server
5. กด `Update_Clone.bat` เมื่อต้องการอัปเดตไฟล์จากต้นฉบับ และ `Check_Clone.bat` เมื่อต้องการตรวจสอบไฟล์สำคัญ

**หมายเหตุ:** หากไม่มีไฟล์ `site/` และไม่มีอินเทอร์เน็ต Launcher จะแสดงข้อผิดพลาดและไม่เปิดหน้าเว็บว่าง; หลังมีแคชแล้วสามารถเปิดใหม่แบบไม่ดาวน์โหลดซ้ำได้ ฟีเจอร์บางอย่างอาจต้องใช้บริการออนไลน์ของต้นฉบับจึงจะใช้แบบ Offline ไม่ได้

## Project layout

```text
Python-SimulationLearning/
├── ESP32/                 # port 8121
├── Arduino/               # port 8122
├── RoverKit/              # port 8123
├── Multimeter/            # port 8124
├── Protocol/              # port 8125
├── DesignedToScale/       # port 8126
├── RoboticsLab/           # port 8127
├── ByteSizedAlgorithms/   # port 8128
├── MoonLife/              # port 8129 (independent Thai support)
├── ESP32Labs/             # port 8130 (subpath mirror, Thai UI)
├── localization/
│   ├── thai_overlay.js
│   ├── thai_overlay.css
│   ├── common_th.json
│   └── sites/              # one dictionary per website
├── tools/
│   ├── clone_runtime.py   # original shared mirror/server
│   ├── esp_labs_runtime.py # ESP32 Labs cache-slot/subpath adapter
│   ├── moon_runtime.py    # existing Moon Life Thai feature
│   └── thai_runtime.py    # Thai UI server wrapper
├── tests/
│   └── test_thai_ui.py    # Thai UI regression suite (plus existing tests)
├── docs/
├── THAI_TEST_CHECKLIST.md
├── VERSION                 # 1.5.0
├── Launch_All.bat
├── Update_All.bat
├── Check_All.bat
└── README.md
```

Each website folder contains `Launcher.bat`, `Update_Clone.bat`, `Check_Clone.bat`, `server.py`, `mirror.py`, `verify_clone.py`, and `config.json` plus per-site README. Its `site/` cache is created locally on first run and is **not included** in this archive.

## Commands

Run from repository root (or click the corresponding BAT file):

```powershell
python ESP32/server.py --no-browser
python Arduino/mirror.py --jobs 8
python RoverKit/verify_clone.py
python Multimeter/server.py --port 8124
python DesignedToScale/server.py --update
python RoboticsLab/server.py --no-browser
python ESP32Labs/server.py --no-browser
python -m unittest discover -s tests -v
```

### ESP32 Labs (port 8130): Windows-safe cache management

The new ESP32 Labs adapter preserves the upstream `/esp-labs/` subpath and adds a display-only Thai language overlay. Following the approved rc.3 hotfix, a verified `site.__staging__/` cache is served directly without copying or renaming hundreds of files. Explicit updates download into an inactive slot (`site.__next__/` or `site.__staging__/`) and select it using the small `site.__active__.json` marker. If an update fails, the last verified cache remains available. See [ESP32 Labs instructions](ESP32Labs/README.md) and [test checklist](ESP32Labs/TEST_CHECKLIST.md).

### How updates work

- Standard sites stage downloads before replacing the active cache. ESP32 Labs uses its verified-cache-slot approach described above. Failed updates retain the last verified cache.
- Unresolved/lazy dynamic assets may be fetched from the original public site on demand while online.
- `Check_Clone.bat` checks key local files, **not** image-perfect accuracy or all runtime features.
- If the original website changes its bundler, requires authentication, blocks mirroring or serves assets from a third-party host, some content may not work offline.
- Port bindings are localhost-only (`127.0.0.1`), not publicly accessible from other network devices.

## Version control & releases

- Current stable toolkit version: **`1.5.0`** (`VERSION`). Thai language overlays are available across all ten websites (Moon Life retains its independent implementation).
- Recommended workflow: `main` = stable, `develop/vX.Y.Z` = development, `feature/*` = changes, `fix/*` = bug fixes; merge to main after tests. Release tags: `vX.Y.Z`.
- `site/` is ignored intentionally: downloaded third-party content must not be pushed to a public repository without appropriate rights.
- See [`docs/RELEASE_PROCESS.md`](docs/RELEASE_PROCESS.md) for release commands and [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) for Windows help.

## Robotics Lab quality checks

Robotics Lab features 3D/WebGL boards, Workbench, lessons, quizzes and assembly. Its local launcher, mirroring, startup, health endpoint and restart were tested with offline fixtures. **Visual/functional equivalence of the original WebGL experience has not been independently verified**. Compare the local site with upstream and follow the checklist in [`RoboticsLab/README.md`](RoboticsLab/README.md).

## Source, attribution & license

These ten websites are the work of their respective original owners; see the source links above and their original websites for credits and usage terms. This project is an *independent local-run toolkit*, not an official mirror or ownership claim. The repository's **MIT LICENSE applies only to code written for this toolkit**, not to the original sites' bundled code, visual design, lessons, images, models, or trademarks. Respect the source websites' terms, intellectual property rights and server capacity. Do not mass-redistribute their assets.
