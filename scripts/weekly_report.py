#!/usr/bin/env python3
"""weekly_report.py — '금주 리포트': 매주 금요일, 수십년차 직무 분석가 관점의 5분 칼럼 리포트를 쓴다.

데이터
  data/reports/index.json          리포트 목록 (최신순) — 사이트의 게시판이 읽는다
  data/reports/YYYY-MM-DD.json     그 주(토~금) 리포트 본문, 직군마다 하나
  routine/role_knowledge/<id>.md   직군별 수십년차 분석가 도메인 지식 (매주 리포트 작성 후 최신화)

루틴 (routine/daily_feed_prompt.txt › WEEKLY REPORT, routine/report_agent_prompt.txt)
  python3 scripts/weekly_report.py due                       금요일(KST)이고 아직 안 썼으면 DUE
  python3 scripts/weekly_report.py context [YYYY-MM-DD]      /tmp/report/context.json·context.md (직군별 그 주 기사)
  python3 scripts/weekly_report.py add /tmp/report/entries.json '<json>'   리포트 하나 검사 후 저장
  python3 scripts/weekly_report.py merge /tmp/report/entries.json          data/reports/ 에 반영
  python3 scripts/weekly_report.py validate                  data/reports/ 및 role_knowledge 검사

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
KNOWLEDGE_DIR = os.path.join(feed_data.REPO, 'routine', 'role_knowledge')
WORK = '/tmp/report'
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')

# 5분 분량 통글 칼럼 기준 (한국어 2,000 ~ 3,000자, 핵심 이슈 1~2개 집중)
LIMITS = {
    'title': 45,
    'lede': 180,
    'subhead': 45,
    'para_min': 180,
    'para_max': 850,
    # 구버전(2026-10-02 ~ 2026-10-23) 하위 호환용
    'legacy_lede': 150,
    'item': 160,
    'implication': 220,
}
PARA_COUNT = (4, 8)          # 본문(body) 산문 문단 수 (## 소제목 제외)
SUBHEAD_MAX = 2              # 선택적 소제목('## ...') 최대 개수 (핵심 포인트 최대 2개)
TOTAL_MIN = 2000             # 제목·'## ' 기호 제외 전체 글자 수 최소 (5분 읽기)
TOTAL_MAX = 3000             # 제목·'## ' 기호 제외 전체 글자 수 최대
REFS_NEW = (1, 4)            # 핵심 이슈 1~2개에 집중하기 위해 참고 기사는 1~4건
COUNTS = {'must_know': (2, 4), 'implications': (4, 8)}
LEGACY_TOTAL_MAX = 2000
LEGACY_REFS = (1, 8)
KNOWLEDGE_LEN = (800, 5000)  # 직무별 도메인 지식 .md 파일 글자 수 범위

# 말투: 정중한 칼럼 합쇼체(~습니다/~니다) 기본 + 수사적 질문(~까요?/~니까?) 허용, AI 상투어·대시 금지
BANNED = ['본격화', '가속화', '패러다임', '게임 체인저', '게임체인저', '혁신적', '주목할 만', '기대된다',
          '시사한다', '의 강세', '의 시대', '새로운 국면', '판도', '흐름이 뚜렷', '넘어갔다', '넘어가고 있다',
          '넘어가는', '에 불과', '단순히 ']
SENT_END = re.compile(r'(습니다\.|니다\.|십시오\.|세요\.|까요\?|니까\?|인가\?)$')
BODY_EXCERPT = 1200          # context.md에 넣는 기사 본문 글자 수


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
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def normalize_entry(e: dict) -> dict:
    """신규 통글 스키마(body) 또는 sections 입력을 정규화한다."""
    out = {'role': e.get('role'), 'title': (e.get('title') or '').strip(),
           'lede': (e.get('lede') or '').strip(), 'refs': e.get('refs')}
    if 'body' in e and isinstance(e.get('body'), list):
        body = []
        for item in e['body']:
            if not isinstance(item, str):
                continue
            for part in re.split(r'\n{2,}', item.strip()):
                part = part.strip()
                if part:
                    body.append(part)
        out['body'] = body
    elif 'sections' in e and isinstance(e.get('sections'), list):
        body = []
        for sec in e['sections']:
            if not isinstance(sec, dict):
                continue
            h = (sec.get('heading') or sec.get('subhead') or '').strip()
            if h:
                body.append(h if h.startswith('## ') else f'## {h}')
            for p in sec.get('paragraphs') or []:
                if isinstance(p, str) and p.strip():
                    body.append(p.strip())
        out['body'] = body
    else:
        for k in ('must_know', 'implications'):
            if k in e:
                out[k] = e.get(k)
    return out


def body_char_count(e: dict) -> int:
    """제목과 소제목 마크다운 기호('## ')를 제외한 리포트 전체 글자 수."""
    total = len(e.get('lede') or '')
    if 'body' in e and isinstance(e.get('body'), list):
        for s in e['body']:
            if isinstance(s, str):
                total += len(s[3:].strip() if s.startswith('## ') else s.strip())
    else:
        for k in COUNTS:
            for s in e.get(k) or []:
                if isinstance(s, str):
                    total += len(s)
    return total


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
            'url': a.get('url', ''), 'headline': a['headline'], 'summary': a['summary'],
            'keywords': a.get('keywords', [])}


def cmd_context(args):
    import build_site
    date = args[0] if args else today_kst()
    if not DATE_RE.match(date):
        sys.exit('date must be YYYY-MM-DD')
    start, end = week_range(date)
    arts = week_articles(start, end)
    rs = roles()
    ctx = {'date': date, 'from': start, 'to': end, 'roles': [], 'all': [slim(a) for a in arts]}
    md = [
        f'# 금주 리포트 자료 — {start} ~ {end} (기사 {len(arts)}건)\n',
        '- 작성 페르소나: **수십년차 해당 직무 분석가** (비판적·창의적 시각, 5분 분량 통글 칼럼 2,000~3,000자)',
        '- 핵심 포인트: **많아야 2개** (가장 깊은 인사이트를 줄 수 있는 1~2개 이슈만 골라 `refs` 1~4건으로 집중 분석)',
        '- 도메인 지식: 각 직무 리포트 작성 전 `routine/role_knowledge/<role>.md`를 반드시 읽고, 작성 후 섹션 2·3을 최신화할 것\n',
    ]
    for r in rs:
        mine = build_site.role_articles(r, arts)
        kpath = f'routine/role_knowledge/{r["id"]}.md'
        ctx['roles'].append({'id': r['id'], 'label': r['label'], 'desc': r['desc'],
                             'knowledge': kpath, 'articles': [slim(a) for a in mine]})
        md.append(f'\n## {r["id"]} — {r["label"]} ({r["desc"]}) · 관련 기사 {len(mine)}건')
        md.append(f'  · 직무 도메인 지식 파일: `{kpath}`\n')
        for a in mine:
            md.append(f'- [{a["id"]}] {a["_date"]} · {a["source"]} · {a["headline"]}\n  {a["summary"]}')
        print(f'{r["id"]:9} {r["label"]:14} {len(mine)} articles')
    md.append('\n## 그 밖의 이번 주 기사 (모든 직군 공통 참고)\n')
    used = {a['id'] for r in ctx['roles'] for a in r['articles']}
    for a in arts:
        if a['id'] not in used:
            md.append(f'- [{a["id"]}] {a["_date"]} · {a["source"]} · {a["headline"]}\n  {a["summary"]}')
    md.append('\n## 기사 상세 (본문 — 구체적 사실·수치 확인 및 공식 가이드 웹 검색 기준)\n')
    for a in arts:
        body = html.unescape(re.sub(r'<[^>]+>', ' ', a.get('body', '')))
        body = re.sub(r'\s+', ' ', body).strip()
        md.append(f'### [{a["id"]}] {a["headline"]}\n{a["_date"]} · {a["source"]} · {a.get("url", "")}\n'
                  f'{body[:BODY_EXCERPT]}{"…" if len(body) > BODY_EXCERPT else ""}\n')
    os.makedirs(WORK, exist_ok=True)
    write_json(os.path.join(WORK, 'context.json'), ctx)
    with open(os.path.join(WORK, 'context.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(md) + '\n')
    print(f'Week {start} ~ {end}: {len(arts)} articles → {WORK}/context.json, {WORK}/context.md')


# ---------------------------------------------------------------- check / add
def check(e: dict, ctx: dict | None = None, allow_legacy: bool = False) -> list:
    errs = []
    if ctx is not None:
        ids = {r['id'] for r in ctx['roles']}
        week_ids = {a['id'] for a in ctx['all']}
    else:
        ids = {r['id'] for r in roles()}
        week_ids = None

    if e.get('role') not in ids:
        errs.append(f'role must be one of {sorted(ids)}')

    is_legacy = ('body' not in e) and ('must_know' in e or 'implications' in e)
    if is_legacy and not allow_legacy:
        errs.append('must_know/implications format is deprecated — use "body": ["문단1...", "## 소제목(선택)", "문단2..."] (2,000~3,000 chars prose)')
        return errs

    lede_limit = LIMITS['legacy_lede'] if is_legacy else LIMITS['lede']
    for k, lim in (('title', LIMITS['title']), ('lede', lede_limit)):
        v = e.get(k)
        if not isinstance(v, str) or not v.strip():
            errs.append(f'{k} is required')
        elif len(v) > lim:
            errs.append(f'{k} is {len(v)} chars (max {lim})')

    if not is_legacy:
        body = e.get('body')
        if not isinstance(body, list) or not body:
            errs.append('body must be a non-empty list of prose paragraphs (and up to 2 optional "## 소제목" strings)')
        else:
            paras = []
            subheads = []
            prev_sub = False
            for i, s in enumerate(body):
                if not isinstance(s, str) or not s.strip():
                    errs.append(f'body[{i}] is empty')
                    continue
                s_clean = s.strip()
                if s_clean.startswith('## '):
                    sh = s_clean[3:].strip()
                    subheads.append((i, sh))
                    if not (2 <= len(sh) <= LIMITS['subhead']):
                        errs.append(f'body[{i}] subheading is {len(sh)} chars (must be 2–{LIMITS["subhead"]})')
                    if sh.endswith('.'):
                        errs.append(f'body[{i}] subheading must not end with a period: "{sh}"')
                    if prev_sub:
                        errs.append(f'body[{i}] has consecutive subheadings without a paragraph in between')
                    prev_sub = True
                else:
                    if s_clean.startswith('#') or s_clean.startswith('- ') or s_clean.startswith('* ') or s_clean.startswith('•'):
                        errs.append(f'body[{i}] must be continuous prose, not a bullet or other markdown heading')
                    if not (LIMITS['para_min'] <= len(s_clean) <= LIMITS['para_max']):
                        errs.append(f'body[{i}] paragraph is {len(s_clean)} chars (must be {LIMITS["para_min"]}–{LIMITS["para_max"]})')
                    paras.append((i, s_clean))
                    prev_sub = False
            if prev_sub and body:
                errs.append('body cannot end with a subheading')
            if len(subheads) > SUBHEAD_MAX:
                errs.append(f'body has {len(subheads)} subheadings (max {SUBHEAD_MAX} — focus on at most 2 core points)')
            if not (PARA_COUNT[0] <= len(paras) <= PARA_COUNT[1]):
                errs.append(f'body has {len(paras)} prose paragraphs (must be {PARA_COUNT[0]}–{PARA_COUNT[1]})')

        total = body_char_count(e)
        if not (TOTAL_MIN <= total <= TOTAL_MAX):
            errs.append(f'total length (lede + body) is {total} chars (must be {TOTAL_MIN}–{TOTAL_MAX} chars for a 5-minute read)')

        refs = e.get('refs')
        if not isinstance(refs, list) or not (REFS_NEW[0] <= len(refs) <= REFS_NEW[1]):
            errs.append(f'refs must be a list of {REFS_NEW[0]}–{REFS_NEW[1]} article ids (focus deeply on 1–2 core issues)')
        elif week_ids is not None:
            bad = [r for r in refs if r not in week_ids]
            if bad:
                errs.append(f'refs not in this week\'s articles: {bad}')

        text_parts = [e.get('title') or '', e.get('lede') or ''] + [s for s in (e.get('body') or []) if isinstance(s, str)]
        sent_targets = [('lede', [e.get('lede') or '']),
                        ('body', [s for s in (e.get('body') or []) if isinstance(s, str) and not s.strip().startswith('## ')])]
    else:
        total = len(e.get('lede') or '')
        for k, (lo, hi) in COUNTS.items():
            v = e.get(k)
            if not isinstance(v, list) or not (lo <= len(v) <= hi):
                errs.append(f'{k} must be a list of {lo}-{hi} strings')
                continue
            for i, s in enumerate(v):
                if not isinstance(s, str) or not s.strip():
                    errs.append(f'{k}[{i}] is empty')
                elif len(s) > (lim := LIMITS['implication' if k == 'implications' else 'item']):
                    errs.append(f'{k}[{i}] is {len(s)} chars (max {lim})')
                else:
                    total += len(s)
        if total > LEGACY_TOTAL_MAX:
            errs.append(f'body is {total} chars (max {LEGACY_TOTAL_MAX})')
        refs = e.get('refs')
        if not isinstance(refs, list) or not (LEGACY_REFS[0] <= len(refs) <= LEGACY_REFS[1]):
            errs.append(f'refs must be a list of {LEGACY_REFS[0]}-{LEGACY_REFS[1]} article ids')
        elif week_ids is not None:
            bad = [r for r in refs if r not in week_ids]
            if bad:
                errs.append(f'refs not in this week\'s articles: {bad}')
        text_parts = [e.get('title') or '', e.get('lede') or ''] + sum((e.get(k) or [] for k in COUNTS), [])
        sent_targets = [('lede', [e.get('lede') or ''])] + [(k, e.get(k) or []) for k in COUNTS]

    text = ' '.join(text_parts)
    if '\ufffd' in text:
        errs.append('text contains broken encoding character (U+FFFD)')
    for w in BANNED:
        if w in text:
            errs.append(f'banned phrase "{w}" (see READER AND TONE)')
    if '—' in text or '–' in text:
        errs.append('no em/en dashes (—, –) — write plain sentences')
    for k, v in sent_targets:
        for i, para in enumerate(v):
            if not isinstance(para, str) or not para.strip():
                continue
            for sent in re.split(r'(?<=[.?!])\s+', para.strip()):
                if sent and not SENT_END.search(sent):
                    errs.append(f'{k}[{i}]: every sentence must end in 합쇼체 (-습니다/-니다/-세요/-까요?/-니까?): "{sent[-30:]}"')
                    break
    if re.search(r'\[[^\]]*\]|TODO|REPLACE', text):
        errs.append('placeholder text left in the report')
    return errs


def cmd_add(args):
    if len(args) == 3 and args[1] == '--file':          # JSON을 파일로 받기 (Windows 셸 따옴표 문제 회피)
        args = [args[0], open(args[2], encoding='utf-8-sig').read()]
    if len(args) != 2:
        sys.exit("usage: weekly_report.py add /tmp/report/entries.json '<json>'  (or --file PATH)")
    path, raw = args
    ctx = read_json(os.path.join(WORK, 'context.json'), None)
    if not ctx:
        sys.exit('run `weekly_report.py context` first')
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as err:
        sys.exit(f'REJECTED: not valid JSON ({err})')
    e = normalize_entry(parsed)
    errs = check(e, ctx, allow_legacy=False)
    if errs:
        print('REJECTED:\n  - ' + '\n  - '.join(errs))
        sys.exit(1)
    entries = [x for x in read_json(path, []) if x.get('role') != e['role']]
    entries.append(e)
    write_json(path, entries)
    chars = body_char_count(e)
    paras = sum(1 for s in e['body'] if not s.startswith('## '))
    subs = sum(1 for s in e['body'] if s.startswith('## '))
    print(f'SAVED {e["role"]}: "{e["title"]}" ({chars} chars, {paras} paragraphs, {subs} subheads, '
          f'{len(e["refs"])} refs) — {len(entries)} reports so far')


# ---------------------------------------------------------------- merge / validate
def cmd_merge(args):
    path = args[0] if args else os.path.join(WORK, 'entries.json')
    ctx = read_json(os.path.join(WORK, 'context.json'), None)
    raw_entries = read_json(path, [])
    if not ctx or not raw_entries:
        sys.exit('nothing to merge')
    entries = [normalize_entry(e) for e in raw_entries]
    order = [r['id'] for r in ctx['roles']]
    bad = [(e.get('role'), errs) for e in entries for errs in [check(e, ctx, allow_legacy=False)] if errs]
    if bad:
        sys.exit(f'REJECTED: {bad}')
    # 그 주 파일이 이미 있으면 같은 직군만 바꾸고 나머지 직군 리포트는 그대로 둔다
    # (한 직군만 다시 써서 merge해도 다른 직군이 지워지지 않게)
    target = os.path.join(REPORTS_DIR, ctx['date'] + '.json')
    kept = [e for e in read_json(target, {}).get('reports', [])
            if e.get('role') not in {x['role'] for x in entries}]
    replaced = len(read_json(target, {}).get('reports', [])) - len(kept)
    merged = sorted(kept + entries, key=lambda e: order.index(e['role']) if e['role'] in order else len(order))
    missing = [r for r in order if r not in {e['role'] for e in merged}]
    write_json(target, {'date': ctx['date'], 'from': ctx['from'], 'to': ctx['to'], 'articles': len(ctx['all']),
                        'reports': merged})
    write_index()
    print(f'Merged weekly report {ctx["date"]}: {len(entries)} written ({replaced} replaced), '
          f'{len(kept)} kept, {len(merged)} roles in total'
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


def validate_role_knowledge(role_ids: set) -> list:
    problems = []
    for rid in sorted(role_ids):
        p = os.path.join(KNOWLEDGE_DIR, f'{rid}.md')
        if not os.path.isfile(p):
            problems.append(f'routine/role_knowledge/{rid}.md: missing file')
            continue
        txt = open(p, encoding='utf-8', errors='replace').read()
        if '\ufffd' in txt:
            problems.append(f'routine/role_knowledge/{rid}.md: contains broken character (U+FFFD)')
        if not (KNOWLEDGE_LEN[0] <= len(txt) <= KNOWLEDGE_LEN[1]):
            problems.append(f'routine/role_knowledge/{rid}.md: {len(txt)} chars (must be {KNOWLEDGE_LEN[0]}–{KNOWLEDGE_LEN[1]})')
        for sec in ('## 1.', '## 2.', '## 3.'):
            if sec not in txt:
                problems.append(f'routine/role_knowledge/{rid}.md: missing section "{sec}"')
    return problems


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
            errs = check(e, ctx=None, allow_legacy=True)
            for err in errs:
                problems.append(f'{name} {e.get("role")}: {err}')
    idx = read_json(INDEX, {}).get('reports', [])
    if len(idx) != n:
        problems.append(f'index.json lists {len(idx)} reports, files hold {n} — run merge again')
    problems += validate_role_knowledge(role_ids)
    if problems:
        print('❌ data/reports/ problems:\n  - ' + '\n  - '.join(problems))
        sys.exit(1)
    print(f'✅ data/reports/ is valid: {n} reports, {len(role_ids)} role knowledge files')


if __name__ == '__main__':
    cmds = {'due': cmd_due, 'context': cmd_context, 'add': cmd_add, 'merge': cmd_merge, 'validate': cmd_validate}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit('usage: weekly_report.py due|context|add|merge|validate ...')
    extra = [a for a in sys.argv[2:] if a.startswith('-') and a != '--file']
    if extra:      # --help·오타 옵션은 거부 — 엉뚱한 값으로 merge·add가 돌지 않게
        sys.exit(f'usage: weekly_report.py {sys.argv[1]} ... (unknown option {extra[0]}; nothing was run)')
    cmds[sys.argv[1]](sys.argv[2:])
