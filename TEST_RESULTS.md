# How It's Wired — Preview Verification (before approval) (before approval) Results

Preview label: `v1.7.0` (approved integration). The table records the pre-release local test results.

| Test area | Result | Scope |
|---|---|---|
| Python Launcher-Server regression | PASS 73/73 | Includes seven new offline HowItsWired fixture tests, original clone tests and localization tests |
| Existing Portable EXE regression | PASS 11/11 | Ten previously approved PyInstaller apps remain untouched |
| Native Go Portable tests | PASS 4/4 | Mirror fixtures, Thai dictionary delivery, `/lead-load`, dynamic asset recovery, blocked traversal, build-time identity report |
| Windows EXE build | PASS (cross-compilation) | Go 1.23.2, GOOS=windows, GOARCH=amd64, Windows GUI x64 PE32+ |
| Updated 11-file release packager | PASS fixture | Validates 11 placeholder PE signatures/ZIP integrity; NOT a real Windows execution test |
| Real Windows execution | NOT YET TESTED | User to test the actual portable EXE |
| Real website 3D/lesson parity | NOT VERIFIED | Internet access to the upstream website from build environment was unavailable |
| Thai coverage | PARTIAL / CURATED | 498 site-specific strings + shared dictionary; full dynamic prose via optional online translation |

Source website: https://how-its-wired.vercel.app/lead-load  
Locally assigned URL: http://127.0.0.1:8131/lead-load

The published website provides 37 lesson entries across 7 categories. All chapter names and lesson titles are included in the local translation dictionary. Content in WebGL/canvas and any unseen page text may not be translated automatically in offline mode.
