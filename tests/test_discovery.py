import pytest
from backend.app.services.discovery.hot_score import hot_score_calculator
from backend.app.services.discovery.trend_topic_provider import trend_topic_provider
from backend.app.services.discovery.discovery_service import discovery_service, DiscoveredPost
from backend.app.api.discovery import (
    get_categories,
    get_topics,
    get_discovery_status,
    search_discovery,
    DiscoverySearchRequest
)

def test_hot_score_prioritizes_replies_and_recency():
    # Post A: 500 likes, 10 replies, 72 hours old
    score_a, reason_a = hot_score_calculator.calculate_score(
        like_count=500,
        reply_count=10,
        repost_count=5,
        published_at_iso="2026-10-28T00:00:00+00:00"
    )

    # Post B: 200 likes, 150 replies (active discussion!), 6 hours old
    score_b, reason_b = hot_score_calculator.calculate_score(
        like_count=200,
        reply_count=150,
        repost_count=20,
        published_at_iso="2026-10-31T17:00:00+00:00"
    )

    # Post B must have a higher score because of rich discussion and recency
    assert score_b > score_a
    assert "Thảo luận" in reason_b or "bình luận" in reason_b
    assert 5.0 <= score_a <= 100.0
    assert 5.0 <= score_b <= 100.0

def test_hot_score_handles_none_metrics():
    score, reason = hot_score_calculator.calculate_score(
        like_count=None,
        reply_count=None,
        repost_count=None,
        published_at_iso=None
    )
    assert score >= 5.0
    assert len(reason) > 0

def test_trend_topic_provider_distinct_sources():
    topics = trend_topic_provider.get_trending_topics(force_refresh=True)
    assert len(topics) >= 5

    # Check distinct source labels
    sources = set(t.source for t in topics)
    assert "seed_catalog" in sources or "google_trends_vn" in sources

    # Ensure no external source is mislabeled as threads_trending
    for t in topics:
        if t.source == "seed_catalog":
            assert t.source_label == "Gợi ý hệ thống"
        elif t.source == "google_trends_vn":
            assert t.source_label == "Google Trends VN"

def test_discovery_service_filters_and_deduplication():
    # Test filtering by category
    res_tech = discovery_service.search_trending(category="technology", limit=10)
    assert res_tech.total > 0
    assert any("AI" in p.content or "technology" in (p.topic or "").lower() for p in res_tech.posts)

    # Test media filter
    res_text = discovery_service.search_trending(media_type="TEXT_POST", limit=10)
    assert all(p.media_type == "TEXT_POST" for p in res_text.posts)

def test_discovery_sorting_modes():
    # 1. Sort by latest
    res_latest = discovery_service.search_trending(category="lifestyle", sort_by="latest", limit=10)
    assert len(res_latest.posts) > 1
    # Check that published_at is ordered descending
    dates = [p.published_at for p in res_latest.posts if p.published_at]
    assert dates == sorted(dates, reverse=True)

    # 2. Sort by comments
    res_comments = discovery_service.search_trending(category="all", sort_by="comments", limit=10)
    assert len(res_comments.posts) > 1
    replies = [p.reply_count or 0 for p in res_comments.posts]
    assert replies == sorted(replies, reverse=True)

def test_discovery_api_endpoints():
    # 1. Categories
    r_cat = get_categories()
    assert r_cat.success is True
    assert "entertainment" in r_cat.data

    # 2. Topics
    r_top = get_topics()
    assert r_top.success is True
    assert len(r_top.data) > 0

    # 3. Status
    r_stat = get_discovery_status()
    assert r_stat.success is True
    assert "configured" in r_stat.data

    # 4. Search with sort_by latest
    req = DiscoverySearchRequest(
        category="lifestyle",
        search_type="BOTH",
        media_type="ALL",
        time_window="7d",
        sort_by="latest",
        limit=5
    )
    r_search = search_discovery(req)
    assert r_search.success is True
    data = r_search.data
    assert "posts" in data
    assert len(data["posts"]) > 0
    assert data["posts"][0]["hot_score"] >= 5.0
    assert "age_label" in data["posts"][0]
