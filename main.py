from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import aiofiles
import os
import random
import string
import json
import time
from pathlib import Path

app = FastAPI(title="DropZone File Sharing")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
META_FILE = Path("meta.json")

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
CODE_EXPIRE_SECONDS = 24 * 60 * 60  # 24 hours

# ── Load/Save metadata ──
def load_meta():
    if META_FILE.exists():
        with open(META_FILE) as f:
            return json.load(f)
    return {}

def save_meta(data):
    with open(META_FILE, "w") as f:
        json.dump(data, f, indent=2)

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def cleanup_expired(meta):
    now = time.time()
    expired = [code for code, info in meta.items()
               if now - info["uploaded_at"] > CODE_EXPIRE_SECONDS]
    for code in expired:
        fpath = UPLOAD_DIR / meta[code]["stored_name"]
        if fpath.exists():
            fpath.unlink()
        del meta[code]
    return meta

# ── Routes ──

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Size check
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 100MB)")

    meta = load_meta()
    meta = cleanup_expired(meta)

    # Generate unique code
    code = generate_code()
    while code in meta:
        code = generate_code()

    # Save file with code-based name to avoid collisions
    ext = Path(file.filename).suffix
    stored_name = f"{code}{ext}"
    fpath = UPLOAD_DIR / stored_name

    async with aiofiles.open(fpath, "wb") as f:
        await f.write(content)

    meta[code] = {
        "original_name": file.filename,
        "stored_name": stored_name,
        "size": len(content),
        "content_type": file.content_type or "application/octet-stream",
        "uploaded_at": time.time(),
    }
    save_meta(meta)

    return {
        "code": code,
        "filename": file.filename,
        "size": len(content),
        "expires_in": "24 hours",
    }

@app.get("/info/{code}")
async def file_info(code: str):
    code = code.upper().strip()
    meta = load_meta()
    meta = cleanup_expired(meta)
    save_meta(meta)

    if code not in meta:
        raise HTTPException(status_code=404, detail="Code not found or expired")

    info = meta[code]
    elapsed = time.time() - info["uploaded_at"]
    remaining = max(0, CODE_EXPIRE_SECONDS - elapsed)

    return {
        "filename": info["original_name"],
        "size": info["size"],
        "content_type": info["content_type"],
        "expires_in_seconds": int(remaining),
        "code": code,
    }

@app.get("/download/{code}")
async def download_file(code: str):
    code = code.upper().strip()
    meta = load_meta()
    meta = cleanup_expired(meta)
    save_meta(meta)

    if code not in meta:
        raise HTTPException(status_code=404, detail="Code not found or expired")

    info = meta[code]
    fpath = UPLOAD_DIR / info["stored_name"]

    if not fpath.exists():
        raise HTTPException(status_code=404, detail="File no longer available")

    return FileResponse(
        path=fpath,
        filename=info["original_name"],
        media_type=info["content_type"],
    )

@app.get("/stats")
async def stats():
    meta = load_meta()
    meta = cleanup_expired(meta)
    save_meta(meta)
    total_size = sum(v["size"] for v in meta.values())
    return {"active_files": len(meta), "total_size_bytes": total_size}

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
