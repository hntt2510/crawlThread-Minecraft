import sys
sys.stdout.reconfigure(encoding='utf-8')
from backend.app.services.discovery.threads_search_provider import threads_search_provider

queries = ['chuyện đi làm', 'sếp', 'đồng nghiệp', 'red flag', 'hẹn hò', 'sinh viên', 'ở trọ', 'quán cafe', 'đồ gia dụng', 'dọn nhà', 'overthinking']

for q in queries:
    items = threads_search_provider.search_threads_web(q, limit=10)
    print(f'Query "{q}": {len(items)} items')
    if items:
        first = items[0]
        print(f'   First: @{first["username"]} ({first["like_count"]} likes, {first["reply_count"]} replies): {first["text"][:70]}...')

