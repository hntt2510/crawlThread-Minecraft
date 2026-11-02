from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List

from backend.app.core.database import get_db
from backend.app.models.db_models import Project, ThreadsPost, CommentSelection
from backend.app.services.timeline.timeline_planner import timeline_planner
from backend.app.services.caption.caption_engine import caption_engine, CaptionConfig
from backend.app.services.sfx.sfx_manager import sfx_manager

router = APIRouter(prefix="/timeline", tags=["timeline"])

@router.get("/project/{project_id}/plan")
def get_timeline_plan(
    project_id: str,
    pace: str = Query("balanced"),
    db: Session = Depends(get_db)
):
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
        comments=selections,
        pace=pace
    )

    return {
        "success": True,
        "data": plan.model_dump()
    }

@router.post("/project/{project_id}/reorder")
def reorder_timeline_scenes(
    project_id: str,
    payload: Dict[str, List[str]],  # {"ordered_comment_ids": ["c1", "c2", ...]}
    db: Session = Depends(get_db)
):
    ordered_ids = payload.get("ordered_comment_ids", [])
    if not ordered_ids:
        raise HTTPException(status_code=400, detail="Danh sách ID không hợp lệ.")

    for new_idx, c_id in enumerate(ordered_ids):
        sel = db.query(CommentSelection).filter(
            CommentSelection.project_id == project_id,
            CommentSelection.comment_id == c_id
        ).first()
        if sel:
            sel.sequence_order = new_idx

    db.commit()
    return {"success": True, "message": "Đã cập nhật lại thứ tự phân cảnh timeline."}

@router.get("/sfx/library")
def get_sfx_library():
    """Returns available sound effect library."""
    items = sfx_manager.get_available_sfx()
    return {
        "success": True,
        "items": [it.model_dump() for it in items]
    }
