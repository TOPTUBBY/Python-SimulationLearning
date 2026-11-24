# Byte-Sized Algorithms / Algo Lab — Local Clone (Port 8128)

**Original:** https://byte-sized-algorithms.vercel.app/#/big-o/1  
**Local:** http://127.0.0.1:8128/#/big-o/1  
**Toolkit release:** `v1.2.0` — approved for integration into the main repository.

## How it works / วิธีการทำงาน

This is a **local mirror launcher**, not a rewritten UI. On its first run, Python 3.8+ downloads publicly available HTML, JavaScript, CSS, fonts and discoverable static assets from the source into a local `site/` cache. The launcher then starts a local server on port **8128** and automatically opens the browser. Reopening the launcher reuses the existing cache.

เป็นระบบสำเนาไฟล์เว็บต้นฉบับลงเครื่อง ไม่ใช่การสร้าง UI เลียนแบบ เปิดครั้งแรกต้องเชื่อมต่ออินเทอร์เน็ตเพื่อดาวน์โหลดไฟล์ และเปิดหน้าเว็บอัตโนมัติที่พอร์ต **8128** เมื่อเปิดครั้งถัดไปจะใช้ Cache ที่บันทึกไว้

### Requirements / สิ่งที่ต้องมี

- Windows 10/11, Chrome or Microsoft Edge (JavaScript enabled)
- Python 3.8+ accessible as `py -3` or `python`, without additional pip packages
- Internet on first launch and for updates or any missing online assets

### Quick Start / เริ่มใช้งาน

1. Download/clone the **entire repository**, keeping the `tools/` directory alongside `ByteSizedAlgorithms/`.
2. Double-click **`ByteSizedAlgorithms/Launcher.bat`**.
3. On the first launch, connect to the internet and let the mirror finish downloading.
4. Open `http://127.0.0.1:8128/#/big-o/1` (browser opens automatically when ready).
5. Keep the command prompt open during use; close it or press Ctrl+C to stop. Reopen Launcher to use the cached site.

### Files

| File | Purpose |
|---|---|
| `Launcher.bat` | Start the local server and browser |
| `Update_Clone.bat` | Refresh from the original site, retaining old cache if validation fails |
| `Check_Clone.bat` | Check local index and critical JavaScript/CSS files |
| `server.py` | Local HTTP server entrypoint |
| `mirror.py` | Asset mirror updater entrypoint |
| `verify_clone.py` | Cache integrity check |
| `config.json` | Source, port and default hash route |
| `../tools/clone_runtime.py` | Shared Python standard-library engine |
| `site/` | Downloaded source-site assets (gitignored, not distributed) |

From the repository root:

```bat
py -3 ByteSizedAlgorithms\server.py
py -3 ByteSizedAlgorithms\verify_clone.py
py -3 ByteSizedAlgorithms\mirror.py
py -3 -m unittest discover -s tests -v
```

## Functional verification checklist / รายการตรวจสอบ

Compare the local and original websites side-by-side on the same browser:

- [ ] Big-O Notation opens directly on **Step 1** via `/#/big-o/1`, without a blank screen.
- [ ] Learn, Practice, Cheatsheets, Challenges and Progress navigation works.
- [ ] The sidebar lists **86 lessons** in **14 chapters**.
- [ ] Big-O animated blocks, step counts and pseudocode update with each step.
- [ ] Next/Back, all 7 Big-O steps and keyboard left/right arrows work.
- [ ] Lessons in Arrays, Linked Lists, Graphs, Sorting and Dynamic Programming load.
- [ ] Search (`Ctrl+K`) finds and opens lessons.
- [ ] Practice and Challenges display and respond correctly.
- [ ] Cheatsheets render correctly.
- [ ] Progress updates and persists after refresh.
- [ ] Language and Dark/Light theme options work.
- [ ] Refresh and hard-refresh display the page correctly.
- [ ] Closing CMD and reopening Launcher reuses the cached assets.
- [ ] Test offline after a successful mirror and note features still requiring live services.

**Limitations:** A local asset downloader alone cannot guarantee 100% visual or functional equality. Some dynamically requested assets and external APIs may still require internet access. `Check_Clone.bat` and automated tests validate the entrypoint and local infrastructure, **not every lesson or animation**. Keep the original website as the reference for comparison.

## Troubleshooting / วิธีแก้ปัญหา

**Black screen:** Run `Check_Clone.bat`; if assets are missing, reconnect online and run `Update_Clone.bat`. Restart Launcher and use Ctrl+Shift+R. Inspect DevTools Console/Network for failed JavaScript requests.

**Browser does not open:** Open `http://127.0.0.1:8128/#/big-o/1` manually and check CMD output. Verify Python via `py -3 --version`.

**Port conflict:** Run `netstat -ano | findstr :8128`. An existing matching local clone server can be reused; another app using the port will not be terminated.

**Failed update:** Check network, proxy, antivirus or website availability. Failed staged updates preserve the previously working cache.

**Offline:** Some same-origin assets are fetched lazily while internet is available; third-party services and undiscovered routes may fail offline.

## Attribution / Ownership

The original website, animations, lessons and visual assets are owned by their respective rights holders. This repository distributes **only independently authored local launcher, mirror, server, verification and test tooling**, not the third-party website bundles or the 86 original lessons. The repository MIT license applies only to our own tooling.

Repository: https://github.com/TOPTUBBY/Python-SimulationLearning  
Status: **Approved and committed as part of v1.2.0**.
