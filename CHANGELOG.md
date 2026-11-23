# Changelog

This changelog tracks **SimulationLearning's local launcher/mirror toolkit**, not changes to the original third-party websites. Versions follow [Semantic Versioning](https://semver.org/).

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
