# Python-SimulationLearning — Launcher/Server & Portable EXE

**Version 1.7.0 | 11 websites | Ports 8121–8131 | Thai language support**

The repository contains an independently authored local launch/mirror toolkit. Run each simulation/learning website from its original public website on your own PC, with two usage options:

| Section | What it provides | Requirements for recipients |
|---|---|---|
| [Launcher-Server/](Launcher-Server/) | Python launcher, update/check, local HTTP server, Thai UI, tests | Windows + Python 3.8+ |
| [Portable/](Portable/) | 11 standalone Windows x64 executables, build sources and Release downloader | Windows 10/11 x64; no Python required |

## Quick start / วิธีใช้งาน

**Portable (แนะนำสำหรับผู้ใช้ทั่วไป):** Download the [v1.7.0 Release](https://github.com/TOPTUBBY/Python-SimulationLearning/releases/tag/v1.7.0) or run [Portable/EXE/Download_All_EXEs.bat](Portable/EXE/Download_All_EXEs.bat) after downloading the source repository. It downloads `SimulationLearning_Portable_11_EXEs.zip` and extracts the EXEs into `Portable/EXE/`. Double-click the desired EXE. A browser opens at its designated local URL. Keep the small control window open during use; close it to stop the server. On the first run, internet is required to download the upstream public frontend into `%LOCALAPPDATA%\SimulationLearning\<Site>\`.

**Launcher-Server:** Install Python 3.8+ on Windows, download/clone the *whole repository*, then double-click `Launcher-Server/<Site>/Launcher.bat`. First launch requires internet to download the site's public assets. Use `Update_Clone.bat` to refresh the cache or `Check_Clone.bat` to validate it. `Launcher-Server/Launch_All.bat` launches all 11 sites on different ports. Keep the CMD window open while using a site.

**สร้าง EXE เอง:** On Windows, use `Portable/Build_Portable_All.bat` to build 10 legacy PyInstaller apps plus the new Go-based HowItsWired EXE. Requires Python/PyInstaller and Go 1.23+ on the *builder PC only*. GitHub Actions builds all 11 apps on Windows, smoke-tests each binary, then packages them for GitHub Releases. Compiled EXEs are not committed to Git history.

## Sites and local ports

| Site | Port | Original website | Local route |
|---|---:|---|---|
| ESP32 | 8121 | https://learn-esp32.vercel.app/#board | `/#board` |
| Arduino | 8122 | https://learn-arduino-red.vercel.app/#board | `/#board` |
| RoverKit | 8123 | https://roverkit.vercel.app/#drive | `/#drive` |
| Multimeter | 8124 | https://electronics-101-six.vercel.app/multimeter | `/multimeter` |
| Protocol Explorer | 8125 | https://protocol-explorer-alpha.vercel.app/ | `/` |
| Designed to Scale | 8126 | https://designed-to-scale.vercel.app/#/ | `/#/` |
| Robotics Lab | 8127 | https://robotics-lab-app.vercel.app/#uno | `/#uno` |
| Byte-Sized Algorithms | 8128 | https://byte-sized-algorithms.vercel.app/#/big-o/1 | `/#/big-o/1` |
| Moon Life | 8129 | https://project-moon-life.vercel.app/ | `/` |
| ESP32 Labs | 8130 | https://ionloft.com/esp-labs/#/?lang=en | `/esp-labs/#/?lang=en` |
| **How It’s Wired** | **8131** | https://how-its-wired.vercel.app/lead-load | **`/lead-load`** |

## Repository structure

```text
Python-SimulationLearning/
├── Launcher-Server/
│   ├── ESP32/ ... ESP32Labs/
│   ├── HowItsWired/           # 8131 launcher, mirror, checker and config
│   ├── tools/                 # shared Python runtime and site-specific wrappers
│   ├── localization/          # Thai/Original UI dictionaries and overlay
│   │   └── sites/how-its-wired.json
│   ├── tests/  docs/
│   ├── Launch_All.bat  Update_All.bat  Check_All.bat
│   └── README.md
├── Portable/
│   ├── EXE/                   # EXEs downloaded from Releases or built locally
│   │   ├── Download_All_EXEs.bat
│   │   └── README.md
│   ├── HowItsWired/           # Go source, embedded Thai UI, Windows builder
│   ├── build_portable.py  portable_launcher.py  package_exes.py
│   ├── Build_Portable_All.bat  Check_Portable_Caches.bat
│   ├── docs/  tests/
│   └── README.md
├── .github/workflows/build-portable-exes.yml
├── README.md  CHANGELOG.md  VERSION  LICENSE
```

The Python Launcher and Portable versions use separate, persistent per-user caches. Avoid launching the Python and Portable version of the *same* website simultaneously because they bind to the same port.

## Thai UI and scope

The **TH · ไทย / Original** picker is available in all 11 sites, including How It’s Wired. Local dictionaries cover major controls and lesson names; optional online translation is OFF by default for HowIt’sWired and most other sites. Enabling it can send visible text to Google Translate. It does not translate raw Canvas/WebGL pixels or executable code. Switching languages should not alter the simulator’s underlying logic.

Original site JavaScript, CSS, 3D models, images and lesson content are **not embedded into the bootstrap EXEs and are not tracked in this repository**. The first run downloads publicly accessible assets onto the user's machine. Some external API calls or lazy resources can still require internet afterward. Toolkit MIT license does **not** relicense third-party website content.

## Validation & troubleshooting

```bash
python -m unittest discover -s Launcher-Server/tests -v
python -m unittest discover -s Portable/tests -v
cd Portable/HowItsWired && go test -v ./...
```

Python tests cover launcher/server and optional localization using offline fixtures. Windows CI tests actual compiled EXE identity and bundled runtime resources. **These checks do not prove visual/functional parity with each upstream website or complete offline operation.** See [HowItsWired/README.md](Launcher-Server/HowItsWired/README.md), [Portable usage](Portable/README.md) and [test checklist](TEST_CHECKLIST.md).

**Security and rights:** Local servers bind to `127.0.0.1` only. Follow each source website's terms and intellectual property rights. Do not redistribute mirrored third-party assets unless authorized. Electrical wiring lessons are educational and are not a substitute for local electrical codes or professional inspection.
