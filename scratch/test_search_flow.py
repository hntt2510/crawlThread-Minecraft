import sys
sys.stdout.reconfigure(encoding='utf-8')
from backend.app.services.discovery.discovery_service import discovery_service

for s in ["hot", "comments", "latest"]:
    res = discovery_service.search_trending(keyword='giẻ lau', sort_by=s, limit=5)
    print(f"\n--- Sort by {s.upper()} ({res.total} posts) ---")
    for idx, p in enumerate(res.posts[:3]):
        print(f" {idx+1}. @{p.author_username} | likes={p.like_count}, replies={p.reply_count}, score={p.hot_score}:")
        print(f"    {p.content[:70]}...")
