# ESP32 — Local Clone (Port 8121)

- Original site: https://learn-esp32.vercel.app/
- Local: http://127.0.0.1:8121/#board

Requires Python 3.8+ and the shared `../tools/` directory. Run `Launcher.bat`, `Update_Clone.bat`, `Check_Clone.bat`. First mirror download requires Internet.

---

## Thai UI — v1.4.0

- Website: **ESP32** (ESP32 board lessons / 3D / simulator)
- Local address: **http://127.0.0.1:8121/#board**
- Language panel: `TH · ไทย` / `Original` at the bottom-right (collapsible).
- **Original is the default** to avoid unexpected changes. Click `TH · ไทย` to enable Thai, and `Original` to restore the source language.
- Each site's language and online-translation setting is remembered in browser localStorage.
- Offline: curated Thai UI dictionary (shared + site-specific) and previously cached translations.
- Optional online: click **แปลข้อความใหม่ผ่านออนไลน์** to translate unseen, dynamically loaded sentences. **Displayed text** may be transmitted to Google Translate, then cached in the current project folder in `translation_cache.json`.
- Code examples, editable fields, numeric readouts and canvas/WebGL pixels are intentionally excluded; not all dynamic text can be translated offline or guaranteed exact.

### How to test / วิธีทดสอบ

1. Download/extract the entire Repository ZIP from GitHub. Do not move `ESP32/` away from the shared `tools/` and `localization/` folders.
2. Open `ESP32/Launcher.bat` while online for the first download; the browser opens automatically at port 8121.
3. Click `TH · ไทย`. Verify menus, lesson headings, buttons, descriptions and new panels as you navigate the website.
4. Enable online translation if a long explanation remains in English. Check whether it changes to Thai and remains translated after reloading.
5. Select `Original`: all displayed text should return to the original site language; compare interactions with the source website.
6. Close CMD; reopen Launcher. Check no blank screen and selected language persists.
7. Run `Check_Clone.bat` to verify cached website entrypoint and localization resource files.

**Status:** Included in the approved v1.4.0 release. Source website bundles are not packaged and still download into ignored `site/` on the user's device.
