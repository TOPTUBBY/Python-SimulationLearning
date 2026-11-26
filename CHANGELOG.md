# Changelog

## [1.7.0] - 2026-11-26

### Added
- **How It’s Wired** as website #11 (`Launcher-Server/HowItsWired/`), opening `/lead-load` on port `8131`.
- Matching `Launcher.bat`, `Update_Clone.bat`, `Check_Clone.bat`, Python runtime wrapper, curated Thai dictionary and offline fixture tests.
- Single-file native Windows x64 **Portable/HowItsWired** Go EXE with its own local HTTP server, Thai/Original picker, and user-local cache.
- Updated Launch/Update/Check All and Windows GitHub Actions build matrix for **11** EXEs; actual compiled-binary smoke tests and ZIP checksum verification.

### Changed
- Extended the two-section `Launcher-Server/` and `Portable/` layout without changing the previous ten site configurations/ports.
- Updated README, VERSION, executable downloader and release packaging for `SimulationLearning_Portable_11_EXEs.zip`.
- Added `.active-cache.json` patterns to Git exclusions (HowIt’sWired uses a Windows-safe slot selector).

### Verification & limitations
- User approved the HowItsWired preview for integration.
- Local Python Launcher-Server tests passed 73/73; legacy Portable suite passed 11/11; Go tests passed 4/4 on offline fixtures before integration.
- User should still compare the live 3D simulator and all language strings against the original. The bootstrap executable does not distribute third-party site assets; internet is required for first launch.

## [1.6.0] - 2026-11-24

### Added
- Stable integration of the approved Portable EXE build for all 10 websites (ports 8121–8130).
- Two clearly separated user-facing sections: `Launcher-Server/` and `Portable/`.
- `Portable/EXE/` destination with one-click GitHub Release download helper.
- GitHub Actions Windows matrix build, runtime smoke-tests, and automatic release asset publication.
- `Portable/package_exes.py` for EXE completeness, `MZ` signature and checksum validation.

### Changed
- Existing Python launchers, shared runtime, Thai localization and regression tests moved together under `Launcher-Server/` (no website port or feature changes).
- Portable EXE sources, tests, documentation, build scripts and output collected under `Portable/`.
- Portable Python builder updated for the new directory layout; no runtime selection JSON required.
- Published bootstrap builds download original site assets only on first run; no third-party website bundles committed.

### Verification
- Existing Portable EXEs were user-tested after the packaged identity hotfix.
- Python regression suites and generated startup tests should pass after reorganizing paths.
- Windows GitHub Actions will rebuild and test binaries for the new structure.

---
# Changelog — SimulationLearning

## [1.4.0] — 2026-11-24

- Thai / Original switcher added for ESP32, Arduino, RoverKit, Multimeter, Protocol, DesignedToScale, RoboticsLab and ByteSizedAlgorithms.
- 265 curated common UI strings and per-site topic dictionaries; opt-in online fallback, local cache, dynamic DOM updates, reversible switching.
- New shared `tools/thai_runtime.py` and `localization/` folder, no original upstream app bundles.
- Existing Moon Life Thai runtime left unchanged.
- Approved for release to `main`; original site assets excluded from source control.

# Changelog

This changelog tracks **SimulationLearning's local launcher/mirror toolkit**, not changes to the original third-party websites. Versions follow [Semantic Versioning](https://semver.org/).

## [1.3.0] — Approved stable · 2026-11-24

- Added Project Moon Life on port 8129, with an independent Thai translation overlay, optional online translation and cached results.
- Updated release docs, launchers and port range to 8121–8129.
- Source-site game assets remain untracked.

## [1.2.0] — Approved stable · 2026-11-24

- Added Byte-Sized Algorithms on port 8128, with dedicated launcher, updater and checker.
- Updated README, changelog, shared runtime version and all-site launchers.

## [1.1.0] - 2026-11-23

### Added
- Added **Robotics Lab** as the seventh local simulation website (`RoboticsLab/`), using `http://127.0.0.1:8127/#uno`.
- Added the same launcher, updater, validator and Python entrypoints used by the six existing sites.
- Included Robotics Lab in the root `Launch_All.bat`, `Update_All.bat`, and `Check_All.bat` commands.
- Added a WebGL/Workbench/Quiz/Assembly verification checklist and local fixture regression test.

### Changed
- Updated bilingual README, project layout, version metadata and release guide for seven websites.
- Bumped shared runtime version to `1.1.0` without changing existing mirroring behavior.

### Notes
- Robotics Lab was approved by the user for integration into the GitHub repository.
- Upstream JavaScript/CSS, 3D models and other third-party assets remain excluded from Git.
- Actual visual parity and all browser-only features require testing on the user’s Windows PC.

## [1.0.0] - 2026-11-23

### Added
- Unified structure for ESP32, Arduino, RoverKit, Multimeter, Protocol Explorer and Designed to Scale.
- Dedicated Windows launchers and ports `8121`–`8126` with automatic browser opening.
- Standard `Update_Clone.bat`, `Check_Clone.bat`, `server.py`, `mirror.py`, `verify_clone.py` per project.
- Shared Python-standard-library engine and per-project `config.json`.
- Atomic cache updates with rollback on failure, incremental on-demand recovery of missing assets, and an online-first initial setup.
- HTTP health endpoint, SPA route support (including `/multimeter`), cache-control headers, and explicit port collision handling.
- Local validation checks and test suite.
- Bilingual README and documented version/branch/release workflow.

### Notes
- Public third-party website assets are **not** committed. They are retrieved by users directly from the original websites.
- Online first-run mirroring and full visual parity have not been verified for all sites in this execution environment.

## [Unreleased] — feature/portable-exe-all-sites (2026-11-24)

### Added (development only)
- Portable Windows EXE launcher with background localhost server, automatic browser opening, Tk control window and persistent AppData.
- Two packaging modes: small Bootstrap EXE (downloads original website assets on first launch) and optional Embedded EXE (bundles validated local assets).
- One-file PyInstaller build tooling for all ten websites, Windows build batch script, local QA checklist, cross-platform fixtures and matrix GitHub Actions Windows builds.
- Cache-slot recovery without copying or renaming hundreds of original website files, retaining Thai UI, Moon Life and ESP32 Labs path handling.

### Notes
- Main branch remains v1.5.0 until explicit validation and merge.
- Do not publish embedded third-party website assets without permission.
- Windows EXEs and real-browser functionality require validation on Windows before a stable release.


## [Unreleased]
- No changes yet.
