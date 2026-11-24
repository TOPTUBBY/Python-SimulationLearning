# Python-SimulationLearning — Launcher/Server & Portable EXE

**Version 1.6.0 | 10 websites | ports 8121–8130 | Thai language support**

The project provides two ways to run the same interactive simulation/learning sites.

| Section | Purpose | How to run |
|---|---|---|
| [Launcher-Server/](Launcher-Server/) | Python launchers, local web servers, mirror/update/check and Thai UI | Double-click `Launcher-Server/<Site>/Launcher.bat` (Python 3.8+ required) |
| [Portable/](Portable/) | **Ten standalone Windows EXEs**, builder, tests and release downloader | Download [Portable/EXE/](Portable/EXE/) builds; double-click an EXE (no Python installation) |

### Quick start / วิธีใช้งาน

**Portable:** Download the [latest GitHub Release](https://github.com/TOPTUBBY/Python-SimulationLearning/releases/latest) containing `SimulationLearning_Portable_10_EXEs.zip`, or double-click `Portable/EXE/Download_All_EXEs.bat` after downloading this source repository. The batch downloader extracts all ten EXEs to `Portable/EXE/`. Double-click any EXE to open a localhost web server and browser automatically; close its control window to stop it. **Internet is needed on first launch**, because EXEs are bootstrap builds: original website assets are downloaded to `%LOCALAPPDATA%\SimulationLearning\<Site>\` on your machine.

**Launcher/Server:** Install Python 3.8+, download the entire repository, then double-click `Launcher-Server/ESP32/Launcher.bat` (or another website). Shared code lives in `Launcher-Server/tools/` and Thai dictionaries in `Launcher-Server/localization/`. Run `Launcher-Server/Launch_All.bat` to start ten local sites.

**Build your own EXEs:** On Windows, run `Portable/Build_Portable_All.bat`. Built programs go to `Portable/EXE/`. A GitHub Actions workflow builds, smoke-tests and publishes the ten standalone apps in release assets; compiled binaries are intentionally **not committed to Git history**.

### Websites and assigned ports

| Site | Port | Original website |
|---|---:|---|
| ESP32 | 8121 | https://learn-esp32.vercel.app/#board |
| Arduino | 8122 | https://learn-arduino-red.vercel.app/#board |
| RoverKit | 8123 | https://roverkit.vercel.app/#drive |
| Multimeter | 8124 | https://electronics-101-six.vercel.app/multimeter |
| Protocol Explorer | 8125 | https://protocol-explorer-alpha.vercel.app/ |
| Designed to Scale | 8126 | https://designed-to-scale.vercel.app/#/ |
| Robotics Lab | 8127 | https://robotics-lab-app.vercel.app/#uno |
| Byte-Sized Algorithms | 8128 | https://byte-sized-algorithms.vercel.app/#/big-o/1 |
| Moon Life | 8129 | https://project-moon-life.vercel.app/ |
| ESP32 Labs | 8130 | https://ionloft.com/esp-labs/#/?lang=en |

### Folder structure
```text
Python-SimulationLearning/
├── Launcher-Server/
│   ├── ESP32/ Arduino/ RoverKit/ Multimeter/ Protocol/
│   ├── DesignedToScale/ RoboticsLab/ ByteSizedAlgorithms/ MoonLife/ ESP32Labs/
│   ├── tools/  localization/  tests/  docs/
│   ├── Launch_All.bat  Update_All.bat  Check_All.bat
│   └── README.md
├── Portable/
│   ├── EXE/                   # EXEs downloaded from a Release or built locally
│   │   ├── Download_All_EXEs.bat
│   │   └── README.md
│   ├── build_portable.py  portable_launcher.py  package_exes.py
│   ├── Build_Portable_All.bat  Check_Portable_Caches.bat
│   ├── docs/  tests/
│   └── README.md
├── .github/workflows/build-portable-exes.yml
├── README.md  CHANGELOG.md  VERSION  LICENSE
```

### Tests and limits

```bash
python -m unittest discover -s Launcher-Server/tests -v
python -m unittest discover -s Portable/tests -v
```

The original website's 3D content, lessons, scripts and models are **not packaged in the bootstrap EXEs or uploaded to this source repository**. They remain subject to their original authors' rights; the MIT toolkit license does not cover them. Thai translations cover many UI labels but not all Canvas/WebGL or dynamically generated text. Full browser parity and offline behavior must be tested per site.
