from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from backend.app.core.database import get_db
from backend.app.models.db_models import Project, ThreadsPost, ThreadsComment, CommentSelection, TTSAsset
from backend.app.schemas.pydantic_schemas import ThreadsCommentSchema, CommentSelectionItem, ApiResponse

router = APIRouter(prefix="/comments", tags=["comments"])

@router.get("/project/{project_id}", response_model=List[ThreadsCommentSchema])
def get_project_comments(project_id: str, db: Session = Depends(get_db)):
    post = db.query(ThreadsPost).filter(ThreadsPost.project_id == project_id).first()
    if not post:
        return []
    comments = db.query(ThreadsComment).filter(ThreadsComment.post_id == post.id).order_by(ThreadsComment.like_count.desc().nullslast()).all()
    return comments

@router.get("/project/{project_id}/selections")
def get_project_selections(project_id: str, db: Session = Depends(get_db)):
    selections = db.query(CommentSelection).filter(
        CommentSelection.project_id == project_id
    ).order_by(CommentSelection.sequence_order.asc()).all()

    result = []
    for s in selections:
        c = s.comment
        result.append({
            "id": s.id,
            "project_id": s.project_id,
            "comment_id": s.comment_id,
            "sequence_order": s.sequence_order,
            "display_text": s.display_text,
            "tts_text": s.tts_text,
            "voice_id": s.voice_id,
            "voice_rate": s.voice_rate,
            "is_active": s.is_active,
            "author_username": c.author_username if c else "unknown",
            "author_display_name": c.author_display_name if c else "User",
            "author_avatar_url": c.author_avatar_url if c else "",
            "like_count": c.like_count if c else 0,
            "reply_count": c.reply_count if c else 0,
            "has_audio": bool(s.tts_asset),
            "audio_duration_ms": s.tts_asset.duration_ms if s.tts_asset else 0,
        })
    return result

@router.post("/project/{project_id}/selections")
def update_selections(project_id: str, items: List[CommentSelectionItem], db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")

    # Remove previous selections and overwrite with updated order and texts
    db.query(CommentSelection).filter(CommentSelection.project_id == project_id).delete()
    db.flush()

    new_selections = []
    for idx, it in enumerate(items):
        sel = CommentSelection(
            project_id=project_id,
            comment_id=it.comment_id,
            sequence_order=idx,
            display_text=it.display_text,
            tts_text=it.tts_text,
            voice_id=it.voice_id or "vi-VN-HoaiMyNeural",
            voice_rate=it.voice_rate or 1.0,
            is_active=it.is_active
        )
        db.add(sel)
        new_selections.append(sel)

    db.commit()
    return {"success": True, "count": len(new_selections)}

@router.post("/project/{project_id}/restore/{comment_id}")
def restore_comment_text(project_id: str, comment_id: str, db: Session = Depends(get_db)):
    original_comment = db.query(ThreadsComment).filter(ThreadsComment.id == comment_id).first()
    if not original_comment:
        raise HTTPException(status_code=404, detail="Không tìm thấy bình luận gốc.")

    selection = db.query(CommentSelection).filter(
        CommentSelection.project_id == project_id,
        CommentSelection.comment_id == comment_id
    ).first()

    if selection:
        selection.display_text = original_comment.content
        selection.tts_text = original_comment.content
        db.commit()

    return {"success": True, "content": original_comment.content}

@router.post("/project/{project_id}/curate")
def auto_curate_comments(
    project_id: str,
    target_count: int = 5,
    mode: str = "balanced",
    auto_apply: bool = False,
    db: Session = Depends(get_db)
):
    from backend.app.services.ai_curation.comment_curator import comment_curator
    post = db.query(ThreadsPost).filter(ThreadsPost.project_id == project_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết gốc của dự án.")
    comments = db.query(ThreadsComment).filter(ThreadsComment.post_id == post.id).all()
    if not comments:
        raise HTTPException(status_code=400, detail="Dự án chưa có bình luận nào để phân tích.")

    curation_res = comment_curator.curate(comments, target_count=target_count, mode=mode)

    if auto_apply and curation_res.curated_comments:
        db.query(CommentSelection).filter(CommentSelection.project_id == project_id).delete()
        db.flush()
        for idx, c in enumerate(curation_res.curated_comments):
            sel = CommentSelection(
                project_id=project_id,
                comment_id=c.comment_id,
                sequence_order=idx,
                display_text=c.display_text,
                tts_text=c.tts_text,
                voice_id="vi-VN-HoaiMyNeural",
                voice_rate=1.0,
                is_active=True
            )
            db.add(sel)
        db.commit()

    return {
        "success": True,
        "data": curation_res.model_dump()
    }
