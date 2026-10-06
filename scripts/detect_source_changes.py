#!/usr/bin/env python3
"""
detect_source_changes.py — 업데이트 출처 126곳 중 '지난번 이후 바뀐 곳'만 골라낸다 (AI 토큰을 쓰지 않는다).

업데이트 에이전트(routine/updates_agent_prompt.txt)는 이 결과에 나온 출처만 읽는다.
바뀌지 않은 출처는 새 업데이트가 없다는 뜻이라 열지 않는다.

    python3 scripts/detect_source_changes.py check  [--out /tmp/updates/changed.json]
        모든 출처를 받아 지난 상태(data/updates/source_state.json)와 비교한다.
        바뀐 출처·새 RSS 글·받지 못한 출처를 서비스별로 출력하고, 새 상태는
        /tmp/updates/source_state.next.json에 둔다 (아직 저장하지 않는다).
    python3 scripts/detect_source_changes.py commit [--failed /tmp/updates/failed_sources.txt]
        에이전트가 끝난 뒤 새 상태를 data/updates/source_state.json에 저장한다.
        --failed 파일에 적힌 출처(에이전트가 읽지 못한 곳)는 예전 상태를 남겨 다음 날 다시 고른다.

비교 방법:
    RSS·Atom  글마다 (링크, 제목)을 기억해 새 글이 있으면 '바뀜' — 새 글 목록도 함께 넘긴다
    그 밖     다음 중 하나라도 해당하면 '바뀜'
                - 스크립트·스타일·태그를 뺀 본문 텍스트가 달라짐
                - 페이지 안(스크립트 데이터 포함)에 처음 보는 같은 사이트 글 링크가 생김 — 글 목록이
                  스크립트 데이터에만 있는 블로그도 새 글을 알아챈다
                - 페이지 안에 처음 보는 날짜 문자열(2026-10-07, October 7, 2026 …)이 생김
              링크·날짜는 한 번 본 것을 기억해 두므로 순환하는 추천 글 링크 때문에 계속 바뀜으로 잡히지 않는다
    본문이 거의 없는 페이지(스크립트로 그리는 페이지)와 받지 못한 출처는 비교할 수 없어 매번 '확인 필요'
    서비스에 저장된 업데이트가 하나도 없으면(BACKFILL) 그 서비스의 출처는 모두 '확인 필요'
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import read_source  # noqa: E402
import service_updates as su  # noqa: E402

STATE_PATH = os.path.join(su.UPD_DIR, 'source_state.json')
NEXT_PATH = '/tmp/updates/source_state.next.json'
KEEP_EXTRA = 200          # 피드에서 빠진 예전 글을 더 기억해 둘 수 (지금 피드의 글은 모두 기억한다)
MIN_TEXT = 500            # 이보다 짧으면 스크립트로 그리는 페이지로 본다
KEEP_SEEN = 3000          # 페이지마다 기억할 링크·날짜 수
_MON = ('January|February|March|April|May|June|July|August|September|October|November|December|'
        'Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec')
DATE_RES = [re.compile(r'\b20\d\d-\d\d-\d\d\b'), re.compile(r'\b(?:%s)\.? \d{1,2},? 20\d\d\b' % _MON),
            re.compile(r'\b\d{1,2} (?:%s) 20\d\d\b' % _MON)]
ASSET_RE = re.compile(r'\.(js|css|png|jpe?g|svg|webp|gif|avif|woff2?|ttf|ico|json|xml|map|mp4|webm)$', re.I)


def short(x: str) -> str:
    return hashlib.sha1(x.encode('utf-8')).hexdigest()[:10]


def page_links(url: str, raw: str) -> set:
    """페이지(스크립트 데이터 포함)에 있는 같은 사이트 글 경로들."""
    host = urlparse(url).netloc
    raw = raw.replace('\\/', '/')
    paths = set(re.findall(r'(?:https?://' + re.escape(host) + r')?(/[A-Za-z0-9._~%-]+(?:/[A-Za-z0-9._~%-]+)+)', raw))
    def looks_like_post(p):
        segs = p.strip('/').split('/')
        # 긴 데이터 덩어리(base64 등)·해시 같은 경로·추적용 경로(/akam/…)는 글 링크가 아니다
        return (all(len(x) <= 100 for x in segs) and not any(re.fullmatch(r'[0-9a-f]{6,}', x) for x in segs)
                and segs[0] not in ('akam', 'cdn-cgi'))
    return {p for p in paths if not ASSET_RE.search(p) and '/_next/' not in p and '/static/' not in p
            and '/assets/' not in p and looks_like_post(p)}


def page_dates(raw: str) -> set:
    out = set()
    for r in DATE_RES:
        out |= {m.group(0) for m in r.finditer(raw)}
    return out


def load_json(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def fingerprint(url: str) -> dict:
    fp = _fingerprint(url)
    return _fingerprint(url) if fp['kind'] == 'failed' else fp   # 일시 오류는 한 번 더


def _fingerprint(url: str) -> dict:
    status, ctype, body = read_source.fetch(url)
    if not status.startswith('2'):
        return {'kind': 'failed', 'status': status}
    head = body.lstrip()[:400].lower()
    if head.startswith('<?xml') or '<rss' in head or '<feed' in head:
        try:
            root = ET.fromstring(body.lstrip().encode('utf-8'))
        except ET.ParseError:
            return {'kind': 'failed', 'status': 'parse-error'}
        items = []
        for r in read_source.feed_items(root):
            d = r['date'].strftime('%Y.%m.%d') if r['date'] else ''
            key = hashlib.sha1(((r['link'] or '') + '|' + (r['title'] or '')).encode('utf-8')).hexdigest()[:12]
            items.append({'key': key, 'date': d,
                          'title': r['title'], 'link': r['link']})
        return {'kind': 'feed', 'items': items}
    raw = body
    if 'json' in ctype or head.startswith(('{', '[')):
        text = body
    elif url.endswith(('.md', '.txt')) or 'text/plain' in ctype or 'markdown' in ctype:
        text = body
    else:
        text = read_source.strip_tags(body)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) < MIN_TEXT:
        return {'kind': 'js', 'status': status}
    # 숫자는 빼고 비교한다 ('3시간 전', 조회수 같은 값 때문에 매번 바뀜으로 잡히지 않게 — 날짜는 dates로 따로 본다)
    return {'kind': 'page', 'hash': hashlib.sha1(re.sub(r'\d+', '', text).encode('utf-8')).hexdigest()[:16],
            'chars': len(text),
            'links': sorted(short(p) for p in page_links(url, raw)), 'dates': sorted(page_dates(raw))}


def cmd_check(args):
    services = su.load_services()
    state = load_json(STATE_PATH, {})
    urls = sorted({u for s in services for k in ('notice', 'dev') for u in s[k]})
    def fp_for(u):
        fp, old = fingerprint(u), state.get(u) or {}
        # 같은 주소가 가끔 다른 형식(RSS ↔ 페이지)으로 응답한다 — 지난번과 형식이 다르면 다시 받아 본다
        for _ in range(2):
            if old.get('kind') not in ('feed', 'page') or fp['kind'] == old['kind']:
                break
            fp = _fingerprint(u)
        return fp
    with ThreadPoolExecutor(max_workers=10) as ex:
        fps = dict(zip(urls, ex.map(fp_for, urls)))
    today = su.today_kst().strftime('%Y.%m.%d')

    nxt, report = {}, []
    for s in services:
        backfill = not su.read_service(s['slug'])
        todo = []
        for kind in ('notice', 'dev'):
            for u in s[kind]:
                fp, old = fps[u], state.get(u)
                rec = {'url': u, 'source': kind}
                if fp['kind'] == 'feed':
                    known = set(old.get('items', [])) if old and old.get('kind') == 'feed' else None
                    new_items = [i for i in fp['items'] if known is None or i['key'] not in known]
                    keys = [i['key'] for i in fp['items']] + [k for k in (old or {}).get('items', [])
                                                             if k not in {i['key'] for i in fp['items']}]
                    nxt[u] = {'kind': 'feed', 'items': keys[:len(fp['items']) + KEEP_EXTRA]}
                    if known is None:
                        rec['why'] = 'first check'
                    elif new_items:
                        rec['why'] = f'{len(new_items)} new feed item(s)'
                        rec['new_items'] = [{k: i[k] for k in ('date', 'title', 'link')} for i in new_items]
                    else:
                        rec = None
                elif fp['kind'] == 'page':
                    first = not old or old.get('kind') != 'page' or 'links' not in old
                    seen_l, seen_d = set((old or {}).get('links', [])), set((old or {}).get('dates', []))
                    new_l = [x for x in fp['links'] if x not in seen_l]
                    new_d = [x for x in fp['dates'] if x not in seen_d]
                    nxt[u] = {'kind': 'page', 'hash': fp['hash'], 'chars': fp['chars'],
                              'links': sorted(seen_l | set(fp['links']))[-KEEP_SEEN:],
                              'dates': sorted(seen_d | set(fp['dates']))[-KEEP_SEEN:]}
                    why = []
                    if not first and old.get('hash') != fp['hash']:
                        why.append(f"page text changed ({old.get('chars')} → {fp['chars']} chars)")
                    if not first and new_l:
                        why.append(f'{len(new_l)} new link(s) on the page')
                    if not first and new_d:
                        why.append('new date(s) on the page: ' + ', '.join(new_d[:5]))
                    if first:
                        rec['why'] = 'first check'
                    elif why:
                        rec['why'] = '; '.join(why)
                    else:
                        rec = None
                else:   # js / failed — 비교할 수 없다
                    nxt[u] = old or {'kind': fp['kind']}
                    rec['why'] = ('page is drawn by JavaScript — read it with WebFetch' if fp['kind'] == 'js'
                                  else f"could not fetch (status {fp.get('status')}) — try WebFetch once")
                if rec:
                    todo.append(rec)
        # 비교할 수 없는 출처(js·failed)는, 같은 서비스·같은 종류(notice/dev)에 비교 가능한 출처가 따로 있으면
        # 건너뛴다 — 사람이 보는 링크로 함께 넣어 둔 페이지(예: RSS가 따로 있는 변경 기록 페이지)
        comparable = {k for k in ('notice', 'dev') for u in s[k] if fps[u]['kind'] in ('feed', 'page')}
        todo = [r for r in todo if not (fps[r['url']]['kind'] in ('js', 'failed') and r['source'] in comparable)]
        if backfill:
            todo = [{'url': u, 'source': k, 'why': 'BACKFILL'} for k in ('notice', 'dev') for u in s[k]]
        if todo:
            report.append({'service': s['slug'], 'name': s['name'], 'category': s['category'],
                           'mode': 'BACKFILL' if backfill else 'INCREMENTAL',
                           'match': s['match'], 'sources': todo})

    os.makedirs(os.path.dirname(NEXT_PATH), exist_ok=True)
    with open(NEXT_PATH, 'w', encoding='utf-8') as f:
        json.dump(nxt, f, ensure_ascii=False, indent=1)
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=1)

    n_src = sum(len(r['sources']) for r in report)
    print(f'Checked {len(urls)} sources of {len(services)} services: '
          f'{n_src} source(s) of {len(report)} service(s) need reading today.')
    for r in report:
        print(f"\n{r['category']} › {r['name']}  slug={r['service']}  {r['mode']}"
              + (f"  match={r['match']}" if r['match'] else ''))
        for src in r['sources']:
            print(f"    {src['source']:<6} {src['url']}\n           → {src['why']}")
            for i in src.get('new_items', [])[:15]:
                print(f"             + [{i['date'] or '????.??.??'}] {i['title']}  {i['link']}")
    if not report:
        print('Nothing changed since the last check — no service needs reading today.')


def cmd_commit(args):
    nxt = load_json(NEXT_PATH, None)
    if nxt is None:
        sys.exit(f'{NEXT_PATH} not found — run check first')
    state = load_json(STATE_PATH, {})
    failed = set()
    if args.failed and os.path.exists(args.failed):
        failed = {l.strip() for l in open(args.failed, encoding='utf-8') if l.strip().startswith('http')}
    for u, rec in nxt.items():
        if u in failed:
            continue   # 예전 상태를 두어 다음 날 다시 고른다
        state[u] = rec
    # config에서 빠진 출처는 지운다
    current = {u for s in su.load_services() for k in ('notice', 'dev') for u in s[k]}
    state = {u: r for u, r in sorted(state.items()) if u in current}
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(f'Saved source state: {len(state)} sources ({len(failed)} kept for retry).')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('check'); p.add_argument('--out'); p.set_defaults(fn=cmd_check)
    p = sub.add_parser('commit'); p.add_argument('--failed'); p.set_defaults(fn=cmd_commit)
    args = ap.parse_args()
    args.fn(args)


if __name__ == '__main__':
    main()
