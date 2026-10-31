import logging
from typing import List, Dict, Any, Optional
import httpx
from backend.app.core.config import settings

logger = logging.getLogger("studio.discovery.threads_search")

class ThreadsSearchProvider:
    """Performs keyword search against Meta Threads Official API."""

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout

    @property
    def access_token(self) -> str:
        return getattr(settings, "THREADS_ACCESS_TOKEN", "")

    @property
    def base_url(self) -> str:
        return getattr(settings, "THREADS_API_BASE_URL", "https://graph.threads.net/v1.0").rstrip("/")

    def is_configured(self) -> bool:
        return bool(self.access_token and self.access_token.strip())

    def check_api_status(self) -> Dict[str, Any]:
        """Validates API token and keyword search capability."""
        if not self.is_configured():
            return {
                "configured": False,
                "status": "missing_credentials",
                "message": "Chưa cấu hình THREADS_ACCESS_TOKEN trong file .env."
            }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(
                    f"{self.base_url}/me",
                    params={"access_token": self.access_token, "fields": "id,username"}
                )
                if resp.status_code == 200:
                    user_data = resp.json()
                    return {
                        "configured": True,
                        "status": "connected",
                        "username": user_data.get("username"),
                        "message": "Kết nối Meta Threads API thành công."
                    }
                elif resp.status_code == 401:
                    return {
                        "configured": True,
                        "status": "invalid_token",
                        "message": "Access Token đã hết hạn hoặc không hợp lệ."
                    }
                elif resp.status_code == 403:
                    return {
                        "configured": True,
                        "status": "permission_required",
                        "message": "Tài khoản thiếu quyền 'threads_keyword_search' (yêu cầu Meta App Review)."
                    }
                else:
                    return {
                        "configured": True,
                        "status": "error",
                        "message": f"Meta Threads API phản hồi HTTP {resp.status_code}."
                    }
        except Exception as e:
            return {
                "configured": True,
                "status": "network_error",
                "message": f"Không thể kết nối tới Meta Threads API: {str(e)}"
            }

    def search_keyword(
        self,
        query: str,
        search_type: str = "TOP",  # "TOP" or "RECENT"
        limit: int = 25,
        media_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Queries /keyword_search with specified mode and filters."""
        if not self.is_configured():
            return {
                "success": False,
                "status": "missing_credentials",
                "message": "THREADS_ACCESS_TOKEN chưa được cấu hình.",
                "data": []
            }

        params: Dict[str, Any] = {
            "q": query,
            "search_type": search_type.upper(),
            "limit": min(limit, 50),
            "access_token": self.access_token,
            "fields": "id,text,username,permalink,timestamp,media_type,like_count,reply_count,repost_count"
        }
        if media_type and media_type != "ALL":
            params["media_type"] = media_type

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(f"{self.base_url}/keyword_search", params=params)

                if resp.status_code == 200:
                    payload = resp.json()
                    items = payload.get("data", [])
                    return {
                        "success": True,
                        "status": "ok",
                        "data": items,
                        "paging": payload.get("paging", {})
                    }
                elif resp.status_code == 403:
                    logger.warning("Meta Threads API 403: Missing threads_keyword_search permission.")
                    return {
                        "success": False,
                        "status": "permission_required",
                        "message": "Cần quyền 'threads_keyword_search' được phê duyệt qua Meta App Review để tìm kiếm bài viết công khai.",
                        "data": []
                    }
                elif resp.status_code == 429:
                    logger.warning("Meta Threads API 429: Rate limit hit.")
                    return {
                        "success": False,
                        "status": "rate_limited",
                        "message": "Đã đạt giới hạn tần suất yêu cầu Meta Threads API (Rate Limit 429).",
                        "data": []
                    }
                else:
                    return {
                        "success": False,
                        "status": f"http_{resp.status_code}",
                        "message": f"Lỗi Meta Threads API (HTTP {resp.status_code}): {resp.text[:120]}",
                        "data": []
                    }
        except Exception as e:
            logger.error(f"Error querying Threads /keyword_search: {e}")
            return {
                "success": False,
                "status": "network_error",
                "message": str(e),
                "data": []
            }

threads_search_provider = ThreadsSearchProvider()
