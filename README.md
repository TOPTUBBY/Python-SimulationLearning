# SimulationLearning

A Windows-friendly collection of nine local-launch learning/simulation frontends. Each website is mirrored *from its original public site to your own PC on first launch*, then served from `127.0.0.1` at a fixed port. This repository contains **our own launcher, Python web server, mirror utility, validator, config, tests and documentation**. It does **not** contain the third-party frontends themselves.

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
| ByteSizedAlgorithms | [Byte-Sized Algorithms — Algo Lab](https://byte-sized-algorithms.vercel.app/#/big-o/1) | http://127.0.0.1:8128/#/big-o/1 | `ByteSizedAlgorithms/` |
| MoonLife | [Project Moon Life](https://project-moon-life.vercel.app/) | http://127.0.0.1:8129/ | `MoonLife/` |

## Quick start (Windows)

1. Install **Python 3.8+** from [python.org](https://www.python.org/downloads/windows/) and select **Add Python to PATH**. No pip packages or Node.js are required.
2. `git clone https://github.com/TOPTUBBY/Python-SimulationLearning.git` or download the repository as ZIP and extract it.
3. Double-click `ESP32/Launcher.bat` (or another project's `Launcher.bat`). On its **first launch**, it downloads that site's public JavaScript, CSS, models and other referenced assets to that project's local ignored `site/` directory. Internet access is required.
4. After the download passes the entrypoint check, the browser opens automatically at the assigned port. **Leave the CMD window running** while using the site. Close it or press Ctrl+C to stop the server.
5. On later launches the cached site is served without re-downloading. Use `Update_Clone.bat` when you want to refresh to the latest original version; use `Check_Clone.bat` to check local entrypoint integrity.

To start all nine servers at once, double-click `Launch_All.bat`. The nine servers use different ports. Expect nine CMD windows/browser tabs; downloading every site may take time the first time.

### ภาษาไทย — เริ่มใช้งาน

1. ติดตั้ง **Python 3.8 ขึ้นไป** โดยเลือก `Add Python to PATH` (ไม่ต้องติดตั้งไลบรารีเสริม)
2. ดาวน์โหลด ZIP จาก GitHub หรือ `git clone` แล้วแตกไฟล์โดย **คงโครงสร้างทุกโฟลเดอร์ไว้** เพราะ `tools/` เป็นส่วนกลาง
3. ดับเบิลคลิก `Launcher.bat` ในโฟลเดอร์เว็บที่ต้องการ เช่น `ESP32/Launcher.bat` ระบบจะดาวน์โหลดไฟล์ต้นฉบับเข้ามาใน `site/` เมื่อใช้งานครั้งแรก (ต้องมีอินเทอร์เน็ต)
4. หลังดาวน์โหลดเสร็จ เว็บจะเปิดเองที่พอร์ตของโครงการนั้น เปิดหน้าต่าง CMD ทิ้งไว้ระหว่างใช้งาน และปิดหน้าต่างเพื่อหยุด Server
5. กด `Update_Clone.bat` เมื่อต้องการอัปเดตไฟล์จากต้นฉบับ และ `Check_Clone.bat` เมื่อต้องการตรวจสอบไฟล์สำคัญ

**หมายเหตุ:** หากไม่มีไฟล์ `site/` และไม่มีอินเทอร์เน็ต Launcher จะแสดงข้อผิดพลาดและไม่เปิดหน้าเว็บว่าง; หลังมีแคชแล้วสามารถเปิดใหม่แบบไม่ดาวน์โหลดซ้ำได้ ฟีเจอร์บางอย่างอาจต้องใช้บริการออนไลน์ของต้นฉบับจึงจะใช้แบบ Offline ไม่ได้

## Project layout

```text
Python-SimulationLearning/
├── ESP32/
├── Arduino/
├── RoverKit/
├── Multimeter/
├── Protocol/
├── DesignedToScale/
├── RoboticsLab/
│   ├── Launcher.bat
│   ├── Update_Clone.bat
│   ├── Check_Clone.bat
│   ├── config.json
│   ├── server.py
│   ├── mirror.py
│   ├── verify_clone.py
│   └── site/                 # downloaded by user; gitignored
├── ByteSizedAlgorithms/
├── MoonLife/
│   ├── Launcher.bat
│   ├── Update_Clone.bat
│   ├── Check_Clone.bat
│   ├── config.json
│   ├── server.py
│   ├── mirror.py
│   ├── verify_clone.py
│   ├── README.md
│   └── translation/
│       ├── thai_dictionary.json
│       ├── thai_overlay.js
│       └── thai_overlay.css
│   ├── Launcher.bat
│   ├── Update_Clone.bat
│   ├── Check_Clone.bat
│   ├── config.json
│   ├── server.py
│   ├── mirror.py
│   ├── verify_clone.py
│   └── site/                 # downloaded locally; gitignored
├── tools/
│   ├── clone_runtime.py
│   └── moon_runtime.py     # common mirroring/check/server implementation
├── tests/
│   ├── test_runtime.py
│   ├── test_robotics.py
│   ├── test_byte_sized_algorithms.py
│   └── test_moonlife.py
├── docs/
│   ├── RELEASE_PROCESS.md
│   └── TROUBLESHOOTING.md
├── Launch_All.bat
├── Update_All.bat
├── Check_All.bat
├── CHANGELOG.md
├── VERSION
├── .gitignore
└── LICENSE
```

Every project directory contains the **same filenames** and the same small Python entrypoints. Different ports, routes and sources are read from its `config.json`; fixes to shared functionality are made once in `tools/clone_runtime.py`.

## Commands

Run from repository root (or click the corresponding BAT file):

```powershell
python ESP32/server.py --no-browser
python Arduino/mirror.py --jobs 8
python RoverKit/verify_clone.py
python Multimeter/server.py --port 8124
python DesignedToScale/server.py --update
python RoboticsLab/server.py --no-browser
python ByteSizedAlgorithms/server.py --no-browser
python MoonLife/server.py --no-browser
python -m unittest discover -s tests -v
```

### How updates work

- Updates download to `site.__staging__/`, validate the HTML plus root CSS/JS and only then replace `site/`. A failed update keeps the previous cache.
- Unresolved/lazy dynamic assets may be fetched from the original public site on demand while online.
- `Check_Clone.bat` checks key local files, **not** image-perfect accuracy or all runtime features.
- If the original website changes its bundler, requires authentication, blocks mirroring or serves assets from a third-party host, some content may not work offline.
- Port bindings are localhost-only (`127.0.0.1`), not publicly accessible from other network devices.

## Version control & releases

- Toolkit version: **`1.3.0`**, tracked in root `VERSION` and `CHANGELOG.md`.
- Recommended workflow: `main` = stable, `develop/vX.Y.Z` = development, `feature/*` = changes, `fix/*` = bug fixes; merge to main after tests. Release tags: `vX.Y.Z`.
- `site/` is ignored intentionally: downloaded third-party content must not be pushed to a public repository without appropriate rights.
- See [`docs/RELEASE_PROCESS.md`](docs/RELEASE_PROCESS.md) for release commands and [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) for Windows help.

## Robotics Lab validation

Robotics Lab includes eight interactive 3D boards, a Workbench, lessons, quizzes and assembly. Its new port, local mirroring, cache validation, HTTP health endpoint, and restart behavior are covered by local fixture tests. **The upstream WebGL visuals and all browser-only interactions require separate comparison on your Windows PC; 100% parity is not independently verified.** See [`RoboticsLab/README.md`](RoboticsLab/README.md) for the full checklist.

## Byte-Sized Algorithms validation

Byte-Sized Algorithms (Algo Lab) is an interactive course with 86 lessons in 14 chapters covering algorithm fundamentals, data structures, and complexity. It runs at `127.0.0.1:8128` after the first cache download. See [`ByteSizedAlgorithms/README.md`](ByteSizedAlgorithms/README.md) for the checklist covering animations, practice, cheatsheets, challenges, search, progress and restart behavior. **Automated fixture tests verify the local mirror/server infrastructure, not exact visual parity or offline behavior of every lesson.**

## Moon Life: Thai language support / ภาษาไทย

The ninth project, **[MoonLife](MoonLife/README.md)** on port **8129**, uses the same mirror/server launcher architecture and adds a **separate display-only Thai localization overlay**. It keeps the original game's bundled code unmodified. You can switch between **TH · ไทย** and **EN · Original** from the lower-right language panel.

- 249 built-in Thai translations cover menus, character creation, controls, status values and common UI terms.
- For unseen story/event strings, **optional online translation** sends text displayed in the game to Google Translate through the local server; translations are cached locally. Disable online translation in the panel to use the local dictionary/cache only.
- Translations and original game content may not match in all situations; new events can remain untranslated when offline. Save data at localhost is **separate** from saves on the original website due to browser origin isolation.
- The original game contains serious themes including death, illness and crime, and recommends ages 15+.
- The user approved integrating the preview; local fixture tests passed **12/12**, but actual full-game parity and comprehensive Thai translation still require real-world testing. See [MoonLife test notes](MoonLife/TEST_RESULTS.md).

## Source, attribution & license

These nine websites are the work of their respective original owners; see the source links above and their original websites for credits and usage terms. This project is an *independent local-run toolkit*, not an official mirror or ownership claim. The repository's **MIT LICENSE applies only to code written for this toolkit**, not to the original sites' bundled code, visual design, lessons, images, models, or trademarks. Respect the source websites' terms, intellectual property rights and server capacity. Do not mass-redistribute their assets.
