#!/usr/bin/env python3
"""'무료로 써보기'(/free/) 데이터 — 아트 AI 서비스의 무료 체험·무료 플랜과 원래 무료인 서비스.

    python3 scripts/free_tools.py due                 # 이번 주 조사할 차례인지 (DUE / NOT DUE)
    python3 scripts/free_tools.py list                # 조사할 서비스 목록 (slug, 이름, 종류, 주소, 지난 결과)
    python3 scripts/free_tools.py add <entries.json> '<한 서비스 JSON>'  # 조사 결과 하나를 검사해 넘겨줄 파일에 저장
    python3 scripts/free_tools.py merge <entries.json>  # 조사 결과를 검사하고 data/free/tools.json에 반영
    python3 scripts/free_tools.py validate            # data/free/tools.json 검사

서비스 목록은 config.js의 freeTools (이름·분류·종류·주소).
조사 결과(혜택 내용)는 매주 루틴의 무료 혜택 에이전트(routine/free_agent_prompt.txt)가 채운다.

data/free/tools.json:
{
  "updated": "2026.10.13",          # 마지막 조사일 (KST)
  "tools": { "<slug>": { ...ENTRY_FIELDS..., "checked": "2026.10.13" } },
  "changes": [ { "date", "slug", "kind", "text" } ]   # 최근 바뀐 혜택 (최신순, 최대 CHANGES_KEEP개)
}
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, 'data', 'free', 'tools.json')
KST = dt.timezone(dt.timedelta(hours=9))
DUE_DAYS = 6            # 마지막 조사 후 이만큼 지나면 다시 조사 (주 1회, 하루 밀려도 다음 날 잡힌다)
CHANGES_KEEP = 60

STATUS = {'ok', 'unverified', 'ended', 'paid'}
#   ok         확인함
#   unverified 가격 페이지를 읽지 못했거나 확실하지 않음 (지난 결과를 그대로 두고 '확인 필요' 표시)
#   ended      무료 체험·무료 플랜이 없어짐
#   paid       원래 무료(kind 'free')였는데 유료로 바뀜
TYPES = {'plan', 'trial', 'credits', 'free', 'none'}
#   plan    계속 쓸 수 있는 무료 플랜 (매일·매달 충전 등)
#   trial   기간제 무료 체험 (예: 7일)
#   credits 가입 때 한 번 주는 무료 크레딧
#   free    원래 무료 (오픈소스·무료 소프트웨어)
#   none    무료로 쓸 방법 없음
DIRECTIONS = {'new', 'up', 'down', 'same'}
TEXT_LIMITS = {'offer': 40, 'limits': 80, 'note': 100, 'change_note': 80}
HANGUL = re.compile(r'[가-힣]')


def kw_slug(label: str) -> str:
    """app.jsx kwSlug와 같은 규칙."""
    return re.sub(r'[\s·/]+', '-', label).strip('-').lower()


def today() -> str:
    return dt.datetime.now(KST).strftime('%Y.%m.%d')


def load_tools() -> list:
    js = ("global.window={};require(process.argv[1]);"
          "console.log(JSON.stringify(window.AIAD.freeTools||[]))")
    out = subprocess.run(['node', '-e', js, os.path.join(REPO, 'config.js')],
                         check=True, capture_output=True, text=True).stdout
    tools = json.loads(out)
    for t in tools:
        t['slug'] = kw_slug(t['name'])
    return tools


def load_data() -> dict:
    if not os.path.exists(DATA):
        return {'updated': None, 'tools': {}, 'changes': []}
    with open(DATA, encoding='utf-8') as f:
        return json.load(f)


def save_data(data: dict) -> None:
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    with open(DATA, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write('\n')


def is_url(v) -> bool:
    return isinstance(v, str) and v.startswith('https://') and ' ' not in v


def check_entry(e: dict, tool: dict) -> list:
    """한 서비스의 조사 결과를 검사한다. 문제 목록을 돌려준다 (없으면 [])."""
    errs = []
    st = e.get('status')
    if st not in STATUS:
        errs.append(f'status must be one of {sorted(STATUS)}')
    if st == 'unverified':
        return errs                                   # 나머지는 지난 결과를 쓴다
    if e.get('type') not in TYPES:
        errs.append(f'type must be one of {sorted(TYPES)}')
    if tool['kind'] == 'free' and st == 'ok' and e.get('type') != 'free':
        errs.append("kind 'free' service with status 'ok' must have type 'free' (use status 'paid' if it is no longer free)")
    if st in ('ended', 'paid') and e.get('type') not in ('none', 'trial', 'credits', 'plan'):
        errs.append("status 'ended'/'paid' needs type 'none' (or the new limited offer type)")
    for k in ('offer',):
        if not isinstance(e.get(k), str) or not e[k].strip():
            errs.append(f'{k} is required')
    for k, n in TEXT_LIMITS.items():
        v = e.get(k)
        if v is None or v == '':
            continue
        if not isinstance(v, str):
            errs.append(f'{k} must be a string')
        elif len(v) > n:
            errs.append(f'{k} is {len(v)} chars (max {n})')
        elif not HANGUL.search(v):
            errs.append(f'{k} must be written in Korean')
    for k in ('card', 'watermark', 'commercial'):
        if e.get(k) not in (True, False, None):
            errs.append(f'{k} must be true, false or null')
    for k in ('try_url', 'source_url'):
        if not is_url(e.get(k)):
            errs.append(f'{k} must be an https:// URL')
    if e.get('direction') not in (None, *DIRECTIONS):
        errs.append(f'direction must be one of {sorted(DIRECTIONS)}')
    return errs


KEEP = ('status', 'type', 'offer', 'limits', 'card', 'watermark', 'commercial',
        'try_url', 'source_url', 'note')


def change_of(old: dict, new: dict, tool: dict, e: dict):
    """지난 결과와 비교해 바뀐 혜택을 한 줄로 (없으면 None)."""
    if new['status'] == 'unverified':
        return None
    if not old:
        return None                                   # 처음 조사한 서비스는 '변경'으로 세지 않는다
    if new['status'] == 'paid' and old.get('status') != 'paid':
        return 'paid', e.get('change_note') or '무료에서 유료로 바뀌었어요'
    if new['status'] == 'ended' and old.get('status') != 'ended':
        return 'ended', e.get('change_note') or '무료 혜택이 없어졌어요'
    if old.get('status') in ('ended', 'paid') and new['status'] == 'ok':
        return 'new', e.get('change_note') or f'무료 혜택이 다시 생겼어요: {new["offer"]}'
    if (old.get('type'), old.get('offer')) != (new.get('type'), new.get('offer')):
        d = e.get('direction')
        if d == 'same':
            return None                               # 표현만 바뀜
        kind = {'up': 'up', 'down': 'down', 'new': 'new'}.get(d, 'changed')
        return kind, e.get('change_note') or f'{old.get("offer")} → {new["offer"]}'
    return None


def cmd_add(path: str, raw: str) -> int:
    tools = {t['slug']: t for t in load_tools()}
    try:
        e = json.loads(raw)
    except ValueError as x:
        print(f'REJECTED — not valid JSON: {x}')
        return 1
    slug = e.get('slug') if isinstance(e, dict) else None
    if slug not in tools:
        print(f'REJECTED — unknown slug {slug!r} (see `free_tools.py list`)')
        return 1
    errs = check_entry(e, tools[slug])
    if errs:
        print(f'REJECTED — {slug}:')
        for x in errs:
            print('  -', x)
        return 1
    entries = []
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            entries = json.load(f)
    entries = [x for x in entries if x.get('slug') != slug] + [e]
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=1)
    print(f'SAVED {slug} ({e["status"]}) — {len(entries)}/{len(tools)} services in {path}')
    return 0


def cmd_due() -> int:
    data = load_data()
    last = data.get('updated')
    if not last:
        print('DUE (never checked)')
        return 0
    days = (dt.datetime.strptime(today(), '%Y.%m.%d') - dt.datetime.strptime(last, '%Y.%m.%d')).days
    print(f'{"DUE" if days >= DUE_DAYS else "NOT DUE"} (last checked {last}, {days} days ago)')
    return 0


def cmd_list() -> int:
    data = load_data()
    for t in load_tools():
        prev = data['tools'].get(t['slug'])
        was = f' | last: {prev.get("status")}/{prev.get("type")} "{prev.get("offer")}"' if prev else ''
        print(f'{t["slug"]}\t{t["name"]}\t{t["kind"]}\t{t["category"]}\t{t["url"]}{was}')
    return 0


def cmd_merge(path: str) -> int:
    tools = {t['slug']: t for t in load_tools()}
    with open(path, encoding='utf-8') as f:
        entries = json.load(f)
    if not isinstance(entries, list):
        print('REJECTED — nothing was merged: the file must hold a JSON list')
        return 1
    problems = []
    seen = set()
    for i, e in enumerate(entries):
        slug = e.get('slug') if isinstance(e, dict) else None
        if slug not in tools:
            problems.append(f'#{i}: unknown slug {slug!r} (see `free_tools.py list`)')
            continue
        if slug in seen:
            problems.append(f'#{i}: duplicate slug {slug}')
        seen.add(slug)
        for err in check_entry(e, tools[slug]):
            problems.append(f'{slug}: {err}')
    if problems:
        print('REJECTED — nothing was merged. Fix these entries and run merge again:')
        for p in problems:
            print('  -', p)
        return 1

    data = load_data()
    day = today()
    counts = {'ok': 0, 'unverified': 0, 'ended': 0, 'paid': 0, 'changed': 0}
    new_changes = []
    for e in entries:
        slug, tool = e['slug'], tools[e['slug']]
        old = data['tools'].get(slug, {})
        counts[e['status']] += 1
        if e['status'] == 'unverified':
            if old:
                old['status_note'] = 'unverified'   # 지난 결과는 두고 '확인 필요'만 표시
            else:
                data['tools'][slug] = {'status': 'unverified', 'checked': day}
            continue
        new = {k: e.get(k) for k in KEEP if e.get(k) not in (None, '')}
        for k in ('card', 'watermark', 'commercial'):
            new[k] = e.get(k)
        new['checked'] = day
        ch = change_of(old, new, tool, e)
        if ch:
            counts['changed'] += 1
            new_changes.append({'date': day, 'slug': slug, 'kind': ch[0], 'text': ch[1]})
        data['tools'][slug] = new
    # 목록에서 빠진 서비스의 지난 결과는 지운다
    for slug in list(data['tools']):
        if slug not in tools:
            del data['tools'][slug]
    data['changes'] = (new_changes + [c for c in data.get('changes', []) if c['slug'] in tools])[:CHANGES_KEEP]
    data['updated'] = day
    save_data(data)
    missing = [s for s in tools if s not in seen]
    print(f'Merged {len(entries)} services: ' + ', '.join(f'{k} {v}' for k, v in counts.items()))
    if missing:
        print(f'Not in this run ({len(missing)}): {", ".join(missing)}')
    return 0


def cmd_validate() -> int:
    tools = {t['slug']: t for t in load_tools()}
    data = load_data()
    errs = []
    for slug, e in data.get('tools', {}).items():
        if slug not in tools:
            errs.append(f'{slug}: not in config.js freeTools')
        elif e.get('status') != 'unverified':
            errs += [f'{slug}: {x}' for x in check_entry(e, tools[slug])]
    if errs:
        print('❌ data/free/tools.json has problems:')
        for x in errs:
            print('  -', x)
        return 1
    print(f'✅ data/free/tools.json is valid ({len(data.get("tools", {}))} services)')
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    if cmd == 'due':
        return cmd_due()
    if cmd == 'list':
        return cmd_list()
    if cmd == 'add' and len(sys.argv) == 5 and sys.argv[3] == '--file':   # JSON을 파일로 받기
        return cmd_add(sys.argv[2], open(sys.argv[4], encoding='utf-8').read())
    if cmd == 'add' and len(sys.argv) == 4:
        return cmd_add(sys.argv[2], sys.argv[3])
    if cmd == 'merge' and len(sys.argv) == 3:
        return cmd_merge(sys.argv[2])
    if cmd == 'validate':
        return cmd_validate()
    print(__doc__)
    return 1


if __name__ == '__main__':
    sys.exit(main())
