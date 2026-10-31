import logging
from typing import Optional, List, Dict, Any, Tuple
import httpx
from backend.app.core.config import settings
from backend.app.services.crawler.base import CrawledPost, CrawledComment, CrawlQualityReport
from backend.app.services.crawler.comment_parser import RawCommentCandidate, comment_parser

logger = logging.getLogger("studio.crawler.official")

class ThreadsConversationProvider:
    """Retrieves post and conversation comments using official Meta Threads API."""

    def __init__(self, access_token: Optional[str] = None, base_url: Optional[str] = None, timeout: float = 20.0):
        self.access_token = access_token or getattr(settings, "THREADS_ACCESS_TOKEN", "")
        self.base_url = (base_url or getattr(settings, "THREADS_API_BASE_URL", "https://graph.threads.net/v1.0")).rstrip("/")
        self.timeout = timeout

    def is_configured(self) -> bool:
        return bool(self.access_token and self.access_token.strip())

    def get_connection_status(self) -> Dict[str, Any]:
        """Checks if Meta Threads API token is present and tests token validity."""
        if not self.is_configured():
            return {
                "configured": False,
                "status": "missing_token",
                "message": "Chưa cấu hình THREADS_ACCESS_TOKEN trong file .env."
            }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(
                    f"{self.base_url}/me",
                    params={"access_token": self.access_token, "fields": "id,username,threads_profile_picture_url"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "configured": True,
                        "status": "connected",
                        "username": data.get("username"),
                        "user_id": data.get("id"),
                        "message": "Kết nối Meta Threads API thành công."
                    }
                elif resp.status_code == 401:
                    return {
                        "configured": True,
                        "status": "invalid_token",
                        "message": "Token Meta Threads đã hết hạn hoặc không hợp lệ."
                    }
                elif resp.status_code == 403:
                    return {
                        "configured": True,
                        "status": "permission_denied",
                        "message": "Token thiếu quyền truy cập (yêu cầu Meta App Review)."
                    }
                else:
                    return {
                        "configured": True,
                        "status": "error",
                        "message": f"Meta Threads API phản hồi HTTP {resp.status_code}: {resp.text[:100]}"
                    }
        except Exception as e:
            logger.warning(f"Error checking Threads API status: {e}")
            return {
                "configured": True,
                "status": "network_error",
                "message": f"Không thể kết nối tới Meta Threads API: {str(e)}"
            }

    def fetch_conversation(self, media_id: str, max_comments: int = 50) -> CrawledPost:
        """Retrieves root post and its conversation tree via official endpoints."""
        if not self.is_configured():
            raise RuntimeError("THREADS_ACCESS_TOKEN chưa được cấu hình.")

        with httpx.Client(timeout=self.timeout) as client:
            # 1. Fetch Root Post
            post_fields = "id,media_type,text,permalink,timestamp,username,like_count,reply_count,repost_count,quotes_count,views"
            p_resp = client.get(
                f"{self.base_url}/{media_id}",
                params={"access_token": self.access_token, "fields": post_fields}
            )
            if p_resp.status_code != 200:
                raise RuntimeError(f"Lỗi khi tải bài viết từ Threads API (HTTP {p_resp.status_code}): {p_resp.text}")

            p_data = p_resp.json()
            post_id = p_data.get("id", media_id)
            permalink = p_data.get("permalink", f"https://www.threads.net/t/{post_id}")
            author_username = p_data.get("username", "threads_user")
            content = p_data.get("text", "")
            like_count = p_data.get("like_count")
            reply_count = p_data.get("reply_count")
            repost_count = p_data.get("repost_count")
            pub_date = p_data.get("timestamp")

            # 2. Fetch Conversation / Replies
            # Supported endpoints: /{media_id}/conversation or /{media_id}/replies
            reply_fields = "id,text,username,timestamp,permalink,is_reply,root_post,replied_to,has_replies,media_type,like_count,reply_count"
            replies_url = f"{self.base_url}/{media_id}/conversation"
            r_resp = client.get(
                replies_url,
                params={"access_token": self.access_token, "fields": reply_fields, "limit": min(max_comments, 100)}
            )
            if r_resp.status_code == 404:
                # Try fallback endpoint /{media_id}/replies
                replies_url = f"{self.base_url}/{media_id}/replies"
                r_resp = client.get(
                    replies_url,
                    params={"access_token": self.access_token, "fields": reply_fields, "limit": min(max_comments, 100)}
                )

            candidates: List[RawCommentCandidate] = []
            if r_resp.status_code == 200:
                r_json = r_resp.json()
                raw_items = r_json.get("data", [])

                for item in raw_items:
                    c_id = item.get("id")
                    if not c_id:
                        continue

                    # Extract parent reference
                    replied_to = item.get("replied_to") or {}
                    parent_id = replied_to.get("id")
                    root_post = item.get("root_post") or {}
                    cand_root_id = root_post.get("id") or post_id

                    reply_level = 1 if (parent_id == post_id or not parent_id) else 2

                    candidates.append(RawCommentCandidate(
                        id=c_id,
                        content=item.get("text", ""),
                        author_username=item.get("username", ""),
                        root_post_id=cand_root_id,
                        parent_id=parent_id,
                        like_count=item.get("like_count"),
                        reply_count=item.get("reply_count"),
                        published_at=item.get("timestamp"),
                        reply_level=reply_level
                    ))

            # 3. Validate and parse through CommentParser
            comments, quality_report = comment_parser.parse_conversation(
                target_root_id=post_id,
                target_root_code=None,
                candidates=candidates,
                expected_reply_count=reply_count,
                data_source="threads_official_api"
            )

            if max_comments and len(comments) > max_comments:
                comments = comments[:max_comments]

            return CrawledPost(
                id=post_id,
                url=permalink,
                author_username=author_username,
                author_display_name=author_username,
                author_avatar_url="",
                content=content,
                media_urls=[],
                like_count=like_count,
                reply_count=reply_count,
                repost_count=repost_count,
                published_at=pub_date,
                comments=comments,
                quality_report=quality_report
            )

threads_conversation_provider = ThreadsConversationProvider()
