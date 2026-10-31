import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    threads_url = Column(Text, nullable=False)
    status = Column(String(50), default="draft", nullable=False)  # draft, crawled, ready_render, rendered, published
    settings = Column(JSON, default=dict)  # video_bg_id, bg_volume, voice_volume, ducking, font_size, etc.
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    post = relationship("ThreadsPost", back_populates="project", uselist=False, cascade="all, delete-orphan")
    selections = relationship("CommentSelection", back_populates="project", cascade="all, delete-orphan", order_by="CommentSelection.sequence_order")
    render_jobs = relationship("RenderJob", back_populates="project", cascade="all, delete-orphan")
    capcut_exports = relationship("CapCutProject", back_populates="project", cascade="all, delete-orphan")
    publishing_jobs = relationship("PublishingJob", back_populates="project", cascade="all, delete-orphan")

class ThreadsPost(Base):
    __tablename__ = "threads_posts"

    id = Column(String(64), primary_key=True)  # Threads post PK
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False)
    url = Column(Text, nullable=False)
    author_username = Column(String(128), nullable=False)
    author_display_name = Column(String(255), default="")
    author_avatar_url = Column(Text, default="")
    content = Column(Text, default="")
    media_urls = Column(JSON, default=list)
    like_count = Column(Integer, nullable=True)
    reply_count = Column(Integer, nullable=True)
    repost_count = Column(Integer, nullable=True)
    published_at = Column(DateTime, nullable=True)
    crawled_at = Column(DateTime, default=utc_now, nullable=False)

    project = relationship("Project", back_populates="post")
    comments = relationship("ThreadsComment", back_populates="post", cascade="all, delete-orphan")

class ThreadsComment(Base):
    __tablename__ = "threads_comments"

    id = Column(String(64), primary_key=True)  # Threads comment PK
    post_id = Column(String(64), ForeignKey("threads_posts.id", ondelete="CASCADE"), nullable=False)
    parent_comment_id = Column(String(64), ForeignKey("threads_comments.id", ondelete="CASCADE"), nullable=True)
    author_username = Column(String(128), nullable=False)
    author_display_name = Column(String(255), default="")
    author_avatar_url = Column(Text, default="")
    content = Column(Text, default="")
    like_count = Column(Integer, nullable=True)
    reply_count = Column(Integer, nullable=True)
    nesting_depth = Column(Integer, default=0, nullable=False)
    published_at = Column(DateTime, nullable=True)
    crawled_at = Column(DateTime, default=utc_now, nullable=False)

    post = relationship("ThreadsPost", back_populates="comments")
    replies = relationship("ThreadsComment", backref="parent", remote_side=[id])

class CommentSelection(Base):
    __tablename__ = "comment_selections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    comment_id = Column(String(64), ForeignKey("threads_comments.id", ondelete="CASCADE"), nullable=False)
    sequence_order = Column(Integer, default=0, nullable=False)
    display_text = Column(Text, nullable=False)
    tts_text = Column(Text, nullable=False)
    voice_id = Column(String(100), nullable=True)
    voice_rate = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    project = relationship("Project", back_populates="selections")
    comment = relationship("ThreadsComment")
    tts_asset = relationship("TTSAsset", back_populates="selection", uselist=False, cascade="all, delete-orphan")

class TTSAsset(Base):
    __tablename__ = "tts_assets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    selection_id = Column(String(36), ForeignKey("comment_selections.id", ondelete="CASCADE"), unique=True, nullable=False)
    provider = Column(String(50), nullable=False)  # edge_tts, fpt_ai, google_tts
    voice = Column(String(100), nullable=False)
    audio_path = Column(Text, nullable=False)
    duration_ms = Column(Integer, default=0, nullable=False)
    file_size_bytes = Column(Integer, default=0, nullable=False)
    content_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    selection = relationship("CommentSelection", back_populates="tts_asset")

class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    type = Column(String(50), nullable=False)  # background_video, background_music, watermark
    name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    duration_ms = Column(Integer, default=0)
    width = Column(Integer, default=0)
    height = Column(Integer, default=0)
    file_size_bytes = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now, nullable=False)

class RenderJob(Base):
    __tablename__ = "render_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    progress = Column(Integer, default=0, nullable=False)  # 0 to 100
    error_message = Column(Text, nullable=True)
    video_output_path = Column(Text, nullable=True)
    duration_sec = Column(Float, default=0.0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="render_jobs")

class CapCutProject(Base):
    __tablename__ = "capcut_projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    draft_name = Column(String(255), nullable=False)
    draft_path = Column(Text, nullable=False)
    package_zip_path = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    project = relationship("Project", back_populates="capcut_exports")

class PublishingAccount(Base):
    __tablename__ = "publishing_accounts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    platform = Column(String(50), nullable=False)  # youtube, facebook, tiktok
    account_name = Column(String(255), nullable=False)
    account_id = Column(String(255), nullable=False)
    credentials_json = Column(Text, nullable=True)  # encrypted/safe token store
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

class PublishingJob(Base):
    __tablename__ = "publishing_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, uploading, processing, completed, failed
    progress = Column(Integer, default=0)
    video_id = Column(String(255), nullable=True)
    published_url = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="publishing_jobs")
