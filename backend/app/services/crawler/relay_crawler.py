import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Set
import httpx
from bs4 import BeautifulSoup

from backend.app.services.crawler.base import CrawledPost, CrawledComment, parse_threads_url

logger = logging.getLogger("studio.crawler")

class ThreadsRelayCrawler:
    """Crawler that extracts structured Post and Comments directly from Threads Relay Stream Cache."""
    
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
    }

    def __init__(self, timeout: float = 20.0):
        self.timeout = timeout

    def crawl_post_and_comments(self, url: str, max_comments: int = 50) -> CrawledPost:
        url_info = parse_threads_url(url)
        canonical_url = url_info["canonical_url"]
        target_post_id = url_info["post_id"]
        target_username = url_info["username"]

        with httpx.Client(headers=self.DEFAULT_HEADERS, timeout=self.timeout, follow_redirects=True) as client:
            # 1. Initialize session cookies
            try:
                client.get("https://www.threads.net")
            except Exception as e:
                logger.warning(f"Error fetching Threads homepage cookie: {e}")

            # 2. Fetch target post page
            resp = client.get(canonical_url)
            if resp.status_code != 200:
                raise RuntimeError(f"Threads trả về mã lỗi HTTP {resp.status_code} khi tải bài viết.")

        soup = BeautifulSoup(resp.text, "html.parser")
        return self._parse_html(soup, target_post_id, canonical_url, target_username, max_comments)

    def _parse_html(self, soup: BeautifulSoup, target_post_id: str, canonical_url: str, target_username: str, max_comments: int) -> CrawledPost:
        raw_items: List[Dict[str, Any]] = []

        # Find all JSON script tags with data-sjs
        for s in soup.find_all("script"):
            if "data-sjs" not in s.attrs and s.get("type") != "application/json":
                continue
            content = s.string or s.get_text()
            if not content:
                continue
            if "RelayPrefetchedStreamCache" in content or "text_fragments" in content or "containing_thread" in content:
                try:
                    data = json.loads(content.strip())
                    self._walk_and_collect(data, raw_items)
                except Exception:
                    pass

        # Also inspect standard og: tags as fallback for root post
        og_desc = ""
        meta_desc = soup.find("meta", {"property": "og:description"}) or soup.find("meta", {"name": "description"})
        if meta_desc and meta_desc.get("content"):
            og_desc = meta_desc["content"]

        og_title = ""
        meta_title = soup.find("meta", {"property": "og:title"})
        if meta_title and meta_title.get("content"):
            og_title = meta_title["content"]

        # Disambiguate root post vs comments
        root_candidate: Optional[Dict[str, Any]] = None
        comments_list: List[CrawledComment] = []
        seen_pks: Set[str] = set()

        for item in raw_items:
            pk = str(item.get("pk") or item.get("id") or "")
            if not pk or pk in seen_pks:
                continue
            seen_pks.add(pk)

            user = item.get("user") or {}
            username = user.get("username") or ""
            display_name = user.get("full_name") or username
            avatar = user.get("profile_pic_url") or ""

            # Extract text
            text = ""
            if "text_fragments" in item and isinstance(item["text_fragments"], dict):
                frags = item["text_fragments"].get("fragments", [])
                text = "".join(f.get("plaintext", "") for f in frags if isinstance(f, dict))
            elif "caption" in item and isinstance(item["caption"], dict):
                text = item["caption"].get("text", "")
            elif "text" in item and isinstance(item["text"], str):
                text = item["text"]

            text = text.strip()
            like_count = item.get("like_count")
            reply_count = item.get("reply_count")
            taken_at = item.get("taken_at")
            pub_date_str = None
            if taken_at:
                try:
                    pub_date_str = datetime.fromtimestamp(int(taken_at), tz=timezone.utc).isoformat()
                except Exception:
                    pass

            # Determine whether this is root post
            # Root post matches target_post_id (or code), or author is target_username and matches post context
            is_root = False
            code = item.get("code") or ""
            if code and code.lower() == target_post_id.lower():
                is_root = True
            elif target_username and username.lower() == target_username.lower() and not root_candidate:
                is_root = True

            if is_root and not root_candidate:
                root_candidate = {
                    "id": pk or target_post_id,
                    "url": canonical_url,
                    "author_username": username or target_username,
                    "author_display_name": display_name or target_username,
                    "author_avatar_url": avatar,
                    "content": text or og_desc,
                    "like_count": like_count,
                    "reply_count": reply_count,
                    "repost_count": item.get("repost_count"),
                    "published_at": pub_date_str,
                }
            else:
                if text:  # Ignore completely empty comments
                    comments_list.append(CrawledComment(
                        id=pk,
                        parent_comment_id=None,
                        author_username=username,
                        author_display_name=display_name,
                        author_avatar_url=avatar,
                        content=text,
                        like_count=like_count,
                        reply_count=reply_count,
                        nesting_depth=0,
                        published_at=pub_date_str
                    ))

        # Fallback for root post if Relay stream only contained comments
        if not root_candidate:
            root_candidate = {
                "id": target_post_id,
                "url": canonical_url,
                "author_username": target_username or "threads_user",
                "author_display_name": target_username or "Threads Creator",
                "author_avatar_url": "",
                "content": og_desc or og_title or "Threads Post",
                "like_count": None,
                "reply_count": len(comments_list),
                "repost_count": None,
                "published_at": datetime.now(timezone.utc).isoformat(),
            }

        # Apply max_comments limit
        if max_comments and len(comments_list) > max_comments:
            comments_list = comments_list[:max_comments]

        return CrawledPost(
            id=root_candidate["id"],
            url=canonical_url,
            author_username=root_candidate["author_username"],
            author_display_name=root_candidate["author_display_name"],
            author_avatar_url=root_candidate["author_avatar_url"],
            content=root_candidate["content"],
            media_urls=[],
            like_count=root_candidate["like_count"],
            reply_count=root_candidate["reply_count"],
            repost_count=root_candidate["repost_count"],
            published_at=root_candidate["published_at"],
            comments=comments_list
        )

    def _walk_and_collect(self, obj: Any, output: List[Dict[str, Any]], depth: int = 0):
        if depth > 25:
            return
        if isinstance(obj, dict):
            if "post" in obj and isinstance(obj["post"], dict):
                output.append(obj["post"])
            elif "text_fragments" in obj and ("pk" in obj or "id" in obj):
                output.append(obj)
            for v in obj.values():
                self._walk_and_collect(v, output, depth + 1)
        elif isinstance(obj, list):
            for v in obj:
                self._walk_and_collect(v, output, depth + 1)
