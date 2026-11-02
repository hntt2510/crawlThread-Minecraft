from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from backend.app.core.database import get_db
from backend.app.models.db_models import Project, ThreadsPost, CommentSelection
from backend.app.services.timeline.timeline_planner import timeline_planner
from backend.app.services.quality_checker.quality_checker import quality_checker

router = APIRouter(prefix="/quality", tags=["quality"])

@router.get("/project/{project_id}/check")
def check_quality(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")

    post = db.query(ThreadsPost).filter(ThreadsPost.project_id == project_id).first()
    selections = db.query(CommentSelection).filter(
        CommentSelection.project_id == project_id,
        CommentSelection.is_active == True
    ).order_by(CommentSelection.sequence_order).all()

    settings_dict = project.settings or {}
    hook_data = settings_dict.get("hook")

    plan = timeline_planner.plan_timeline(
        hook=hook_data,
        post=post,
        comments=selections
    )

    report = quality_checker.check_project_readiness(
        timeline_plan=plan,
        voice_volume=settings_dict.get("voice_volume", 1.0),
        bgm_volume=settings_dict.get("bg_volume", 0.2)
    )

    return {
        "success": True,
        "report": report.model_dump()
    }

@router.post("/project/{project_id}/auto-fix")
def auto_fix_issues(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")

    cur_settings = dict(project.settings or {})
    fixed_count = 0

    # Fix 1: Normalize voice volume if too high
    if cur_settings.get("voice_volume", 1.0) > 1.2:
        cur_settings["voice_volume"] = 1.0
        fixed_count += 1

    # Fix 2: Normalize BGM volume if too loud
    if cur_settings.get("bg_volume", 0.2) > 0.35:
        cur_settings["bg_volume"] = 0.20
        fixed_count += 1

    # Fix 3: Ensure ducking is enabled
    cur_settings["ducking_enabled"] = True

    # Fix 4: Trim comments if list is excessively long (> 8 comments causes > 90s)
    selections = db.query(CommentSelection).filter(
        CommentSelection.project_id == project_id,
        CommentSelection.is_active == True
    ).order_by(CommentSelection.sequence_order).all()

    if len(selections) > 7:
        # Keep top 5
        for idx, sel in enumerate(selections):
            if idx >= 5:
                sel.is_active = False
                fixed_count += 1

    project.settings = cur_settings
    db.commit()

    return {
        "success": True,
        "message": f"Đã tự động tối ưu {fixed_count} tiêu chí chất lượng cho video.",
        "settings": cur_settings
    }
