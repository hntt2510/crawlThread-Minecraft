import logging
from pathlib import Path
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger("studio.publishing.tiktok")

class TikTokPublisher:
    """Publishes videos to TikTok using TikTok Content Posting API v2 Direct Post protocol."""

    INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"

    def publish_video(
        self,
        video_path: Path,
        access_token: str,
        caption: str,
        privacy_level: str = "PUBLIC_TO_EVERYONE",  # PUBLIC_TO_EVERYONE, MUTUAL_FOLLOW_FRIENDS, SELF_ONLY
        progress_callback: Optional[Any] = None
    ) -> Dict[str, Any]:
        if not video_path.exists():
            raise FileNotFoundError(f"Video file không tồn tại: {video_path}")

        file_size = video_path.stat().st_size

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        }

        body = {
            "post_info": {
                "title": caption[:150],
                "privacy_level": privacy_level,
                "disable_duet": False,
                "disable_stitch": False,
                "disable_comment": False,
                "video_cover_timestamp_ms": 1000
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": file_size,
                "chunk_size": file_size,
                "total_chunk_count": 1
            }
        }

        with httpx.Client(timeout=60.0) as client:
            # 1. Initialize Direct Post
            logger.info("Initializing TikTok Direct Video Post...")
            resp = client.post(self.INIT_URL, headers=headers, json=body)
            if resp.status_code != 200:
                raise RuntimeError(f"TikTok API lỗi khởi tạo ({resp.status_code}): {resp.text}")

            res_json = resp.json()
            data = res_json.get("data", {})
            publish_id = data.get("publish_id")
            upload_url = data.get("upload_url")
            if not upload_url:
                raise RuntimeError(f"TikTok API không trả về upload_url: {res_json}")

            # 2. Upload video binary
            logger.info(f"Uploading video binary to TikTok ({file_size} bytes)...")
            upload_headers = {
                "Content-Type": "video/mp4",
                "Content-Range": f"bytes 0-{file_size - 1}/{file_size}",
                "Content-Length": str(file_size),
            }
            with open(video_path, "rb") as f:
                upload_resp = client.put(upload_url, headers=upload_headers, content=f.read())

            if upload_resp.status_code not in (200, 201):
                raise RuntimeError(f"TikTok API upload video thất bại ({upload_resp.status_code}): {upload_resp.text}")

            return {
                "platform": "tiktok",
                "publish_id": publish_id,
                "status": "processing",
                "message": "Video đã được gửi tới TikTok thành công và đang được xử lý.",
                "raw_response": res_json
            }

tiktok_publisher = TikTokPublisher()
