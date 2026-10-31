import json
import pytest
from bs4 import BeautifulSoup
from backend.app.services.crawler.base import parse_threads_url, CrawledPost
from backend.app.services.crawler.relay_crawler import ThreadsRelayCrawler

def test_parse_threads_url_valid():
    u1 = "https://www.threads.net/@zuck/post/DeZgeQhm6RW"
    res1 = parse_threads_url(u1)
    assert res1["username"] == "zuck"
    assert res1["post_id"] == "DeZgeQhm6RW"
    assert res1["canonical_url"] == "https://www.threads.net/@zuck/post/DeZgeQhm6RW"

    u2 = "https://www.threads.com/@someone/post/XYZ123?hl=en"
    res2 = parse_threads_url(u2)
    assert res2["username"] == "someone"
    assert res2["post_id"] == "XYZ123"

def test_parse_threads_url_invalid():
    with pytest.raises(ValueError):
        parse_threads_url("https://facebook.com/watch?v=123")

def test_crawler_html_parsing_synthetic():
    crawler = ThreadsRelayCrawler()
    
    # Generate clean valid JSON payload
    payload = {
        "require": [
            [
                "ScheduledServerJS", "handle", None, [
                    {
                        "__bbox": {
                            "require": [
                                [
                                    "RelayPrefetchedStreamCache", "insert", None, [
                                        {
                                            "data": {
                                                "containing_thread": {
                                                    "thread_items": [
                                                        {
                                                            "post": {
                                                                "pk": "9998881",
                                                                "caption": {"text": "Hôm nay trời rất đẹp, các bạn nghĩ sao?"},
                                                                "user": {"username": "creator", "full_name": "Studio Creator"},
                                                                "like_count": 520,
                                                                "reply_count": 12
                                                            }
                                                        },
                                                        {
                                                            "post": {
                                                                "pk": "9998882",
                                                                "caption": {"text": "Quá tuyệt vời luôn bạn ơi!"},
                                                                "user": {"username": "fan1", "full_name": "Fan Cung"},
                                                                "like_count": 35,
                                                                "reply_count": 2
                                                            }
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    ]
                                ]
                            ]
                        }
                    }
                ]
            ]
        ]
    }
    json_str = json.dumps(payload, ensure_ascii=False)
    html_fixture = f"""
    <html>
      <head>
        <meta property="og:description" content="Hôm nay trời rất đẹp, các bạn nghĩ sao?" />
        <meta property="og:title" content="Creator (@creator) on Threads" />
      </head>
      <body>
        <script type="application/json" data-sjs>{json_str}</script>
      </body>
    </html>
    """
    soup = BeautifulSoup(html_fixture, "html.parser")
    post = crawler._parse_html(soup, "test_id", "https://threads.net/@creator/post/test_id", "creator", 20)
    assert post.author_username == "creator"
    assert "Hôm nay trời rất đẹp" in post.content
    assert len(post.comments) >= 1
    assert any(c.author_username == "fan1" for c in post.comments)
