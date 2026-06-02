import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import ATTACHMENTS_DIR, MAX_UPLOAD_SIZE, ALLOWED_MIME_TYPES
from ..database import get_db
from ..schemas import FileUploadOut

router = APIRouter(prefix="/api/files", tags=["files"])


@router.post("/upload", response_model=FileUploadOut)
async def upload_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")

    ext = os.path.splitext(file.filename or "file")[1] or ".bin"
    file_id = uuid.uuid4().hex
    filename = f"{file_id}{ext}"

    os.makedirs(ATTACHMENTS_DIR, exist_ok=True)
    file_path = ATTACHMENTS_DIR / filename
    with open(file_path, "wb") as f:
        f.write(content)

    return FileUploadOut(
        id=file_id,
        filename=file.filename or filename,
        mime_type=file.content_type or "application/octet-stream",
        size=len(content),
        url=f"/api/files/{filename}",
    )


@router.get("/{filename}")
async def download_file(filename: str):
    file_path = ATTACHMENTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=str(file_path), filename=filename)
