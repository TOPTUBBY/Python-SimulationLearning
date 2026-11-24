# ESP32 Labs — acceptance checklist (Port 8130)

Compare local `http://127.0.0.1:8130/esp-labs/#/?lang=en` against https://ionloft.com/esp-labs/#/?lang=en on the **same computer/browser**.

- [ ] Initial download completes without error; `Check_Clone.bat` reports PASS.
- [ ] Home view loads, not a black/blank screen; similar layout and theme.
- [ ] Menu: Labs / Datasheet / Settings; navigation works.
- [ ] Board 3D rotates/zooms; pinout and part details are interactive.
- [ ] All 32 lab entries show correct status; open available lessons across Intro, Display, Wi-Fi, RFID, BLE and Sound.
- [ ] Each lab: wiring, commands, steps, preview and step completion checkboxes work.
- [ ] Simulators, serial monitor, code reader, guided tour and datasheet figures work wherever upstream supports them.
- [ ] Selecting `TH · ไทย` translates known headings/menu labels; clicking buttons still works.
- [ ] Toggle translation online and inspect at least 3 lessons with long paragraphs, then switch it off.
- [ ] Select `Original`: known labels revert; then switch to TH again.
- [ ] Check both light/dark mode and mobile screen sizing; floating toolbar must not block main controls.
- [ ] Refresh page; settings/progress remain saved on localhost.
- [ ] Close CMD and double-click Launcher again; cached website opens without re-download.
- [ ] Disconnect internet after successful cache; test entry navigation and identify missing remote API/images.
- [ ] Run Update_Clone.bat while online, Check_Clone.bat after update; compare version and page behavior.

**Limitations:** full English-to-Thai translation requires optional online translation where curated phrases are missing; code, pin names, Canvas/WebGL graphics and hardware readings remain unchanged. The acceptance criteria are **not** satisfied automatically by local infrastructure tests.
