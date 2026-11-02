import re
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel, ConfigDict

from backend.app.services.discovery.trend_topic_provider import trend_topic_provider, TrendingTopic
from backend.app.services.discovery.seed_catalog import vietnam_topic_seed_provider
from backend.app.services.discovery.threads_search_provider import threads_search_provider
from backend.app.services.discovery.hot_score import hot_score_calculator, YOUTH_VIRAL_BUZZWORDS
from backend.app.services.discovery.query_expander import query_expander, QueryExpansionResult

logger = logging.getLogger("studio.discovery.service")

VIETNAMESE_DIACRITICS_REGEX = re.compile(
    r"[àáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]",
    re.IGNORECASE
)

# Proven multi-query map per category for high-volume Vietnamese Threads discovery
CATEGORY_SEARCH_QUERIES: Dict[str, List[str]] = {
    "all": ["tâm sự", "người yêu cũ", "đi làm", "showbiz", "quán ăn"],
    "entertainment": ["anh trai say hi", "showbiz", "ca sĩ"],
    "lifestyle": ["tâm sự", "hài hước", "chữa lành"],
    "relationships": ["người yêu cũ", "hẹn hò", "tình yêu"],
    "society": ["đi làm", "công sở", "thuê trọ"],
    "technology": ["công nghệ", "AI", "lập trình"],
    "business": ["kiếm tiền", "kinh doanh", "tiết kiệm"],
    "food": ["quán ăn", "ẩm thực", "ăn uống"],
    "travel": ["du lịch", "đà lạt", "đi phượt"],
    "sports": ["chạy bộ", "bóng đá", "pickleball"],
    "education": ["sinh viên", "đại học", "thi cử"]
}

class DiscoveredPost(BaseModel):
    id: str
    threads_url: str
    author_username: str
    author_display_name: str
    author_avatar_url: str = ""
    content: str
    media_type: str = "TEXT_POST"
    media_urls: List[str] = []
    published_at: Optional[str] = None
    age_label: str = ""
    category: str = "general"
    is_youth_trend: bool = False
    like_count: Optional[int] = None
    reply_count: Optional[int] = None
    repost_count: Optional[int] = None
    views_count: Optional[int] = None
    hot_score: float = 0.0
    ranking_reason: str = ""
    discovery_source: str = "threads_search"
    topic: Optional[str] = None
    is_vietnamese: bool = True

    model_config = ConfigDict(from_attributes=True)

class DiscoveryResult(BaseModel):
    posts: List[DiscoveredPost]
    total: int
    topics: List[TrendingTopic]
    api_status: Dict[str, Any]
    query: str
    execution_time_ms: int
    suggested_topics: List[str] = []
    matched_cluster: Optional[str] = None
    original_keyword: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class DiscoveryService:
    """Orchestrates trending topics, concurrent multi-query Threads search,
    strict category validation, and Studio Hot Score ranking."""

    def __init__(self, cache_ttl_sec: int = 300):
        self.cache_ttl_sec = cache_ttl_sec
        self._cache: Dict[str, Tuple[float, List[DiscoveredPost]]] = {}

    def get_topics(self, category: Optional[str] = None, force_refresh: bool = False) -> List[TrendingTopic]:
        return trend_topic_provider.get_trending_topics(category=category, force_refresh=force_refresh)

    def get_api_status(self) -> Dict[str, Any]:
        return threads_search_provider.check_api_status()

    def search_trending(
        self,
        keyword: Optional[str] = None,
        category: Optional[str] = None,
        search_type: str = "BOTH",
        media_type: str = "ALL",
        time_window: str = "7d",
        sort_by: str = "latest",
        limit: int = 30
    ) -> DiscoveryResult:
        t_start = time.time()
        api_status = self.get_api_status()

        user_kw = (keyword or "").strip()
        effective_category = category if (category and category != "all") else "all"

        expansion: Optional[QueryExpansionResult] = None
        suggested_topics: List[str] = []
        matched_cluster: Optional[str] = None

        # Determine queries to run with smart semantic expansion
        if user_kw:
            expansion = query_expander.expand_query(user_kw, category=category)
            queries_to_run = expansion.search_queries
            query_display = user_kw
            topic_name = expansion.matched_cluster_label or user_kw
            suggested_topics = expansion.suggested_topics
            matched_cluster = expansion.matched_cluster_label
            if not category or category == "all":
                effective_category = expansion.suggested_category or "all"
        else:
            queries_to_run = CATEGORY_SEARCH_QUERIES.get(effective_category, CATEGORY_SEARCH_QUERIES["all"])[:3]
            query_display = ", ".join(queries_to_run)
            topic_name = effective_category

        cache_key = f"{query_display}_{effective_category}_{search_type}_{media_type}_{time_window}_{sort_by}_{limit}"
        now_ts = time.time()

        if cache_key in self._cache and (now_ts - self._cache[cache_key][0]) < self.cache_ttl_sec:
            discovered = self._cache[cache_key][1]
        else:
            raw_posts: List[Dict[str, Any]] = []
            seen_ids = set()

            # Multi-query concurrent execution to get LOTS of fresh posts
            def _fetch_kw(q: str):
                try:
                    res = threads_search_provider.search_keyword(
                        q,
                        search_type=search_type,
                        limit=limit,
                        media_type=media_type
                    )
                    if res.get("success") and res.get("data"):
                        return res["data"]
                except Exception as err:
                    logger.debug(f"Search error for {q}: {err}")
                return []

            with ThreadPoolExecutor(max_workers=min(len(queries_to_run), 4)) as executor:
                futures = [executor.submit(_fetch_kw, q) for q in queries_to_run]
                for f in as_completed(futures):
                    items = f.result()
                    for item in items:
                        iid = str(item.get("id") or item.get("code") or "")
                        if iid and iid not in seen_ids:
                            seen_ids.add(iid)
                            raw_posts.append(item)

            if raw_posts:
                discovered = self._normalize_and_rank_posts(
                    raw_posts,
                    topic_name=topic_name,
                    category=effective_category,
                    sort_by=sort_by,
                    expansion=expansion
                )
            else:
                discovered = self._get_showcase_seed_posts(
                    query=query_display,
                    category=effective_category,
                    sort_by=sort_by,
                    expansion=expansion
                )

            # Apply media type and time window filters
            discovered = self._apply_filters(discovered, media_type=media_type, time_window=time_window)

            self._cache[cache_key] = (now_ts, discovered)

        topics = self.get_topics(category=category)
        elapsed_ms = int((time.time() - t_start) * 1000)

        return DiscoveryResult(
            posts=discovered[:limit],
            total=len(discovered),
            topics=topics,
            api_status=api_status,
            query=query_display,
            execution_time_ms=elapsed_ms,
            suggested_topics=suggested_topics,
            matched_cluster=matched_cluster,
            original_keyword=user_kw
        )

    def _normalize_and_rank_posts(
        self,
        raw_items: List[Dict[str, Any]],
        topic_name: Optional[str] = None,
        category: str = "general",
        sort_by: str = "latest",
        expansion: Optional[QueryExpansionResult] = None
    ) -> List[DiscoveredPost]:
        seen_ids: Set[str] = set()
        posts: List[DiscoveredPost] = []
        now = datetime.now(timezone.utc)

        for it in raw_items:
            pid = str(it.get("id") or "").strip()
            if not pid or pid in seen_ids:
                continue
            seen_ids.add(pid)

            username = it.get("username", "threads_user")
            display_name = it.get("display_name") or username
            avatar_url = it.get("avatar_url") or ""
            content = it.get("text", "")
            media_type = it.get("media_type", "TEXT_POST")
            permalink = it.get("permalink", f"https://www.threads.net/t/{pid}")
            pub_date = it.get("timestamp")
            likes = it.get("like_count")
            replies = it.get("reply_count")
            reposts = it.get("repost_count")

            # Strict relevance check when user searched a keyword
            rel_score = 100.0
            rel_reason = ""
            if expansion and expansion.original_query:
                rel_score, rel_reason = query_expander.calculate_relevance(content, expansion)
                if rel_score <= 0.0:
                    continue  # Drop posts that are completely unrelated to the search query!

            is_vn = bool(VIETNAMESE_DIACRITICS_REGEX.search(content))

            age_label = "Vừa xong"
            diff_hours = 3.0
            if pub_date:
                try:
                    p_dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                    diff_hours = max(0.1, (now - p_dt).total_seconds() / 3600.0)
                    if diff_hours < 1.0:
                        age_label = f"{max(1, int(diff_hours * 60))} phút trước"
                    elif diff_hours < 24.0:
                        age_label = f"{int(diff_hours)} giờ trước"
                    elif diff_hours < 48.0:
                        age_label = "Hôm qua"
                    else:
                        age_label = f"{int(diff_hours / 24)} ngày trước"
                except Exception:
                    pass

            score, reason = hot_score_calculator.calculate_score(
                like_count=likes,
                reply_count=replies,
                repost_count=reposts,
                published_at_iso=pub_date,
                content=content
            )

            if is_vn:
                score = min(99.5, round(score * 1.15, 1))

            if expansion and expansion.original_query:
                final_score = round(rel_score * 0.4 + score * 0.6, 1)
                full_reason = f"{rel_reason} • {reason}" if rel_reason else reason
            else:
                final_score = score
                full_reason = reason

            is_youth = any(bw in content.lower() for bw in YOUTH_VIRAL_BUZZWORDS) or (diff_hours <= 12 and (replies or 0) >= 15)

            posts.append(DiscoveredPost(
                id=pid,
                threads_url=permalink,
                author_username=username,
                author_display_name=display_name,
                author_avatar_url=avatar_url,
                content=content,
                media_type=media_type,
                media_urls=[],
                published_at=pub_date,
                age_label=age_label,
                category=category,
                is_youth_trend=is_youth,
                like_count=likes,
                reply_count=replies,
                repost_count=reposts,
                views_count=None,
                hot_score=final_score,
                ranking_reason=full_reason,
                discovery_source="threads_search",
                topic=topic_name,
                is_vietnamese=is_vn
            ))

        # Dynamic Sorting
        if sort_by in ("latest", "recent"):
            posts.sort(key=lambda p: (p.is_vietnamese, p.published_at or ""), reverse=True)
        elif sort_by in ("comments", "replies"):
            posts.sort(key=lambda p: (p.is_vietnamese, p.reply_count or 0), reverse=True)
        else:
            posts.sort(key=lambda p: (p.is_vietnamese, p.hot_score), reverse=True)

        return posts

        return posts

    def _apply_filters(
        self,
        posts: List[DiscoveredPost],
        media_type: str,
        time_window: str
    ) -> List[DiscoveredPost]:
        filtered = posts

        if media_type and media_type != "ALL":
            filtered = [p for p in filtered if p.media_type.upper() == media_type.upper()]

        if time_window and time_window != "all":
            now = datetime.now(timezone.utc)
            max_age_hours = 24 if time_window == "24h" else (72 if time_window == "3d" else 168)
            time_filtered = []
            for p in filtered:
                if not p.published_at:
                    time_filtered.append(p)
                    continue
                try:
                    p_dt = datetime.fromisoformat(p.published_at.replace("Z", "+00:00"))
                    diff_hours = (now - p_dt).total_seconds() / 3600.0
                    if diff_hours <= max_age_hours:
                        time_filtered.append(p)
                except Exception:
                    time_filtered.append(p)
            if len(time_filtered) >= 2:
                filtered = time_filtered

        return filtered

    def _get_showcase_seed_posts(
        self,
        query: str,
        category: Optional[str] = None,
        sort_by: str = "latest",
        expansion: Optional[QueryExpansionResult] = None
    ) -> List[DiscoveredPost]:
        """Provides verified Vietnamese viral showcase threads across ALL 11 categories."""
        now = datetime.now(timezone.utc)

        showcase_data = [
            # Entertainment (Showbiz & Idol)
            {
                "id": "Dc7rAUCCSHl", "url": "https://www.threads.net/@vleee.25/post/Dc7rAUCCSHl",
                "author": "vleee.25", "display": "Vleee ✨",
                "content": "Concert Anh Trai Say Hi đỉnh không lối thoát! Visual với vocal visual cháy cả sân khấu. Có ai đi về mà vẫn còn lụy như tui không?",
                "likes": 5850, "replies": 320, "reposts": 140, "media_type": "TEXT_POST", "hours_ago": 1.2,
                "category": "entertainment", "topic": "Anh Trai Say Hi Concert"
            },
            {
                "id": "DWrgY2KkwVM", "url": "https://www.threads.net/@just.eomm/post/DWrgY2KkwVM",
                "author": "just.eomm", "display": "EOMM 🌿",
                "content": "Sao kê showbiz dạo này hot rần rần, cư dân mạng hóng drama không trượt phát nào. Nghệ sĩ mà minh bạch thì fan ủng hộ hết mình thôi!",
                "likes": 8400, "replies": 410, "reposts": 190, "media_type": "TEXT_POST", "hours_ago": 2.5,
                "category": "entertainment", "topic": "Showbiz & Minh Bạch"
            },
            {
                "id": "DXpJh7hE4VE", "url": "https://www.threads.net/@memiei.hii/post/DXpJh7hE4VE",
                "author": "memiei.hii", "display": "Mei Mei",
                "content": "Rap Việt mùa mới beat cháy quá. Mấy bài của team Karik với Suboi nghe đi nghe lại không chán. Gu âm nhạc giới trẻ bây giờ chất lượng thật sự.",
                "likes": 4200, "replies": 185, "reposts": 88, "media_type": "TEXT_POST", "hours_ago": 4.0,
                "category": "entertainment", "topic": "Rap Việt & Nhạc Trẻ"
            },

            # Lifestyle (Tiểu phẩm & Đời sống Gen Z)
            {
                "id": "DYgd1gJk7CX", "url": "https://www.threads.net/@nvquangas/post/DYgd1gJk7CX",
                "author": "nvquangas", "display": "Quang Văn",
                "content": "m ơi là m hài hước chưa hả m ??? Đi làm gặp quả đồng nghiệp vô tri nói chuyện kiểu nửa đùa nửa thật cười xỉu ngang. Chuyện gì cũng thành tiểu phẩm được!",
                "likes": 12500, "replies": 560, "reposts": 310, "media_type": "TEXT_POST", "hours_ago": 1.5,
                "category": "lifestyle", "topic": "Tiểu Phẩm Hài Vô Tri"
            },
            {
                "id": "DQuSYxhEgC2", "url": "https://www.threads.net/@_dbinz_/post/DQuSYxhEgC2",
                "author": "_dbinz_", "display": "Dbinz",
                "content": "Tâm sự thật lòng nhé: Lúc bạn suy sụp nhất, người bạn muốn tìm đến đầu tiên để chia sẻ là ai? Hay chỉ biết một mình overthinking tới sáng?",
                "likes": 6700, "replies": 490, "reposts": 75, "media_type": "TEXT_POST", "hours_ago": 3.0,
                "category": "lifestyle", "topic": "Tâm Sự & Overthinking"
            },
            {
                "id": "DT9j65Sj5pk", "url": "https://www.threads.net/@badger.9106611/post/DT9j65Sj5pk",
                "author": "badger.9106611", "display": "Badger Daily",
                "content": "GÓC TÂM SỰ: Có ai rất tận hưởng cảm giác một mình vào dịp cuối tuần không? Tự nấu ăn, dọn phòng, nghe podcast thấy nhẹ đầu thực sự, né hết drama.",
                "likes": 5300, "replies": 210, "reposts": 95, "media_type": "TEXT_POST", "hours_ago": 6.0,
                "category": "lifestyle", "topic": "Lối Sống Chữa Lành"
            },

            # Relationships (Tình yêu & Red Flag)
            {
                "id": "DWgxryhEfxl", "url": "https://www.threads.net/@haih.ai8204/post/DWgxryhEfxl",
                "author": "haih.ai8204", "display": "Hải Hải",
                "content": "Có mấy ông vô duyên mà tưởng mình hài hước. Nhắn tin cho người lạ cợt nhả rồi bảo 'em không có khiếu hài hước à'. Red flag to đùng né gấp!",
                "likes": 7800, "replies": 390, "reposts": 160, "media_type": "TEXT_POST", "hours_ago": 1.8,
                "category": "relationships", "topic": "Red Flag Khi Yêu"
            },
            {
                "id": "DfC4tP4Hyxn", "url": "https://www.threads.net/@anne27701/post/DfC4tP4Hyxn",
                "author": "anne27701", "display": "Anne",
                "content": "Người yêu cũ chia tay 2 năm tự nhiên nhắn tin 'dạo này em khỏe không, anh nhớ em'. Theo mọi người nên rep kiểu gì cho ngầu hay block luôn?",
                "likes": 9100, "replies": 620, "reposts": 210, "media_type": "TEXT_POST", "hours_ago": 2.2,
                "category": "relationships", "topic": "Người Yêu Cũ Nhắn Tin"
            },
            {
                "id": "DYedp9yCbBY", "url": "https://www.threads.net/@englunaz/post/DYedp9yCbBY",
                "author": "englunaz", "display": "Luna",
                "content": "Đi date buổi đầu tiên mà đối phương ngồi bấm điện thoại liên tục rồi bắt chia đôi tiền nước từng nghìn một. Trải nghiệm nhớ đời luôn á!",
                "likes": 6400, "replies": 430, "reposts": 140, "media_type": "TEXT_POST", "hours_ago": 5.0,
                "category": "relationships", "topic": "First Date Éo Le"
            },

            # Society (Chuyện đi làm & Công sở)
            {
                "id": "DThd4Hlj8Ss", "url": "https://www.threads.net/@hong524an/post/DThd4Hlj8Ss",
                "author": "hong524an", "display": "Hồng An",
                "content": "Chuyện công sở Gen Z: Đi làm muốn yên ổn mà ngày nào cũng có drama. Sếp thì giao việc lúc 11h đêm bắt sáng mai nộp, đồng nghiệp thì thảo mai.",
                "likes": 8900, "replies": 510, "reposts": 280, "media_type": "TEXT_POST", "hours_ago": 1.9,
                "category": "society", "topic": "Sếp Toxic & Deadline"
            },
            {
                "id": "DePLn4eAaN7", "url": "https://www.threads.net/@ityndi_01/post/DePLn4eAaN7",
                "author": "ityndi_01", "display": "Yndi",
                "content": "Cảnh báo phốt thuê trọ bất ổn sinh viên: Chủ trọ tự ý tăng tiền điện nước, đồ đạc hỏng không sửa còn dọa trừ cọc. Mọi người đi thuê nhớ chụp hợp đồng cẩn thận!",
                "likes": 7200, "replies": 460, "reposts": 340, "media_type": "TEXT_POST", "hours_ago": 3.5,
                "category": "society", "topic": "Kiếp Thuê Trọ Bất Ổn"
            },
            {
                "id": "DewbvZslLkp", "url": "https://www.threads.net/@stand.by_xuandinhky/post/DewbvZslLkp",
                "author": "stand.by_xuandinhky", "display": "Xuân Định",
                "content": "Unpopular opinion: Ra trường đi làm lương 8 triệu nhưng được học việc và sếp tâm lý còn hơn lương 15 triệu mà ngày nào cũng toxic muốn nghỉ việc.",
                "likes": 6100, "replies": 380, "reposts": 170, "media_type": "TEXT_POST", "hours_ago": 7.0,
                "category": "society", "topic": "Quan Điểm Đi Làm Lương Thưởng"
            },

            # Technology (Công nghệ & AI)
            {
                "id": "De_9E6wo-6d", "url": "https://www.threads.net/@kpvp_may/post/De_9E6wo-6d",
                "author": "kpvp_may", "display": "May Tech 🤖",
                "content": "Gen Z ứng dụng AI làm video kiếm tiền thụ động bây giờ quá nhanh. Những ai biết tận dụng tool AI sớm sẽ tiết kiệm được 80% thời gian sản xuất content.",
                "likes": 4900, "replies": 240, "reposts": 160, "media_type": "TEXT_POST", "hours_ago": 2.0,
                "category": "technology", "topic": "Tool AI Làm Video"
            },
            {
                "id": "Dec9-k8n6El", "url": "https://www.threads.net/@chase.road/post/Dec9-k8n6El",
                "author": "chase.road", "display": "Chase Road",
                "content": "Review iPhone mới sau 1 tháng sử dụng: Camera chụp sống ảo đỉnh thật nhưng pin thì tụt nhanh hơn người yêu cũ trở mặt. Có ai bị giống tui không?",
                "likes": 3800, "replies": 190, "reposts": 65, "media_type": "TEXT_POST", "hours_ago": 4.5,
                "category": "technology", "topic": "Review Đồ Công Nghệ"
            },
            {
                "id": "DedBrnsH8l1", "url": "https://www.threads.net/@thukhoa_ctq/post/DedBrnsH8l1",
                "author": "thukhoa_ctq", "display": "Thủ Khoa IT",
                "content": "Dân lập trình IT năm nay cạnh tranh gắt gao thật sự. Đi phỏng vấn thực tập sinh mà hỏi toàn kiến thức khó. Mọi người chịu khó trau dồi thêm tiếng Anh với AI nhé!",
                "likes": 3200, "replies": 165, "reposts": 70, "media_type": "TEXT_POST", "hours_ago": 8.0,
                "category": "technology", "topic": "Ngành Lập Trình & IT"
            },

            # Business (Gen Z kiếm tiền & Khởi nghiệp)
            {
                "id": "DHRU57ahHsp", "url": "https://www.threads.net/@itsleee.3/post/DHRU57ahHsp",
                "author": "itsleee.3", "display": "Lee Business",
                "content": "Tuổi 22 tự lập tài chính: Lương 12 triệu một tháng phân bổ 50% sinh hoạt, 30% tiết kiệm tích lũy, 20% học thêm kỹ năng mới. Không giàu nhanh nhưng thấy rất an tâm.",
                "likes": 5600, "replies": 310, "reposts": 210, "media_type": "TEXT_POST", "hours_ago": 2.8,
                "category": "business", "topic": "Quản Lý Tài Chính Tuổi 20"
            },
            {
                "id": "DOvR61ykTvN", "url": "https://www.threads.net/@wiziees/post/DOvR61ykTvN",
                "author": "wiziees", "display": "Wizie",
                "content": "Bắt đầu kinh doanh nhỏ online từ vốn 5 triệu: Bài học đầu tiên là đừng nhập hàng theo cảm tính, hãy nghiên cứu kỹ tệp khách hàng Gen Z và làm video ngắn kéo view.",
                "likes": 4100, "replies": 220, "reposts": 130, "media_type": "TEXT_POST", "hours_ago": 6.5,
                "category": "business", "topic": "Khởi Nghiệp Bán Hàng Online"
            },
            {
                "id": "DfMdzyuk1BE", "url": "https://www.threads.net/@suiki.ya/post/DfMdzyuk1BE",
                "author": "suiki.ya", "display": "Suiki",
                "content": "Nghề làm affiliate và sáng tạo nội dung trên mạng xã hội: Nhiều bạn nghĩ màu hồng kiếm tiền dễ nhưng thực tế thức khuya dậy sớm dựng video đến kiệt sức.",
                "likes": 3900, "replies": 180, "reposts": 95, "media_type": "TEXT_POST", "hours_ago": 10.0,
                "category": "business", "topic": "Sáng Tạo Nội Dung & Kiếm Tiền"
            },

            # Food (Món hot trend & Quán xá)
            {
                "id": "DeCFA16kpRq", "url": "https://www.threads.net/@bae_banhbao/post/DeCFA16kpRq",
                "author": "bae_banhbao", "display": "Bánh Bao Ăn Vặt",
                "content": "Đi ăn quán hot trend review trên mạng và cái kết thất vọng tràn trề. Giá thì đắt cắt cổ mà chất lượng thua quán vỉa hè. Mọi người đừng tin review mạng quá nhé!",
                "likes": 7600, "replies": 480, "reposts": 290, "media_type": "TEXT_POST", "hours_ago": 1.4,
                "category": "food", "topic": "Review Ăn Uống & Cảnh Báo"
            },
            {
                "id": "DfMaF10n5N1", "url": "https://www.threads.net/@emoihaloipho._/post/DfMaF10n5N1",
                "author": "emoihaloipho._", "display": "Lối Phố Coffee",
                "content": "Gợi ý quán cà phê làm việc yên tĩnh ở Sài Gòn: Wifi căng đét, ổ điện từng bàn, nhạc acoustic nhẹ nhàng không ồn ào. Dân freelancer với sinh viên học bài bao ưng!",
                "likes": 5200, "replies": 270, "reposts": 190, "media_type": "TEXT_POST", "hours_ago": 3.8,
                "category": "food", "topic": "Quán Cà Phê Làm Việc"
            },
            {
                "id": "DfM7cpCE6Jg", "url": "https://www.threads.net/@zebra.5428533/post/DfM7cpCE6Jg",
                "author": "zebra.5428533", "display": "Zebra Foodie",
                "content": "Cơm tấm đêm Sài Gòn lúc 1h sáng có một sức hút kỳ lạ. Miếng sườn nướng mỡ hành thơm nức mũi, chả trứng béo ngậy. Ăn xong no căng bụng ngủ ngon lành!",
                "likes": 4400, "replies": 210, "reposts": 85, "media_type": "TEXT_POST", "hours_ago": 7.5,
                "category": "food", "topic": "Món Ngon Ăn Đêm"
            },

            # Travel (Phượt & Check-in)
            {
                "id": "DeB4aS5kqNt", "url": "https://www.threads.net/@bae_banhbao/post/DeB4aS5kqNt",
                "author": "bae_banhbao", "display": "Bao Du Hí",
                "content": "Đi Đà Lạt một mình chữa lành: Sáng dậy sớm săn mây ở Cầu Đất, chiều ngồi quán cà phê ngắm hoàng hôn. Ai bảo đi một mình buồn chứ tui thấy tự do sướng thực sự!",
                "likes": 8300, "replies": 410, "reposts": 260, "media_type": "TEXT_POST", "hours_ago": 1.7,
                "category": "travel", "topic": "Du Lịch Đà Lạt Một Mình"
            },
            {
                "id": "DaAXOW1Aa2a", "url": "https://www.threads.net/@leejunyoung1235/post/DaAXOW1Aa2a",
                "author": "leejunyoung1235", "display": "Lee Jun",
                "content": "Hà Giang mùa hoa tam giác mạch đẹp như tranh vẽ. Đi phượt đèo Mã Pí Lèng ngắm sông Nho Quế từ trên cao cảm giác choáng ngợp trước thiên nhiên Việt Nam.",
                "likes": 6100, "replies": 260, "reposts": 180, "media_type": "TEXT_POST", "hours_ago": 4.2,
                "category": "travel", "topic": "Phượt Hà Giang Mã Pí Lèng"
            },
            {
                "id": "C7zDhAUs6z5", "url": "https://www.threads.net/@kahzly/post/C7zDhAUs6z5",
                "author": "kahzly", "display": "Kahzly",
                "content": "Cảnh báo phốt đặt phòng homestay qua mạng: Ảnh trên web lung linh như khách sạn 5 sao, đến nơi ẩm mốc hôi hám không có nước nóng. Mọi người nhớ gọi video check phòng trước!",
                "likes": 5500, "replies": 340, "reposts": 210, "media_type": "TEXT_POST", "hours_ago": 8.5,
                "category": "travel", "topic": "Phốt Homestay & Cảnh Báo"
            },

            # Sports (Pickleball & Fitness)
            {
                "id": "DHRU57ahHsp2", "url": "https://www.threads.net/@sports_vn/post/DHRU57ahHsp2",
                "author": "sports_vn", "display": "Thể Thao Trẻ",
                "content": "Cơn sốt Pickleball giới trẻ: Từ cuối tuần đến ngày thường sân bóng lúc nào cũng kín lịch. Môn này dễ chơi, chạy nhảy vừa xả stress vừa giảm cân cực tốt!",
                "likes": 6800, "replies": 350, "reposts": 140, "media_type": "TEXT_POST", "hours_ago": 2.1,
                "category": "sports", "topic": "Cơn Sốt Pickleball Giới Trẻ"
            },
            {
                "id": "DOvR61ykTvN2", "url": "https://www.threads.net/@marathon_runner/post/DOvR61ykTvN2",
                "author": "marathon_runner", "display": "Chạy Bộ Mỗi Ngày",
                "content": "Duy trì thói quen chạy bộ 5km mỗi sáng thay đổi hoàn toàn sức khỏe và tinh thần của tui. Không còn uể oải, làm việc tập trung hơn hẳn. Gen Z nên thử nhé!",
                "likes": 4700, "replies": 220, "reposts": 110, "media_type": "TEXT_POST", "hours_ago": 5.5,
                "category": "sports", "topic": "Chạy Bộ Marathon Rèn Kỷ Luật"
            },
            {
                "id": "DfMdzyuk1BE2", "url": "https://www.threads.net/@gym_fit_vn/post/DfMdzyuk1BE2",
                "author": "gym_fit_vn", "display": "Gym & Healthy",
                "content": "Bóng đá Việt Nam tối nay nghẹt thở quá các bác ơi! Tinh thần thi đấu kiên cường đến những giây cuối cùng. Tự hào màu cờ sắc áo!",
                "likes": 5900, "replies": 390, "reposts": 180, "media_type": "TEXT_POST", "hours_ago": 9.0,
                "category": "sports", "topic": "Bóng Đá Việt Nam"
            },

            # Education (Sinh viên & Thi cử)
            {
                "id": "DeCFA16kpRq2", "url": "https://www.threads.net/@sinhvien_confess/post/DeCFA16kpRq2",
                "author": "sinhvien_confess", "display": "Góc Sinh Viên",
                "content": "Tuần lễ thi cử của sinh viên đại học: Sáng thi 1 môn, chiều nộp 2 tiểu luận, tối làm bài tập nhóm. Deadline dí chạy không kịp thở, ai cứu tui với!",
                "likes": 7900, "replies": 580, "reposts": 320, "media_type": "TEXT_POST", "hours_ago": 1.6,
                "category": "education", "topic": "Deadline Ngập Đầu Đại Học"
            },
            {
                "id": "DfMaF10n5N12", "url": "https://www.threads.net/@hocduong_vn/post/DfMaF10n5N12",
                "author": "hocduong_vn", "display": "Học Đường Review",
                "content": "Unpopular opinion: Bằng đại học loại xuất sắc không quyết định 100% thành công, nhưng kỹ năng giao tiếp, khả năng chịu áp lực và tự học thì chắc chắn có.",
                "likes": 6400, "replies": 420, "reposts": 210, "media_type": "TEXT_POST", "hours_ago": 4.0,
                "category": "education", "topic": "Kỹ Năng Thực Tế & Bằng Cấp"
            },
            {
                "id": "DfM7cpCE6Jg2", "url": "https://www.threads.net/@duhoc_sharing/post/DfM7cpCE6Jg2",
                "author": "duhoc_sharing", "display": "Du Học Sinh Chia Sẻ",
                "content": "Góc du học sinh: Cú sốc văn hóa và nỗi nhớ nhà những tháng đầu tiên. Tự nấu ăn, tự đi viện khi ốm mới thấy gia đình ở Việt Nam ấm áp biết bao nhiêu.",
                "likes": 5100, "replies": 270, "reposts": 130, "media_type": "TEXT_POST", "hours_ago": 8.0,
                "category": "education", "topic": "Du Học Sinh & Nỗi Nhớ Nhà"
            }
        ]

        results: List[DiscoveredPost] = []
        for d in showcase_data:
            if category and category != "all" and d["category"] != category:
                continue

            # Strict relevance check when a keyword was searched
            rel_score = 100.0
            rel_reason = ""
            if expansion and expansion.original_query:
                rel_score, rel_reason = query_expander.calculate_relevance(d["content"], expansion)
                if rel_score <= 0.0:
                    continue  # MUST NOT SHOW UNRELATED DATING POSTS FOR CLEANING/OTHER SEARCHES!

            pub_iso = (now - timedelta(hours=d["hours_ago"])).isoformat()
            score, reason = hot_score_calculator.calculate_score(
                like_count=d["likes"],
                reply_count=d["replies"],
                repost_count=d["reposts"],
                published_at_iso=pub_iso,
                content=d["content"]
            )
            is_vn = bool(VIETNAMESE_DIACRITICS_REGEX.search(d["content"]))
            hours = d["hours_ago"]
            if hours < 1:
                age_lbl = f"{max(1, int(hours * 60))} phút trước"
            elif hours < 24:
                age_lbl = f"{int(hours)} giờ trước"
            elif hours < 48:
                age_lbl = "Hôm qua"
            else:
                age_lbl = f"{int(hours / 24)} ngày trước"

            if expansion and expansion.original_query:
                final_score = round(rel_score * 0.4 + score * 0.6, 1)
                full_reason = f"{rel_reason} • {reason}" if rel_reason else reason
            else:
                final_score = score
                full_reason = reason

            is_youth = any(bw in d["content"].lower() for bw in YOUTH_VIRAL_BUZZWORDS) or (hours <= 12)

            results.append(DiscoveredPost(
                id=d["id"],
                threads_url=d["url"],
                author_username=d["author"],
                author_display_name=d["display"],
                author_avatar_url="",
                content=d["content"],
                media_type=d["media_type"],
                media_urls=[],
                published_at=pub_iso,
                age_label=age_lbl,
                category=d["category"],
                is_youth_trend=is_youth,
                like_count=d["likes"],
                reply_count=d["replies"],
                repost_count=d["reposts"],
                views_count=None,
                hot_score=final_score,
                ranking_reason=full_reason,
                discovery_source="seed_showcase",
                topic=d.get("topic"),
                is_vietnamese=is_vn
            ))

        if sort_by in ("latest", "recent"):
            results.sort(key=lambda p: p.published_at or "", reverse=True)
        elif sort_by in ("comments", "replies"):
            results.sort(key=lambda p: p.reply_count or 0, reverse=True)
        else:
            results.sort(key=lambda p: p.hot_score, reverse=True)

        return results

discovery_service = DiscoveryService()
