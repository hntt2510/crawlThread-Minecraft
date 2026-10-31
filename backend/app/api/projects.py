from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.models.db_models import Project, ThreadsPost, CommentSelection
from backend.app.schemas.pydantic_schemas import ProjectCreate, ProjectUpdate, ProjectDetail, ApiResponse

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("", response_model=List[ProjectDetail])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.updated_at.desc()).all()
    return projects

@router.post("", response_model=ProjectDetail)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(
        title=data.title,
        threads_url=data.threads_url,
        status="draft",
        settings={
            "aspect_ratio": "9:16",
            "resolution": "1080x1920",
            "background_volume": 0.2,
            "voice_volume": 1.0,
            "ducking_enabled": True,
            "default_voice": "vi-VN-HoaiMyNeural",
            "default_rate": 1.0,
            "card_theme": "dark"
        }
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")
    return project

@router.patch("/{project_id}", response_model=ProjectDetail)
def update_project(project_id: str, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")
    if data.title:
        project.title = data.title
    if data.settings:
        current_settings = dict(project.settings or {})
        current_settings.update(data.settings)
        project.settings = current_settings
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", response_model=ApiResponse)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án.")
    db.delete(project)
    db.commit()
    return ApiResponse(message="Đã xóa dự án thành công.")
