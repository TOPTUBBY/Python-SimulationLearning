# ESP32 Labs Port 8130 - rc.3 Test Results

**Version:** v1.5.0 (approved rc.3 baseline)

**26/26 fixture-based Python tests passed.** New checks verify:
- Reusing previously verified staging with no copies or rename
- First launch downloads assets and serves them from staging
- Simulated `PermissionError` on file copy/directory rename does not prevent startup
- Explicit update alternates cache slots, preserves the previous working copy, and selects via JSON marker
- Failed downloads or pointer activation leave the previous verified cache usable
- Check command accepts a staging-only cache
- The local server serves HTML, JS, CSS and health checks from staging
- 583 staged files (the count in the screenshot) do not trigger bulk copies or redownload
- Restart with the network unavailable still reuses the verified staging cache

These tests use local simulated web assets and Python mocks on Linux.
**Not tested:** actual Windows file locks, original source website parity, completeness of
3D models, all 32 Labs, Thai translations, and 298 source download warnings.

To run: `py -3 -m unittest discover -s tests -v` (from package root).
