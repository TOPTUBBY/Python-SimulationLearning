# Changelog

## [1.5.0] - 2026-11-24 (approved rc.3)

### Fixed
- Bypass the per-file install operation that hung at `Copying 583 downloaded files` on Windows.
- Serve previously verified `site.__staging__` directly on first and subsequent launches.
- Select the most complete verified cache when rc.2 left a partially copied `site/` directory.
- Check the active cache instead of assuming only `site/` can be valid.
- Explicit updates download to an inactive verified cache slot and switch using a small local JSON pointer, not folder renames.
- Preserve the last verified cache when update download or cache activation fails.

### Testing
- 26/26 Python fixture tests passed, including a 583-file staged cache with copy/rename blocked.
- This is **not** verification against actual user's Windows filesystem or the live original website.
- Approved for stable repository integration.

## v1.5.0-rc.2 (2026-11-24) — Windows cache install hotfix
- Fix `PermissionError [WinError 5]` during first-run `site.__staging__` to `site` directory rename.
- Copy validated staging assets into the first-run cache instead of renaming the directory.
- Retry transient file locks, preserve complete staged downloads, and resume without redownloading.
- For persistent cache-copy locks, start the local server using the verified staging folder temporarily.
- Do not corrupt existing verified caches when update rename is locked.
- Add regression tests for failure, recovery and retry. No change to source site or GitHub.

## [1.5.0-rc.1] — 2026-11-24

### Added
- Standalone Windows Local Clone for ESP32 Labs / ESP32-S3 Bench Guide, port `8130`.
- Dedicated `/esp-labs/` subpath-aware mirror to prevent missing CSS/JS on first launch.
- `Launcher.bat`, `Update_Clone.bat`, `Check_Clone.bat`, `server.py`, `mirror.py`, `verify_clone.py`.
- Thai UI overlay and offline dictionaries for main navigation, ESP32-S3 terms, parts and common lesson controls.
- Optional dynamic translation with explicit opt-in; UI language selection persists locally.
- Staged mirror updates with rollback and verification of the real `/esp-labs/index.html` entrypoint.
- Local fixture tests and a manual acceptance checklist.

### Limitations
- Original site JS/CSS/assets are not bundled. First use requires Internet.
- Real-site visual parity, exact behavior across 32 labs and 100% Thai translation are not yet verified.
- Preview only, pending user approval **before** any GitHub update.
