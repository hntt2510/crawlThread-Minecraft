import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.parse
import httpx
import re
from bs4 import BeautifulSoup

query = 'giẻ lau site:threads.net'
url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

with httpx.Client(headers=headers, timeout=10.0, follow_redirects=True) as client:
    resp = client.get(url)
    print('DuckDuckGo Status:', resp.status_code)
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = soup.find_all('a', class_='result__snippet')
    links = soup.find_all('a', class_='result__url')
    print(f'Snippets found: {len(results)}')
    for i, (r, l) in enumerate(zip(results[:5], links[:5])):
        print(f'{i+1}. URL: {l.get_text().strip()}')
        print(f'   Snippet: {r.get_text().strip()}')

