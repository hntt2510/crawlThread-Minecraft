import logging
from pathlib import Path
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger("studio.publishing.facebook")

class FacebookReelsPublisher:
    """Publishes videos to Facebook Fanpage Reels using Meta Graph API v19+ chunked Reels protocol."""

    GRAPH_BASE = "https://graph.facebook.com/v19.0"

    def publish_reel(
        self,
        video_path: Path,
        page_id: str,
        page_access_token: str,
        description: str,
        progress_callback: Optional[Any] = None
    ) -> Dict[str, Any]:
        if not video_path.exists():
            raise FileNotFoundError(f"Video file không tồn tại: {video_path}")

        file_size = video_path.stat().st_size

        with httpx.Client(timeout=60.0) as client:
            # 1. Initialize Reel upload session
            logger.info(f"Initializing Facebook Reel upload for Page ID: {page_id}...")
            init_url = f"{self.GRAPH_BASE}/{page_id}/video_reels"
            init_params = {
                "upload_phase": "start",
                "access_token": page_access_token
            }
            init_resp = client.post(init_url, params=init_params)
            if init_resp.status_code != 200:
                raise RuntimeError(f"Meta Graph API lỗi khởi tạo Reel ({init_resp.status_code}): {init_resp.text}")

            init_data = init_resp.json()
            video_id = init_data.get("video_id")
            upload_url = init_data.get("upload_url")
            if not video_id or not upload_url:
                raise RuntimeError(f"Meta API không trả về video_id hoặc upload_url: {init_data}")

            # 2. Upload video binary
            logger.info(f"Uploading Reel binary ({file_size} bytes)...")
            upload_headers = {
                "Authorization": f"OAuth {page_access_token}",
                "offset": "0",
                "file_size": str(file_size),
                "Content-Type": "application/octet-stream"
            }
            with open(video_path, "rb") as f:
                upload_resp = client.post(upload_url, headers=upload_headers, content=f.read())
            
            if upload_resp.status_code != 200:
                raise RuntimeError(f"Meta API lỗi truyền tải dữ liệu video ({upload_resp.status_code}): {upload_resp.text}")

            # 3. Finish and publish Reel
            logger.info("Finalizing and publishing Facebook Reel...")
            finish_params = {
                "upload_phase": "finish",
                "access_token": page_access_token,
                "video_id": video_id,
                "video_state": "PUBLISHED",
                "description": description,
            }
            finish_resp = client.post(init_url, params=finish_params)
            if finish_resp.status_code != 200:
                raise RuntimeError(f"Meta API lỗi hoàn tất xuất bản Reel ({finish_resp.status_code}): {finish_resp.text}")

            finish_data = finish_resp.json()
            reel_url = f"https://www.facebook.com/reel/{video_id}"

            return {
                "platform": "facebook",
                "video_id": video_id,
                "video_url": reel_url,
                "status": "success",
                "raw_response": finish_data
            }

facebook_publisher = FacebookReelsPublisher()
