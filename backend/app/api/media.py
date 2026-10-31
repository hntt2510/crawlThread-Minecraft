import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models.db_models import MediaAsset
from backend.app.services.tts.edge_tts_provider import probe_audio_duration_ms

router = APIRouter(prefix="/media", tags=["media"])

@router.get("")
def list_media(type: str = None, db: Session = Depends(get_db)):
    query = db.query(MediaAsset)
    if type:
        query = query.filter(MediaAsset.type == type)
    assets = query.order_by(MediaAsset.created_at.desc()).all()
    return assets

@router.post("/upload")
async def upload_media(
    file: UploadFile = File(...),
    media_type: str = Form("background_video"),  # background_video, background_music
    db: Session = Depends(get_db)
):
    media_dir = settings.DATA_DIR / "media" / media_type
    media_dir.mkdir(parents=True, exist_ok=True)

    file_id = str(uuid.uuid4())
    ext = Path(file.filename).suffix or ".mp4"
    dest_path = media_dir / f"{file_id}{ext}"

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    duration_ms = probe_audio_duration_ms(dest_path)
    file_size = dest_path.stat().st_size

    asset = MediaAsset(
        id=file_id,
        type=media_type,
        name=file.filename,
        file_path=str(dest_path),
        duration_ms=duration_ms,
        file_size_bytes=file_size
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset

@router.get("/{asset_id}/file")
def get_media_file(asset_id: str, db: Session = Depends(get_db)):
    asset = db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
    if not asset or not Path(asset.file_path).exists():
        raise HTTPException(status_code=404, detail="File media không tồn tại.")
    media_type = "video/mp4" if asset.type == "background_video" else "audio/mpeg"
    return FileResponse(asset.file_path, media_type=media_type)
