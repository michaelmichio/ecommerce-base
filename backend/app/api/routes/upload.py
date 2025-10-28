from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
from uuid import uuid4
from fastapi.responses import FileResponse

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = os.path.join(os.getcwd(), "app", "storage", "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/image")
async def upload_image(files: List[UploadFile] = File(...)):
    urls = []
    for file in files:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail=f"{file.filename} is not an image")

        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        # Save file
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Generate public URL
        urls.append(f"/upload/{filename}")

    return {"urls": urls}

@router.get("/{filename}")
async def get_uploaded_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)
