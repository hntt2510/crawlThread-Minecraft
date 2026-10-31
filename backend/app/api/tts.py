import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db, SessionLocal
from backend.app.core.job_manager import job_manager, Job
from backend.app.models.db_models import Project, ThreadsPost, CommentSelection, TTSAsset
from backend.app.schemas.pydantic_schemas import VoiceInfo, TTSPreviewRequest, TTSGenerateRequest
from backend.app.services.tts.tts_service import tts_service

router = APIRouter(prefix="/tts", tags=["tts"])

@router.get("/voices", response_model=List[VoiceInfo])
def get_voices():
    voices = tts_service.get_all_voices()
    return [
        VoiceInfo(
            id=v.id,
            name=v.name,
            provider=v.provider,
            gender=v.gender,
            accent=v.accent
        )
        for v in voices
    ]

@router.post("/preview")
async def preview_voice(data: TTSPreviewRequest):
    result = await tts_service.synthesize_text(
        text=data.text,
        provider=data.provider,
        voice=data.voice,
        rate=data.rate
    )
    return FileResponse(
        str(result.file_path),
        media_type="audio/mpeg",
        filename="preview.mp3"
    )

def _execute_tts_batch(job: Job, project_id: str, default_voice: str, default_rate: float):
    db: Session = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Không tìm thấy dự án {project_id}")

        selections = db.query(CommentSelection).filter(
            CommentSelection.project_id == project_id,
            CommentSelection.is_active == True
        ).order_by(CommentSelection.sequence_order.asc()).all()

        if not selections:
            raise ValueError("Chưa có bình luận nào được chọn để tạo giọng đọc.")

        # Also include root post
        total_items = len(selections) + (1 if project.post else 0)
        completed_items = 0

        # 1. Synthesize root post audio
        if project.post and project.post.content:
            job.update(int((completed_items / total_items) * 100), "Đang đọc bài viết gốc...")
            # Run async call in sync thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            post_audio = loop.run_until_complete(
                tts_service.synthesize_text(
                    text=project.post.content,
                    provider="edge_tts",
                    voice=default_voice,
                    rate=default_rate
                )
            )
            completed_items += 1

        # 2. Synthesize each comment
        for idx, sel in enumerate(selections):
            pct = int((completed_items / total_items) * 100)
            job.update(pct, f"Đang đọc bình luận {idx + 1}/{len(selections)}: {sel.tts_text[:25]}...")
            target_voice = sel.voice_id or default_voice
            target_rate = sel.voice_rate or default_rate

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(
                tts_service.synthesize_text(
                    text=sel.tts_text,
                    provider="edge_tts",
                    voice=target_voice,
                    rate=target_rate
                )
            )

            # Save TTSAsset in db
            existing_asset = db.query(TTSAsset).filter(TTSAsset.selection_id == sel.id).first()
            if existing_asset:
                existing_asset.provider = res.provider
                existing_asset.voice = res.voice
                existing_asset.audio_path = str(res.file_path)
                existing_asset.duration_ms = res.duration_ms
                existing_asset.file_size_bytes = res.file_size_bytes
                existing_asset.content_hash = res.content_hash
            else:
                new_asset = TTSAsset(
                    selection_id=sel.id,
                    provider=res.provider,
                    voice=res.voice,
                    audio_path=str(res.file_path),
                    duration_ms=res.duration_ms,
                    file_size_bytes=res.file_size_bytes,
                    content_hash=res.content_hash
                )
                db.add(new_asset)
            db.commit()
            completed_items += 1

        project.status = "synthesized"
        db.commit()
        job.update(100, f"Đã tạo hoàn tất {completed_items} đoạn giọng đọc tiếng Việt!")
        return {"total_synthesized": completed_items}
    finally:
        db.close()

@router.post("/generate/{project_id}")
def generate_project_tts(project_id: str, data: TTSGenerateRequest):
    job = job_manager.create_job("tts_generation", project_id=project_id)
    job_manager.run_in_background(job, _execute_tts_batch, project_id, data.default_voice, data.default_rate)
    return {
        "job_id": job.id,
        "status": "pending",
        "message": "Đang bắt đầu tạo giọng đọc cho dự án..."
    }

@router.get("/status/{job_id}")
def get_tts_status(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy tiến trình giọng đọc.")
    return job.to_dict()
