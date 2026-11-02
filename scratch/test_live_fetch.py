import sys
sys.stdout.reconfigure(encoding='utf-8')
from backend.app.services.discovery.threads_search_provider import threads_search_provider

posts = threads_search_provider.search_threads_web('dọn nhà', limit=10)
print(f'Found {len(posts)} posts for "dọn nhà":')
for p in posts[:5]:
    txt = p["text"].replace('\n', ' ')
    print(f'- @{p["username"]}: {txt[:100]}... (likes: {p["like_count"]}, replies: {p["reply_count"]})')

