# Changelog

This changelog tracks **SimulationLearning's local launcher/mirror toolkit**, not changes to the original third-party websites. Versions follow [Semantic Versioning](https://semver.org/).

## [1.2.0] - 2026-11-24

### Added
- Byte-Sized Algorithms (Algo Lab) as website #8 on port `8128` and route `/#/big-o/1`.
- Standard launcher, updater, validator, configuration, bilingual guide and offline fixture tests.
- Added the eighth website to `Launch_All.bat`, `Update_All.bat` and `Check_All.bat`.

### Changed
- Updated root README, release notes, toolkit version and shared runtime version to `1.2.0`.

### Notes
- User-approved integration into the stable repository.
- No original website JS/CSS/content bundles are committed.
- Visual fidelity, animations, and offline functionality need independent browser testing.

## [1.1.0] - 2026-11-23

### Added
- Robotics Lab as website #7 with a dedicated launcher at `http://127.0.0.1:8127/#uno`.
- Standard `Launcher.bat`, `Update_Clone.bat`, `Check_Clone.bat`, Python entrypoints and source configuration.
- Added Robotics Lab to the global Launch/Update/Check scripts.
- Added a board/WebGL/Workbench/Quiz/Assembly validation checklist and local fixture tests.

### Changed
- Updated bilingual README, project layout, release notes and version metadata.
- Bumped shared runtime version to `1.1.0` without changing mirror functionality.

### Notes
- Approved by the user for repository integration.
- Original website JavaScript, CSS, 3D models and other third-party assets remain excluded from Git.
- Automated tests cover infrastructure only; actual visual parity still requires browser testing.

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

## [Unreleased]
- No changes yet.
