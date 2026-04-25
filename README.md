# DDCM WorkFlow - Browser Automation Tool

เครื่องมือช่วยจัดการ Workflow งานออกแบบ (DDCM) และการลงสินค้าบน Etsy แบบอัตโนมัติ สำหรับ macOS และ Windows

## 📋 คุณสมบัติหลัก
- **13-Step Sequential Workflow:** ลำดับขั้นตอนการทำงานที่ชัดเจนตั้งแต่ต้นจนจบ
- **Gemini Automation:** ดึง Prompt จาก DDCM ไปสร้างรูปใน Gemini อัตโนมัติ
- **File Management:** สร้างโฟลเดอร์, ย้ายไฟล์, แตกไฟล์ Zip, และเปลี่ยนชื่อไฟล์ (Smart Renaming) ให้อัตโนมัติ
- **Canva Automation:** ส่งออกไฟล์ PNG, JPG, PDF ตามช่วงหน้าที่กำหนด
- **Etsy Listing:** กรอกข้อมูลสินค้าลง Etsy Draft ให้โดยอัตโนมัติ

---

## 🛠 การติดตั้ง (Installation)

### 1. ติดตั้ง Python
แนะนำให้ใช้ **Python 3.10 ขึ้นไป** (แนะนำ 3.12 หรือ 3.14 เพื่อความเสถียรบน macOS)
- ตรวจสอบเวอร์ชัน: `python3 --version`

### 2. ติดตั้ง Tkinter (สำคัญมากสำหรับ macOS)
หากคุณติดตั้ง Python ผ่าน Homebrew ปุ่มและตัวหนังสืออาจจะไม่แสดงผล ให้รันคำสั่งนี้ใน Terminal:
```bash
# สำหรับ Python 3.14
brew install python-tk@3.14

# สำหรับ Python 3.12
brew install python-tk@3.12
```

### 3. เตรียมโปรเจกต์
1. Clone หรือก๊อปปี้โฟลเดอร์โปรเจกต์มาที่เครื่อง
2. เปิด Terminal ในโฟลเดอร์โปรเจกต์
3. สร้าง Virtual Environment และติดตั้ง Library:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 การตั้งค่าก่อนเริ่มงาน (Setup)

### 1. เปิด Chrome ในโหมด Debug
โปรแกรมนี้จะควบคุม Chrome ตัวปัจจุบันของคุณ คุณต้องเปิด Chrome ด้วยคำสั่งพิเศษเพื่อให้บอทเชื่อมต่อได้ (Port 9222)

**สำหรับ macOS:** (รันผ่านไฟล์ script ที่เตรียมไว้ให้)
```bash
chmod +x run.sh
./run.sh
```
*ตัวบอทจะพยายามเปิด Chrome ให้เอง หรือถ้าเปิดอยู่แล้วต้องตรวจสอบว่าเปิดด้วย Port 9222 หรือไม่*

---

## 📖 วิธีการใช้งาน

1. **Step 1:** กรอก Folder Name และตรวจสอบ Path ต่างๆ (กด **Set Default** เพื่อบันทึกค่าไว้ใช้ครั้งหน้า)
2. **Step 2:** กด **Create Folders** เพื่อเตรียมพื้นที่เก็บงาน
3. **Step 3:** เปิดหน้า Gemini และหน้า Modal ของ DDCM ทิ้งไว้ จากนั้นกดปุ่ม **Gen** ตามโหมดที่ต้องการ
4. **Step 4-7:** ทำตามลำดับการจัดเก็บรูป, ตัดพื้นหลัง (Photoshop) และขยายขนาด (Upscale)
5. **Step 8-11:** ออกแบบปกใน Canva และใช้ปุ่ม **Export**, **Unzip**, **Download to Local** เพื่อรวบรวมไฟล์งาน
6. **Step 12-13:** สำรองงานขึ้น Drive และกด **Create Listing** เพื่อลงสินค้าใน Etsy

---

## 💡 แก้ไขปัญหาที่พบบ่อย (Troubleshooting)

- **มองไม่เห็นตัวหนังสือ/ปุ่ม:** เกิดจาก Mac ไม่มี `python-tk` ให้ทำตามขั้นตอน "การติดตั้งข้อ 2"
- **บอทหา Chrome ไม่เจอ:** ให้ปิด Chrome ทั้งหมดก่อน แล้วรันผ่าน `./run.sh`
- **Error: Path is not absolute:** ตรวจสอบในช่อง Input ว่ามีเครื่องหมายอัญประกาศ (") เกินมาหรือไม่
- **หาปุ่ม PNG ใน Canva ไม่เจอ:** ตรวจสอบว่าหน้าจอ Canva ไม่ได้ถูกย่อจนปุ่มหายไป หรือโครงสร้างเว็บ Canva เปลี่ยน (แจ้งผู้พัฒนาเพื่ออัปเดต XPath)

---
*จัดทำเพื่อช่วยลดระยะเวลาการทำงานและเพิ่มความถูกต้องของข้อมูล*
