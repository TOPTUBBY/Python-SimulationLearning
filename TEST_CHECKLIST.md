# How It’s Wired — QA checklist (8131)

Compare against https://how-its-wired.vercel.app/lead-load using the same Windows PC and browser.

## Launcher-Server (Python)
- [ ] Open `Launcher-Server/HowItsWired/Launcher.bat`; first-run download creates a verified cache slot.
- [ ] Browser opens on `/lead-load`, without a blank/black screen.
- [ ] `Check_Clone.bat` reports PASS.
- [ ] Close CMD, restart Launcher, verify it reuses cache without downloading again.
- [ ] `Update_Clone.bat` preserves the old cache on a failed update.

## Portable (single EXE; no Python)
- [ ] Double-click `Portable/EXE/SimulationLearning-HowItsWired-8131.exe` without installing Python.
- [ ] Browser opens automatically; first-run progress screen shows while the original assets download.
- [ ] Page loads and works when preparation finishes; switching TH/Original works.
- [ ] Closing the control message (OK) stops the local server.
- [ ] Restart EXE: cached website works without re-downloading the main bundle.
- [ ] Logs/cache are at `%LOCALAPPDATA%\SimulationLearning\HowItsWired`.

## Course functionality
- [ ] Review all 37 lesson entries in the seven chapters.
- [ ] Confirm `/lead-load` circuit and load calculation match the original.
- [ ] Test drag/WASD pan, Q/E rotation and wheel zoom in 3D.
- [ ] Test navigation, overview, components, circuit, maths and settings screens.
- [ ] Verify any switching/trip/overload animations against the original.
- [ ] Switch language TH ↔ Original; confirm titles, buttons, chapter names and explanations.
- [ ] With online translation OFF, curated Thai content still works offline.
- [ ] If enabled, online translation of unknown dynamic text works and user has consented to sending that text externally.
- [ ] Reload the page while navigating to different history routes; no blank screen.
- [ ] After successful online launch, test offline functionality and note anything needing online services.

**Scope**: Python regression tests and Go cross-compiled binary do not verify the 3D simulator on a real Windows PC. There are no copied third-party site bundles in this archive.

**Safety**: These electrical simulations are educational. Do not treat them as instructions for working on live mains equipment.
