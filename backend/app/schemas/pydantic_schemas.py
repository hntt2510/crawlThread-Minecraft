from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# Base & Shared
class ApiResponse(BaseModel):
    success: bool = True
    message: str = "Success"
    data: Optional[Any] = None

# Project Schemas
class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    threads_url: str = Field(...)

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class ThreadsPostSchema(BaseModel):
    id: str
    url: str
    author_username: str
    author_display_name: Optional[str] = ""
    author_avatar_url: Optional[str] = ""
    content: str
    media_urls: List[str] = []
    like_count: Optional[int] = None
    reply_count: Optional[int] = None
    repost_count: Optional[int] = None
    published_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ThreadsCommentSchema(BaseModel):
    id: str
    post_id: str
    parent_comment_id: Optional[str] = None
    author_username: str
    author_display_name: Optional[str] = ""
    author_avatar_url: Optional[str] = ""
    content: str
    like_count: Optional[int] = None
    reply_count: Optional[int] = None
    nesting_depth: int = 0
    published_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class CommentSelectionItem(BaseModel):
    comment_id: str
    sequence_order: int
    display_text: str
    tts_text: str
    voice_id: Optional[str] = None
    voice_rate: Optional[float] = 1.0
    is_active: bool = True

class CommentSelectionSchema(CommentSelectionItem):
    id: str
    project_id: str
    audio_path: Optional[str] = None
    audio_duration_ms: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class ProjectDetail(BaseModel):
    id: str
    title: str
    threads_url: str
    status: str
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    post: Optional[ThreadsPostSchema] = None
    selections: List[CommentSelectionSchema] = []

    model_config = ConfigDict(from_attributes=True)

# Crawl Schemas
class CrawlRequest(BaseModel):
    project_id: Optional[str] = None
    threads_url: str
    max_comments: int = 50

class CrawlJobResponse(BaseModel):
    job_id: str
    status: str
    total_comments: int = 0
    total_replies: int = 0
    message: str = ""

# TTS Schemas
class VoiceInfo(BaseModel):
    id: str
    name: str
    provider: str
    gender: str
    accent: str
    preview_url: Optional[str] = None

class TTSPreviewRequest(BaseModel):
    provider: str = "edge_tts"
    voice: str = "vi-VN-HoaiMyNeural"
    text: str = "Xin chào! Đây là bản nghe thử giọng đọc tiếng Việt."
    rate: float = 1.0

class TTSGenerateRequest(BaseModel):
    project_id: str
    default_voice: str = "vi-VN-HoaiMyNeural"
    default_rate: float = 1.0

# Render Schemas
class RenderRequest(BaseModel):
    project_id: str
    background_asset_id: Optional[str] = None
    background_start_sec: float = 0.0
    background_volume: float = 0.2
    voice_volume: float = 1.0
    ducking_enabled: bool = True
    aspect_ratio: str = "9:16"
    card_theme: str = "dark"

class CapCutExportRequest(BaseModel):
    project_id: str
    install_to_local: bool = True

# Publishing Schemas
class PublishingRequest(BaseModel):
    project_id: str
    platforms: List[str]  # ["youtube", "facebook", "tiktok"]
    youtube_metadata: Optional[Dict[str, Any]] = None
    facebook_metadata: Optional[Dict[str, Any]] = None
    tiktok_metadata: Optional[Dict[str, Any]] = None
    confirm_publish: bool = Field(..., description="Must explicitly confirm publish")
