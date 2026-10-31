from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.database import get_db, SessionLocal
from backend.app.models.db_models import Project, CommentSelection, MediaAsset, CapCutProject
from backend.app.schemas.pydantic_schemas import CapCutExportRequest
from backend.app.services.video_composer.ffmpeg_composer import VideoScene
from backend.app.services.capcut_exporter.builder import capcut_exporter

router = APIRouter(prefix="/capcut", tags=["capcut"])

@router.post("/export")
def export_capcut(data: CapCutExportRequest, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")

    project_dir = settings.DATA_DIR / "projects" / data.project_id
    cards_dir = project_dir / "cards"

    if not cards_dir.exists():
        raise HTTPException(status_code=400, detail="Vui lòng bấm 'Dựng Video' hoặc tạo hình ảnh thẻ trước khi xuất dự án CapCut.")

    # Reconstruct scenes from project cards and audio
    scenes: list[VideoScene] = []
    
    # 1. Post card
    post_card = cards_dir / "root_post_card.png"
    if post_card.exists():
        # Check audio
        scenes.append(VideoScene(
            card_image_path=post_card,
            audio_path=None,
            duration_sec=3.5
        ))

    # 2. Comment cards
    selections = db.query(CommentSelection).filter(
        CommentSelection.project_id == data.project_id,
        CommentSelection.is_active == True
    ).order_by(CommentSelection.sequence_order.asc()).all()

    for idx, sel in enumerate(selections):
        card_p = cards_dir / f"comment_card_{idx}.png"
        audio_p = Path(sel.tts_asset.audio_path) if sel.tts_asset and Path(sel.tts_asset.audio_path).exists() else None
        dur_sec = max(2.0, (sel.tts_asset.duration_ms / 1000.0) + 0.6) if sel.tts_asset else 3.0

        if card_p.exists():
            scenes.append(VideoScene(
                card_image_path=card_p,
                audio_path=audio_p,
                duration_sec=dur_sec
            ))

    if not scenes:
        raise HTTPException(status_code=400, detail="Không tìm thấy dữ liệu phân cảnh hợp lệ để xuất sang CapCut.")

    # Run CapCut exporter
    res = capcut_exporter.export_project(
        project_name=project.title,
        scenes=scenes,
        install_to_local=data.install_to_local
    )

    # Save to database
    capcut_record = CapCutProject(
        project_id=data.project_id,
        draft_name=res.draft_name,
        draft_path=str(res.draft_dir),
        package_zip_path=str(res.package_zip_path) if res.package_zip_path else None
    )
    db.add(capcut_record)
    db.commit()

    return {
        "success": True,
        "draft_name": res.draft_name,
        "draft_dir": str(res.draft_dir),
        "installed_to_capcut": res.installed_to_capcut,
        "package_zip_path": str(res.package_zip_path) if res.package_zip_path else None,
        "message": "Đã xuất dự án CapCut Desktop thành công với đầy đủ các track riêng biệt!"
    }

@router.get("/download/{project_id}")
def download_capcut_package(project_id: str, db: Session = Depends(get_db)):
    record = db.query(CapCutProject).filter(CapCutProject.project_id == project_id).order_by(CapCutProject.created_at.desc()).first()
    if not record or not record.package_zip_path or not Path(record.package_zip_path).exists():
        raise HTTPException(status_code=404, detail="Gói CapCut ZIP chưa được tạo.")

    return FileResponse(
        record.package_zip_path,
        media_type="application/zip",
        filename=Path(record.package_zip_path).name
    )
