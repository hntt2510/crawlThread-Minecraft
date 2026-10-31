import re
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict

class CrawlQualityReport(BaseModel):
    original_post_id: str
    expected_reply_count: Optional[int] = None
    retrieved_comment_count: int = 0
    retrieved_reply_count: int = 0
    duplicate_count: int = 0
    rejected_record_count: int = 0
    unresolved_relationship_count: int = 0
    data_source: str = "relay_cache"  # "threads_official_api" or "relay_cache"
    crawl_status: str = "success"     # "success", "partial", "error"
    completeness_warnings: List[str] = []

    model_config = ConfigDict(from_attributes=True)

class CrawledComment(BaseModel):
    id: str
    parent_comment_id: Optional[str] = None
    parent_author_username: Optional[str] = None
    author_username: str
    author_display_name: str = ""
    author_avatar_url: str = ""
    content: str
    like_count: Optional[int] = None
    reply_count: Optional[int] = None
    nesting_depth: int = 0
    published_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class CrawledPost(BaseModel):
    id: str
    url: str
    author_username: str
    author_display_name: str = ""
    author_avatar_url: str = ""
    content: str
    media_urls: List[str] = []
    like_count: Optional[int] = None
    reply_count: Optional[int] = None
    repost_count: Optional[int] = None
    published_at: Optional[str] = None
    comments: List[CrawledComment] = []
    quality_report: Optional[CrawlQualityReport] = None

    model_config = ConfigDict(from_attributes=True)

def parse_threads_url(url: str) -> Dict[str, str]:
    """Extract username and post_id from public Threads URL.
    Supports formats:
    - https://www.threads.net/@username/post/POST_ID
    - https://www.threads.com/@username/post/POST_ID
    - https://threads.net/t/POST_ID
    """
    clean_url = url.strip()
    match = re.search(r'threads\.(?:net|com)/@([a-zA-Z0-9._]+)/post/([a-zA-Z0-9_-]+)', clean_url)
    if match:
        return {
            "username": match.group(1),
            "post_id": match.group(2),
            "canonical_url": f"https://www.threads.net/@{match.group(1)}/post/{match.group(2)}"
        }
    
    match_short = re.search(r'threads\.(?:net|com)/t/([a-zA-Z0-9_-]+)', clean_url)
    if match_short:
        return {
            "username": "",
            "post_id": match_short.group(1),
            "canonical_url": f"https://www.threads.net/t/{match_short.group(1)}"
        }

    raise ValueError(f"URL Threads không hợp lệ: '{url}'. Vui lòng nhập link dạng https://www.threads.net/@username/post/POST_ID")
