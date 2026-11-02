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
from backend.app.services.video_composer.ffmpeg_composer import ffmpeg_composer, VideoScene, VideoRenderConfig, SFXCue
from backend.app.services.tts.tts_service import tts_service
from backend.app.services.timeline.timeline_planner import timeline_planner
from backend.app.services.caption.caption_engine import caption_engine, CaptionConfig
from backend.app.services.sfx.sfx_manager import sfx_manager
from backend.app.services.gameplay.gameplay_manager import gameplay_manager
from backend.app.services.quality_checker.quality_checker import quality_checker

router = APIRouter(prefix="/render", tags=["render"])

def _execute_render(job: Job, data: RenderRequest):
    db: Session = SessionLocal()
    try:
        project_id = data.project_id
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Không tìm thấy dự án {project_id}")

        job.update(5, "Đang chuẩn bị kịch bản AI Timeline và kiểm định chất lượng...")

        project_dir = settings.DATA_DIR / "projects" / project_id
        cards_dir = project_dir / "cards"
        cards_dir.mkdir(parents=True, exist_ok=True)

        selections = db.query(CommentSelection).filter(
            CommentSelection.project_id == project_id,
            CommentSelection.is_active == True
        ).order_by(CommentSelection.sequence_order.asc()).all()

        if not selections and not project.post:
            raise ValueError("Không có nội dung bài viết hoặc bình luận nào để dựng video.")

        settings_dict = project.settings or {}
        hook_data = settings_dict.get("hook")

        # 1. AI Timeline Planning
        plan = timeline_planner.plan_timeline(
            hook=hook_data,
            post=project.post,
            comments=selections,
            pace=settings_dict.get("video_pace", "balanced")
        )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # 2. Pre-flight Quality Check
        quality_rep = quality_checker.check_project_readiness(
            timeline_plan=plan,
            voice_volume=data.voice_volume,
            bgm_volume=data.background_volume
        )
        if not quality_rep.is_passed:
            err_msg = "; ".join(e.message for e in quality_rep.errors)
            raise ValueError(f"Kiểm định chất lượng chưa đạt: {err_msg}")

        job.update(12, "Đang tạo thẻ đồ họa và tổng hợp giọng thuyết minh...")

        scenes: list[VideoScene] = []

        # 3. Build VideoScenes matching TimelinePlan
        for s in plan.scenes:
            if s.scene_type == "hook":
                hook_card_path = cards_dir / "scene_00_hook.png"
                card_generator.create_card(
                    author_username="threads_studio",
                    author_display_name="Điểm Nhấn Mở Đầu",
                    content=s.display_text,
                    output_path=hook_card_path,
                    card_type="hook",
                    theme=data.card_theme
                )
                # Hook audio
                hook_audio_path = None
                if hook_data and hook_data.get("audio_path") and Path(hook_data["audio_path"]).exists():
                    hook_audio_path = Path(hook_data["audio_path"])
                else:
                    tts_h = loop.run_until_complete(
                        tts_service.synthesize_text(
                            text=s.tts_text,
                            provider="edge_tts",
                            voice=settings_dict.get("default_voice", "vi-VN-HoaiMyNeural")
                        )
                    )
                    hook_audio_path = tts_h.file_path

                # SFX Cues
                cues = []
                if s.sfx_id and sfx_manager.get_sfx_path(s.sfx_id):
                    cues.append(SFXCue(
                        sfx_id=s.sfx_id,
                        file_path=sfx_manager.get_sfx_path(s.sfx_id),
                        timestamp_sec=s.start_time_sec + s.sfx_offset_sec,
                        volume=s.sfx_volume
                    ))

                scenes.append(VideoScene(
                    card_image_path=hook_card_path,
                    audio_path=hook_audio_path,
                    duration_sec=s.duration_sec,
                    start_time_sec=s.start_time_sec,
                    sfx_cues=cues,
                    zoom_effect=s.zoom_effect,
                    is_hook=True,
                    caption_text=s.tts_text
                ))

            elif s.scene_type == "post":
                post_card_path = cards_dir / f"scene_{s.scene_index:02d}_post.png"
                card_generator.create_card(
                    author_username=project.post.author_username,
                    author_display_name=project.post.author_display_name,
                    content=s.display_text,
                    output_path=post_card_path,
                    card_type="post",
                    like_count=project.post.like_count,
                    reply_count=project.post.reply_count,
                    theme=data.card_theme
                )

                post_tts = loop.run_until_complete(
                    tts_service.synthesize_text(
                        text=s.tts_text,
                        provider="edge_tts",
                        voice=settings_dict.get("default_voice", "vi-VN-HoaiMyNeural")
                    )
                )

                cues = []
                if s.sfx_id and sfx_manager.get_sfx_path(s.sfx_id):
                    cues.append(SFXCue(
                        sfx_id=s.sfx_id,
                        file_path=sfx_manager.get_sfx_path(s.sfx_id),
                        timestamp_sec=s.start_time_sec + s.sfx_offset_sec,
                        volume=s.sfx_volume
                    ))

                scenes.append(VideoScene(
                    card_image_path=post_card_path,
                    audio_path=post_tts.file_path,
                    duration_sec=s.duration_sec,
                    start_time_sec=s.start_time_sec,
                    sfx_cues=cues,
                    zoom_effect=s.zoom_effect,
                    is_hook=False,
                    caption_text=s.tts_text
                ))

            else:  # comment
                c_card_path = cards_dir / f"scene_{s.scene_index:02d}_comment.png"
                card_generator.create_card(
                    author_username=s.author_username or "user",
                    author_display_name=s.author_display_name or "Bình luận",
                    content=s.display_text,
                    output_path=c_card_path,
                    card_type="comment",
                    theme=data.card_theme
                )

                # Match selection
                sel = next((item for item in selections if item.comment_id in s.id or item.display_text == s.display_text), None)
                if sel and sel.tts_asset and Path(sel.tts_asset.audio_path).exists():
                    audio_path = Path(sel.tts_asset.audio_path)
                else:
                    c_tts = loop.run_until_complete(
                        tts_service.synthesize_text(
                            text=s.tts_text,
                            provider="edge_tts",
                            voice=settings_dict.get("default_voice", "vi-VN-HoaiMyNeural")
                        )
                    )
                    audio_path = c_tts.file_path

                cues = []
                if s.sfx_id and sfx_manager.get_sfx_path(s.sfx_id):
                    cues.append(SFXCue(
                        sfx_id=s.sfx_id,
                        file_path=sfx_manager.get_sfx_path(s.sfx_id),
                        timestamp_sec=s.start_time_sec + s.sfx_offset_sec,
                        volume=s.sfx_volume
                    ))

                scenes.append(VideoScene(
                    card_image_path=c_card_path,
                    audio_path=audio_path,
                    duration_sec=s.duration_sec,
                    start_time_sec=s.start_time_sec,
                    sfx_cues=cues,
                    zoom_effect=s.zoom_effect,
                    is_hook=False,
                    caption_text=s.tts_text
                ))

        # 4. Resolve Background Gameplay Video
        bg_video_path = None
        start_sec = data.background_start_sec
        if data.background_asset_id:
            asset = db.query(MediaAsset).filter(MediaAsset.id == data.background_asset_id).first()
            if asset and Path(asset.file_path).exists():
                bg_video_path = Path(asset.file_path)

        if not bg_video_path or not bg_video_path.exists():
            smart_bg = gameplay_manager.select_smart_segment(required_duration_sec=plan.total_duration_sec)
            bg_video_path = smart_bg["file_path"]
            start_sec = smart_bg["start_time_sec"]

        # 5. Generate Smart Captions (ASS format)
        ass_path = None
        if settings_dict.get("captions_enabled", True) and plan.caption_segments:
            ass_path = project_dir / "captions.ass"
            caption_engine.generate_ass_subtitles(
                segments=plan.caption_segments,
                output_path=ass_path,
                config=CaptionConfig()
            )

        output_mp4 = project_dir / f"{project.title}_rendered.mp4"

        render_config = VideoRenderConfig(
            output_path=output_mp4,
            scenes=scenes,
            background_video_path=bg_video_path,
            background_start_sec=start_sec,
            background_volume=data.background_volume,
            voice_volume=data.voice_volume,
            ducking_enabled=data.ducking_enabled,
            ass_subtitle_path=ass_path,
            width=1080,
            height=1920,
            fps=30
        )

        job.update(25, "Đang tiến hành dựng video hoàn chỉnh với FFmpeg...")

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
        "message": "Đang bắt đầu dựng video AI Studio..."
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
