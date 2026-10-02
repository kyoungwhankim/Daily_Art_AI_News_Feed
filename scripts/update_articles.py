"""
update_articles.py — /tmp/feed/articles.json의 새 기사들을
                     오늘 날짜 파일(data/articles/YYYY-MM-DD.json)에 추가한다.

사용법:
    python3 scripts/update_articles.py

전제:
    - 작업 디렉터리 = 레포 루트 (Routine 환경에서는 /home/user/Daily_Art_AI_News_Feed)
    - /tmp/feed/articles.json — PHASE 2가 만든 새 기사 리스트

동작:
    1. data/articles/*.json 전체에서 기존 id, url을 수집.
    2. 새 기사 중 url이 이미 존재하면 스킵 (URL dedup — scheme·www.·끝 '/'·
       fragment 차이는 같은 URL로 본다. calendar-day RECENCY 룰의 부작용으로
       같은 글이 어제·오늘에 두 번 게시되는 것을 방지).
    3. 각 새 기사에 고유 slug id를 생성 (`{tab}-{md5_8자}-{YYYY-MM}` 형식,
       충돌 시 `-2`, `-3` 접미사 추가)하고 publishedAt에 오늘 날짜를 넣는다.
       keywords는 루틴이 고른 값을 쓰되, 그 탭의 고정 목록(data/keywords.json)에
       없는 값은 경고를 출력하고 버린다. 순서는 목록 순서로 맞춘다.
    4. 오늘 날짜 파일에 탭(games → industry → art)별로, 같은 탭의 기존 기사보다
       앞에 삽입한다. 파일이 없으면 새로 만든다.
    5. data/index.json을 다시 생성한다.

출력:
    추가된 기사 수와 섹션별 분포를 stdout에 출력.
"""

import hashlib
import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feed_data  # noqa: E402

NEW_ARTICLES_JSON = '/tmp/feed/articles.json'


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


def build_entry(art: dict, idx: int, slug_suffix: str, upload_date: str,
                existing_ids: set, keyword_lists: dict) -> dict:
    """기사 dict를 사이트 데이터 형식으로 변환 (필드 순서 고정)."""
    entry = {
        'id': make_slug(art['headline'], art['tab'], idx,
                        slug_suffix, existing_ids),
        'tab': art['tab'],
        'headline': art['headline'],
        'summary': art['summary'],
        'body': art['body'],
        'source': art['source'],
        'publishedAt': upload_date,
        'hue': int(art['hue']),
    }
    if art.get('image'):
        entry['image'] = art['image']
    allowed = keyword_lists.get(art['tab'], [])
    given = art.get('keywords') or []
    unknown = [k for k in given if k not in allowed]
    if unknown:
        print(f"⚠️  Dropped keywords not in the {art['tab']} list: {unknown} "
              f"— {art['headline'][:40]}")
    entry['keywords'] = [k for k in allowed if k in given]
    entry['url'] = art['url']
    if art.get('urls'):
        entry['urls'] = [{'label': lk['label'], 'href': lk['href']}
                         for lk in art['urls']]
    return entry


def main():
    today = date.today()
    upload_date = today.strftime('%Y.%m.%d')
    slug_suffix = today.strftime('%Y-%m')
    day_file = feed_data.date_to_filename(upload_date)

    with open(NEW_ARTICLES_JSON) as f:
        new_articles = json.load(f)

    keyword_lists = feed_data.keyword_lists()

    # 기존 id와 url 수집 — id는 충돌 방지용, url은 dedup용
    existing_ids, existing_urls = set(), set()
    for name in feed_data.date_files():
        for a in feed_data.read_day(name):
            existing_ids.add(a['id'])
            existing_urls.add(feed_data.normalize_url(a['url']))

    # tab별로 그룹화하면서 이미 게시된 url은 스킵 (URL dedup).
    by_tab = {t: [] for t in feed_data.TABS}
    skipped_dup = 0
    for i, art in enumerate(new_articles):
        key = feed_data.normalize_url(art.get('url'))
        if key in existing_urls:
            skipped_dup += 1
            continue
        if art['tab'] not in by_tab:
            raise RuntimeError(f"Unknown tab: {art['tab']!r}")
        existing_urls.add(key)
        by_tab[art['tab']].append(
            build_entry(art, i, slug_suffix, upload_date, existing_ids,
                        keyword_lists))

    if skipped_dup:
        print(f"Skipped {skipped_dup} article(s) already present in "
              f"data/articles (URL dedup).")

    added = sum(len(v) for v in by_tab.values())
    if added:
        existing_today = (feed_data.read_day(day_file)
                          if day_file in feed_data.date_files() else [])
        merged = []
        for tab in feed_data.TABS:
            merged += by_tab[tab]
            merged += [a for a in existing_today if a['tab'] == tab]
        merged += [a for a in existing_today if a['tab'] not in feed_data.TABS]
        feed_data.write_day(day_file, merged)
    feed_data.write_index()

    print(f"Updated data/articles/{day_file}: +{added} new articles.")
    print(f"  games:    +{len(by_tab['games'])}")
    print(f"  industry: +{len(by_tab['industry'])}")
    print(f"  art:      +{len(by_tab['art'])}")
    for tab in feed_data.TABS:
        for e in by_tab[tab]:
            print(f"  [{tab}] {', '.join(e['keywords']) or '(no keywords)'}"
                  f" — {e['headline'][:40]}")


if __name__ == '__main__':
    main()
