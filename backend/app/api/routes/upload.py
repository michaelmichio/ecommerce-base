import os
from uuid import uuid4
from typing import List

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends,
    status,
)

from fastapi.responses import FileResponse

from app.core.rbac import require_role
from app.core.utils import delete_file_safe
from app.schemas.response import SuccessResponse


router = APIRouter(prefix="/upload", tags=["upload"])

# ------------------------------------------------------------------------------
# 🗂 Directory Setup
# ------------------------------------------------------------------------------

UPLOAD_DIR = os.path.join(os.getcwd(), "app", "storage", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed image extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# Maximum allowed size: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024


# ------------------------------------------------------------------------------
# 🔧 Helper
# ------------------------------------------------------------------------------

def success(data):
    return SuccessResponse(data=data)


def ensure_safe_filename(filename: str) -> str:
    """
    Prevent directory traversal:
    - Reject '..'
    - Reject slashes
    - Only allow simple filenames
    """
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid file name")
    return filename


def validate_image(file: UploadFile):
    """Validate file extension and content type."""
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}",
        )

    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"{file.filename} is not a valid image",
        )

    return ext


# ------------------------------------------------------------------------------
# 🔒 Upload Image (Admin Only)
# ------------------------------------------------------------------------------

@router.post("/image", response_model=SuccessResponse)
async def upload_image(
    files: List[UploadFile] = File(...),
    admin=Depends(require_role("admin")),
):
    """
    Upload one or multiple images.
    Admin-only for security reasons.

    - Deep validation for file type
    - Safe filename generation
    - File size limit (5MB)
    - Returns list of public URLs
    """

    urls = []

    for file in files:
        # Validate extension and MIME type
        ext = validate_image(file)

        # Enforce size limit
        file_bytes = await file.read()
        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"{file.filename} exceeds size limit (5MB)",
            )

        # Generate safe filename
        filename = f"{uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        # Save file securely
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        urls.append(f"/upload/{filename}")

    return success({"uploaded": urls})


# ------------------------------------------------------------------------------
# 🔒 Serve Uploaded File (Safe)
# ------------------------------------------------------------------------------

@router.get("/{filename}")
async def get_uploaded_file(filename: str):
    """
    Securely serve uploaded files.
    """

    filename = ensure_safe_filename(filename)

    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")

    return FileResponse(file_path)
