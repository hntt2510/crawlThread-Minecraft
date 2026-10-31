import sys
sys.stdout.reconfigure(encoding='utf-8')
from backend.app.services.crawler.relay_crawler import ThreadsRelayCrawler

def test_crawler_live():
    crawler = ThreadsRelayCrawler()
    url = "https://www.threads.net/@zuck/post/DeZgeQhm6RW"
    post = crawler.crawl_post_and_comments(url, max_comments=10)
    print("Crawled post root:")
    print("  ID:", post.id)
    print("  Author:", post.author_username, f"({post.author_display_name})")
    print("  Content:", post.content[:80])
    print("  Comments found:", len(post.comments))
    for i, c in enumerate(post.comments[:5]):
        print(f"  [{i}] @{c.author_username}: {c.content[:50]} (Likes: {c.like_count})")
    assert len(post.id) > 0
    assert len(post.comments) > 0
    print("TEST CRAWLER PASSED!")

if __name__ == "__main__":
    test_crawler_live()
