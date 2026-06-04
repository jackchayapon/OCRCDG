# OCR Document Capture

ระบบเว็บสำหรับรับภาพเอกสารจากไฟล์หรือกล้อง จัดกรอบเอกสารก่อนส่ง OCR และแสดงผลแบบ Plaintext กับ JSON โดยใช้ Python backend proxy เพื่อซ่อน token และลดปัญหา CORS

รายละเอียดด้านสถาปัตยกรรมและ Tech Stack อ่านได้ที่ [TECH_STACK.md](TECH_STACK.md)

## ความสามารถหลัก

- Upload ไฟล์ `PDF`, `JPG`, `JPEG`, `PNG`, `TIFF`, `BMP`
- เปิดกล้องและ Capture ภาพเอกสาร
- PDF Page Selection สำหรับเลือกหน้า PDF ก่อน OCR
- Render PDF เป็นภาพ JPG รายหน้า ไม่ส่ง PDF ต้นฉบับเข้า OCR API
- Crop Document Mode สำหรับจัดกรอบเอกสารก่อน OCR
- Auto Detect Document และ Trim White Area
- ลากและ Resize กรอบ Crop ได้
- Preview Document Mode แยกจาก Crop Mode
- Zoom, Pan, Fit to Screen, 100%, Reset View
- OCR API selector รวม 9 รายการ
- Mock Mode สำหรับ Demo โดยไม่เรียก API จริง
- Debug Mode สำหรับตรวจ request metadata โดยไม่แสดง token
- Plaintext View, JSON View, Copy JSON, Download Text และ Download JSON

## Requirements

ต้องมี:

- Python `3.10+`
- Browser รุ่นใหม่ เช่น Chrome หรือ Edge
- Internet สำหรับโหลด PDF.js จาก CDN เมื่อใช้งานไฟล์ PDF
- กล้องและสิทธิ์ Camera Permission หากต้องการ Capture ภาพ
- Network ที่เข้าถึง OCR API ภายนอกได้

Python package ภายนอกทั้งหมดระบุใน [requirements.txt](requirements.txt):

```text
fastapi==0.115.6
uvicorn[standard]==0.32.1
python-multipart==0.0.20
requests==2.32.5
```

Backend ใช้ FastAPI สำหรับ route/API, Uvicorn สำหรับ ASGI server, `python-multipart` สำหรับรับ upload แบบ multipart และ `requests` สำหรับส่งต่อไป OCR API ภายนอก

## Setup

1. เปิด PowerShell ในโฟลเดอร์โปรเจกต์

```powershell
cd C:\Users\66160167\Desktop\OCRCDG
```

2. สร้าง virtual environment:

```powershell
python -m venv .venv
```

3. เปิดใช้งาน virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

หาก PowerShell ไม่อนุญาตให้รัน activation script สามารถข้ามขั้นตอนนี้ และใช้ `python` จากเครื่องโดยตรงได้

4. ติดตั้ง dependency:

```powershell
python -m pip install -r requirements.txt
```

5. สร้างไฟล์ `.env` จาก [.env.example](.env.example) เฉพาะเมื่อยังไม่มีไฟล์นี้ เพื่อไม่ให้ token เดิมถูกเขียนทับ:

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

6. เปิด `.env` และใส่ token สำหรับ API กลุ่ม Other:

```text
OCR_OTHER_AUTH_TOKEN=replace-with-server-token
```

ไฟล์ `.env` ถูก ignore ไว้ใน [.gitignore](.gitignore) ห้าม commit หรือย้าย token ไปไว้ใน `app.js`

## Run

เปิดระบบด้วย Uvicorn:

```powershell
uvicorn server:app --host 127.0.0.1 --port 3000
```

จากนั้นเปิด:

```text
http://127.0.0.1:3000
```

หยุดระบบด้วย `Ctrl+C`

## วิธีใช้งาน

### Upload File

1. กด `Upload File`
2. เลือกเอกสารจากเครื่อง
3. ถ้าเป็น PDF ระบบจะแสดง thumbnail รายหน้า ให้เลือกหน้าที่ต้องการ OCR แล้วกด `OCR Selected Page`
4. ระบบจะ render หน้าที่เลือกเป็น JPG และเข้าสู่ Crop Document Mode
5. สำหรับรูปภาพทั่วไป ระบบจะเข้าสู่ Crop Document Mode และ Auto Detect ขอบเอกสารทันที
6. ตรวจกรอบ Crop และปรับเองได้หากจำเป็น
7. กด `Apply Crop`
8. ตรวจรายละเอียดใน Preview Document Mode
9. เลือก OCR API จาก Sidebar
10. กด `Run OCR`
11. ดูผลใน `Plaintext` หรือ `JSON`

### Open Camera

1. กด `Open Camera`
2. อนุญาต Camera Permission
3. เลือกกรอบเอกสาร เช่น บัตรประชาชนหรือพาสปอร์ต
4. จัดเอกสารให้อยู่ในกรอบและกด `ถ่ายภาพ`
5. ตรวจและปรับ Crop อีกครั้ง
6. กด `Apply Crop`
7. ตรวจ Preview และกด `Run OCR`

### Crop Document Mode

- `Auto Detect Document`: ตรวจจับขอบเอกสารจากภาพ
- `Trim White Area`: ตัดขอบขาวหรือพื้นที่ว่าง พร้อมเหลือ padding เล็กน้อย
- ลากกรอบ: ย้ายตำแหน่ง Crop
- ลากจุดมุม: Resize Crop
- `Reset Crop`: กลับไปกรอบเริ่มต้น
- `Apply Crop`: สร้างภาพ Crop + Resize + Enhance แล้วเข้าสู่ Preview
- `Skip Crop`: ใช้ไฟล์ต้นฉบับ

สำหรับ PDF จะไม่มีการส่ง PDF ต้นฉบับเข้า OCR และไม่อนุญาตให้ `Skip Crop` หน้า PDF ต้องถูก render เป็นภาพ, Crop, Resize, Enhance และ Convert เป็น JPG ก่อนเสมอ

### Preview Document Mode

- `+` / `-`: Zoom In และ Zoom Out
- `Fit to Screen`: แสดงภาพให้พอดีพื้นที่ Preview
- `100%`: แสดงภาพตามขนาดจริง
- `Reset View`: รีเซ็ต Zoom และ Pan
- `Back to PDF Pages`: กลับไปเลือกหน้า PDF ใหม่ เฉพาะกรณีไฟล์ PDF
- `Back to Crop`: กลับไปแก้กรอบ
- `Run OCR`: ส่งไฟล์เข้า OCR API

### Result

- `Plaintext`: แสดง key และค่าตาม OCR API
- `JSON`: แสดง JSON โดยซ่อน encoded image payload ที่ยาวและมีข้อมูล sensitive
- `Copy JSON`: Copy JSON ที่ผ่านการ sanitize
- `Download Text`: ดาวน์โหลด `.txt`
- `Download JSON`: ดาวน์โหลด `.json`

## OCR API

ระบบรองรับ API 9 รายการ:

| กลุ่ม | รายการ | หมายเหตุ |
|---|---|---|
| บัตรประชาชนด้านหน้า | อ่านหน้าบัตร | WebSolution `/ocr/id` |
| บัตรประชาชนด้านหน้า | อ่านหน้าบัตร Custom Result | Middleware `/ocrmid/`, `type=id` |
| บัตรประชาชนด้านหน้า | อ่านหน้าบัตร Other | FacePOC พร้อม Authorization |
| บัตรประชาชนด้านหลัง | อ่านหลังบัตร | WebSolution `/ocr/back_id` |
| บัตรประชาชนด้านหลัง | อ่านหลังบัตร Custom Result | Middleware `/ocrmid/`, `type=backid` |
| บัตรประชาชนด้านหลัง | อ่านหลังบัตร Other | FacePOC พร้อม Authorization |
| พาสปอร์ต | อ่านพาสปอร์ต | WebSolution `/ocr/passport` |
| พาสปอร์ต | อ่านพาสปอร์ต Custom Result | Middleware `/ocrmid/`, `type=passport` |
| เอกสารอื่น ๆ | อ่านเอกสาร Custom | WebSolution `/ocr/custom` |

API กลุ่ม WebSolution ใช้ multipart key:

```text
image_file[]
```

API กลุ่ม FacePOC Other ใช้ multipart key:

```text
file
```

## PDF และ TIFF

- PDF จะถูกอ่านด้วย PDF.js ใน browser เพื่อ render เป็นภาพรายหน้า
- PDF หลายหน้าจะมี thumbnail/page selector ให้เลือกหน้า OCR
- หน้า PDF ที่เลือกจะถูกแปลงเป็น JPG แล้วผ่าน Crop, Resize และ Enhance ก่อน OCR
- ระบบห้ามส่ง PDF ต้นฉบับเข้า OCR API โดยตรง เพื่อลดปัญหา API รับ PDF หลายหน้าหรือไฟล์ที่ไม่ใช่รูปไม่ได้
- TIFF อาจ Preview หรือ Crop ไม่ได้ขึ้นกับ Browser ระบบจะส่งไฟล์ต้นฉบับ
- JPG, JPEG, PNG และ BMP รองรับ Crop, Resize, Enhance และ Convert เป็น JPG

## Environment Variables

| Variable | Default | หน้าที่ |
|---|---|---|
| `HOST` | `127.0.0.1` | Host ของ Python server |
| `PORT` | `3000` | Port ของ Python server |
| `WEBSOLUTION_BASE_URL` | `https://websolution.cdgs.co.th` | Base URL ของ WebSolution OCR |
| `OCR_OTHER_AUTH_TOKEN` | ไม่มี | Authorization token สำหรับ FacePOC Other |

## Security Notes

- Token อยู่ใน `.env` ฝั่ง server เท่านั้น
- Frontend ไม่รับและไม่แสดง token
- Debug Panel แสดง Authorization เป็น `******`
- ไม่เก็บภาพหรือ OCR result ลง `localStorage`
- Object URL ถูก revoke เมื่อเปลี่ยนภาพ
- Camera stream ถูก stop เมื่อออกจากหน้ากล้อง

## Troubleshooting

### API Other ขึ้นว่าต้องตั้ง Token

ตรวจสอบ `.env`:

```text
OCR_OTHER_AUTH_TOKEN=your-token
```

จากนั้น restart server

### เชื่อมต่อ Backend Proxy ไม่สำเร็จ

ตรวจสอบว่าเปิด server อยู่:

```powershell
uvicorn server:app --host 127.0.0.1 --port 3000
```

### Port 3000 ถูกใช้งาน

เปลี่ยน port ชั่วคราว:

```powershell
$env:PORT="3001"
uvicorn server:app --host 127.0.0.1 --port 3001
```

แล้วเปิด `http://127.0.0.1:3001`
#   O C R C D G  
 