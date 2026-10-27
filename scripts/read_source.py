#!/usr/bin/env python3
"""
read_source.py — 업데이트 출처(config.js updateSources의 notice·dev 주소) 하나를 읽어 텍스트로 보여 준다.
업데이트 수집 에이전트(routine/updates_agent_prompt.txt)가 쓴다.

    python3 scripts/read_source.py URL [--since YYYY.MM.DD] [--limit N] [--chars N] [--offset N]

    RSS·Atom  → 글마다 날짜 · 제목 · 링크 · 요약 (최신순). --since로 그 날짜 이후 글만
    JSON      → 보기 좋게 펼친 텍스트
    HTML·기타 → 본문 텍스트 (스크립트·스타일 제거). 길면 --offset으로 이어 읽는다

첫 줄은 항상 `SOURCE: <url>  STATUS: <code>  TYPE: <rss|atom|json|html|text>`.
STATUS가 200이 아니거나 본문이 거의 비어 있으면(스크립트로만 그리는 페이지) WebFetch로 다시 읽는다.
"""

import argparse
import datetime as dt
import email.utils
import html as htmlmod
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'



def parse_xml(body: str):
    """피드·사이트맵 XML을 읽는다. 끝 태그 뒤에 스크립트가 붙었거나 뿌리 요소가 여럿인 파일도 받아 준다."""
    raw = body.lstrip()
    try:
        return ET.fromstring(raw.encode('utf-8'))
    except ET.ParseError:
        pass
    raw = re.sub(r'^<\?xml[^>]*\?>', '', raw).strip()
    m = re.match(r'<(rss|feed|rdf:RDF|urlset|sitemapindex)\b', raw)
    if m:
        # 끝 태그 뒤의 스크립트를 떼고, 중간에 잘못 들어간 끝 태그(</urlset> 뒤에 <url>이 더 있는 사이트맵)를 지운다
        name = m.group(1)
        ends = [raw.rfind(t) + len(t) for t in ('</item>', '</entry>', '</url>', '</sitemap>', f'</{name}>')
                if raw.rfind(t) >= 0]
        body = raw[:max(ends)] if ends else raw
        body = body.replace(f'</{name}>', '')
        if name == 'rss':
            body = body.replace('</channel>', '') + '</channel>'
        try:
            return ET.fromstring((body + f'</{name}>').encode('utf-8'))
        except ET.ParseError:
            pass
    return ET.fromstring(('<root>' + raw + '</root>').encode('utf-8'))   # 뿌리가 여럿이면 하나로 묶는다


def fetch(url: str):
    r = subprocess.run(['curl', '-sS', '-L', '--max-time', '25', '-A', UA, '-H', 'Accept: */*',
                        '-w', '\n__STATUS__%{http_code} %{content_type}', url],
                       capture_output=True, timeout=40)
    out = r.stdout.decode('utf-8', 'replace')
    body, _, tail = out.rpartition('\n__STATUS__')
    status, _, ctype = tail.partition(' ')
    return status or '000', ctype, body


def strip_tags(s: str) -> str:
    s = re.sub(r'<(script|style|noscript|svg|nav|footer|form)[^>]*>.*?</\1>', ' ', s, flags=re.S | re.I)
    s = re.sub(r'<br\s*/?>|</(p|div|li|h[1-6]|tr|section|article)>', '\n', s, flags=re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = htmlmod.unescape(s)
    s = re.sub(r'[ \t\r\f\v]+', ' ', s)
    s = re.sub(r'\n\s*\n+', '\n', s)
    return s.strip()


def parse_date(s: str):
    s = (s or '').strip()
    if not s:
        return None
    try:
        return email.utils.parsedate_to_datetime(s).date()
    except (TypeError, ValueError):
        pass
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        return dt.date(*map(int, m.groups()))
    return None


def local(tag: str) -> str:
    return tag.rsplit('}', 1)[-1]


def feed_items(root):
    items = []
    for el in root.iter():
        t = local(el.tag)
        if t not in ('item', 'entry', 'url'):
            continue
        rec = {'title': '', 'link': '', 'date': None, 'text': ''}
        if t == 'url':      # 사이트맵: <loc> 주소와 <lastmod> 날짜만 있다 — 주소 끝부분을 제목으로
            for c in el:
                if local(c.tag) == 'loc':
                    rec['link'] = (c.text or '').strip()
                    rec['title'] = rec['link'].rstrip('/').rsplit('/', 1)[-1].replace('-', ' ')
                elif local(c.tag) == 'lastmod':
                    rec['date'] = parse_date(c.text)
            if rec['link']:
                items.append(rec)
            continue
        for c in el:
            ct = local(c.tag)
            if ct == 'title':
                rec['title'] = strip_tags(c.text or '')
            elif ct == 'link':
                rec['link'] = c.get('href') or (c.text or '').strip() or rec['link']
            elif ct in ('pubDate', 'published', 'updated', 'date') and not rec['date']:
                rec['date'] = parse_date(c.text)
            elif ct in ('description', 'summary', 'content', 'encoded') and len(rec['text']) < 50:
                rec['text'] = strip_tags(c.text or '')
        items.append(rec)
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('url')
    ap.add_argument('--since', help='YYYY.MM.DD — feeds: only items on or after this date')
    ap.add_argument('--limit', type=int, default=60, help='feeds: max items (default 60)')
    ap.add_argument('--chars', type=int, default=12000, help='html/text: characters to print')
    ap.add_argument('--offset', type=int, default=0, help='html/text: start position')
    args = ap.parse_args()

    status, ctype, body = fetch(args.url)
    head = body.lstrip()[:400].lower()
    kind = 'html'
    if head.startswith('<?xml') or '<rss' in head or '<feed' in head:
        kind = 'atom' if '<feed' in head else 'rss'
    elif 'json' in ctype or head.startswith(('{', '[')):
        kind = 'json'
    elif args.url.endswith(('.md', '.txt')) or 'text/plain' in ctype or 'markdown' in ctype:
        kind = 'text'
    print(f'SOURCE: {args.url}  STATUS: {status}  TYPE: {kind}')


    if kind in ('rss', 'atom'):
        try:
            root = parse_xml(body)
        except ET.ParseError as e:
            print(f'PARSE_ERROR: {e} — read it as HTML/WebFetch instead')
            return
        since = dt.date(*map(int, args.since.split('.'))) if args.since else None
        items = feed_items(root)
        items.sort(key=lambda r: r['date'] or dt.date.min, reverse=True)
        shown = 0
        for r in items:
            if since and r['date'] and r['date'] < since:
                continue
            d = r['date'].strftime('%Y.%m.%d') if r['date'] else '????.??.??'
            print(f"\n[{d}] {r['title']}\n  {r['link']}\n  {r['text'][:400]}")
            shown += 1
            if shown >= args.limit:
                break
        print(f'\n--- {shown} of {len(items)} items shown'
              + (f' (since {args.since})' if since else '') + ' ---')
        return

    if kind == 'json':
        try:
            text = json.dumps(json.loads(body), ensure_ascii=False, indent=1)
        except ValueError:
            text = body
    elif kind == 'text':
        text = body
    else:
        text = strip_tags(body)
    part = text[args.offset:args.offset + args.chars]
    print(part)
    more = len(text) - (args.offset + len(part))
    print(f'\n--- chars {args.offset}–{args.offset + len(part)} of {len(text)}'
          + (f'; {more} more → --offset {args.offset + len(part)}' if more > 0 else '') + ' ---')
    if kind == 'html' and len(text) < 500:
        print('NOTE: almost no text — the page is probably drawn by JavaScript. Use WebFetch for this URL.')


if __name__ == '__main__':
    sys.exit(main())
