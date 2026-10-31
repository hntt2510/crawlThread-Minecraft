import asyncio
from pathlib import Path
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.database import get_db, SessionLocal
from backend.app.core.job_manager import job_manager, Job
from backend.app.models.db_models import Project, ThreadsPost, CommentSelection, TTSAsset, MediaAsset, RenderJob
from backend.app.schemas.pydantic_schemas import RenderRequest
from backend.app.services.card_renderer.card_generator import card_generator
from backend.app.services.video_composer.ffmpeg_composer import ffmpeg_composer, VideoScene, VideoRenderConfig
from backend.app.services.tts.tts_service import tts_service

router = APIRouter(prefix="/render", tags=["render"])

def _execute_render(job: Job, data: RenderRequest):
    db: Session = SessionLocal()
    try:
        project_id = data.project_id
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Không tìm thấy dự án {project_id}")

        job.update(5, "Đang chuẩn bị các phân cảnh và thẻ hình ảnh...")

        project_dir = settings.DATA_DIR / "projects" / project_id
        cards_dir = project_dir / "cards"
        cards_dir.mkdir(parents=True, exist_ok=True)

        selections = db.query(CommentSelection).filter(
            CommentSelection.project_id == project_id,
            CommentSelection.is_active == True
        ).order_by(CommentSelection.sequence_order.asc()).all()

        if not selections and not project.post:
            raise ValueError("Không có nội dung bài viết hoặc bình luận nào để dựng video.")

        scenes: list[VideoScene] = []
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # 1. Post scene (Root Threads Post)
        if project.post and project.post.content:
            post_card_path = cards_dir / "root_post_card.png"
            card_generator.create_card(
                author_username=project.post.author_username,
                author_display_name=project.post.author_display_name,
                content=project.post.content,
                output_path=post_card_path,
                card_type="post",
                like_count=project.post.like_count,
                reply_count=project.post.reply_count,
                theme=data.card_theme
            )

            # Generate or fetch audio
            post_tts = loop.run_until_complete(
                tts_service.synthesize_text(
                    text=project.post.content,
                    provider="edge_tts",
                    voice=project.settings.get("default_voice", "vi-VN-HoaiMyNeural")
                )
            )
            # Duration: speech duration + 0.6s pause buffer (min 2.5s)
            dur_sec = max(2.5, (post_tts.duration_ms / 1000.0) + 0.6)
            scenes.append(VideoScene(
                card_image_path=post_card_path,
                audio_path=post_tts.file_path,
                duration_sec=dur_sec
            ))

        # 2. Comment scenes
        for idx, sel in enumerate(selections):
            c = sel.comment
            c_card_path = cards_dir / f"comment_card_{idx}.png"
            card_generator.create_card(
                author_username=c.author_username if c else "user",
                author_display_name=c.author_display_name if c else "Bình luận",
                content=sel.display_text,
                output_path=c_card_path,
                card_type="comment",
                like_count=c.like_count if c else 0,
                reply_count=c.reply_count if c else 0,
                theme=data.card_theme
            )

            # Check if selection already has audio
            if sel.tts_asset and Path(sel.tts_asset.audio_path).exists():
                audio_path = Path(sel.tts_asset.audio_path)
                dur_ms = sel.tts_asset.duration_ms
            else:
                c_tts = loop.run_until_complete(
                    tts_service.synthesize_text(
                        text=sel.tts_text,
                        provider="edge_tts",
                        voice=sel.voice_id or "vi-VN-HoaiMyNeural",
                        rate=sel.voice_rate or 1.0
                    )
                )
                audio_path = c_tts.file_path
                dur_ms = c_tts.duration_ms

            dur_sec = max(2.0, (dur_ms / 1000.0) + 0.6)
            scenes.append(VideoScene(
                card_image_path=c_card_path,
                audio_path=audio_path,
                duration_sec=dur_sec
            ))

        # 3. Resolve background video
        bg_video_path = None
        if data.background_asset_id:
            asset = db.query(MediaAsset).filter(MediaAsset.id == data.background_asset_id).first()
            if asset and Path(asset.file_path).exists():
                bg_video_path = Path(asset.file_path)

        output_mp4 = project_dir / f"{project.title}_rendered.mp4"

        render_config = VideoRenderConfig(
            output_path=output_mp4,
            scenes=scenes,
            background_video_path=bg_video_path,
            background_start_sec=data.background_start_sec,
            background_volume=data.background_volume,
            voice_volume=data.voice_volume,
            width=1080,
            height=1920,
            fps=30
        )

        job.update(25, "Đang tiến hành dựng video với FFmpeg...")

        def on_progress(pct: int, msg: str):
            job.update(pct, msg)

        final_video = ffmpeg_composer.render_video(render_config, progress_callback=on_progress)

        # Update Project and RenderJob in database
        project.status = "rendered"
        render_record = RenderJob(
            project_id=project_id,
            status="completed",
            progress=100,
            video_output_path=str(final_video),
            duration_sec=sum(s.duration_sec for s in scenes),
            completed_at=datetime.now(timezone.utc)
        )
        db.add(render_record)
        db.commit()

        return {
            "project_id": project_id,
            "video_path": str(final_video),
            "duration_sec": render_record.duration_sec
        }
    finally:
        db.close()

@router.post("/start")
def start_render(data: RenderRequest):
    job = job_manager.create_job("video_render", project_id=data.project_id)
    job_manager.run_in_background(job, _execute_render, data)
    return {
        "job_id": job.id,
        "status": "pending",
        "message": "Đang bắt đầu dựng video..."
    }

@router.get("/status/{job_id}")
def get_render_status(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy tiến trình dựng video.")
    return job.to_dict()

@router.get("/video/{project_id}")
def get_rendered_video(project_id: str, db: Session = Depends(get_db)):
    render = db.query(RenderJob).filter(
        RenderJob.project_id == project_id,
        RenderJob.status == "completed"
    ).order_by(RenderJob.completed_at.desc()).first()

    if not render or not render.video_output_path or not Path(render.video_output_path).exists():
        raise HTTPException(status_code=404, detail="Chưa có video nào được dựng cho dự án này.")

    return FileResponse(render.video_output_path, media_type="video/mp4", filename=Path(render.video_output_path).name)
