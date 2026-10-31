from pathlib import Path
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db, SessionLocal
from backend.app.core.job_manager import job_manager, Job
from backend.app.models.db_models import Project, RenderJob, PublishingJob, PublishingAccount
from backend.app.schemas.pydantic_schemas import PublishingRequest, ApiResponse
from backend.app.services.publishing.publishing_service import publishing_service

router = APIRouter(prefix="/publishing", tags=["publishing"])

@router.get("/accounts")
def list_accounts(db: Session = Depends(get_db)):
    accounts = db.query(PublishingAccount).filter(PublishingAccount.is_active == True).all()
    return accounts

def _execute_publish(job: Job, data: PublishingRequest):
    db: Session = SessionLocal()
    try:
        project_id = data.project_id
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Không tìm thấy dự án {project_id}")

        render = db.query(RenderJob).filter(
            RenderJob.project_id == project_id,
            RenderJob.status == "completed"
        ).order_by(RenderJob.completed_at.desc()).first()

        if not render or not render.video_output_path or not Path(render.video_output_path).exists():
            raise ValueError("Không tìm thấy file video MP4 đã dựng để xuất bản.")

        video_path = Path(render.video_output_path)

        job.update(20, f"Đang kết nối tới các nền tảng ({', '.join(data.platforms)})...")

        results = publishing_service.publish_to_platforms(
            video_path=video_path,
            platforms=data.platforms,
            youtube_meta=data.youtube_metadata or {},
            facebook_meta=data.facebook_metadata or {},
            tiktok_meta=data.tiktok_metadata or {},
        )

        job.update(80, "Đang cập nhật lịch sử xuất bản...")

        for platform, res in results.items():
            pj = PublishingJob(
                project_id=project_id,
                platform=platform,
                status=res.get("status", "completed"),
                video_id=res.get("video_id") or res.get("publish_id"),
                published_url=res.get("video_url"),
                metadata_json=res,
                completed_at=datetime.now(timezone.utc)
            )
            db.add(pj)

        project.status = "published"
        db.commit()

        job.update(100, "Đăng tải video hoàn tất lên các nền tảng đã chọn!")
        return results
    finally:
        db.close()

@router.post("/publish")
def publish_video(data: PublishingRequest):
    if not data.confirm_publish:
        raise HTTPException(
            status_code=400,
            detail="Bắt buộc phải có sự xác nhận của người dùng (confirm_publish = true) trước khi xuất bản."
        )

    job = job_manager.create_job("social_publishing", project_id=data.project_id)
    job_manager.run_in_background(job, _execute_publish, data)
    return {
        "job_id": job.id,
        "status": "pending",
        "message": "Đang bắt đầu xuất bản video lên mạng xã hội..."
    }

@router.get("/jobs/{job_id}")
def get_publish_job(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy tiến trình xuất bản.")
    return job.to_dict()
