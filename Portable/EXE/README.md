# Portable EXE — 11 programs

This directory is the destination for the Windows x64 bootstrap executables. They are **distributed in GitHub Releases** rather than committed to Git history. Run `Download_All_EXEs.bat` to download and extract `SimulationLearning_Portable_11_EXEs.zip` from the [v1.7.0 Release](https://github.com/TOPTUBBY/Python-SimulationLearning/releases/tag/v1.7.0).

**วิธีใช้:** ดับเบิลคลิก `Download_All_EXEs.bat` เพื่อดาวน์โหลด EXE ทั้ง 11 ตัว แล้วดับเบิลคลิกโปรแกรมที่ต้องการ ไม่มีข้อกำหนดให้ติดตั้ง Python หรือ Go บนเครื่องผู้ใช้ ตัวโปรแกรมดาวน์โหลดไฟล์เว็บไซต์ต้นฉบับเมื่อเปิดใช้งานครั้งแรก (ต้องมีอินเทอร์เน็ต)

The first 10 apps are bundled through PyInstaller; **SimulationLearning-HowItsWired-8131.exe** uses native Go. Both architectures use only the local loopback HTTP server and a persistent user cache. A successful CI smoke test is not a guarantee of full website parity.
