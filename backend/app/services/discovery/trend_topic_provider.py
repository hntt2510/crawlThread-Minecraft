import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import httpx
from pydantic import BaseModel, ConfigDict
from backend.app.core.config import settings
from backend.app.services.discovery.seed_catalog import vietnam_topic_seed_provider

logger = logging.getLogger("studio.discovery.topics")

class TrendingTopic(BaseModel):
    id: str
    name: str
    category: str = "general"
    source: str         # "threads_trending", "google_trends_vn", "seed_catalog"
    source_label: str   # "Threads Trending", "Google Trends VN", "Gợi ý hệ thống"
    traffic_hint: Optional[str] = None
    updated_at: str
    updated_at_human: str = ""

    model_config = ConfigDict(from_attributes=True)

class TrendTopicProvider:
    """Discovers Vietnam trending topics from official API, external RSS feeds, or catalog seeds,
    with real-time date/time stamps and smart categorization."""

    def __init__(self, cache_ttl_sec: int = 600):  # 10 minutes TTL
        self.cache_ttl_sec = cache_ttl_sec
        self._cached_topics: List[TrendingTopic] = []
        self._last_fetch_time: Optional[datetime] = None

    def get_trending_topics(self, category: Optional[str] = None, force_refresh: bool = False) -> List[TrendingTopic]:
        now = datetime.now(timezone.utc)
        if (
            not force_refresh
            and self._cached_topics
            and self._last_fetch_time
            and (now - self._last_fetch_time).total_seconds() < self.cache_ttl_sec
        ):
            if category and category != "all":
                return [t for t in self._cached_topics if t.category == category]
            return self._cached_topics

        all_topics: List[TrendingTopic] = []
        seen_names = set()
        now_human = now.strftime("%H:%M %d/%m/%Y")

        # 1. Native Threads Trending (if configured and supported)
        threads_trends = self._fetch_threads_native_trends()
        for t in threads_trends:
            norm = t.name.lower().strip()
            if norm not in seen_names:
                seen_names.add(norm)
                t.updated_at_human = now_human
                all_topics.append(t)

        # 2. External Real-Time Vietnam Trend Feeds (Google Trends VN RSS)
        feed_trends = self._fetch_vietnam_rss_trends()
        for t in feed_trends:
            norm = t.name.lower().strip()
            if norm not in seen_names:
                seen_names.add(norm)
                t.updated_at_human = now_human
                all_topics.append(t)

        # 3. Built-in Catalog Seeds (Ensures rich variety across categories)
        seed_items = vietnam_topic_seed_provider.get_seeds(category=None)
        for idx, s in enumerate(seed_items):
            norm = s["name"].lower().strip()
            if norm not in seen_names:
                seen_names.add(norm)
                all_topics.append(TrendingTopic(
                    id=f"seed_{idx}_{s['category']}",
                    name=s["name"],
                    category=s.get("category", "lifestyle"),
                    source="seed_catalog",
                    source_label="Gợi ý hệ thống",
                    traffic_hint=s.get("traffic_hint"),
                    updated_at=now.isoformat(),
                    updated_at_human=now_human
                ))

        self._cached_topics = all_topics
        self._last_fetch_time = now

        if category and category != "all":
            return [t for t in all_topics if t.category == category]
        return all_topics

    def _fetch_threads_native_trends(self) -> List[TrendingTopic]:
        """Queries Meta Threads API for official trending topics if token & permission allow."""
        access_token = getattr(settings, "THREADS_ACCESS_TOKEN", "")
        if not access_token:
            return []

        base_url = getattr(settings, "THREADS_API_BASE_URL", "https://graph.threads.net/v1.0").rstrip("/")
        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.get(
                    f"{base_url}/trending_topics",
                    params={"access_token": access_token}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results = []
                    now = datetime.now(timezone.utc)
                    now_human = now.strftime("%H:%M %d/%m/%Y")
                    for idx, item in enumerate(data.get("data", [])):
                        topic_name = item.get("topic") or item.get("name")
                        if topic_name:
                            cat = self._infer_category(topic_name)
                            results.append(TrendingTopic(
                                id=f"threads_trend_{idx}",
                                name=topic_name,
                                category=cat,
                                source="threads_trending",
                                source_label="Threads Trending (Thời gian thực)",
                                traffic_hint="Xu hướng Threads",
                                updated_at=now.isoformat(),
                                updated_at_human=now_human
                            ))
                    return results
        except Exception as e:
            logger.debug(f"Official Threads trending endpoint not available: {e}")
        return []

    def _fetch_vietnam_rss_trends(self) -> List[TrendingTopic]:
        """Fetches public Vietnam trending search feed (Google Trends RSS) with real-time timestamps."""
        feed_url = getattr(settings, "VIETNAM_TRENDS_FEED_URL", "https://trends.google.com/trending/rss?geo=VN")
        if not feed_url:
            return []

        try:
            with httpx.Client(timeout=8.0, follow_redirects=True) as client:
                resp = client.get(feed_url)
                if resp.status_code != 200:
                    return []

                root = ET.fromstring(resp.text)
                items = root.findall(".//item")
                results: List[TrendingTopic] = []

                ns = {"ht": "https://trends.google.com/trends/trendingsearches/daily"}
                now = datetime.now(timezone.utc)
                now_human = now.strftime("%H:%M %d/%m/%Y")

                for idx, it in enumerate(items[:20]):
                    title_elem = it.find("title")
                    if title_elem is None or not title_elem.text:
                        continue
                    title = title_elem.text.strip()

                    traffic_elem = it.find("ht:approx_traffic", ns)
                    traffic = traffic_elem.text.strip() if (traffic_elem is not None and traffic_elem.text) else "Đang thịnh hành"

                    pub_elem = it.find("pubDate")
                    item_updated = now.isoformat()
                    if pub_elem is not None and pub_elem.text:
                        try:
                            parsed_pub = datetime.strptime(pub_elem.text.strip()[:25], "%a, %d %b %Y %H:%M:%S")
                            item_updated = parsed_pub.replace(tzinfo=timezone.utc).isoformat()
                        except Exception:
                            pass

                    cat = self._infer_category(title)

                    results.append(TrendingTopic(
                        id=f"rss_{idx}_{abs(hash(title)) % 10000}",
                        name=title,
                        category=cat,
                        source="google_trends_vn",
                        source_label="Google Trends VN",
                        traffic_hint=traffic,
                        updated_at=item_updated,
                        updated_at_human=now_human
                    ))
                return results
        except Exception as e:
            logger.warning(f"Could not load Vietnam RSS trends feed: {e}")
            return []

    def _infer_category(self, title: str) -> str:
        t_low = " " + title.lower() + " "
        def has_any(keywords):
            return any(k in t_low for k in keywords)

        # 1. Entertainment
        if has_any(["phim", "ca sĩ", "nhạc", "show", "diễn viên", "rap", "tập", "concert", "hoa hậu", "mv", "album", "idol", "showbiz", "anh trai"]):
            return "entertainment"
        # 2. Sports
        if has_any(["đấu với", " vs ", "bóng đá", "cup", "marathon", "thể thao", "trận", "al-nassr", "arsenal", "chelsea", "liverpool", "pickleball", "cầu thủ", "vô địch"]):
            return "sports"
        # 3. Technology
        if has_any(["điện thoại", "máy tính", "máy ảnh", "iphone", "samsung", "công nghệ", "chip", "ai", "laptop", "nvidia", "intel", "lập trình", "phần mềm"]):
            return "technology"
        # 4. Business & Finance
        if has_any(["cổ phiếu", "chứng khoán", "giá vàng", "ngân hàng", "tỷ giá", "doanh thu", "lợi nhuận", "kinh tế", "đầu tư", "tiết kiệm", "bất động sản"]):
            return "business"
        # 5. Food & Drinks
        if has_any(["món ăn", "quán ăn", "ẩm thực", "ăn uống", "cà phê", "nhà hàng", "buffet", "trà sữa", "nấu ăn"]):
            return "food"
        # 6. Travel
        if has_any(["du lịch", "khách sạn", "homestay", "đà lạt", "phú quốc", "sapa", "vé máy bay", "check in", "phượt"]):
            return "travel"
        # 7. Education
        if has_any(["sinh viên", "đại học", "thi cử", "học sinh", "điểm chuẩn", "học bổng", "tuyển sinh", "kỳ thi"]):
            return "education"
        # 8. Relationships
        if has_any(["người yêu", "hẹn hò", "tình yêu", "crush", "chia tay", "cắm sừng", "bạn thân"]):
            return "relationships"

        return "society"

trend_topic_provider = TrendTopicProvider()
