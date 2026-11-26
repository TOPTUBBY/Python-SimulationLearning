# How It’s Wired — Local Clone (8131)

Original: https://how-its-wired.vercel.app/lead-load  
Local: http://127.0.0.1:8131/lead-load  
Release: v1.7.0 (approved integration)

## Quick start (Windows)

1. Keep this folder under `Launcher-Server/`, alongside `tools/` and `localization/`.
2. Install Python 3.8+ (only for **Launcher** mode; Portable EXE does not need Python).
3. Double-click `HowItsWired/Launcher.bat` while online. The first launch downloads public frontend assets from the source website into `site/`.
4. The browser opens at `http://127.0.0.1:8131/lead-load` and the program uses the cached assets on later runs.
5. Close CMD to stop. Use `Update_Clone.bat` to update, `Check_Clone.bat` to validate entrypoint assets.

## Thai / English

The independent `TH · ไทย / Original` overlay uses a shared dictionary and a site-specific dictionary with 37 lesson titles, chapter names, electrical terms and selected lesson descriptions. Default: Thai. Original language is one click away. Optional online translation is OFF by default (when enabled, displayed text may be sent to Google Translate). Canvas/WebGL pixels, code and unrecognized text may not translate. No upstream frontend logic is modified.

## Verification scope

- Test every 3D lesson and all controls, especially drag/WASD, Q/E, scroll zoom, circuit toggles and calculations.
- Verify correct lesson navigation and `/lead-load` on refresh.
- Toggle TH / Original; check the 37 lesson titles and content as you navigate.
- Test after closing CMD and relaunching, and test offline after a successful download.
- Compare the original site in another browser tab; **100% functional and visual parity is not guaranteed**.
- Any live electrical wiring in real life must comply with local safety regulations and be performed by appropriately qualified personnel.

The local mirror/translation tooling is separately authored; original website assets remain in user-local cache and are not distributed with the source ZIP.
