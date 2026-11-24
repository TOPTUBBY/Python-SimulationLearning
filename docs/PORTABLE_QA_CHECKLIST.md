# Portable EXE: Windows QA checklist (10 websites)

The following checks MUST be executed by a person on Windows after building each `.exe`; Linux fixtures do not prove real-browser parity.

- [ ] Windows 10/11 x64, Microsoft Edge or Chrome, no Python installed on recipient PC.
- [ ] Double-click EXE: no CMD, visible small progress UI and control window.
- [ ] On first run, original assets download (internet required). Browser opens automatically at assigned port.
- [ ] Port is localhost only; health `http://127.0.0.1:<port>/__clone_health__` identifies the correct app.
- [ ] Close browser tab; reopen from controller. Close controller; port is released.
- [ ] Launch twice: second launch reopens existing app, without spawning another competing server.
- [ ] Disconnect internet and relaunch: cached pages work as supported. Missing external dependencies are recorded.
- [ ] TH / Original switch works; saved language selection and translation cache persist after closing EXE.
- [ ] Reboot Windows and relaunch without Python or admin rights.
- [ ] Build report contains EXE SHA-256 and lists any mirror warnings.

## Site-specific checks

| Site | Port | Verify |
|---|---:|---|
| ESP32 | 8121 | 3D board, pins, lessons, dynamic content, Thai switching |
| Arduino | 8122 | Uno board, lessons, wiring actions, Thai labels |
| RoverKit | 8123 | Drive, navigation, controls, input feedback |
| Multimeter | 8124 | Instrument display, range selection, measurement controls |
| Protocol Explorer | 8125 | Protocol menus, diagrams, stateful exercises |
| DesignedToScale | 8126 | 40 lessons, step navigation, diagrams, search, theme |
| RoboticsLab | 8127 | 8 3D boards, WebGL, Workbench, Quiz/Assembly |
| ByteSizedAlgorithms | 8128 | 86 lessons, animated Big-O, Challenges, cheatsheets |
| MoonLife | 8129 | New game, save/continue, time speed, event choices, Thai UI |
| ESP32Labs | 8130 | `/esp-labs/` path, 3D, 32 labs, pinout, code reader, Thai UI; no copy stall |

**Status:** Development branch. No Windows end-to-end results are claimed until executed and recorded here.
