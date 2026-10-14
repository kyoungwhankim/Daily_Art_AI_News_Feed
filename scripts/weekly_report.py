#!/usr/bin/env python3
"""weekly_report.py — '금주 리포트': 매주 금요일, 그 주 기사를 바탕으로 직군별 1분 리포트를 쓴다.

데이터
  data/reports/index.json        리포트 목록 (최신순) — 사이트의 게시판이 읽는다
  data/reports/YYYY-MM-DD.json   그 주(토~금) 리포트 본문, 직군마다 하나

루틴 (routine/daily_feed_prompt.txt › WEEKLY REPORT, routine/report_agent_prompt.txt)
  python3 scripts/weekly_report.py due                       금요일(KST)이고 아직 안 썼으면 DUE
  python3 scripts/weekly_report.py context [YYYY-MM-DD]      /tmp/report/context.json·context.md (직군별 그 주 기사)
  python3 scripts/weekly_report.py add /tmp/report/entries.json '<json>'   리포트 하나 검사 후 저장
  python3 scripts/weekly_report.py merge /tmp/report/entries.json          data/reports/ 에 반영
  python3 scripts/weekly_report.py validate                  data/reports/ 검사

직군별 기사 고르기는 사이트의 아티스트 브리핑과 같다 (build_site.role_articles, config.js roles).
"""
import html
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feed_data  # noqa: E402

KST = timezone(timedelta(hours=9))
REPORTS_DIR = os.path.join(feed_data.DATA_DIR, 'reports')
INDEX = os.path.join(REPORTS_DIR, 'index.json')
WORK = '/tmp/report'
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')

# 1분 읽기 분량 — 글자 수 제한 (한국어 기준)
LIMITS = {'title': 40, 'lede': 120, 'item': 120}
COUNTS = {'must_know': (2, 4), 'implications': (2, 3), 'prepare': (2, 3)}
TOTAL_MAX = 900          # 제목 제외 본문 전체 글자 수
REFS = (1, 8)            # 참고 기사 수
BODY_EXCERPT = 700       # context.md에 넣는 기사 본문 앞부분 글자 수


def today_kst() -> str:
    return datetime.now(KST).strftime('%Y-%m-%d')


def week_range(date: str) -> tuple:
    """리포트 날짜(금요일)를 끝으로 하는 7일 (토~금)."""
    end = datetime.strptime(date, '%Y-%m-%d')
    return (end - timedelta(days=6)).strftime('%Y-%m-%d'), date


def roles() -> list:
    import build_site
    return build_site.load_roles()


def week_articles(start: str, end: str) -> list:
    out = []
    for name in feed_data.date_files():
        d = name[:-5]
        if start <= d <= end:
            for a in feed_data.read_day(name):
                out.append({**a, '_date': d})
    out.sort(key=lambda a: a['_date'], reverse=True)
    return out


def read_json(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


# ---------------------------------------------------------------- due
def cmd_due(args):
    date = args[0] if args else today_kst()
    friday = datetime.strptime(date, '%Y-%m-%d').weekday() == 4
    done = os.path.exists(os.path.join(REPORTS_DIR, date + '.json'))
    if friday and not done:
        print(f'DUE (weekly report for {date})')
    else:
        print(f'NOT DUE ({date}: ' + ('already written' if done else 'not Friday') + ')')


# ---------------------------------------------------------------- context
def slim(a: dict) -> dict:
    return {'id': a['id'], 'date': a['_date'], 'tab': a['tab'], 'source': a['source'],
            'headline': a['headline'], 'summary': a['summary'], 'keywords': a.get('keywords', [])}


def cmd_context(args):
    import build_site
    date = args[0] if args else today_kst()
    if not DATE_RE.match(date):
        sys.exit('date must be YYYY-MM-DD')
    start, end = week_range(date)
    arts = week_articles(start, end)
    rs = roles()
    ctx = {'date': date, 'from': start, 'to': end, 'roles': [], 'all': [slim(a) for a in arts]}
    md = [f'# 금주 리포트 자료 — {start} ~ {end} (기사 {len(arts)}건)\n']
    for r in rs:
        mine = build_site.role_articles(r, arts)
        ctx['roles'].append({'id': r['id'], 'label': r['label'], 'desc': r['desc'],
                             'articles': [slim(a) for a in mine]})
        md.append(f'\n## {r["id"]} — {r["label"]} ({r["desc"]}) · 관련 기사 {len(mine)}건\n')
        for a in mine:
            md.append(f'- [{a["id"]}] {a["_date"]} · {a["source"]} · {a["headline"]}\n  {a["summary"]}')
        print(f'{r["id"]:9} {r["label"]:14} {len(mine)} articles')
    md.append(f'\n## 그 밖의 이번 주 기사 (모든 직군 공통 참고)\n')
    used = {a['id'] for r in ctx['roles'] for a in r['articles']}
    for a in arts:
        if a['id'] not in used:
            md.append(f'- [{a["id"]}] {a["_date"]} · {a["source"]} · {a["headline"]}\n  {a["summary"]}')
    md.append(f'\n## 기사 상세 (본문 앞부분 — 구체적인 사실·숫자는 여기서 확인)\n')
    for a in arts:
        body = html.unescape(re.sub(r'<[^>]+>', ' ', a.get('body', '')))
        body = re.sub(r'\s+', ' ', body).strip()
        md.append(f'### [{a["id"]}] {a["headline"]}\n{a["_date"]} · {a["source"]} · {a.get("url", "")}\n'
                  f'{body[:BODY_EXCERPT]}{"…" if len(body) > BODY_EXCERPT else ""}\n')
    os.makedirs(WORK, exist_ok=True)
    write_json(os.path.join(WORK, 'context.json'), ctx)
    with open(os.path.join(WORK, 'context.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')
    print(f'Week {start} ~ {end}: {len(arts)} articles → {WORK}/context.json, {WORK}/context.md')


# ---------------------------------------------------------------- check / add
def check(e: dict, ctx: dict) -> list:
    errs = []
    ids = {r['id'] for r in ctx['roles']}
    week_ids = {a['id'] for a in ctx['all']}
    if e.get('role') not in ids:
        errs.append(f'role must be one of {sorted(ids)}')
    for k in ('title', 'lede'):
        v = e.get(k)
        if not isinstance(v, str) or not v.strip():
            errs.append(f'{k} is required')
        elif len(v) > LIMITS[k]:
            errs.append(f'{k} is {len(v)} chars (max {LIMITS[k]})')
    total = len(e.get('lede') or '')
    for k, (lo, hi) in COUNTS.items():
        v = e.get(k)
        if not isinstance(v, list) or not (lo <= len(v) <= hi):
            errs.append(f'{k} must be a list of {lo}-{hi} strings')
            continue
        for i, s in enumerate(v):
            if not isinstance(s, str) or not s.strip():
                errs.append(f'{k}[{i}] is empty')
            elif len(s) > LIMITS['item']:
                errs.append(f'{k}[{i}] is {len(s)} chars (max {LIMITS["item"]})')
            else:
                total += len(s)
    if total > TOTAL_MAX:
        errs.append(f'body is {total} chars (max {TOTAL_MAX} — a one-minute read)')
    refs = e.get('refs')
    if not isinstance(refs, list) or not (REFS[0] <= len(refs) <= REFS[1]):
        errs.append(f'refs must be a list of {REFS[0]}-{REFS[1]} article ids')
    else:
        bad = [r for r in refs if r not in week_ids]
        if bad:
            errs.append(f'refs not in this week\'s articles: {bad}')
    text = ' '.join([e.get('title') or '', e.get('lede') or ''] + sum((e.get(k) or [] for k in COUNTS), []))
    if re.search(r'\[[^\]]*\]|TODO|REPLACE', text):
        errs.append('placeholder text left in the report')
    return errs


def cmd_add(args):
    if len(args) != 2:
        sys.exit("usage: weekly_report.py add /tmp/report/entries.json '<json>'")
    path, raw = args
    ctx = read_json(os.path.join(WORK, 'context.json'), None)
    if not ctx:
        sys.exit('run `weekly_report.py context` first')
    try:
        e = json.loads(raw)
    except json.JSONDecodeError as err:
        sys.exit(f'REJECTED: not valid JSON ({err})')
    e = {k: e.get(k) for k in ('role', 'title', 'lede', 'must_know', 'implications', 'prepare', 'refs')}
    errs = check(e, ctx)
    if errs:
        print('REJECTED:\n  - ' + '\n  - '.join(errs))
        sys.exit(1)
    entries = [x for x in read_json(path, []) if x.get('role') != e['role']]
    entries.append(e)
    write_json(path, entries)
    body = len(e['lede']) + sum(len(s) for k in COUNTS for s in e[k])
    print(f'SAVED {e["role"]}: "{e["title"]}" ({body} chars, {len(e["refs"])} refs) — {len(entries)} reports so far')


# ---------------------------------------------------------------- merge / validate
def cmd_merge(args):
    path = args[0] if args else os.path.join(WORK, 'entries.json')
    ctx = read_json(os.path.join(WORK, 'context.json'), None)
    entries = read_json(path, [])
    if not ctx or not entries:
        sys.exit('nothing to merge')
    order = [r['id'] for r in ctx['roles']]
    bad = [(e.get('role'), errs) for e in entries for errs in [check(e, ctx)] if errs]
    if bad:
        sys.exit(f'REJECTED: {bad}')
    entries.sort(key=lambda e: order.index(e['role']))
    missing = [r for r in order if r not in {e['role'] for e in entries}]
    write_json(os.path.join(REPORTS_DIR, ctx['date'] + '.json'),
               {'date': ctx['date'], 'from': ctx['from'], 'to': ctx['to'], 'articles': len(ctx['all']),
                'reports': entries})
    write_index()
    print(f'Merged weekly report {ctx["date"]}: {len(entries)} roles'
          + (f' (missing: {", ".join(missing)})' if missing else ''))


def write_index():
    items = []
    for name in sorted(os.listdir(REPORTS_DIR), reverse=True):
        if not DATE_RE.match(name[:-5]) or not name.endswith('.json'):
            continue
        d = read_json(os.path.join(REPORTS_DIR, name), {})
        for e in d.get('reports', []):
            items.append({'date': d['date'], 'from': d['from'], 'to': d['to'], 'role': e['role'],
                          'title': e['title'], 'lede': e['lede']})
    write_json(INDEX, {'reports': items})
    return items


def cmd_validate(args):
    if not os.path.isdir(REPORTS_DIR):
        print('No reports yet.')
        return
    role_ids = {r['id'] for r in roles()}
    n, problems = 0, []
    for name in sorted(os.listdir(REPORTS_DIR)):
        if name == 'index.json':
            continue
        if not (name.endswith('.json') and DATE_RE.match(name[:-5])):
            problems.append(f'{name}: unexpected file')
            continue
        d = read_json(os.path.join(REPORTS_DIR, name), {})
        if d.get('date') != name[:-5]:
            problems.append(f'{name}: date field does not match the file name')
        for e in d.get('reports', []):
            n += 1
            if e.get('role') not in role_ids:
                problems.append(f'{name}: unknown role {e.get("role")}')
            for k in ('title', 'lede', 'must_know', 'implications', 'prepare', 'refs'):
                if not e.get(k):
                    problems.append(f'{name} {e.get("role")}: missing {k}')
    idx = read_json(INDEX, {}).get('reports', [])
    if len(idx) != n:
        problems.append(f'index.json lists {len(idx)} reports, files hold {n} — run merge again')
    if problems:
        print('❌ data/reports/ problems:\n  - ' + '\n  - '.join(problems))
        sys.exit(1)
    print(f'✅ data/reports/ is valid: {n} reports')


if __name__ == '__main__':
    cmds = {'due': cmd_due, 'context': cmd_context, 'add': cmd_add, 'merge': cmd_merge, 'validate': cmd_validate}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit('usage: weekly_report.py due|context|add|merge|validate ...')
    cmds[sys.argv[1]](sys.argv[2:])
