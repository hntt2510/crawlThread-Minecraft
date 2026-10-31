import logging
from pathlib import Path
from typing import Dict, Any, List
from backend.app.services.publishing.youtube_adapter import youtube_publisher
from backend.app.services.publishing.facebook_adapter import facebook_publisher
from backend.app.services.publishing.tiktok_adapter import tiktok_publisher

logger = logging.getLogger("studio.publishing.service")

class PublishingService:
    def publish_to_platforms(
        self,
        video_path: Path,
        platforms: List[str],
        youtube_meta: Dict[str, Any],
        facebook_meta: Dict[str, Any],
        tiktok_meta: Dict[str, Any],
        progress_callback: Any = None
    ) -> Dict[str, Any]:
        results = {}

        if "youtube" in platforms:
            token = youtube_meta.get("access_token")
            if not token:
                raise ValueError("YouTube Access Token chưa được cung cấp.")
            res = youtube_publisher.publish_short(
                video_path=video_path,
                title=youtube_meta.get("title", "Video Threads"),
                description=youtube_meta.get("description", ""),
                access_token=token,
                privacy=youtube_meta.get("privacy", "public")
            )
            results["youtube"] = res

        if "facebook" in platforms:
            page_id = facebook_meta.get("page_id")
            token = facebook_meta.get("page_access_token")
            if not page_id or not token:
                raise ValueError("Facebook Page ID hoặc Page Access Token chưa được cung cấp.")
            res = facebook_publisher.publish_reel(
                video_path=video_path,
                page_id=page_id,
                page_access_token=token,
                description=facebook_meta.get("description", "")
            )
            results["facebook"] = res

        if "tiktok" in platforms:
            token = tiktok_meta.get("access_token")
            if not token:
                raise ValueError("TikTok Access Token chưa được cung cấp.")
            res = tiktok_publisher.publish_video(
                video_path=video_path,
                access_token=token,
                caption=tiktok_meta.get("caption", "Video Threads #trending"),
                privacy_level=tiktok_meta.get("privacy", "PUBLIC_TO_EVERYONE")
            )
            results["tiktok"] = res

        return results

publishing_service = PublishingService()
