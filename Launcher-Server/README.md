# Launcher + Local Server (Python)

This directory contains all eleven browser-based website clones plus their launchers, shared mirror/download utilities, localization dictionaries and tests.

**การใช้งาน:** ติดตั้ง Python 3.8+ บน Windows จากนั้นดับเบิลคลิก `Launcher-Server/ESP32/Launcher.bat` (หรือเว็บอื่น) เพื่อให้โปรแกรมดาวน์โหลด Assets ครั้งแรกแล้วเปิด Browser อัตโนมัติ

## Programs

| Program | Port |
|---|---:|
| ESP32 | 8121 |
| Arduino | 8122 |
| RoverKit | 8123 |
| Multimeter | 8124 |
| Protocol | 8125 |
| DesignedToScale | 8126 |
| RoboticsLab | 8127 |
| ByteSizedAlgorithms | 8128 |
| MoonLife | 8129 |
| ESP32Labs | 8130 |
| **HowItsWired** | **8131** |
| **HowItsWired** | **8131** |

- `Launch_All.bat`: launch all eleven servers
- `Update_All.bat`: update local cached websites
- `Check_All.bat`: validate downloaded caches
- `Check_Thai_UI.bat`: test Thai localization
- `tools/`: shared Python server and localizer code
- `localization/`: original Thai translations and site-specific dictionaries
- `tests/`: server/mirror regression tests

Offline after first run depends on the original website's reliance on remote APIs or lazy assets. Site caches remain under each project folder and are not committed to Git.


## How It’s Wired (Port 8131)

`HowItsWired/Launcher.bat` launches the 37-lesson interactive 3D wiring course at `http://127.0.0.1:8131/lead-load`. The cache manager is Windows-safe and uses verified cache slots without moving hundreds of files. `Update_Clone.bat` and `Check_Clone.bat` are included. Language picker: TH / Original; new text can optionally be translated online. See `HowItsWired/README.md`. Approved for stable v1.7.0 integration. Functionality of the third-party site still depends on first-run download.
