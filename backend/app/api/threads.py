from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.core.database import get_db, SessionLocal
from backend.app.core.job_manager import job_manager, Job
from backend.app.models.db_models import Project, ThreadsPost, ThreadsComment, CommentSelection
from backend.app.schemas.pydantic_schemas import CrawlRequest, ApiResponse
from backend.app.services.crawler.service import crawler_service

router = APIRouter(prefix="/threads", tags=["threads"])

def _execute_crawl(job: Job, project_id: str, threads_url: str, max_comments: int):
    db: Session = SessionLocal()
    try:
        job.update(15, "Đang kết nối tới Threads và giải mã Relay cache...")
        crawled_post = crawler_service.crawl(threads_url, max_comments=max_comments)

        job.update(60, f"Đã trích xuất bài viết và {len(crawled_post.comments)} bình luận. Đang lưu vào cơ sở dữ liệu...")

        # Find or create project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Không tìm thấy dự án {project_id}")

        # Remove previous crawled post for this project if re-crawling
        db.query(ThreadsPost).filter(ThreadsPost.project_id == project_id).delete()
        db.flush()

        post_record = ThreadsPost(
            id=crawled_post.id,
            project_id=project_id,
            url=crawled_post.url,
            author_username=crawled_post.author_username,
            author_display_name=crawled_post.author_display_name,
            author_avatar_url=crawled_post.author_avatar_url,
            content=crawled_post.content,
            media_urls=crawled_post.media_urls,
            like_count=crawled_post.like_count,
            reply_count=crawled_post.reply_count,
            repost_count=crawled_post.repost_count,
            published_at=datetime.fromisoformat(crawled_post.published_at) if crawled_post.published_at else None
        )
        db.add(post_record)
        db.flush()

        # Save comments
        # Clear existing selections
        db.query(CommentSelection).filter(CommentSelection.project_id == project_id).delete()
        db.flush()

        saved_comments = []
        for c in crawled_post.comments:
            comment_record = ThreadsComment(
                id=c.id,
                post_id=post_record.id,
                parent_comment_id=c.parent_comment_id,
                author_username=c.author_username,
                author_display_name=c.author_display_name,
                author_avatar_url=c.author_avatar_url,
                content=c.content,
                like_count=c.like_count,
                reply_count=c.reply_count,
                nesting_depth=c.nesting_depth,
                published_at=datetime.fromisoformat(c.published_at) if c.published_at else None
            )
            db.merge(comment_record)
            saved_comments.append(comment_record)

        db.flush()

        # By default, select top 5 comments by likes (or first 5) for video creation
        sorted_comments = sorted(saved_comments, key=lambda x: (x.like_count or 0), reverse=True)
        top_selections = sorted_comments[:min(5, len(sorted_comments))]

        for idx, sc in enumerate(top_selections):
            selection = CommentSelection(
                project_id=project_id,
                comment_id=sc.id,
                sequence_order=idx,
                display_text=sc.content,
                tts_text=sc.content,
                voice_id="vi-VN-HoaiMyNeural",
                voice_rate=1.0,
                is_active=True
            )
            db.add(selection)

        project.status = "crawled"
        report_dict = crawled_post.quality_report.model_dump() if crawled_post.quality_report else None
        curr_settings = dict(project.settings or {})
        curr_settings["quality_report"] = report_dict
        project.settings = curr_settings

        db.commit()

        job.update(100, f"Thu thập thành công {len(saved_comments)} bình luận!")
        return {
            "post_id": post_record.id,
            "author": post_record.author_username,
            "total_comments": len(saved_comments),
            "selected_count": len(top_selections),
            "quality_report": report_dict
        }

    finally:
        db.close()

@router.post("/crawl")
def start_crawl(data: CrawlRequest, db: Session = Depends(get_db)):
    # If no project_id, create project automatically
    project_id = data.project_id
    if not project_id:
        new_project = Project(
            title="Dự án Threads mới",
            threads_url=data.threads_url,
            status="draft"
        )
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        project_id = new_project.id

    job = job_manager.create_job("threads_crawl", project_id=project_id)
    job_manager.run_in_background(job, _execute_crawl, project_id, data.threads_url, data.max_comments)

    return {
        "job_id": job.id,
        "project_id": project_id,
        "status": "pending",
        "message": "Đang bắt đầu cào bài viết và bình luận..."
    }

@router.get("/crawl/{job_id}")
def get_crawl_status(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy tiến trình cào dữ liệu.")
    return job.to_dict()
