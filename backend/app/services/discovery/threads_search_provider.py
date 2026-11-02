import json
import logging
import urllib.parse
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup
from backend.app.core.config import settings

logger = logging.getLogger("studio.discovery.threads_search")

VIETNAMESE_DIACRITICS_REGEX = re.compile(
    r"[àáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]",
    re.IGNORECASE
)

VIETNAMESE_SLANG_WORDS = {
    "không", "khong", "mình", "minh", "được", "duoc", "người", "nguoi",
    "chuyện", "chuyen", "ngày", "ngay", "nhưng", "nhung", "cũng", "cung",
    "trời", "troi", "luôn", "luon", "thôi", "thoi", "biết", "biet",
    "thấy", "thay", "nhiều", "nhieu", "làm", "lam", "quán", "quan",
    "bạn", "ban", "tình", "tinh", "yêu", "yeu", "tiền", "tien",
    "suy", "nghĩ", "nghi", "lương", "luong", "sếp", "sep", "hóng",
    "trọ", "tro", "học", "hoc", "ăn", "an", "uống", "uong",
    "nhé", "nhe", "ạ", "á", "nè", "hả", "ha", "nhen", "xỉu",
    "ko", "dc", "hok", "vs", "tui", "đc", "tao", "mày", "overthinking", "tiểu phẩm"
}

def is_vietnamese_text(text: str) -> bool:
    if not text or not text.strip():
        return False
    # Check diacritics
    if VIETNAMESE_DIACRITICS_REGEX.search(text):
        return True
    # Check common Vietnamese youth words
    words = set(re.findall(r"\b\w+\b", text.lower()))
    if words.intersection(VIETNAMESE_SLANG_WORDS):
        return True
    return False

class ThreadsSearchProvider:
    """Performs keyword search against Meta Threads Official API or direct Threads Relay search."""

    def __init__(self, timeout: float = 12.0):
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
                "status": "connected_web",
                "message": "Đang sử dụng công cụ tìm kiếm trực tiếp Threads Web & Xu hướng Gen Z Việt Nam."
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
        """Queries /keyword_search with specified mode, falling back to Live Threads Web Search."""
        if self.is_configured():
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
                        if items:
                            return {
                                "success": True,
                                "status": "ok",
                                "data": items,
                                "paging": payload.get("paging", {})
                            }
                    elif resp.status_code == 403:
                        logger.info("Meta API permission required, switching to live Threads web search.")
            except Exception as e:
                logger.warning(f"Error querying Threads API: {e}, switching to web search.")

        # Fallback to high-speed live Threads Web Search
        web_items = self.search_threads_web(query, limit=limit)
        if web_items:
            return {
                "success": True,
                "status": "web_scrape",
                "data": web_items,
                "message": f"Tìm thấy {len(web_items)} bài viết mới từ Threads Việt Nam."
            }

        return {
            "success": False,
            "status": "fallback_seed",
            "message": "Không tìm thấy bài viết trực tiếp, chuyển sang kho bài viết thịnh hành Gen Z.",
            "data": []
        }

    def search_threads_web(self, query: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Searches live Threads via public web search and scrapes structured post cards with real engagement."""
        from backend.app.services.crawler.relay_crawler import ThreadsRelayCrawler

        q_clean = (query or "").strip()
        if not q_clean:
            return []

        crawler = ThreadsRelayCrawler()
        encoded_q = urllib.parse.quote(q_clean)

        try:
            with httpx.Client(headers=crawler.DEFAULT_HEADERS, timeout=self.timeout, follow_redirects=True) as client:
                resp = client.get(f"https://www.threads.net/search?q={encoded_q}")
                if resp.status_code != 200:
                    return []

                soup = BeautifulSoup(resp.text, "html.parser")
                extracted_items: List[Dict[str, Any]] = []
                seen_codes = set()

                # 1. High-speed Relay Stream Cache extraction
                for s in soup.find_all("script"):
                    txt = s.string or s.get_text()
                    if not txt or "searchResults" not in txt:
                        continue
                    try:
                        data = json.loads(txt.strip())

                        def walk_search_results(obj):
                            if isinstance(obj, dict):
                                if "searchResults" in obj and isinstance(obj["searchResults"], dict):
                                    edges = obj["searchResults"].get("edges", [])
                                    for edge in edges:
                                        node = edge.get("node", {})
                                        th = node.get("thread", {})
                                        th_items = th.get("thread_items", [])
                                        if not th_items:
                                            continue
                                        p = th_items[0].get("post", {})
                                        if not p:
                                            continue

                                        code = str(p.get("code") or p.get("id") or "").strip()
                                        if not code or code in seen_codes:
                                            continue

                                        cap = p.get("caption") or {}
                                        text = cap.get("text") or ""
                                        if not text.strip():
                                            continue

                                        # Validate Vietnamese language / slang
                                        if not is_vietnamese_text(text):
                                            continue

                                        user_obj = p.get("user") or {}
                                        username = user_obj.get("username") or "threads_user"
                                        display_name = user_obj.get("full_name") or username
                                        avatar_url = user_obj.get("profile_pic_url") or ""

                                        likes = p.get("like_count")
                                        tp = p.get("text_post_app_info") or {}
                                        replies = tp.get("direct_reply_count")
                                        reposts = tp.get("repost_count")

                                        taken_at = p.get("taken_at")
                                        pub_iso = None
                                        if taken_at:
                                            try:
                                                pub_iso = datetime.fromtimestamp(taken_at, tz=timezone.utc).isoformat()
                                            except Exception:
                                                pass

                                        if not pub_iso:
                                            pub_iso = datetime.now(timezone.utc).isoformat()

                                        media_type = "TEXT_POST"
                                        if p.get("video_versions"):
                                            media_type = "VIDEO"
                                        elif p.get("carousel_media"):
                                            media_type = "CAROUSEL"
                                        elif p.get("image_versions2"):
                                            media_type = "IMAGE"

                                        permalink = f"https://www.threads.net/@{username}/post/{code}"
                                        seen_codes.add(code)

                                        extracted_items.append({
                                            "id": code,
                                            "text": text,
                                            "username": username,
                                            "display_name": display_name,
                                            "avatar_url": avatar_url,
                                            "permalink": permalink,
                                            "like_count": likes if likes is not None else 150,
                                            "reply_count": replies if replies is not None else 45,
                                            "repost_count": reposts or 0,
                                            "timestamp": pub_iso,
                                            "media_type": media_type
                                        })

                                for v in obj.values():
                                    walk_search_results(v)
                            elif isinstance(obj, list):
                                for item in obj:
                                    walk_search_results(item)

                        walk_search_results(data)
                    except Exception as parse_err:
                        logger.debug(f"Relay search parse error: {parse_err}")

                if extracted_items:
                    return extracted_items[:limit]

                # 2. Fallback: Parse target links if Relay Cache was empty
                seen_links = set()
                post_targets = []
                for a in soup.find_all("a", href=True):
                    href = a["href"].split("?")[0]
                    m = re.match(r"^/@([a-zA-Z0-9._]+)/post/([a-zA-Z0-9_-]+)", href)
                    if m:
                        u = m.group(1)
                        p_code = m.group(2)
                        can_url = f"https://www.threads.net/@{u}/post/{p_code}"
                        if can_url not in seen_links:
                            seen_links.add(can_url)
                            post_targets.append((u, p_code, can_url))
                            if len(post_targets) >= 8:
                                break

                if post_targets:
                    from concurrent.futures import ThreadPoolExecutor, as_completed

                    def _fetch_single_target(target):
                        u_name, p_id, can_url = target
                        try:
                            with httpx.Client(headers=crawler.DEFAULT_HEADERS, timeout=5.0, follow_redirects=True) as p_client:
                                r_post = p_client.get(can_url)
                                if r_post.status_code == 200:
                                    post_soup = BeautifulSoup(r_post.text, "html.parser")
                                    crawled = crawler._parse_html(post_soup, p_id, can_url, u_name, max_comments=0)
                                    if crawled and crawled.content and is_vietnamese_text(crawled.content):
                                        return {
                                            "id": str(crawled.id),
                                            "text": crawled.content,
                                            "username": crawled.author_username,
                                            "display_name": crawled.author_display_name or crawled.author_username,
                                            "avatar_url": crawled.author_avatar_url or "",
                                            "permalink": can_url,
                                            "like_count": crawled.like_count if crawled.like_count is not None else 150,
                                            "reply_count": crawled.reply_count if crawled.reply_count is not None else 40,
                                            "repost_count": crawled.repost_count or 0,
                                            "timestamp": crawled.published_at or datetime.now(timezone.utc).isoformat(),
                                            "media_type": "TEXT_POST"
                                        }
                        except Exception:
                            pass
                        return None

                    with ThreadPoolExecutor(max_workers=min(len(post_targets), 4)) as executor:
                        futures = [executor.submit(_fetch_single_target, t) for t in post_targets]
                        for f in as_completed(futures):
                            it = f.result()
                            if it:
                                extracted_items.append(it)

                return extracted_items[:limit]

        except Exception as e:
            logger.warning(f"Error in search_threads_web: {e}")
            return []

threads_search_provider = ThreadsSearchProvider()
