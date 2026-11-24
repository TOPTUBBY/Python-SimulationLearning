# ESP32 Labs — Local Clone + Thai UI (Port 8130)

**Source website:** [ESP32-S3 Bench Guide by ionloft](https://ionloft.com/esp-labs/#/?lang=en)  
**Source repository:** [agharsallah/esp-labs-web](https://github.com/agharsallah/esp-labs-web) (MIT-licensed)  
**Local URL:** `http://127.0.0.1:8130/esp-labs/#/?lang=en`  
**Toolkit version:** `v1.5.0` — approved release (based on tested rc.3).

## วิธีใช้งาน

1. ต้องมี Windows 10/11 และ Python **3.8 ขึ้นไป** (คำสั่ง `py -3` หรือ `python`) ไม่ต้องใช้ Node.js หรือ `pip install` สำหรับระบบ Mirror นี้
2. แตก ZIP **ทั้งชุด** แล้วรักษาโฟลเดอร์ `ESP32Labs/`, `tools/`, `localization/` ให้อยู่ระดับเดียวกัน
3. ดับเบิลคลิก **`ESP32Labs/Launcher.bat`** พร้อมอินเทอร์เน็ตในการเปิดครั้งแรก ระบบจะดาวน์โหลด Frontend ลงใน `ESP32Labs/site.__staging__/esp-labs/` แล้วเปิดจากโฟลเดอร์นี้ได้โดยตรง **ไม่ต้อง Copy/Rename โฟลเดอร์ใหญ่**
4. เมื่อดาวน์โหลดและตรวจไฟล์สำคัญสำเร็จ Browser จะเปิดอัตโนมัติที่พอร์ต **8130** หากไม่มีแคชและดาวน์โหลดไม่สำเร็จ Launcher จะไม่เปิดเว็บดำ
5. ใช้ปุ่มลอย **TH · ไทย / Original** มุมล่างขวา ตัวเลือกภาษาไทยเปิดเป็นค่าเริ่มต้น; ปุ่ม **Original** กลับไปใช้ภาษาเดิมของเว็บไซต์
6. หากข้อความในบทเรียนยังเป็นอังกฤษ ให้เลือก **แปลข้อความใหม่ผ่านออนไลน์** (ต้องมีอินเทอร์เน็ต) ข้อความที่แสดงจะถูกส่งไปยังบริการ Google Translate ผ่าน Local Server โดยการแปลออนไลน์ **ปิดไว้เป็นค่าเริ่มต้น**
7. ปิด CMD หรือ Ctrl+C เพื่อหยุดเซิร์ฟเวอร์ เปิด Launcher อีกครั้งจะใช้ไฟล์แคชเดิมโดยไม่ต้องดาวน์โหลดซ้ำ

## Files / โครงสร้าง

| File | Function |
|---|---|
| `Launcher.bat` | ตรวจสอบ Python, เริ่มเซิร์ฟเวอร์ และเปิดเบราว์เซอร์ |
| `Update_Clone.bat` | ดาวน์โหลดไฟล์ใหม่จาก `https://ionloft.com/esp-labs/` แบบ staging + rollback |
| `Check_Clone.bat` | ตรวจสอบหน้า HTML, JS, CSS และไฟล์แปลไทย |
| `server.py` | HTTP Local Server ที่ 127.0.0.1:8130 |
| `mirror.py` | ดาวน์โหลด Assets ลงเครื่องและรักษาโครงสร้าง `/esp-labs/` |
| `verify_clone.py` | ตรวจสอบความครบถ้วนของไฟล์สำคัญ |
| `config.json` | Source URL, Subpath, Port, Hash Route, ค่าภาษา |
| `../tools/esp_labs_runtime.py` | Runtime สำหรับเว็บไซต์ที่เผยแพร่ใน Subpath |
| `../tools/clone_runtime.py` | Runtime Mirror/Server พื้นฐานเหมือนโครงการอื่น |
| `../tools/thai_runtime.py` | ตัวเสริมภาษาไทยบนเซิร์ฟเวอร์ |
| `../localization/sites/esp32-labs.json` | คำแปลเฉพาะ ESP32 Labs |
| `../localization/common_th.json` | คำแปลกลางที่ใช้กับทุกเว็บ |
| `site.__staging__/`, `site.__next__/` | แคชสองชุดสำหรับสลับอัปเดต; ไม่อยู่ใน ZIP และไม่ Commit ขึ้น Git |
| `site.__active__.json` | ตัวบอกแคชที่กำลังใช้งาน (สร้างอัตโนมัติ ไม่ Commit) |
| `site/` | แคชรูปแบบเดิม (ถ้ามี); ระบบยังอ่านได้ |

## ขอบเขตการแปล

รองรับ **ป้ายชื่อเมนู ข้อความบทเรียนที่อยู่บน DOM, ปุ่ม, คำอธิบาย, Tooltip, Placeholder และบทเรียนที่โหลดใหม่** ผ่าน MutationObserver พร้อมพจนานุกรมคำแปลไทยที่ทำไว้ล่วงหน้า โดยไม่ดัดแปลงไฟล์ JavaScript ของเว็บต้นฉบับและไม่แก้ค่าโค้ด Firmware ใน `<pre>`/`<code>`

ข้อความทั้งหมดใน 32 Labs ที่ไม่มีในพจนานุกรม **ต้องเปิดแปลออนไลน์เพื่อแสดงภาษาไทย** และอาจแปลคลาดเคลื่อน โดยเฉพาะศัพท์เทคนิค ข้อความภายใน Canvas/WebGL/SVG แบบกราฟิก, ผล Serial จริง และซอร์สโค้ดอาจไม่ถูกแปล ยังไม่ใช่คำยืนยันว่าแปลครบ 100% แล้ว

**English:** This is a local frontend mirror with an independently authored Thai DOM localization layer. First run downloads publicly served application files from the original host. Original browser storage, workbench progress and theme persist per browser origin (`127.0.0.1:8130`); data from the original website's domain is *not* automatically imported. External APIs and fonts may require internet even after caching.

## คู่มือแก้ปัญหา

- **หน้าดำ/ไม่พบ JS:** รัน `Check_Clone.bat` ก่อน จากนั้น `Update_Clone.bat` ขณะออนไลน์ แล้ว Ctrl+Shift+R
- **Port 8130 ถูกใช้งาน:** `netstat -ano | findstr :8130` และตรวจสอบ Process ที่ใช้งาน อย่าปิด Process อื่นโดยไม่ทราบที่มา
- **โมเดล 3D ไม่ขึ้น:** เปิด Hardware Acceleration ใน Browser และตรวจสอบ WebGL โดยเทียบกับเว็บไซต์ต้นฉบับบนเครื่องเดียวกัน
- **ไทยบางข้อความยังไม่ขึ้น:** เปิดตัวเลือกแปลออนไลน์, ทดสอบอินเทอร์เน็ต, ตรวจสอบพจนานุกรม `localization/sites/esp32-labs.json`
- **Cache ชำรุด:** เปิด `Update_Clone.bat` ใหม่ ระบบจะโหลดใส่โฟลเดอร์ Staging ก่อนสลับแคช เพื่อเก็บสำเนาก่อนหน้าเมื่ออัปเดตล้มเหลว

### Hotfix v1.5.0-rc.3 — Fix stuck at "Copying 583 downloaded files"

The previous fix copied the verified files one by one from `site.__staging__`
into `site/`. On some Windows systems this step can appear to freeze without
printing progress. **v1.5.0 (approved rc.3) does not copy or rename website cache directories
at all during normal launching.** It serves the verified staging cache directly.

1. Close the CMD window showing `Copying 583 downloaded files` (Ctrl+C or close).
2. Keep `ESP32Labs/site.__staging__/` and `ESP32Labs/site/` exactly as they are.
3. Extract the **rc.3 Hotfix Patch** into the inner folder containing both
   `ESP32Labs/` and `tools/`, allowing `tools/esp_labs_runtime.py` and
   `tools/clone_runtime.py` to be replaced.
4. Double-click `ESP32Labs/Launcher.bat` again. Expected output:
   `[Cache] Reusing verified assets: site.__staging__ (583 files)` and
   `[Cache] No copy or rename required.` Browser opens on port 8130.
5. `Check_Clone.bat` also validates the active staging cache. If the download
   is incomplete, the launcher must download a verified cache again.

Explicit `Update_Clone.bat` now downloads to the **inactive** cache slot and
activates it with a tiny `site.__active__.json` file. The old cache stays intact
if download or activation fails. Do not delete `site.__staging__` or `site.__next__`
while the server is running. Windows Defender / Explorer do not need to be
turned off. Check the browser's Network/Console tabs if 3D assets or lessons
are missing; the earlier **298 download warnings** may still be relevant.


## Validation

Run from repository root:

```bat
py -3 -m unittest discover -s tests -v
```

Fixture tests validate the **mirror/server/Thai toolbar plumbing only**. Verify the original 3D board, 32 labs, code reader, pinout, reference figures, progress, simulation interactions and Thai text visually on your Windows PC using [TEST_CHECKLIST.md](TEST_CHECKLIST.md).

## Licensing / เครดิต

The upstream project belongs to its authors, publicly released under MIT; review its [LICENSE](https://github.com/agharsallah/esp-labs-web/blob/main/LICENSE). This package distributes local tooling and translation dictionaries, *not* the original compiled site assets or a claim of ownership of the site. Cite the upstream developers when sharing, and respect their license and server usage.
