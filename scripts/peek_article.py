#!/usr/bin/env python3
"""peek_article.py — 루틴 PHASE 1 STEP A: 기사 하나를 빠르게 읽어 og:image · 관련 링크 · 본문 앞부분(3000자)을 보여 준다.

    python3 scripts/peek_article.py "https://기사-주소"

(예전에는 루틴 프롬프트에 같은 코드를 직접 넣어 매번 붙여 넣었다. 동작은 같다.)
PHASE 2 STEP 3은 scripts/fetch_article.py(본문 8000자, WebFetch 필요 여부 표시)를 쓴다.
"""
import subprocess, re, sys
from urllib.parse import urljoin, urlparse

url = sys.argv[1]
result = subprocess.run(
    ['curl', '-s', '-L', '--max-time', '8',
     '-H', 'User-Agent: Mozilla/5.0 (compatible; Googlebot/2.1)', url],
    capture_output=True, text=True, timeout=12
)
html = result.stdout

# Extract og:image
image_url = ''
for p in [
    r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
    r'content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']',
    r'name=["\']twitter:image["\'][^>]*content=["\']([^"\']+)["\']',
    r'content=["\']([^"\']+)["\'][^>]*name=["\']twitter:image["\']',
]:
    m = re.search(p, html, re.IGNORECASE)
    if m:
        image_url = m.group(1).strip()
        break

# Extract candidate links
hrefs = re.findall(r'<a[^>]+href=["\']([^"\'#][^"\']*)["\']', html, re.IGNORECASE)
base = urlparse(url).netloc
links, seen = [], set()
for href in hrefs:
    full = href if href.startswith('http') else urljoin(url, href)
    p = urlparse(full)
    if full not in seen and p.netloc and p.netloc != base and (
        any(v in p.netloc for v in ['youtube.com','youtu.be','vimeo.com']) or
        any(k in full.lower() for k in ['github.com','huggingface.co','demo',
            'trial','product','features','release','launch','app'])
    ):
        seen.add(full); links.append(full)
    if len(links) >= 8: break

# Extract visible article body text
clean = re.sub(r'<(script|style|nav|footer|header|aside|iframe|form)[^>]*>.*?</\1>',
               '', html, flags=re.DOTALL|re.IGNORECASE)
clean = re.sub(r'<[^>]+>', ' ', clean)
clean = re.sub(r'[ \t]+', ' ', clean)
clean = re.sub(r'\n\s*\n+', '\n', clean).strip()
article_text = clean[:3000]

print("OG_IMAGE:", image_url or "NO_IMAGE")
for l in links:
    print("LINK:", l)
print("---ARTICLE_TEXT---")
print(article_text)
