# SimulationLearning Portable EXE — 10 one-file Windows apps

**Branch:** [`feature/portable-exe-all-sites`](https://github.com/TOPTUBBY/Python-SimulationLearning/tree/feature/portable-exe-all-sites)

## Concept / แนวคิด

This is a separate development branch. **The 10 existing Python launchers stay unchanged.** The new Windows GUI application has an embedded Python runtime and starts a localhost HTTP server in the background. It opens the original website user interface in Microsoft Edge/Chrome; no CMD window or Python installation is required **on the recipient PC**. Closing the small control window stops the server.

โปรแกรมแยกออกเป็น EXE **1 ไฟล์ต่อ 1 เว็บไซต์** รวม 10 ไฟล์ ผู้ใช้ดับเบิลคลิก EXE แล้วเปิดหน้าเว็บใน Browser ได้เอง โดยไม่ต้องลง Python ที่เครื่องผู้ใช้ การปิดหน้าต่างควบคุมจะหยุด Server

| EXE (Bootstrap) | Port | Source folder |
|---|---:|---|
| `SimulationLearning-ESP32-8121.exe` | 8121 | `ESP32/` |
| `SimulationLearning-Arduino-8122.exe` | 8122 | `Arduino/` |
| `SimulationLearning-RoverKit-8123.exe` | 8123 | `RoverKit/` |
| `SimulationLearning-Multimeter-8124.exe` | 8124 | `Multimeter/` |
| `SimulationLearning-Protocol-8125.exe` | 8125 | `Protocol/` |
| `SimulationLearning-DesignedToScale-8126.exe` | 8126 | `DesignedToScale/` |
| `SimulationLearning-RoboticsLab-8127.exe` | 8127 | `RoboticsLab/` |
| `SimulationLearning-ByteSizedAlgorithms-8128.exe` | 8128 | `ByteSizedAlgorithms/` |
| `SimulationLearning-MoonLife-8129.exe` | 8129 | `MoonLife/` |
| `SimulationLearning-ESP32Labs-8130.exe` | 8130 | `ESP32Labs/` |

## Two build modes

**Bootstrap (recommended to share):** One `.exe` containing *only* our launcher, server and Thai UI code. The first launch **requires internet** to download the original public website's assets directly to `%LOCALAPPDATA%\SimulationLearning\<Site>\`. Later launches reuse the validated local cache; supported content can run offline. Missing/lazy assets, external APIs and online translation may still require network. The EXE does **not** contain or republish upstream website assets.

**Embedded (personal offline builds):** Include the downloaded website cache *inside* the single `.exe`. This can make it much bigger, and complete offline support is not guaranteed for dynamically loaded resources or remote APIs. **Do not distribute** an embedded EXE without verifying the third party's license/permission. Embedded mode disables automatic missing-asset downloads to keep its resource bundle read-only.

## Build on Windows

Builder requirements: **Windows 10/11 64-bit**, Python 3.8+ and an internet connection to install PyInstaller. Recipients do **not** need Python or PyInstaller.

1. Clone/download the complete repository and switch to `feature/portable-exe-all-sites`.
2. Double-click **`Build_Portable_All.bat`**. The build PC installs PyInstaller if needed.
3. Find ten standalone EXEs in `dist/portable/` and a JSON checksum report in the same folder.
4. Share *Bootstrap* EXEs individually. Recipients double-click the file, let first-run download finish, then their browser opens automatically.

### Advanced commands

```powershell
# One site (does not need cached vendor assets)
py -3 -m pip install "pyinstaller>=6,<7"
py -3 tools/build_portable.py --site Multimeter --mode bootstrap

# All ten EXEs, source-free and suitable for distribution
py -3 tools/build_portable.py --all --mode bootstrap

# Check offline cache status for all ten sites
py -3 tools/build_portable.py --all --mode embedded --check

# Optional personal-use EXE with cached website embedded
py -3 tools/build_portable.py --site RoboticsLab --mode embedded --download-missing
```

**Windows build only:** PyInstaller does not cross-compile Windows `.exe` from Linux. A GitHub Actions workflow (`.github/workflows/build-portable-exes.yml`) builds ten **Bootstrap** EXEs on Windows runners and uploads per-site workflow artifacts. The workflow does not package the vendor's website code.

## Startup crash fix (2026-11-24)

The first Windows one-file builds unexpectedly displayed **"No portable_selection.json in packaged application"** because their site selection data was missing from the runtime bundle. This revision **generates a unique Python entrypoint for every website** and compiles its project identity and build mode directly into the frozen EXE. It no longer depends on a JSON selector in the extracted archive.

Windows CI now starts **each actual built EXE** with `--self-test-output <path>` before publishing an artifact. The offline check verifies the frozen entrypoint, exact site identity, fixed port, build mode and required Thai UI assets without triggering any web download or opening a browser. Build success alone is not considered validation. Discard the original EXEs and use newly built artifacts from a passing smoke-tested run.

## First-run cache and updating

- Writable cache and persistent translation data: `%LOCALAPPDATA%\SimulationLearning\<Site>\`.
- Bootstrap first launch downloads to `site.__staging__/` or the ESP32 Labs slot-based cache. The server can use a verified cache **without renaming/copying hundreds of assets**, addressing the earlier ESP32 Labs WinError 5 / copy stall.
- If no verified cache exists and download fails, the app shows a clear error rather than a blank page.
- To refresh later, use the normal `Update_Clone.bat` from a local source checkout, or delete *only that site's downloaded cache* from LocalAppData while the EXE is stopped. Do not delete your `translation_cache.json` if you want to preserve translations.
- Default port remains fixed. If another service uses it, the application reports a port conflict. If the existing server is the same clone, double-clicking the EXE opens the already running website.
- Logs: `%LOCALAPPDATA%\SimulationLearning\<Site>\portable.log`.

## Testing / Verification

```powershell
py -3 -m unittest discover -s tests -p test_portable_exe.py -v
```

Automated tests cover all ten configs, modes, endpoint routing, local Thai UI, Moon Life overlay, ESP32 Labs subpath, offline missing asset handling and build arguments. They are **not** proof that the full original websites operate pixel-perfect, that all 3D interactions are offline, or that compiled Windows builds run on every PC. Run the [functional QA checklist](PORTABLE_QA_CHECKLIST.md) on a real Windows PC before merging this branch to `main`.

## Rights and safety

The MIT license in this repository covers independently authored toolkit code only. Original websites, their images, code, lessons, models and third-party assets remain under their respective licenses. Bootstrap EXEs do not ship third-party website content. Embedded builds are for private local verification unless rights permit distribution. Keep the server bound to `127.0.0.1` and do not forward ports publicly.
