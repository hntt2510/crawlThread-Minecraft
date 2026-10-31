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

    model_config = ConfigDict(from_attributes=True)

class TrendTopicProvider:
    """Discovers Vietnam trending topics from official API, external RSS feeds, or catalog seeds."""

    def __init__(self, cache_ttl_sec: int = 900):  # 15 minutes TTL
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

        # 1. Native Threads Trending (if configured and supported)
        threads_trends = self._fetch_threads_native_trends()
        for t in threads_trends:
            norm = t.name.lower().strip()
            if norm not in seen_names:
                seen_names.add(norm)
                all_topics.append(t)

        # 2. External Vietnam Trend Feeds (Google Trends VN RSS)
        feed_trends = self._fetch_vietnam_rss_trends()
        for t in feed_trends:
            norm = t.name.lower().strip()
            if norm not in seen_names:
                seen_names.add(norm)
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
                    updated_at=now.isoformat()
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
                # Meta documented endpoint for trends when permitted
                resp = client.get(
                    f"{base_url}/trending_topics",
                    params={"access_token": access_token}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results = []
                    for idx, item in enumerate(data.get("data", [])):
                        topic_name = item.get("topic") or item.get("name")
                        if topic_name:
                            results.append(TrendingTopic(
                                id=f"threads_trend_{idx}",
                                name=topic_name,
                                category="entertainment",
                                source="threads_trending",
                                source_label="Threads Trending (Chính thức)",
                                traffic_hint="Xu hướng Threads",
                                updated_at=datetime.now(timezone.utc).isoformat()
                            ))
                    return results
        except Exception as e:
            logger.debug(f"Official Threads trending endpoint not available or not permitted: {e}")
        return []

    def _fetch_vietnam_rss_trends(self) -> List[TrendingTopic]:
        """Fetches public Vietnam trending search feed (Google Trends RSS)."""
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

                # XML namespace for Google Trends
                ns = {"ht": "https://trends.google.com/trends/trendingsearches/daily"}

                for idx, it in enumerate(items[:15]):
                    title_elem = it.find("title")
                    if title_elem is None or not title_elem.text:
                        continue
                    title = title_elem.text.strip()

                    # Try to extract approx_traffic
                    traffic_elem = it.find("ht:approx_traffic", ns)
                    traffic = traffic_elem.text.strip() if (traffic_elem is not None and traffic_elem.text) else "Đang thịnh hành"

                    # Infer category
                    cat = self._infer_category(title)

                    results.append(TrendingTopic(
                        id=f"rss_{idx}_{abs(hash(title)) % 10000}",
                        name=title,
                        category=cat,
                        source="google_trends_vn",
                        source_label="Google Trends VN",
                        traffic_hint=traffic,
                        updated_at=datetime.now(timezone.utc).isoformat()
                    ))
                return results
        except Exception as e:
            logger.warning(f"Could not load Vietnam RSS trends feed: {e}")
            return []

    def _infer_category(self, title: str) -> str:
        t_low = title.lower()
        if any(w in t_low for w in ["phim", "ca sĩ", "nhạc", "show", "diễn viên", "rap"]):
            return "entertainment"
        if any(w in t_low for w in ["ai", "iphone", "samsung", "công nghệ", "chip"]):
            return "technology"
        if any(w in t_low for w in ["bóng đá", "cup", "marathon", "thể thao", "trận"]):
            return "sports"
        if any(w in t_low for w in ["giá vàng", "chứng khoán", "ngân hàng", "tỷ giá"]):
            return "business"
        if any(w in t_low for w in ["món", "quán", "ẩm thực", "ăn"]):
            return "food"
        return "society"

trend_topic_provider = TrendTopicProvider()
