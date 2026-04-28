"""
update_articles_js.py — /tmp/feed/articles.json의 새 기사들을
                         articles.js의 적절한 섹션에 삽입한다.

사용법:
    python3 scripts/update_articles_js.py

전제:
    - 작업 디렉터리 = articles.js가 있는 레포 루트
      (Routine 환경에서는 /home/user/Daily_Art_AI_News_Feed)
    - /tmp/feed/articles.json — Phase 2가 만든 새 기사 리스트
    - articles.js에 다음 섹션 마커가 정확히 한 번씩 존재:
        /* ---- games ---- */
        /* ---- industry ---- */
        /* ---- art ---- */
        /* ---- repos ---- */

동작:
    1. articles.js를 읽고 기존 id, url을 수집.
    2. 새 기사 중 url이 이미 존재하면 스킵 (URL dedup — calendar-day RECENCY
       룰의 부작용으로 같은 글이 어제·오늘에 두 번 게시되는 것을 방지).
    3. 각 새 기사에 고유 slug id를 생성 (`{tab}-{md5_8자}-{YYYY-MM}` 형식,
       충돌 시 `-2`, `-3` 접미사 추가).
    4. JS 객체 리터럴로 렌더링하고 해당 섹션 마커 바로 다음 줄에 삽입.
    5. 결과를 articles.js에 덮어쓴다.

출력:
    추가된 기사 수와 섹션별 분포를 stdout에 출력.
"""

import json
import re
import os
import hashlib
import sys
from datetime import date


REPO = os.environ.get('REPO_PATH', '/home/user/Daily_Art_AI_News_Feed')
ARTICLES_JS = os.path.join(REPO, 'articles.js')
NEW_ARTICLES_JSON = '/tmp/feed/articles.json'

SECTION_MARKERS = {
    'games':    '/* ---- games ---- */',
    'industry': '/* ---- industry ---- */',
    'art':      '/* ---- art ---- */',
    'repos':    '/* ---- repos ---- */',
}


def js_string(s: str) -> str:
    """파이썬 문자열을 JS 단일 따옴표 문자열 리터럴로 변환."""
    s = s.replace('\\', '\\\\').replace("'", "\\'")
    return "'" + s + "'"


def make_slug(headline: str, tab: str, idx: int,
              slug_suffix: str, existing_ids: set) -> str:
    """`{tab}-{md5_8자}-{YYYY-MM}` 형식의 고유 slug 생성."""
    base = f"{tab}-{hashlib.md5((headline + str(idx)).encode()).hexdigest()[:8]}"
    candidate = f"{base}-{slug_suffix}"
    n = 2
    while candidate in existing_ids:
        candidate = f"{base}-{n}-{slug_suffix}"
        n += 1
    existing_ids.add(candidate)
    return candidate


def render_article(art: dict, idx: int,
                   slug_suffix: str, upload_date: str,
                   existing_ids: set) -> str:
    """기사 dict를 JS 객체 리터럴 문자열로 변환."""
    aid = make_slug(art['headline'], art['tab'], idx,
                    slug_suffix, existing_ids)
    lines = ['        {']
    lines.append(f"            id:          {js_string(aid)},")
    lines.append(f"            tab:         {js_string(art['tab'])},")
    lines.append(f"            headline:    {js_string(art['headline'])},")
    lines.append(f"            summary:     {js_string(art['summary'])},")
    lines.append(f"            body:        {js_string(art['body'])},")
    lines.append(f"            source:      {js_string(art['source'])},")
    lines.append(f"            publishedAt: {js_string(upload_date)},")
    lines.append(f"            hue:         {int(art['hue'])},")
    if art.get('image'):
        lines.append(f"            image:       {js_string(art['image'])},")
    lines.append(f"            url:         {js_string(art['url'])},")
    if art.get('urls'):
        lines.append(f"            urls: [")
        for lk in art['urls']:
            lines.append(
                f"                {{ label: {js_string(lk['label'])}, "
                f"href: {js_string(lk['href'])} }},"
            )
        lines.append(f"            ],")
    lines.append('        },')
    return '\n'.join(lines)


def main():
    today = date.today()
    upload_date = today.strftime('%Y.%m.%d')
    slug_suffix = today.strftime('%Y-%m')

    with open(NEW_ARTICLES_JSON) as f:
        new_articles = json.load(f)

    with open(ARTICLES_JS, 'r', encoding='utf-8') as f:
        original = f.read()

    # 기존 id와 url 수집 — id는 충돌 방지용, url은 dedup용
    existing_ids = set(re.findall(r"id:\s*'([^']+)'", original))
    existing_urls = set(re.findall(r"url:\s*'([^']+)'", original))

    # tab별로 그룹화하면서 이미 게시된 url은 스킵 (URL dedup).
    by_tab = {'games': [], 'industry': [], 'art': [], 'repos': []}
    skipped_dup = 0
    for i, art in enumerate(new_articles):
        if art.get('url') in existing_urls:
            skipped_dup += 1
            continue
        by_tab[art['tab']].append((i, art))

    if skipped_dup:
        print(f"Skipped {skipped_dup} article(s) already present in "
              f"articles.js (URL dedup).")

    # 각 섹션 마커 바로 다음에 새 기사 블록 삽입
    updated = original
    for tab, items in by_tab.items():
        if not items:
            continue
        marker = SECTION_MARKERS[tab]
        if marker not in updated:
            raise RuntimeError(
                f"Section marker not found in articles.js: {marker}"
            )
        block = '\n'.join(
            render_article(a, i, slug_suffix, upload_date, existing_ids)
            for i, a in items
        )
        updated = updated.replace(marker, marker + '\n' + block, 1)

    with open(ARTICLES_JS, 'w', encoding='utf-8') as f:
        f.write(updated)

    added = sum(len(v) for v in by_tab.values())
    print(f"Updated articles.js: +{added} new articles.")
    print(f"  games:    +{len(by_tab['games'])}")
    print(f"  industry: +{len(by_tab['industry'])}")
    print(f"  art:      +{len(by_tab['art'])}")
    print(f"  repos:    +(len(by_tab['repos'])}")


if __name__ == '__main__':
    main()
