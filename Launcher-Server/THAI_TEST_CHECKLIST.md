# Thai UI · Validation checklist (v1.4.0)

The release includes locally authored localization tooling only. The original site files download on first run and are never included in this ZIP.

## Setup

1. Install Python 3.8+; download and extract the **latest GitHub repository ZIP**.
2. Keep sibling folders `tools/`, `localization/` and each website folder intact.
3. Double-click the required `Launcher.bat`; on first run, keep Internet connected.
4. If an older 8121–8128 server is running, close its CMD first. Do not run two copies on the same port.
5. The original site language is default. Use **TH · ไทย**, **Original**, and the optional online-translation checkbox at the lower-right.

| Port | Site | Local URL | Test in Thai |
|---:|---|---|---|
| 8121 | ESP32 | http://127.0.0.1:8121/#board | Lesson 1; board controls, pin explanations, serial monitor, switch a simulation |
| 8122 | Arduino | http://127.0.0.1:8122/#board | Lesson 1; Overview/Pinout/Example/Specifications; simulator controls |
| 8123 | RoverKit | http://127.0.0.1:8123/#drive | Drive controls, direction, speed, model/animations |
| 8124 | Multimeter | http://127.0.0.1:8124/multimeter | Measurement functions, dial, probe explanations, change lesson |
| 8125 | Protocol Explorer | http://127.0.0.1:8125/ | Protocol names, step controls, packet flow, diagrams |
| 8126 | Designed to Scale | http://127.0.0.1:8126/#/ | 40 lesson menu, HLD & LLD, diagram steps, language/theme |
| 8127 | Robotics Lab | http://127.0.0.1:8127/#uno | Board labels, switch eight boards, lesson, quiz, assembly, workbench |
| 8128 | Byte-Sized Algorithms | http://127.0.0.1:8128/#/big-o/1 | 86 lesson menu, Big-O steps, Practice, Challenges, Cheatsheets |

## Verify all eight sites

- [ ] Website opens with no black/blank page; original graphics, canvas, 3D remain intact.
- [ ] TH · ไทย translates known menus, buttons and headings.
- [ ] Switch to Original: original language returns without a reload.
- [ ] Change lesson, open dialogs, execute a simulation: new DOM text is translated.
- [ ] Code blocks, copy code buttons, input values and numeric displays are not altered.
- [ ] Enable online translation for untranslated paragraphs **only if you accept sending displayed text to Google Translate**; confirm text changes, then switch it off.
- [ ] Close CMD, reopen Launcher; TH/Original choice persists and server loads from cache.
- [ ] Run Check_Clone.bat: both website cache and Thai resources pass.
- [ ] Optional offline test after visiting pages while online; uncached text may remain original.

## Limits to report

- Text drawn directly in Canvas/WebGL, SVG paths, and embedded third-party frames cannot be translated with DOM text replacement.
- Online service may be unavailable, rate limited, or imprecise; translations do not prove exact 100% coverage.
- Some source sites render large text blocks as one node, requiring optional online translation.
- HTML, CSS and compiled JavaScript from the source website are **not** shipped or published with this repository.

When reporting untranslated text, include the website, page, original text, and a screenshot if available. New translations can be added in a patch release.
