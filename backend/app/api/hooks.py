import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.db_models import Project, ThreadsPost, ThreadsComment, CommentSelection
from backend.app.services.ai_curation.hook_generator import hook_generator, HookOption
from backend.app.services.tts.tts_service import tts_service
from backend.app.services.card_renderer.card_generator import card_generator

router = APIRouter(prefix="/hooks", tags=["hooks"])

@router.get("/project/{project_id}")
def get_project_hook(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")

    settings_dict = project.settings or {}
    hook_data = settings_dict.get("hook")
    return {
        "success": True,
        "hook": hook_data
    }

@router.post("/project/{project_id}/generate")
def generate_project_hooks(project_id: str, db: Session = Depends(get_db)):
    post = db.query(ThreadsPost).filter(ThreadsPost.project_id == project_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết gốc.")

    selections = db.query(CommentSelection).filter(
        CommentSelection.project_id == project_id,
        CommentSelection.is_active == True
    ).order_by(CommentSelection.sequence_order).all()

    result = hook_generator.generate_hooks(
        post_content=post.content,
        author_username=post.author_username,
        comments=selections
    )

    return {
        "success": True,
        "data": result.model_dump()
    }

class SelectHookRequest(Dict[str, Any]):
    pass

@router.post("/project/{project_id}/select")
async def select_or_update_hook(
    project_id: str,
    payload: Dict[str, Any],
    generate_audio: bool = Query(True),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")

    hook_text = payload.get("hook_text", "").strip()
    tts_text = payload.get("tts_text", "").strip() or hook_text
    style = payload.get("style", "custom")
    title_badge = payload.get("title_badge", "⚡ MỞ ĐẦU")
    voice_id = payload.get("voice_id", "vi-VN-HoaiMyNeural")

    if not hook_text:
        # User wants to disable hook
        cur_settings = dict(project.settings or {})
        cur_settings["hook"] = None
        project.settings = cur_settings
        db.commit()
        return {"success": True, "message": "Đã tắt phân cảnh mở đầu (Hook)."}

    audio_path_str = None
    audio_dur_sec = 0.0

    if generate_audio:
        try:
            tts_res = await tts_service.synthesize(
                text=tts_text,
                provider="edge_tts",
                voice=voice_id,
                rate=1.05
            )
            audio_path_str = str(tts_res.file_path)
            audio_dur_sec = round(tts_res.duration_ms / 1000.0, 2)
        except Exception as e:
            audio_dur_sec = max(2.5, round(len(tts_text.split()) / 3.0, 2))

    # Pre-render Hook card
    hook_card_path = settings.DATA_DIR / "projects" / project_id / "assets" / "hook_card.png"
    card_generator.create_card(
        author_username="threads_studio",
        author_display_name="Điểm Nhấn Mở Đầu",
        content=hook_text,
        output_path=hook_card_path,
        card_type="hook",
        like_count=None,
        reply_count=None,
        theme="dark"
    )

    hook_data = {
        "id": "project_active_hook",
        "style": style,
        "title_badge": title_badge,
        "hook_text": hook_text,
        "tts_text": tts_text,
        "voice_id": voice_id,
        "audio_path": audio_path_str,
        "audio_duration_sec": audio_dur_sec,
        "card_image_path": str(hook_card_path),
        "is_enabled": True
    }

    cur_settings = dict(project.settings or {})
    cur_settings["hook"] = hook_data
    project.settings = cur_settings
    db.commit()

    return {
        "success": True,
        "hook": hook_data
    }
