import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from app.core.config import settings

router = APIRouter(prefix="/uploads", tags=["文件上传"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".pdf"}


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """上传佐证照片/文件，返回存储路径"""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型 {ext}，允许: {sorted(ALLOWED_EXTENSIONS)}")

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过限制")
    if not content:
        raise HTTPException(status_code=400, detail="文件内容为空")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(content)

    return {"filename": filename, "path": path, "size": len(content)}
