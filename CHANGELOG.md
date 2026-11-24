# Changelog

## [Unreleased] — feature/portable-exe-all-sites (2026-11-24)

### Added (development only)
- Windows Portable EXE launcher with GUI controller, loopback local HTTP server, automatic browser opening, and persistent per-user AppData.
- Two packaging modes for all 10 sites: Bootstrap EXE (download public website assets on first run) and optional Embedded EXE (bundles a validated local site cache).
- Single-file PyInstaller builder, Windows BAT commands, portable regression tests, Windows Actions build matrix, QA checklist, and release documentation.
- Verified cache-slot reuse on first run without bulk rename/copy, maintaining Thai UI, Moon Life, and ESP32 Labs subfolder handling.

### Notes
- Branch only. Existing stable main remains v1.5.0.
- Bootstrap EXEs do not redistribute third-party assets. Embedded EXEs require separate permission checks before redistribution.
- Windows binary build and real-browser compatibility must be confirmed before stable merge.


This changelog tracks **SimulationLearning's local launcher/mirror toolkit**, not changes to the original third-party websites. Versions follow [Semantic Versioning](https://semver.org/).

## [1.5.0] - 2026-11-24

### Added
- ESP32 Labs (ESP32-S3 Bench Guide) as website #10 on port 8130 at `/esp-labs/#/?lang=en`.
- Source-subpath-aware mirror, local launcher, update/check commands, Thai dictionary, and 26 fixture tests.
- Integrated ESP32Labs into Launch/Update/Check All and updated release documentation.

### Fixed
- Approved Windows hotfix rc.3: first launch serves a validated staging cache directly without copying/renaming the 583 downloaded files.
- New cache slot selection with `site.__active__.json` and update rollback preserving the previous verified cache.
- Git exclusions for the new cache slots and marker files.

### Verification
- User approved rc.3 for stable integration; 26/26 ESP32 Labs local fixture tests passed.
- Actual browser parity, 3D assets, all 32 labs, offline behavior and complete Thai translations require verification on the target PC.
- Original website JavaScript/CSS and media bundles are not committed.

## [1.4.0] - 2026-11-24

### Added
- Thai / Original language switcher for eight learning sites: ESP32 (8121), Arduino (8122), RoverKit (8123), Multimeter (8124), Protocol Explorer (8125), Designed to Scale (8126), Robotics Lab (8127), and Byte-Sized Algorithms (8128).
- Shared localization runtime, 265 common Thai UI translations plus site-specific dictionaries, dynamic DOM label updates, and reversible language selection.
- Per-site persistent language preferences, optional online translation of previously unknown text, and locally cached translations.
- `Check_Thai_UI.bat`, site documentation, and localization regression tests.

### Changed
- Updated README, release documentation, and toolkit/runtime versions to `1.4.0`.
- Preserved Moon Life (8129) Thai support, all original ports, and shared local-mirroring behavior.

### Notes
- Online translation is disabled by default; activating it may send visible text to Google Translate.
- Original third-party website bundles remain excluded from the repository.
- Local regression suite passed 40/40 tests; full-browser visual parity and every translation require user validation.

## [1.3.0] - 2026-11-24

### Added
- **Project Moon Life / Born as an Individual in the City** as website #9 on port `8129` with local Launcher, Update, Check and Cache management.
- Display-only Thai language overlay with **249** built-in translations, TH / Original switching, and optional dynamic story translation through a local endpoint with persistent local cache.
- `tools/moon_runtime.py` for localized HTML injection and local translation service; `tests/test_moonlife.py` and project test results.
- Moon Life integration in `Launch_All.bat`, `Update_All.bat` and `Check_All.bat`.

### Changed
- Updated README, version metadata, shared runtime version and release notes to `1.3.0`.
- Added translation cache to `.gitignore`; original game assets and story scripts remain excluded from the repository.

### Verification
- User approved the preview for stable integration.
- 12/12 local fixture tests passed for launcher, mirroring, HTML overlay, translation API, cache, server restart and rollback.
- Visual parity, complete Thai translations and real online game/translation behavior require browser verification on the target machine.

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
