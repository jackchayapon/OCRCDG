# OCRCDG - OCR Document Capture

<p align="center">
  <strong>Web application for capturing, preparing, and sending document images to OCR APIs through a secure FastAPI proxy.</strong>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115.6-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img alt="Uvicorn" src="https://img.shields.io/badge/Uvicorn-ASGI-2F6FED?style=for-the-badge">
  <img alt="Vanilla JS" src="https://img.shields.io/badge/Frontend-Vanilla%20JS-F7DF1E?style=for-the-badge&logo=javascript&logoColor=111">
</p>

## Overview

OCRCDG เป็นเว็บแอปสำหรับอัปโหลดไฟล์หรือถ่ายภาพเอกสารจากกล้อง จัดกรอบ Crop, Resize, Enhance แล้วส่งเข้า OCR API ผ่าน backend proxy ที่เขียนด้วย FastAPI เพื่อซ่อน token และลดปัญหา CORS

ระบบออกแบบให้ทำงานแบบ privacy-first: ข้อมูลภาพและผล OCR อยู่ใน memory ของ browser เท่านั้น ไม่มีการเก็บลง `localStorage` และมีระบบ auto cleanup เมื่อผู้ใช้เปลี่ยนไฟล์ กลับหน้าแรก ปิด/refresh หน้าเว็บ หรือจบ OCR session

อ่านรายละเอียดเชิงสถาปัตยกรรมได้ที่ [TECH_STACK.md](TECH_STACK.md)

## Highlights

| Area | What It Does |
|---|---|
| File Upload | รองรับ `PDF`, `JPG`, `JPEG`, `PNG`, `TIFF`, `BMP` |
| Camera Capture | เปิดกล้อง ถ่ายภาพเอกสาร และ export เป็น JPG ตามขนาด preset |
| PDF Workflow | Render PDF เป็นภาพรายหน้า เลือกหน้าที่ต้องการ OCR ได้ |
| Crop Tools | Auto Detect Document, Trim White Area, Manual Crop, Reset Crop |
| Image Processing | Crop, resize, white padding, contrast/brightness enhancement, JPG export |
| OCR Proxy | Browser ส่งไฟล์ไปที่ FastAPI แล้ว server ส่งต่อไป OCR API จริง |
| Result Viewer | Plaintext, JSON, image preview, encoded payload viewer แบบย่อ/ขยาย |
| Privacy Cleanup | Auto clear sensitive data พร้อมปุ่ม Clear Data สำหรับ manual fallback |

## Camera Presets

เมื่อกด `Open Camera` ระบบจะสร้างภาพ JPG ตามขนาดเป้าหมายจริงก่อนนำเข้า workflow:

| Preset | Output Size | Aspect Ratio |
|---|---:|---:|
| ID Card | `1000 x 630` | `1.587:1` |
| Passport | `1000 x 700` | `1.429:1` |
| A4 Portrait | `1240 x 1754` | `0.707:1` |
| A4 Landscape | `1754 x 1240` | `1.414:1` |

## Project Structure

```text
OCRCDG/
├── app.js              # Frontend state, camera, crop, OCR request, result rendering
├── index.html          # Application UI
├── styles.css          # Responsive layout and visual styling
├── server.py           # FastAPI static server and OCR proxy
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Ignored local files and secrets
├── README.md           # Setup and usage guide
└── TECH_STACK.md       # Architecture and implementation notes
```

## Requirements

- Python `3.10+`
- Modern browser เช่น Chrome, Edge, Firefox หรือ Safari
- Camera permission ถ้าต้องการใช้ `Open Camera`
- Internet สำหรับโหลด PDF.js และ pako จาก CDN
- Network ที่เข้าถึง OCR upstream APIs ได้

Python dependencies:

```text
fastapi==0.115.6
uvicorn[standard]==0.32.1
requests==2.32.5
```

## Setup

1. Clone repository:

```powershell
git clone https://github.com/jackchayapon/OCRCDG.git
cd OCRCDG
```

2. Create virtual environment:

```powershell
python -m venv .venv
```

3. Activate virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

4. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

5. Create `.env` from example:

```powershell
Copy-Item .env.example .env
```

6. Add server-side token when needed:

```text
OCR_OTHER_AUTH_TOKEN=replace-with-server-token
```

`OCR_OTHER_AUTH_TOKEN` is required only for OCR APIs that need Authorization. Keep `.env` local. It is ignored by Git.

## Run

Start the FastAPI app with Uvicorn:

```powershell
uvicorn server:app --host 127.0.0.1 --port 3000
```

Open the app:

```text
http://127.0.0.1:3000
```

Stop the server with `Ctrl+C`.

## How To Use

### Upload File

1. Click `Upload File`
2. Select a supported document
3. If the file is PDF, choose a page and click `OCR Selected Page`
4. Check or adjust the crop box
5. Click `Apply Crop` or `Skip Crop`
6. Review the processed preview
7. Select the OCR API from the sidebar
8. Click `Run OCR`
9. View the output in `Plaintext` or `JSON`

### Open Camera

1. Click `Open Camera`
2. Allow camera permission
3. Select a frame preset: ID Card, Passport, A4 Portrait, or A4 Landscape
4. Place the document inside the frame
5. Click capture
6. Review crop and run OCR as usual

## OCR API Mapping

| API ID | Upstream | Multipart Key | Extra Field | Auth |
|---|---|---|---|---|
| `front-id` | WebSolution `/ocr/id` | `image_file[]` | - | No |
| `front-id-custom` | WebSolution `/ocrmid/` | `image_file[]` | `type=id` | No |
| `front-id-other` | FacePOC `/upload_front_file` | `file` | - | Yes |
| `back-id` | WebSolution `/ocr/back_id` | `image_file[]` | - | No |
| `back-id-custom` | WebSolution `/ocrmid/` | `image_file[]` | `type=backid` | No |
| `back-id-other` | FacePOC `/upload_back_file` | `file` | - | Yes |
| `passport` | WebSolution `/ocr/passport` | `image_file[]` | - | No |
| `passport-custom` | WebSolution `/ocrmid/` | `image_file[]` | `type=passport` | No |
| `custom-document` | WebSolution `/ocr/custom` | `image_file[]` | - | No |

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `HOST` | `127.0.0.1` | Host used when running `python server.py` |
| `PORT` | `3000` | Port used when running `python server.py` |
| `WEBSOLUTION_BASE_URL` | `https://websolution.cdgs.co.th` | Base URL for WebSolution OCR APIs |
| `OCR_OTHER_AUTH_TOKEN` | empty | Authorization token for FacePOC Other APIs |

## Privacy And Security

- `.env` stores server-side secrets and is ignored by Git
- The browser never receives OCR API tokens
- Debug output masks Authorization values
- Uploaded images and OCR results are kept in memory only
- Object URLs are revoked during cleanup
- Canvas, image `src`, PDF state, and OCR result state are cleared automatically
- Camera streams are stopped when leaving camera flow
- Pending OCR requests are aborted when the session is cancelled or cleared
- Result image preview is hidden after sensitive data cleanup

## Troubleshooting

### Backend proxy cannot connect

Run the backend:

```powershell
uvicorn server:app --host 127.0.0.1 --port 3000
```

Then open:

```text
http://127.0.0.1:3000
```

### Port 3000 is already in use

Use another port:

```powershell
uvicorn server:app --host 127.0.0.1 --port 3001
```

Then open `http://127.0.0.1:3001`.

### Other API requires token

Check `.env`:

```text
OCR_OTHER_AUTH_TOKEN=your-token-here
```

Restart Uvicorn after editing `.env`.

### PDF preview does not load

PDF rendering uses PDF.js from CDN. Check internet access or use an image file instead.

## License

No license file is included yet. Add one before publishing for wider reuse.
