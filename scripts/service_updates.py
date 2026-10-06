#!/usr/bin/env python3
"""
service_updates.py — 사이드바 '업데이트'(AI 서비스 공식 업데이트) 데이터를 다룬다.

레이아웃:
    data/updates/services/<서비스>/YYYY-MM-DD.json   그 서비스가 그날 발표한 업데이트 배열 (원본)
    data/updates/feed/<분야>.json                    분야별 전체 업데이트, 최신순 (자동 생성 — 직접 고치지 않는다)
    data/updates/index.json                          분야·서비스별 개수와 날짜 범위, 피드 파일 rev (자동 생성)

    <서비스>는 config.js updateSources의 name을 slug로 바꾼 값 (예: 'GPT Image' → gpt-image),
    <분야>는 category의 slug (예: '이미지' → image). 사이트 주소 규칙(app.jsx kwSlug)과 같다.
    파일 날짜는 서비스가 업데이트를 '발표한 날짜'다 (수집한 날짜가 아니다).

항목 (날짜 파일 배열의 원소):
    {
      "id":      "gpt-image-2026-09-08-1",        merge가 채운다
      "service": "gpt-image",
      "date":    "2026.09.08",                    발표 날짜
      "kind":    "모델",                           KINDS 중 하나
      "title":   "ChatGPT Images 2.5 공개",         한국어 제목
      "summary": "…",                             한국어 1~2문장
      "details": ["…", "…"],                      선택 — 세부 변경점 한국어 bullet (최대 6개)
      "url":     "https://…",                     공식 공지 주소 (그 글 / 변경 기록 항목)
      "source":  "notice" | "dev"                 공지인지 개발자 변경 기록인지
    }

    같은 서비스·같은 날짜·같은 url은 한 항목이다 (중복 기준). 하루에 같은 변경 기록 페이지에
    여러 변경이 올라오면 한 항목으로 묶고 details에 나눠 적는다.

명령:
    python3 scripts/service_updates.py services --category 이미지 [--out FILE]
        수집 대상 서비스와 출처(config.js) 출력. --out이 있으면 JSON으로도 저장
    python3 scripts/service_updates.py state --category 이미지
        서비스별로 지금까지 모은 개수·첫/마지막 날짜·최근 항목 (수집 범위와 중복 판단용)
    python3 scripts/service_updates.py save --out FILE  < 항목.json
        표준 입력의 항목(객체 하나 또는 배열)을 검사해 FILE(수집 결과 배열)에 덧붙인다.
        틀린 항목과 url이 404·410(없는 페이지)인 항목은 REJECTED로 이유를 보여 주고 넣지 않는다. 이미 저장됐거나(data/updates)
        FILE에 있는 항목(같은 서비스·날짜·url)은 건너뛴다
    python3 scripts/service_updates.py check FILE
        수집 결과(항목 배열 JSON) 검사만
    python3 scripts/service_updates.py merge FILE
        검사 후 data/updates/에 합치고 feed·index를 다시 만든다
    python3 scripts/service_updates.py rebuild
        feed·index만 다시 만든다
    python3 scripts/service_updates.py validate
        data/updates/ 전체 검사 (scripts/validate_data.py도 부른다)
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys

REPO = os.environ.get('REPO_PATH', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPD_DIR = os.path.join(REPO, 'data', 'updates')
SERVICES_DIR = os.path.join(UPD_DIR, 'services')
FEED_DIR = os.path.join(UPD_DIR, 'feed')
INDEX_PATH = os.path.join(UPD_DIR, 'index.json')

# app.jsx UPDATE_CAT_SLUG, build_site.py UPDATE_CAT_SLUG와 같아야 한다
CAT_SLUG = {'이미지': 'image', '영상': 'video', '3D': '3d', '게임 에셋': 'game-assets',
            '모션': 'motion', '음악·음성': 'audio', '도구': 'tools'}
KINDS = ('모델', '기능', 'API', '앱', '연동', '요금', '정책', '종료')
DATE_RE = re.compile(r'^(\d{4})\.(\d{2})\.(\d{2})$')
FILE_RE = re.compile(r'^(\d{4})-(\d{2})-(\d{2})\.json$')
KST = dt.timezone(dt.timedelta(hours=9))


def kw_slug(label: str) -> str:
    """app.jsx kwSlug와 같은 규칙."""
    return re.sub(r'[\s·/]+', '-', label).strip('-').lower()


def cat_slug(label: str) -> str:
    return CAT_SLUG.get(label, kw_slug(label))


def load_services() -> list:
    """config.js의 updateSources (node로 그대로 읽는다) + slug·catSlug."""
    js = ("global.window={};require(process.argv[1]);"
          "console.log(JSON.stringify(window.AIAD.updateSources))")
    out = subprocess.run(['node', '-e', js, os.path.join(REPO, 'config.js')],
                         check=True, capture_output=True, text=True).stdout
    services = json.loads(out)
    for s in services:
        s['slug'] = kw_slug(s['name'])
        s['catSlug'] = cat_slug(s['category'])
        s.setdefault('notice', [])
        s.setdefault('dev', [])
        s.setdefault('match', [])
    return services


def normalize_url(u: str) -> str:
    """중복 판단용 — scheme, www., 끝의 '/' 차이를 무시한다 (변경 기록 항목을 가리키는 #fragment는 남긴다)."""
    u = (u or '').strip()
    u = re.sub(r'^https?://', '', u, flags=re.IGNORECASE)
    u = re.sub(r'^www\.', '', u, flags=re.IGNORECASE)
    host, _, rest = u.partition('/')
    return (host.lower() + ('/' + rest if rest else '')).rstrip('/')


def today_kst() -> dt.date:
    return dt.datetime.now(KST).date()


def parse_date(s: str):
    m = DATE_RE.match(s or '')
    if not m:
        return None
    try:
        return dt.date(*map(int, m.groups()))
    except ValueError:
        return None


# ---------- 저장된 데이터 읽기 ----------

def service_files(slug: str) -> list:
    d = os.path.join(SERVICES_DIR, slug)
    if not os.path.isdir(d):
        return []
    return sorted(n for n in os.listdir(d) if FILE_RE.match(n))


def read_service(slug: str) -> list:
    items = []
    for name in service_files(slug):
        with open(os.path.join(SERVICES_DIR, slug, name), encoding='utf-8') as f:
            items += json.load(f)
    return items


def all_stored_slugs() -> list:
    if not os.path.isdir(SERVICES_DIR):
        return []
    return sorted(n for n in os.listdir(SERVICES_DIR) if os.path.isdir(os.path.join(SERVICES_DIR, n)))


# ---------- 항목 검사 ----------

def check_entry(e: dict, services_by_slug: dict) -> list:
    p = []
    if not isinstance(e, dict):
        return ['entry must be an object']
    svc = e.get('service')
    if svc not in services_by_slug:
        p.append(f"service {svc!r} is not in config.js updateSources (use the slug, e.g. 'gpt-image')")
    d = parse_date(e.get('date'))
    if not d:
        p.append(f"date {e.get('date')!r} must be YYYY.MM.DD (the day the service announced it)")
    elif d > today_kst():
        p.append(f"date {e['date']} is in the future")
    if e.get('kind') not in KINDS:
        p.append(f"kind {e.get('kind')!r} must be one of {', '.join(KINDS)}")
    title = e.get('title') or ''
    if not title or title.startswith('[') or len(title) > 70:
        p.append('title must be a Korean title of 1–70 characters')
    summary = e.get('summary') or ''
    if not 20 <= len(summary) <= 220 or summary.startswith('['):
        p.append(f'summary is {len(summary)} chars; it must be 20–220 (1–2 Korean sentences)')
    det = e.get('details', [])
    if not isinstance(det, list) or len(det) > 6 or not all(isinstance(x, str) and 0 < len(x) <= 140 for x in det):
        p.append('details must be a list of at most 6 Korean strings (each ≤140 chars)')
    if not re.match(r'^https?://', e.get('url') or ''):
        p.append('url must be the official announcement URL (http/https)')
    if e.get('source') not in ('notice', 'dev'):
        p.append("source must be 'notice' or 'dev'")
    extra = set(e) - {'id', 'service', 'date', 'kind', 'title', 'summary', 'details', 'url', 'source'}
    if extra:
        p.append(f'unknown fields {sorted(extra)}')
    return p


def check_file(path: str, services_by_slug: dict) -> tuple:
    with open(path, encoding='utf-8') as f:
        entries = json.load(f)
    if not isinstance(entries, list):
        return entries, ['the file must be a JSON array of entries']
    problems = []
    for i, e in enumerate(entries):
        for msg in check_entry(e, services_by_slug):
            problems.append(f'[{i}] {e.get("service") if isinstance(e, dict) else "?"} '
                            f'{e.get("date") if isinstance(e, dict) else ""}: {msg}')
    return entries, problems


# ---------- feed / index ----------

def _rev(path: str) -> str:
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:10]


def _dump(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def build_outputs(services: list) -> dict:
    """원본 날짜 파일 → {feed 파일 경로: 내용, INDEX_PATH: 내용}. config에 없는 서비스는 빠진다."""
    by_cat, svc_index = {}, {}
    for s in services:
        items = read_service(s['slug'])
        if not items:
            continue
        dates = sorted(e['date'] for e in items)
        svc_index[s['slug']] = {'count': len(items), 'first': dates[0], 'latest': dates[-1]}
        by_cat.setdefault(s['catSlug'], []).extend(items)
    out = {}
    cats = {}
    for slug, items in by_cat.items():
        items.sort(key=lambda e: (e['date'], e['service'], e['id']), reverse=True)
        path = os.path.join(FEED_DIR, f'{slug}.json')
        out[path] = items
        cats[slug] = {'count': len(items), 'latest': items[0]['date'], 'file': f'updates/feed/{slug}.json'}
    out[INDEX_PATH] = {'categories': cats, 'services': svc_index}
    return out


def write_outputs(services: list) -> dict:
    outputs = build_outputs(services)
    index = outputs.pop(INDEX_PATH)
    # 더 이상 없는 분야 피드는 지운다
    if os.path.isdir(FEED_DIR):
        keep = {os.path.basename(p) for p in outputs}
        for n in os.listdir(FEED_DIR):
            if n.endswith('.json') and n not in keep:
                os.remove(os.path.join(FEED_DIR, n))
    for path, items in outputs.items():
        _dump(path, items)
    for slug, c in index['categories'].items():
        c['rev'] = _rev(os.path.join(FEED_DIR, f'{slug}.json'))
    _dump(INDEX_PATH, index)
    return index


# ---------- 명령 ----------

def cmd_services(args):
    services = [s for s in load_services() if not args.category or s['category'] in args.category]
    if not services:
        sys.exit(f'No services for category {args.category}')
    for s in services:
        print(f"{s['category']} › {s['name']}" + (f" ({s['maker']})" if s.get('maker') else '')
              + f"  slug={s['slug']}")
        for u in s['notice']:
            print(f'    notice  {u}')
        for u in s['dev']:
            print(f'    dev     {u}')
        if s['match']:
            print(f"    match   {s['match']}")
    if args.out:
        _dump(args.out, services)
        print(f'Saved {len(services)} services to {args.out}')


def cmd_state(args):
    services = [s for s in load_services() if not args.category or s['category'] in args.category]
    today = today_kst().strftime('%Y.%m.%d')
    print(f'Today (KST): {today}')
    for s in services:
        items = sorted(read_service(s['slug']), key=lambda e: e['date'], reverse=True)
        if not items:
            print(f"\n{s['slug']}: 0 entries → BACKFILL (collect everything from the service's start to today)")
            continue
        print(f"\n{s['slug']}: {len(items)} entries, {items[-1]['date']} – {items[0]['date']} "
              f"→ INCREMENTAL (collect entries dated {items[0]['date']} or later)")
        for e in items[:args.recent]:
            print(f"    {e['date']}  [{e['kind']}] {e['title']}  <{e['url']}>")


_url_cache = {}


def url_status(url: str) -> str:
    """주소가 실제로 열리는지 (#fragment 제외). '404'·'410'이면 없는 페이지다."""
    base = url.split('#', 1)[0]
    if base not in _url_cache:
        r = subprocess.run(['curl', '-sS', '-o', '/dev/null', '-w', '%{http_code}', '-L', '--max-time', '25',
                            '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36',
                            base], capture_output=True, text=True)
        _url_cache[base] = r.stdout.strip() or '000'
    return _url_cache[base]


def cmd_save(args):
    services = {s['slug']: s for s in load_services()}
    raw = sys.stdin.read()
    try:
        new = json.loads(raw)
    except ValueError as e:
        print(f'REJECTED: input is not valid JSON ({e})')
        sys.exit(1)
    if isinstance(new, dict):
        new = [new]
    entries = []
    if os.path.exists(args.out):
        with open(args.out, encoding='utf-8') as f:
            entries = json.load(f)
    have = {(e['service'], e['date'], normalize_url(e['url'])) for e in entries}
    stored_cache = {}
    saved = dup = bad = 0
    for e in new:
        problems = check_entry(e, services)
        if problems:
            bad += 1
            print(f"REJECTED {e.get('service') if isinstance(e, dict) else '?'} "
                  f"{e.get('date') if isinstance(e, dict) else ''}: " + '; '.join(problems))
            continue
        code = url_status(e['url'])
        if code in ('404', '410'):
            bad += 1
            print(f"REJECTED {e['service']} {e['date']}: url returns {code} (page not found): {e['url']} — "
                  f"feeds sometimes link to a wrong address; find the official page that really opens "
                  f"(open it with read_source.py) and use that URL")
            continue
        key = (e['service'], e['date'], normalize_url(e['url']))
        if e['service'] not in stored_cache:
            stored_cache[e['service']] = {(x['service'], x['date'], normalize_url(x['url']))
                                          for x in read_service(e['service'])}
        if key in have or key in stored_cache[e['service']]:
            dup += 1
            print(f"SKIPPED (already collected) {e['service']} {e['date']} {e['url']}")
            continue
        entries.append({k: e[k] for k in ('service', 'date', 'kind', 'title', 'summary', 'details', 'url', 'source')
                        if k in e})
        have.add(key)
        saved += 1
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=1)
    print(f'Saved {saved}, skipped {dup} duplicates, rejected {bad}. {args.out} now has {len(entries)} entries.')
    if bad:
        sys.exit(1)


def cmd_check(args):
    services = {s['slug']: s for s in load_services()}
    entries, problems = check_file(args.file, services)
    if problems:
        print('REJECTED:')
        for p in problems:
            print('  -', p)
        sys.exit(1)
    print(f'OK: {len(entries)} entries look valid.')


def cmd_merge(args):
    services = load_services()
    by_slug = {s['slug']: s for s in services}
    entries, problems = check_file(args.file, by_slug)
    if problems:
        print('REJECTED — nothing was merged:')
        for p in problems:
            print('  -', p)
        sys.exit(1)
    added, skipped = {}, 0
    for e in entries:
        slug = e['service']
        name = e['date'].replace('.', '-') + '.json'
        path = os.path.join(SERVICES_DIR, slug, name)
        day = []
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                day = json.load(f)
        key = normalize_url(e['url'])
        if any(normalize_url(x['url']) == key for x in day):
            skipped += 1
            continue
        n = 1 + max([int(x['id'].rsplit('-', 1)[1]) for x in day if re.search(r'-\d+$', x['id'])] or [0])
        item = {'id': f"{slug}-{e['date'].replace('.', '-')}-{n}", **{k: e[k] for k in (
            'service', 'date', 'kind', 'title', 'summary') }}
        if e.get('details'):
            item['details'] = e['details']
        item['url'] = e['url']
        item['source'] = e['source']
        day.append(item)
        _dump(path, day)
        added.setdefault(slug, []).append(item)
    index = write_outputs(services)
    total = sum(len(v) for v in added.values())
    print(f'Merged: {total} new entries, {skipped} duplicates skipped.')
    for slug, items in added.items():
        print(f'  {slug}: +{len(items)}  ({min(i["date"] for i in items)} – {max(i["date"] for i in items)})')
    print('Feed:', ', '.join(f"{k} {v['count']}" for k, v in index['categories'].items()) or '-')


def cmd_rebuild(_args):
    index = write_outputs(load_services())
    print('Rebuilt:', ', '.join(f"{k} {v['count']}" for k, v in index['categories'].items()) or 'no data')


def validate() -> list:
    """data/updates/ 전체 검사 → 문제 목록 (validate_data.py가 부른다)."""
    if not os.path.isdir(UPD_DIR):
        return []
    problems = []
    services = load_services()
    by_slug = {s['slug']: s for s in services}
    seen_ids = set()
    for slug in all_stored_slugs():
        if slug not in by_slug:
            problems.append(f'updates/services/{slug}: not in config.js updateSources '
                            f'(rename the folder or add the service)')
            continue
        for name in service_files(slug):
            day = '.'.join(FILE_RE.match(name).groups())
            with open(os.path.join(SERVICES_DIR, slug, name), encoding='utf-8') as f:
                try:
                    items = json.load(f)
                except ValueError as e:
                    problems.append(f'updates/services/{slug}/{name}: invalid JSON ({e})')
                    continue
            if not isinstance(items, list) or not items:
                problems.append(f'updates/services/{slug}/{name}: must be a non-empty array')
                continue
            urls = set()
            for i, e in enumerate(items):
                where = f'updates/services/{slug}/{name}[{i}]'
                problems += [f'{where}: {m}' for m in check_entry(e, by_slug)]
                if e.get('service') != slug:
                    problems.append(f'{where}: service {e.get("service")!r} does not match folder {slug}')
                if e.get('date') != day:
                    problems.append(f'{where}: date {e.get("date")} does not match file date {day}')
                if not e.get('id') or e['id'] in seen_ids:
                    problems.append(f'{where}: missing or duplicate id {e.get("id")!r}')
                seen_ids.add(e.get('id'))
                k = normalize_url(e.get('url'))
                if k in urls:
                    problems.append(f'{where}: duplicate url on the same day')
                urls.add(k)
    expected = build_outputs(services)
    for path, content in expected.items():
        rel = os.path.relpath(path, os.path.join(REPO, 'data'))
        if not os.path.exists(path):
            problems.append(f'{rel} is missing (run scripts/service_updates.py rebuild)')
            continue
        with open(path, encoding='utf-8') as f:
            current = json.load(f)
        if path == INDEX_PATH:
            for c in current.get('categories', {}).values():
                c.pop('rev', None)
        if current != content:
            problems.append(f'{rel} is out of date (run scripts/service_updates.py rebuild)')
    if os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, encoding='utf-8') as f:
            idx = json.load(f)
        for slug, c in idx.get('categories', {}).items():
            fp = os.path.join(FEED_DIR, f'{slug}.json')
            if os.path.exists(fp) and c.get('rev') != _rev(fp):
                problems.append(f'updates/index.json rev for {slug} is stale (run scripts/service_updates.py rebuild)')
    return problems


def cmd_validate(_args):
    problems = validate()
    if problems:
        print('❌ data/updates/ validation failed:')
        for p in problems:
            print('  -', p)
        sys.exit(1)
    n = sum(len(read_service(s)) for s in all_stored_slugs())
    print(f'✅ data/updates/ is valid: {len(all_stored_slugs())} services, {n} entries.')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('services'); p.add_argument('--category', nargs='*'); p.add_argument('--out')
    p.set_defaults(fn=cmd_services)
    p = sub.add_parser('state'); p.add_argument('--category', nargs='*'); p.add_argument('--recent', type=int, default=5)
    p.set_defaults(fn=cmd_state)
    p = sub.add_parser('save'); p.add_argument('--out', required=True); p.set_defaults(fn=cmd_save)
    p = sub.add_parser('check'); p.add_argument('file'); p.set_defaults(fn=cmd_check)
    p = sub.add_parser('merge'); p.add_argument('file'); p.set_defaults(fn=cmd_merge)
    p = sub.add_parser('rebuild'); p.set_defaults(fn=cmd_rebuild)
    p = sub.add_parser('validate'); p.set_defaults(fn=cmd_validate)
    args = ap.parse_args()
    args.fn(args)


if __name__ == '__main__':
    main()
