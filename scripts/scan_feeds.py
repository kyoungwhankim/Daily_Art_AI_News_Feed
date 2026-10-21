#!/usr/bin/env python3
"""scan_feeds.py — 루틴 PHASE 1 시작 때 출처 피드를 한꺼번에 훑어 오늘·어제(KST) 글만 짧은 목록으로 보여 준다.

예전에는 모델이 출처 피드를 하나씩 열어 원문 XML을 대화에 쌓았고, 그 글이 매 턴 다시 읽혀 비용이 컸다.
이 스크립트는 피드를 대화 밖에서 읽고 후보 목록만 남긴다.

  python3 scripts/scan_feeds.py              피드 전부 → 후보 목록 출력 + /tmp/feed/candidates.json 저장
  python3 scripts/scan_feeds.py --days 3     최근 3일(KST)까지 보기 (기본 2 = 오늘·어제)
  python3 scripts/scan_feeds.py --source kotaku.com --all    한 출처만, AI 단어 거르기 없이

피드 주소는 routine/feeds.txt. 이미 data/articles에 실린 주소는 뺀다.
AI 전문 출처가 아니면 제목·요약에 AI 관련 단어가 있는 글만 남긴다.
피드가 없는 출처와 읽기에 실패한 피드는 끝에 따로 알려 준다 — 그쪽은 지침대로 직접 확인한다.
"""
import html
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feed_data import date_files, normalize_url, read_day   # noqa: E402
from fetch_article import BROWSER_UA                        # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEEDS = os.path.join(REPO, 'routine', 'feeds.txt')
OUT = '/tmp/feed/candidates.json'
KST = timezone(timedelta(hours=9))
PER_SOURCE = 12          # 한 출처에서 보여 줄 최대 글 수
DESC_LEN = 60            # 요약 앞부분 글자 수

# AI 전문 출처가 아닌 피드에서 글을 남기는 기준 (제목 + 요약 앞부분)
AI_SHORT = re.compile(r'(?<![A-Za-z])A\.?Is?(?![A-Za-z])|(?<![A-Za-z])KI(?![A-Za-z])|GenAI|\bLLMs?\b')   # 약어는 대문자만
AI_LONG = re.compile(
    r'\bGPT|OpenAI|Anthropic|\bClaude\b|Gemini|Copilot|Midjourney|Stable Diffusion|Stability|\bVeo\b|'
    r'Runway|ElevenLabs|artificial intelligence|machine.learning|deep learning|neural|generative|diffusion model|'
    r'chatbot|agentic|künstliche Intelligenz|인공지능|생성형|人工知能|機械学習|生成系|人工智能|大模型|生成式|智能体', re.I)


def is_ai(item):
    text = item['title'] + ' ' + item['desc'][:200]    # 요약 끝까지 보면 관련 없는 글이 많이 걸린다
    return bool(AI_SHORT.search(text) or AI_LONG.search(text))


def load_feeds():
    rows = []
    for line in open(FEEDS, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        rows.append({'source': parts[0], 'url': parts[1], 'ai': 'ai' in parts[2:]})
    return rows


def fetch(url):
    try:
        r = subprocess.run(['curl', '-s', '-L', '--compressed', '--max-time', '15',
                            '-H', f'User-Agent: {BROWSER_UA}', '-w', '\n%{http_code}', url],
                           capture_output=True, timeout=25)
    except subprocess.TimeoutExpired:
        return None, 'timeout'
    body, _, code = r.stdout.rpartition(b'\n')
    code = code.decode(errors='replace').strip()
    if code != '200':
        return None, f'HTTP {code or "?"}'
    return body, None


def local(tag):
    return tag.rsplit('}', 1)[-1].lower()


def child_text(el, *names):
    for c in el:
        if local(c.tag) in names:
            if local(c.tag) == 'link' and c.get('href'):
                if c.get('rel', 'alternate') == 'alternate':
                    return c.get('href')
                continue
            t = ''.join(c.itertext()).strip()
            if t:
                return t
    return ''


def clean(s):
    s = re.sub(r'<[^>]+>', ' ', html.unescape(s or ''))
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()


def parse_date(s):
    s = (s or '').strip()
    if not s:
        return None
    try:
        d = parsedate_to_datetime(s)
    except (TypeError, ValueError):
        d = None
    if d is None:
        iso = re.sub(r'Z$', '+00:00', s.replace(' ', 'T', 1) if re.match(r'\d{4}-\d\d-\d\d \d', s) else s)
        try:
            d = datetime.fromisoformat(iso)
        except ValueError:
            m = re.match(r'(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})', s)
            if not m:
                return None
            d = datetime(*map(int, m.groups()))
    if d.tzinfo is None:          # 시간대가 없으면 출처 현지 시간으로 보지 않고 KST로 본다 (하루 차이는 범위가 흡수)
        d = d.replace(tzinfo=KST)
    return d.astimezone(KST)


def parse_feed(raw):
    """RSS 2.0 · RSS 1.0(RDF) · Atom 모두 item/entry를 찾아 (제목, 주소, 날짜, 요약)으로 돌려준다."""
    raw = re.sub(rb'^[^<]*', b'', raw, count=1)          # BOM·앞 공백
    end = max(raw.rfind(b'</rss>'), raw.rfind(b'</feed>'), raw.rfind(b'</rdf:RDF>'))
    if end > 0:                                          # 끝 태그 뒤에 스크립트를 붙여 보내는 곳이 있다 (unrealengine)
        raw = raw[:raw.index(b'>', end) + 1]
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        # 깨진 XML: 제어 문자·HTML 엔티티를 고쳐 한 번 더
        fixed = re.sub(rb'[\x00-\x08\x0b\x0c\x0e-\x1f]', b'', raw)
        fixed = re.sub(rb'&(?!(amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)', b'&amp;', fixed)
        root = ET.fromstring(fixed)
    items = []
    for el in root.iter():
        if local(el.tag) not in ('item', 'entry'):
            continue
        link = child_text(el, 'link')
        if not link:
            g = child_text(el, 'guid', 'id')
            link = g if g.startswith('http') else ''
        items.append({
            'title': clean(child_text(el, 'title')),
            'url': tidy_url(link),
            'date': parse_date(child_text(el, 'pubdate', 'published', 'date', 'updated', 'issued')),
            'desc': clean(child_text(el, 'description', 'summary', 'content', 'encoded')),
        })
    return items


def scan(feed):
    raw, err = fetch(feed['url'])
    if err:
        return feed, [], err
    try:
        return feed, parse_feed(raw), None
    except ET.ParseError as e:
        return feed, [], f'not a feed ({e})'


def tidy_url(u):
    """추적용 쿼리(utm_*, wt_mc 등)를 떼어 목록을 짧게 한다."""
    base, _, q = u.strip().partition('?')
    keep = [p for p in q.split('&') if p and not re.match(r'(utm_|wt_|ref=|source=|rss|f=rss)', p, re.I)]
    return base + ('?' + '&'.join(keep) if keep else '')


def published_urls():
    seen = set()
    for name in date_files():
        for a in read_day(name):
            for u in [a.get('url')] + [x.get('url') if isinstance(x, dict) else x for x in a.get('urls') or []]:
                if u:
                    seen.add(normalize_url(u))
    return seen


def main():
    arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    days = int(arg('--days', 2))
    only = arg('--source', None)
    no_filter = '--all' in sys.argv
    now = datetime.now(KST)
    since = (now - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    feeds = [f for f in load_feeds() if not only or f['source'] == only]
    if not feeds:
        sys.exit(f'no feed named {only} in routine/feeds.txt')
    seen = published_urls()
    with ThreadPoolExecutor(12) as ex:
        results = list(ex.map(scan, feeds))

    out, problems, total = [], [], 0
    print(f'Feed scan: {len(feeds)} feeds, items dated {since:%Y-%m-%d} ~ {now:%Y-%m-%d} (KST)')
    print('Format: date | title | url | first words of the summary. Already-published URLs are removed.\n')
    for feed, items, err in results:
        if err:
            problems.append(f"{feed['source']}: {err}")
            continue
        dated = [i for i in items if i['date']]
        if items and not dated:
            problems.append(f"{feed['source']}: feed has no dates")
            continue
        if not items:
            problems.append(f"{feed['source']}: feed is empty")
            continue
        recent = [i for i in dated if i['date'] >= since and i['url']]
        if not recent:
            latest = max(i['date'] for i in dated)
            if now - latest > timedelta(days=7):
                problems.append(f"{feed['source']}: stale feed (latest item {latest:%Y-%m-%d})")
            continue
        keep = [i for i in recent if normalize_url(i['url']) not in seen and (feed['ai'] or no_filter or is_ai(i))]
        keep.sort(key=lambda i: i['date'], reverse=True)
        if not keep:
            continue
        shown = keep if only else keep[:PER_SOURCE]
        total += len(shown)
        label = '' if feed['ai'] or no_filter else ' (AI-related only)'
        print(f"## {feed['source']} — {len(shown)}{' of ' + str(len(keep)) if len(keep) > len(shown) else ''}{label}")
        for i in shown:
            desc = i['desc'][:DESC_LEN] + ('…' if len(i['desc']) > DESC_LEN else '')
            print(f"- {i['date']:%m-%d} | {i['title']} | {i['url']}" + (f' | {desc}' if desc else ''))
            out.append({'source': feed['source'], 'date': i['date'].isoformat(), 'title': i['title'],
                        'url': i['url'], 'desc': i['desc'][:400]})
        print()

    if only:                       # 한 출처만 본 경우 전체 목록 파일은 덮어쓰지 않는다
        print(f'Feed scan done: {total} items.' + (' ' + problems[0] if problems else ''))
        return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f'Feed scan done: {total} candidates from {len(feeds) - len(problems)} readable feeds '
          f'(saved to {OUT}).')
    if problems:
        print('Feeds to check by hand (open the site the way SOURCE ACCESS NOTES says):')
        for p in problems:
            print('  - ' + p)


if __name__ == '__main__':
    main()
