"""
fetch_article.py — Phase 2 STEP A의 본문/이미지/링크/날짜 추출 스크립트.

사용법:
    python3 scripts/fetch_article.py "https://example.com/article"

동작:
    1. curl로 페이지 페치. 빈 응답·짧은 응답·봇 차단 페이지 감지 시
       CURL_FAILED 신호 출력 후 종료(루틴이 WebFetch로 폴백하도록).
    2. og:image / twitter:image / lazy-load 컨테이너 / 큰 이미지 순으로
       정규식 폴백 체인 실행.
    3. 외부 도메인 링크 + YouTube/Vimeo/GitHub/HuggingFace/demo/trial 등
       유용한 추가 링크 후보 8개까지 추출.
    4. 본문 텍스트(스크립트·네비·푸터 제거 후) 6000자 추출.
    5. og:image와 모든 폴백이 실패하면 NEEDS_WEBFETCH_FOR_IMAGE 신호 출력
       (루틴이 WebFetch로 hero image를 찾도록).

출력 형식 (Routine 프롬프트가 의존하는 라인):
    OG_IMAGE: <url-or-NO_IMAGE>
    LINK: <url> (0개 이상)
    ---ARTICLE_TEXT---
    <body text>
    ---NEEDS_WEBFETCH_FOR_IMAGE--- (이미지 추출 실패 시에만)
"""

import sys
import subprocess
import re
from urllib.parse import urljoin, urlparse


def fetch_with_curl(url: str) -> str:
    """curl로 페이지 HTML을 가져온다. Googlebot UA로 봇 차단을 우회한다."""
    result = subprocess.run(
        ['curl', '-s', '-L', '--max-time', '8',
         '-H', 'User-Agent: Mozilla/5.0 (compatible; Googlebot/2.1)', url],
        capture_output=True, text=True, timeout=12
    )
    return result.stdout


def is_curl_failure(html: str) -> bool:
    """빈 응답·짧은 응답·봇 차단 페이지를 curl 실패로 판정."""
    if not html or len(html) < 500:
        return True
    visible_len = len(re.sub(r'<[^>]+>', ' ', html).strip())
    if visible_len < 300:
        return True
    bot_block_patterns = [
        r'just a moment', r'enable javascript', r'access denied',
        r'cloudflare', r'captcha', r'are you a robot',
    ]
    return any(re.search(p, html, re.IGNORECASE) for p in bot_block_patterns)


def extract_image(html: str) -> str:
    """og:image → twitter:image → lazy-load img → 큰 이미지 순으로 시도."""
    patterns = [
        r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
        r'content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']',
        r'name=["\']twitter:image["\'][^>]*content=["\']([^"\']+)["\']',
        r'content=["\']([^"\']+)["\'][^>]*name=["\']twitter:image["\']',
        # 일반 article 컨테이너 내부의 첫 img (lazy-load 속성 포함)
        r'<(?:article|div[^>]*class=["\'][^"\']*(?:post-thumbnail|entry-content|featured-image)[^"\']*["\'])[^>]*>[\s\S]*?<img[^>]+(?:data-src|data-lazy-src|src)=["\']([^"\']+)["\']',
        # 마지막 수단: width 500px 이상의 큰 이미지
        r'<img[^>]+(?:data-src|data-lazy-src|src)=["\']([^"\']+\.(?:jpg|jpeg|png|webp))["\'][^>]*width=["\'](?:[5-9]\d{2}|\d{4,})',
    ]
    for p in patterns:
        m = re.search(p, html, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ''


def extract_extra_links(html: str, source_url: str) -> list:
    """외부 도메인 + 유용한 키워드를 가진 링크 후보 최대 8개 추출."""
    hrefs = re.findall(
        r'<a[^>]+href=["\']([^"\'#][^"\']*)["\']',
        html, re.IGNORECASE
    )
    base = urlparse(source_url).netloc
    links, seen = [], set()
    useful_keywords = [
        'github.com', 'huggingface.co', 'demo', 'trial',
        'product', 'features', 'release', 'launch', 'app'
    ]
    video_hosts = ['youtube.com', 'youtu.be', 'vimeo.com']

    for href in hrefs:
        full = href if href.startswith('http') else urljoin(source_url, href)
        parsed = urlparse(full)
        if full in seen:
            continue
        if not parsed.netloc or parsed.netloc == base:
            continue
        is_video = any(v in parsed.netloc for v in video_hosts)
        is_product = any(k in full.lower() for k in useful_keywords)
        if is_video or is_product:
            seen.add(full)
            links.append(full)
        if len(links) >= 8:
            break
    return links


def extract_body_text(html: str, max_chars: int = 6000) -> str:
    """스크립트·네비·푸터 제거 후 가시 본문 텍스트 추출."""
    clean = re.sub(
        r'<(script|style|nav|footer|header|aside|iframe|form)[^>]*>.*?</\1>',
        '', html, flags=re.DOTALL | re.IGNORECASE
    )
    clean = re.sub(r'<[^>]+>', ' ', clean)
    clean = re.sub(r'[ \t]+', ' ', clean)
    clean = re.sub(r'\n\s*\n+', '\n', clean).strip()
    return clean[:max_chars]


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/fetch_article.py <URL>", file=sys.stderr)
        sys.exit(2)

    url = sys.argv[1]
    html = fetch_with_curl(url)

    if is_curl_failure(html):
        print("CURL_FAILED — body empty, too short, or bot-blocked.")
        print("Retry this article using the WebFetch tool with the same URL,")
        print("then continue with the same image/link/text extraction logic")
        print("on the WebFetch output. Do NOT skip the article unless WebFetch")
        print("also fails or the resulting text is still too short.")
        sys.exit(0)

    image_url = extract_image(html)
    links = extract_extra_links(html, url)
    article_text = extract_body_text(html)

    print("OG_IMAGE:", image_url or "NO_IMAGE")
    for link in links:
        print("LINK:", link)
    print("---ARTICLE_TEXT---")
    print(article_text)

    # curl은 성공했지만 이미지 추출이 실패한 경우 — WebFetch 폴백 트리거
    if not image_url:
        print("---NEEDS_WEBFETCH_FOR_IMAGE---")
        print("OG:image and all fallback patterns failed on this URL.")
        print("Run WebFetch on the same URL and scan its markdown output for")
        print("the article's hero image. Use that URL in the image field.")


if __name__ == '__main__':
    main()
