import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.parse
import httpx
import json
from bs4 import BeautifulSoup
from backend.app.services.crawler.relay_crawler import ThreadsRelayCrawler

crawler = ThreadsRelayCrawler()
test_queries = ['gie lau', 'lau nhà', 'dọn nhà', 'khăn lau', 'giẻ', 'đồ gia dụng']

with httpx.Client(headers=crawler.DEFAULT_HEADERS, timeout=12.0, follow_redirects=True) as client:
    for q in test_queries:
        encoded_q = urllib.parse.quote(q)
        url = f'https://www.threads.net/search?q={encoded_q}'
        resp = client.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        edges_found = []
        for s in soup.find_all('script'):
            txt = s.string or s.get_text()
            if not txt or 'searchResults' not in txt:
                continue
            try:
                data = json.loads(txt.strip())
                def find_edges(obj):
                    if isinstance(obj, dict):
                        if 'searchResults' in obj and isinstance(obj['searchResults'], dict):
                            edges = obj['searchResults'].get('edges', [])
                            if edges:
                                edges_found.extend(edges)
                        for v in obj.values():
                            find_edges(v)
                    elif isinstance(obj, list):
                        for item in obj:
                            find_edges(item)
                find_edges(data)
            except Exception:
                pass
        print(f'Query: "{q}" -> status {resp.status_code}, edges: {len(edges_found)}')

