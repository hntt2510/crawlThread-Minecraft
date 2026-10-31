import logging
from typing import Optional, Tuple
from backend.app.services.crawler.base import CrawledPost, parse_threads_url
from backend.app.services.crawler.relay_crawler import ThreadsRelayCrawler
from backend.app.services.crawler.official_api import ThreadsConversationProvider, threads_conversation_provider

logger = logging.getLogger("studio.crawler.service")

class CrawlerService:
    """Unified crawler service that orchestrates official API and hardened Relay cache scraper."""

    def __init__(self):
        self.relay_crawler = ThreadsRelayCrawler()
        self.official_provider = threads_conversation_provider

    def crawl(self, url: str, max_comments: int = 50) -> CrawledPost:
        url_info = parse_threads_url(url)
        post_id = url_info["post_id"]

        # 1. If official API is configured, attempt retrieval
        if self.official_provider.is_configured():
            try:
                logger.info(f"Using Meta Threads Official API for post {post_id}")
                return self.official_provider.fetch_conversation(post_id, max_comments=max_comments)
            except Exception as e:
                logger.warning(f"Official API crawl failed, falling back to Relay cache: {e}")

        # 2. Hardened Relay Stream Cache Crawler
        logger.info(f"Using hardened Relay stream cache crawler for {url}")
        return self.relay_crawler.crawl_post_and_comments(url, max_comments=max_comments)

crawler_service = CrawlerService()
