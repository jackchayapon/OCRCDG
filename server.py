import os
from email.parser import BytesParser
from email.policy import default
from functools import partial
from pathlib import Path

import requests
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from starlette.concurrency import run_in_threadpool


ROOT = Path(__file__).resolve().parent


def load_env_file(path):
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


load_env_file(ROOT / ".env")

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "3000"))
MAX_UPLOAD_BYTES = 20 * 1024 * 1024
REQUEST_TIMEOUT_SECONDS = 45
WEBSOLUTION_BASE_URL = os.environ.get("WEBSOLUTION_BASE_URL", "https://websolution.cdgs.co.th").rstrip("/")

# Keep upstream routing and secrets on the server. The browser sends only apiId and a file.
PROXY_APIS = {
    "front-id": {
        "endpoint": f"{WEBSOLUTION_BASE_URL}/ocr/id",
        "form_file_key": "image_file[]",
    },
    "front-id-custom": {
        "endpoint": f"{WEBSOLUTION_BASE_URL}/ocrmid/",
        "form_file_key": "image_file[]",
        "extra_form_fields": {"type": "id"},
    },
    "front-id-other": {
        "endpoint": "https://facepoc.cdgs.co.th/ocr/api/v1/upload_front_file",
        "form_file_key": "file",
        "auth_header_name": "Authorization",
        "auth_env_key": "OCR_OTHER_AUTH_TOKEN",
    },
    "back-id": {
        "endpoint": f"{WEBSOLUTION_BASE_URL}/ocr/back_id",
        "form_file_key": "image_file[]",
    },
    "back-id-custom": {
        "endpoint": f"{WEBSOLUTION_BASE_URL}/ocrmid/",
        "form_file_key": "image_file[]",
        "extra_form_fields": {"type": "backid"},
    },
    "back-id-other": {
        "endpoint": "https://facepoc.cdgs.co.th/ocr/api/v1/upload_back_file",
        "form_file_key": "file",
        "auth_header_name": "Authorization",
        "auth_env_key": "OCR_OTHER_AUTH_TOKEN",
    },
    "passport": {
        "endpoint": f"{WEBSOLUTION_BASE_URL}/ocr/passport",
        "form_file_key": "image_file[]",
    },
    "passport-custom": {
        "endpoint": f"{WEBSOLUTION_BASE_URL}/ocrmid/",
        "form_file_key": "image_file[]",
        "extra_form_fields": {"type": "passport"},
    },
    "custom-document": {
        "endpoint": f"{WEBSOLUTION_BASE_URL}/ocr/custom",
        "form_file_key": "image_file[]",
    },
}

STATIC_FILES = {
    "/": "index.html",
    "/index.html": "index.html",
    "/styles.css": "styles.css",
    "/app.js": "app.js",
}

app = FastAPI(title="OCR Document Capture", version="1.0.0")


def no_store_json(status_code, payload):
    return JSONResponse(
        status_code=status_code,
        content=payload,
        headers={"Cache-Control": "no-store"},
    )


def parse_content_length(request):
    raw_value = request.headers.get("content-length", "0")
    try:
        return int(raw_value)
    except ValueError:
        return 0


@app.get("/api/ocr/status")
def get_ocr_status():
    return no_store_json(
        200,
        {
            "apis": {
                api_id: {
                    "available": not api.get("auth_env_key") or bool(os.environ.get(api["auth_env_key"])),
                    "authRequired": bool(api.get("auth_env_key")),
                }
                for api_id, api in PROXY_APIS.items()
            }
        },
    )


@app.post("/api/ocr/proxy")
async def proxy_ocr_request(request: Request):
    content_type = request.headers.get("content-type", "")
    if not content_type.startswith("multipart/form-data;"):
        return no_store_json(400, {"error": "Expected multipart/form-data"})

    if parse_content_length(request) > MAX_UPLOAD_BYTES:
        return no_store_json(413, {"error": "Uploaded file is too large"})

    body = await request.body()
    if len(body) > MAX_UPLOAD_BYTES:
        return no_store_json(413, {"error": "Uploaded file is too large"})

    fields, uploads = parse_multipart_body(body, content_type)
    api_id = fields.get("apiId", "")
    api = PROXY_APIS.get(api_id)
    if not api:
        return no_store_json(400, {"error": "Unsupported proxy API"})

    token = os.environ.get(api.get("auth_env_key", ""), "")
    if api.get("auth_env_key") and not token:
        return no_store_json(503, {"error": f"Missing server environment variable: {api['auth_env_key']}"})

    upload = uploads[0] if uploads else None
    if upload is None:
        return no_store_json(400, {"error": "Missing uploaded file"})

    if len(upload["content"]) > MAX_UPLOAD_BYTES:
        return no_store_json(413, {"error": "Uploaded file is too large"})

    filename = Path(upload["filename"] or "upload.jpg").name
    upload_content_type = upload["content_type"] or "application/octet-stream"
    files = {api["form_file_key"]: (filename, upload["content"], upload_content_type)}
    headers = {api["auth_header_name"]: token} if token else {}
    post_upstream = partial(
        requests.post,
        api["endpoint"],
        files=files,
        data=api.get("extra_form_fields", {}),
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    try:
        upstream = await run_in_threadpool(post_upstream)
    except requests.Timeout:
        return no_store_json(504, {"error": "OCR request timed out"})
    except requests.RequestException:
        return no_store_json(502, {"error": "Cannot connect to upstream OCR API"})

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=upstream.headers.get("Content-Type", "application/json; charset=utf-8"),
        headers={"Cache-Control": "no-store"},
    )


def parse_multipart_body(body, content_type):
    message = BytesParser(policy=default).parsebytes(
        b"Content-Type: " + content_type.encode("latin1") + b"\r\nMIME-Version: 1.0\r\n\r\n" + body
    )
    if not message.is_multipart():
        return {}, []

    fields = {}
    uploads = []
    for part in message.iter_parts():
        name = part.get_param("name", header="content-disposition")
        if not name:
            continue
        content = part.get_payload(decode=True) or b""
        filename = part.get_filename()
        if filename:
            uploads.append(
                {
                    "name": name,
                    "filename": filename,
                    "content_type": part.get_content_type(),
                    "content": content,
                }
            )
        else:
            fields[name] = content.decode(part.get_content_charset() or "utf-8", errors="replace").strip()
    return fields, uploads


@app.get("/{path:path}")
def serve_static_file(path: str, request: Request):
    request_path = request.url.path
    filename = STATIC_FILES.get(request_path)
    if not filename:
        return no_store_json(404, {"error": "Not found"})

    file_path = ROOT / filename
    if not file_path.exists():
        return no_store_json(500, {"error": "Cannot read static file"})

    return FileResponse(
        file_path,
        headers={"Cache-Control": "no-store"},
    )


if __name__ == "__main__":
    print(f"OCR Document Capture running at http://{HOST}:{PORT}")
    uvicorn.run("server:app", host=HOST, port=PORT, reload=False)
