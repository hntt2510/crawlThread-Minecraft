import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger("studio.publishing.youtube")

class YouTubePublisher:
    """Publishes videos to YouTube Shorts using YouTube Data API v3 Resumable Upload protocol."""

    UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"

    def publish_short(
        self,
        video_path: Path,
        title: str,
        description: str,
        access_token: str,
        tags: Optional[list[str]] = None,
        privacy: str = "public",  # public, private, unlisted
        progress_callback: Optional[Any] = None
    ) -> Dict[str, Any]:
        if not video_path.exists():
            raise FileNotFoundError(f"Video file không tồn tại: {video_path}")

        file_size = video_path.stat().st_size
        clean_title = f"{title[:90]} #Shorts" if "#Shorts" not in title else title[:100]

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Type": "video/mp4",
            "X-Upload-Content-Length": str(file_size),
        }

        body = {
            "snippet": {
                "title": clean_title,
                "description": f"{description}\n\n#Shorts #Threads",
                "tags": tags or ["Shorts", "Threads", "Vietnamese"],
                "categoryId": "22",  # People & Blogs
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False,
            }
        }

        with httpx.Client(timeout=60.0) as client:
            # 1. Initiate resumable upload session
            logger.info("Initiating YouTube resumable upload session...")
            init_resp = client.post(self.UPLOAD_URL, headers=headers, json=body)
            if init_resp.status_code != 200:
                raise RuntimeError(f"YouTube API lỗi khởi tạo upload ({init_resp.status_code}): {init_resp.text}")

            session_url = init_resp.headers.get("Location")
            if not session_url:
                raise RuntimeError("YouTube API không trả về Resumable Upload Location header.")

            # 2. Upload video file chunks
            logger.info(f"Uploading {file_size} bytes to YouTube session URL...")
            with open(video_path, "rb") as f:
                upload_headers = {
                    "Content-Type": "video/mp4",
                    "Content-Length": str(file_size),
                }
                upload_resp = client.put(session_url, headers=upload_headers, content=f.read())

            if upload_resp.status_code not in (200, 201):
                raise RuntimeError(f"YouTube API tải video thất bại ({upload_resp.status_code}): {upload_resp.text}")

            res_data = upload_resp.json()
            video_id = res_data.get("id")
            video_url = f"https://www.youtube.com/shorts/{video_id}"

            return {
                "platform": "youtube",
                "video_id": video_id,
                "video_url": video_url,
                "status": "success",
                "raw_response": res_data
            }

youtube_publisher = YouTubePublisher()
