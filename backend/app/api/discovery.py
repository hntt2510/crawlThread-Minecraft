from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from backend.app.schemas.pydantic_schemas import ApiResponse
from backend.app.services.discovery.discovery_service import discovery_service, DiscoveryResult
from backend.app.services.discovery.trend_topic_provider import TrendingTopic
from backend.app.services.discovery.seed_catalog import vietnam_topic_seed_provider

router = APIRouter(prefix="/discovery", tags=["discovery"])

class DiscoverySearchRequest(BaseModel):
    keyword: Optional[str] = None
    category: Optional[str] = None
    search_type: str = Field(default="BOTH", description="TOP, RECENT, or BOTH")
    media_type: str = Field(default="ALL", description="ALL, TEXT_POST, IMAGE, VIDEO, CAROUSEL")
    time_window: str = Field(default="7d", description="24h, 3d, 7d, all")
    limit: int = Field(default=30, ge=1, le=100)

@router.post("/search")
def search_discovery(req: DiscoverySearchRequest):
    """Searches and discovers trending Threads posts in Vietnam."""
    try:
        res: DiscoveryResult = discovery_service.search_trending(
            keyword=req.keyword,
            category=req.category,
            search_type=req.search_type,
            media_type=req.media_type,
            time_window=req.time_window,
            limit=req.limit
        )
        return ApiResponse(success=True, data=res.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tìm kiếm khám phá Threads: {str(e)}")

@router.get("/topics")
def get_topics(category: Optional[str] = None, force_refresh: bool = False):
    """Returns discovered trending topics across Vietnam and catalog seeds."""
    try:
        topics = discovery_service.get_topics(category=category, force_refresh=force_refresh)
        return ApiResponse(success=True, data=[t.model_dump() for t in topics])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy danh sách chủ đề: {str(e)}")

@router.get("/categories")
def get_categories():
    """Returns available Vietnamese content categories."""
    cats = vietnam_topic_seed_provider.get_categories()
    return ApiResponse(success=True, data=cats)

@router.get("/status")
def get_discovery_status():
    """Returns Meta Threads API connection status and permission validation."""
    status = discovery_service.get_api_status()
    return ApiResponse(success=True, data=status)
