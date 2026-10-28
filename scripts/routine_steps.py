#!/usr/bin/env python3
"""routine_steps.py — 매일 루틴(routine/daily_feed_prompt.txt)의 고정 단계를 모은 스크립트.

예전에는 이 코드들이 루틴 지침 안에 그대로 들어 있어 지침이 길었고, 모델이 베껴 쓰다 틀리기도 했다.
지침은 아래 명령만 부른다. 출력 문구("Whitelist loaded:", "Keyword list loaded:", "REJECTED", "Saved article")는
지침의 실행 규칙이 가리키므로 바꾸지 않는다.

  python3 scripts/routine_steps.py init              PHASE 1 시작: /tmp/feed 초기화 (digest 비우기)
  python3 scripts/routine_steps.py sources           출처 목록(routine/sources.txt) → /tmp/feed/whitelist.json
  python3 scripts/routine_steps.py sources games     한 섹션의 출처 목록 다시 보기 (games|industry|art)
  python3 scripts/routine_steps.py digest-add <<'PYEOF' ... PYEOF     기사 하나를 digest에 저장 (검사 포함)
  python3 scripts/routine_steps.py digest-verify     VERIFY DIGEST
  python3 scripts/routine_steps.py review            피드 스캔 ★ 글 중 아직 판단하지 않은 것
  python3 scripts/routine_steps.py skip "<url>" "<이유>"   ★ 글을 싣지 않기로 한 기록
  python3 scripts/routine_steps.py publish-init      PHASE 2 시작: 게시 모드 + articles.json 비우기
  python3 scripts/routine_steps.py digest-list       PHASE 2 STEP 1: digest 목록 (섹션 → 탭)
  python3 scripts/routine_steps.py keywords          PHASE 2 SETUP: 탭별 키워드 목록 → /tmp/feed/keywords.json
  python3 scripts/routine_steps.py article-add <<'PYEOF' ... PYEOF    게시용 기사 하나 저장 (검사 포함)
  python3 scripts/routine_steps.py articles-verify   VERIFY ARTICLES

digest-add / article-add 는 표준 입력으로 파이썬 딕셔너리 리터럴 하나를 받는다
(세 따옴표 문자열·이어 붙인 문자열·주석 가능, 코드 실행은 안 됨 — ast.literal_eval).
표준 입력 대신 --file PATH 로 파일을 줄 수도 있다 (Windows처럼 heredoc이 없는 셸).

셸 문법(test, rm, if, heredoc)에 기대던 단계도 여기 모았다 — bash가 없는 Windows(PowerShell)에서도
같은 명령으로 돌게 하려고. 작업 파일 위치는 /tmp/... 그대로이고, Windows에서는 현재 드라이브의
\\tmp\\... 가 된다 (`paths`로 실제 위치 확인).

  python3 scripts/routine_steps.py env-check         실행 환경 점검 (파이썬·UTF-8 모드·git·curl·node·저장소 위치)
  python3 scripts/routine_steps.py today             오늘 날짜 (KST, YYYY-MM-DD)
  python3 scripts/routine_steps.py paths             작업 폴더의 실제 위치
  python3 scripts/routine_steps.py workdir updates|free|report [--remove]   작업 폴더 비우기 (또는 지우기)
  python3 scripts/routine_steps.py agent-init updates|free|report           에이전트 작업 시작 (빈 entries.json)
  python3 scripts/routine_steps.py agent-note updates|free "한 줄"          failed_sources.txt / candidates.txt에 한 줄 추가
  python3 scripts/routine_steps.py agent-count updates                      서비스별 저장 개수
  python3 scripts/routine_steps.py agent-finish updates|free|report [--file PATH]   REPORT.txt + DONE 표시
  python3 scripts/routine_steps.py agent-status updates|free                에이전트가 끝났는지
  python3 scripts/routine_steps.py apply-updates | save-source-state | apply-free | apply-report
  python3 scripts/routine_steps.py undo-data updates|free|reports           data/<이름> 변경 되돌리기
(이름에 merge·commit·restore를 쓰지 않는다 — 자동 승인 검사가 git 명령으로 오해해 막은 적이 있다)
  python3 scripts/routine_steps.py publish-end       게시 모드 끝 (PUBLISH_PHASE 삭제)
  python3 scripts/routine_steps.py push-local        로컬 git 로그인으로 main에 커밋·푸시 (토큰 없는 환경용)
"""
import ast
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, 'reconfigure'):      # Windows 콘솔(cp949)에서 출력 중 멈추지 않게
    sys.stdout.reconfigure(errors='replace')
FEED = '/tmp/feed'
DIGEST = os.path.join(FEED, 'digest.json')
ARTICLES = os.path.join(FEED, 'articles.json')
KEYWORDS = os.path.join(FEED, 'keywords.json')
ARTICLES_SIG = os.path.join(FEED, 'articles.sig')
SHORTLIST = os.path.join(FEED, 'shortlist.json')      # scan_feeds.py가 ★로 표시한 글 — 하나씩 판단해야 한다
DECISIONS = os.path.join(FEED, 'decisions.json')      # {정규화한 URL: 'saved' | 'skip: 이유'}     # article-add만 쓴다 — push-local이 손으로 고친 파일을 가려낸다
SOURCES = os.path.join(REPO, 'routine', 'sources.txt')
WORK = {'updates': '/tmp/updates', 'free': '/tmp/free', 'report': '/tmp/report'}
NOTE_FILE = {'updates': 'failed_sources.txt', 'free': 'candidates.txt'}
KST = timezone(timedelta(hours=9))
PY = sys.executable or 'python3'
TAB = {1: 'games', 2: 'industry', 3: 'art'}
HUE = {'games': 200, 'industry': 30, 'art': 290}     # 이미지가 없을 때 쓰는 탭 기본 색
BODY_LEN = (600, 800)                                 # 본문 글자 수 (공백 포함, 태그·원문 줄 제외)


def load(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save(path, data):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_literal(args=()):
    args = list(args)
    if '--file' in args:
        src = open(args[args.index('--file') + 1], encoding='utf-8-sig').read().strip()   # BOM이 붙어도 읽음
    else:
        src = sys.stdin.read().strip()
    # 'article = {...}' 처럼 이름을 붙여 써도 받아 준다
    src = re.sub(r'^\s*\w+\s*=\s*', '', src, count=1)
    try:
        obj = ast.literal_eval(src)
    except (ValueError, SyntaxError) as e:
        print(f'REJECTED: could not read the article dict ({e.__class__.__name__}: {e})')
        sys.exit(1)
    if not isinstance(obj, dict):
        print('REJECTED: input must be one dict')
        sys.exit(1)
    return obj


def norm_url(u):
    u = (u or '').strip().split('#', 1)[0]
    u = re.sub(r'^https?://(www\.)?', '', u, flags=re.I)
    return u.rstrip('/').lower()


def decide(url, what):
    d = load(DECISIONS, {})
    d[norm_url(url)] = what
    save(DECISIONS, d)


def open_shortlist():
    d = load(DECISIONS, {})
    return [x for x in load(SHORTLIST, []) if norm_url(x['url']) not in d]


def placeholder(v):
    return not v or (isinstance(v, str) and v.strip().startswith('['))


def broken_text(a, korean_keys):
    """인코딩이 깨진 글자, 또는 한국어여야 할 필드에 한글이 하나도 없는 경우를 찾는다."""
    out = []
    flat = json.dumps(a, ensure_ascii=False)
    if '\ufffd' in flat:
        out.append('text contains broken characters (U+FFFD) — the input was not UTF-8; write it with '
                   'your file tool (UTF-8) and pass --file, never pipe text into python')
    for k in korean_keys:
        v = a.get(k)
        v = ' '.join(v) if isinstance(v, list) else (v or '')
        if v and not re.search('[가-힣]', v):
            out.append(f'{k} has no Korean letters — if you wrote Korean, it was broken on the way '
                       '(use --file with a UTF-8 file)')
    return out


def reject(problems):
    if problems:
        print('REJECTED:', '; '.join(problems))
        sys.exit(1)


# ---------------------------------------------------------------- PHASE 1
def cmd_init(_):
    os.makedirs(FEED, exist_ok=True)
    try:
        os.remove(os.path.join(FEED, 'PUBLISH_PHASE'))   # 조사 단계에서는 컨텍스트 압축 허용
    except FileNotFoundError:
        pass
    save(DIGEST, [])
    print('Initialized: empty digest.')


def parse_sources():
    raw = '\n'.join(l for l in open(SOURCES, encoding='utf-8').read().split('\n') if not l.startswith('#'))
    key = {'공통': 'common', '게임 제작': 'games', '글로벌 스튜디오 AI 도입': 'industry', '아트 전반': 'art'}
    wl = {'common': [], **{k: {'primary': [], 'broadened': []} for k in ('games', 'industry', 'art')}}
    split = lambda s: [x.strip().strip('.,;') for x in s.replace('\n', ' ').split(',') if x.strip().strip('.,;')]
    parts = re.split(r'\n\s*\[([^\]]+)\]\s*\n', '\n' + raw)
    for i in range(1, len(parts), 2):
        k = key.get(parts[i].strip())
        body = parts[i + 1] if i + 1 < len(parts) else ''
        if not k:
            continue
        if k == 'common':
            wl['common'] = split(body)
            continue
        pm = re.search(r'-\s*Primary\s*:\s*([\s\S]*?)(?=\n\s*-\s*Broadened\s*:|\Z)', body, re.I)
        bm = re.search(r'-\s*Broadened\s*:\s*([\s\S]*?)\Z', body, re.I)
        wl[k]['primary'] = split(pm.group(1)) if pm else []
        wl[k]['broadened'] = split(bm.group(1)) if bm else []
    return wl


def cmd_sources(args):
    wl = parse_sources()
    if args:
        sec = args[0]
        if sec not in ('games', 'industry', 'art'):
            sys.exit('section must be games, industry or art')
        print('Common   :', ', '.join(wl['common']))
        print('Primary  :', ', '.join(wl[sec]['primary']))
        print('Broadened:', ', '.join(wl[sec]['broadened']))
        return
    if not wl['common'] or any(not wl[s]['primary'] for s in ('games', 'industry', 'art')):
        print('Whitelist parsing failed: a section has 0 sources.')
        sys.exit(1)
    os.makedirs(FEED, exist_ok=True)
    save(os.path.join(FEED, 'whitelist.json'), wl)
    print('Whitelist loaded:')
    print(f"  common   : {len(wl['common'])} sources")
    for sec in ('games', 'industry', 'art'):
        print(f"  {sec:8s}: primary={len(wl[sec]['primary'])}, broadened={len(wl[sec]['broadened'])}")


def cmd_digest_add(args):
    a = read_literal(args)
    problems = []
    if a.get('section') not in (1, 2, 3):
        problems.append('section must be 1, 2 or 3')
    s = a.get('summary_ko')
    if not (isinstance(s, list) and len(s) == 3):
        problems.append('summary_ko must be a list of exactly 3 sentences')
    elif any(placeholder(x) for x in s):
        problems.append('summary_ko still contains a placeholder')
    for k in ('title_ko', 'source_url', 'source_name'):
        if placeholder(a.get(k)):
            problems.append(f'{k} is empty or still a placeholder')
    if not isinstance(a.get('extra_links', []), list):
        problems.append('extra_links must be a list')
    problems += broken_text(a, ('title_ko', 'summary_ko'))
    reject(problems)
    a.setdefault('image_url', '')
    a.setdefault('extra_links', [])
    if placeholder(a['image_url']):
        a['image_url'] = ''
    digest = load(DIGEST, [])
    digest.append(a)
    save(DIGEST, digest)
    decide(a['source_url'], 'saved')
    for link in a.get('extra_links', []):       # 같은 소식의 다른 매체 기사도 판단한 것으로 친다
        if isinstance(link, dict) and link.get('url'):
            decide(link['url'], 'saved (extra link)')
    print(f"Saved article {len(digest)} (up to 60): {a['title_ko'][:40]}...")


def cmd_skip(args):
    if len(args) != 2 or not args[0].startswith('http') or len(args[1].strip()) < 4:
        sys.exit('usage: routine_steps.py skip "<url>" "<reason: off-topic / older than yesterday / same story as ... / paywall ...>"')
    decide(args[0], 'skip: ' + args[1].strip())
    print(f'Skipped ({args[1].strip()}). Open ★ items left: {len(open_shortlist())}')


def cmd_review(_):
    rest = open_shortlist()
    print(f'Open ★ items: {len(rest)} of {len(load(SHORTLIST, []))}')
    for x in rest:
        print(f"  {x['date'][5:10]} | {x['source']} | {x['title']} | {x['url']}")
    if rest:
        print('Judge each one from its line: clearly off-topic / too old / already on the site → '
              '`routine_steps.py skip "<url>" "<reason>"`; otherwise STEP A (peek_article.py) then digest-add.')


def cmd_digest_verify(_):
    rest = open_shortlist()
    if rest:
        print(f'⚠️  {len(rest)} ★ feed-scan items are not judged yet — run `routine_steps.py review` '
              'and judge them before PHASE 2.')
    arts = load(DIGEST, [])
    for sec in (1, 2, 3):
        titles = [a['title_ko'] for a in arts if a['section'] == sec]
        print(f'Section {sec}: {len(titles)} articles')
        for t in titles:
            print(f'  - {t[:50]}')
    print(f'Total: {len(arts)} articles collected today.')


def file_sig(path):
    import hashlib
    try:
        with open(path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return ''


def write_sig():
    with open(ARTICLES_SIG, 'w') as f:
        f.write(file_sig(ARTICLES))


# ---------------------------------------------------------------- PHASE 2
def cmd_publish_init(_):
    os.makedirs(FEED, exist_ok=True)
    open(os.path.join(FEED, 'PUBLISH_PHASE'), 'w').close()
    save(ARTICLES, [])
    write_sig()
    print('PHASE 2 started — context compaction is now blocked.')
    print('Initialized: empty articles list.')


def cmd_digest_list(_):
    digest = load(DIGEST, [])
    if not digest:
        print('No articles in digest today.')
        return
    for sec in (1, 2, 3):
        items = [a for a in digest if a['section'] == sec]
        print(f'Section {sec} -> tab "{TAB[sec]}": {len(items)} articles')
        for a in items:
            print(f"  - {a['title_ko'][:50]} | {a['source_url']}")


def cmd_keywords(_):
    spec = load(os.path.join(REPO, 'data', 'keywords.json'), {})['tabs']
    save(KEYWORDS, {t: [k['label'] for k in rows] for t, rows in spec.items()})
    print('Keyword list loaded:', ', '.join(t + ' ' + str(len(r)) for t, r in spec.items()))
    for t, rows in spec.items():
        print('[' + t + ']')
        for k in rows:
            print('  - ' + k['label'] + (' — ' + k['desc'] if k.get('desc') else ''))


def cmd_article_add(args):
    a = read_literal(args)
    problems = []
    tab = a.get('tab')
    if tab not in HUE:
        problems.append('tab must be games, industry or art')
    for k in ('id', 'headline', 'summary', 'source', 'url'):
        if placeholder(a.get(k)):
            problems.append(f'{k} is empty or still a placeholder')
    body = a.get('body') or ''
    text = re.sub(r'<[^>]+>', '', re.sub(r'<p>원문:.*?</p>', '', body))
    if not BODY_LEN[0] <= len(text) <= BODY_LEN[1]:
        problems.append(f'body is {len(text)} chars (incl. spaces, without the 원문 line); '
                        f'it must be {BODY_LEN[0]}–{BODY_LEN[1]}')
    if '<p>원문: <a href="' not in body:
        problems.append('body is missing the final 원문 attribution paragraph')
    if '\n' in body:
        problems.append('body contains \\n line breaks')
    problems += broken_text(a, ('headline', 'summary', 'body'))
    kws = a.get('keywords', [])
    if not isinstance(kws, list):
        problems.append('keywords must be a list (use [] when none fits)')
    elif tab in HUE:
        allowed = load(KEYWORDS, {}).get(tab, [])
        bad = [k for k in kws if k not in allowed]
        if bad:
            problems.append(f'keywords {bad} are not in the {tab} KEYWORD LIST — use exact labels from '
                            f'the keywords step, or add the keyword with scripts/add_keyword.py first')
    reject(problems)
    a['keywords'] = kws
    a.setdefault('hue', HUE[tab])
    if not a.get('urls'):
        a.pop('urls', None)
    if placeholder(a.get('image')) or a.get('image') == 'NO_IMAGE':
        a.pop('image', None)
    a.pop('publishedAt', None)    # update_articles.py가 채운다
    arts = load(ARTICLES, [])
    arts.append(a)
    save(ARTICLES, arts)
    write_sig()
    print(f"Saved article {len(arts)}: [{tab}] {a['headline'][:40]}... keywords={kws}")


def cmd_articles_verify(_):
    arts = load(ARTICLES, [])
    no_image = sum(1 for a in arts if not a.get('image'))
    for t in ('games', 'industry', 'art'):
        rows = [a for a in arts if a['tab'] == t]
        print(f'{t}: {len(rows)} articles')
        for a in rows:
            print(f"  - {a['headline'][:50]}  {a.get('keywords', [])}")
    print(f'Total: {len(arts)} articles collected today.')
    print(f'Articles without image: {no_image}/{len(arts)}')
    if arts and no_image / len(arts) > 0.3:
        print('⚠️  More than 30% of articles are missing images — STEP 3 may have')
        print('   been skipped for some articles. Check the logs above.')


# ---------------------------------------------------------------- 셸 없이 돌리는 공용 단계
def run(cmd):
    """저장소 루트에서 명령 실행, 출력은 그대로 보여 준다. 종료 코드를 돌려준다."""
    return subprocess.run(cmd, cwd=REPO).returncode


def py(*args):
    return run([PY] + [os.path.join('scripts', args[0])] + list(args[1:]))


def work(name):
    if name not in WORK:
        sys.exit('name must be updates, free or report')
    return WORK[name]


def cmd_env_check(_):
    ok = True
    print('python   :', sys.version.split()[0], sys.executable)
    utf8 = sys.flags.utf8_mode or os.name != 'nt'
    print('utf-8    :', 'ok' if utf8 else 'NOT SET — set PYTHONUTF8=1 (Korean text breaks without it)')
    ok &= bool(utf8)
    for tool in ('git', 'curl', 'node'):    # node: config.js의 서비스 목록을 읽는다
        path = shutil.which(tool)
        print(f'{tool:9s}:', path or 'NOT FOUND')
        ok &= bool(path)
    print('Text check: 한국어 · 日本語 · 中文 · Größe')
    print('repo     :', REPO)
    head = git('rev-parse', 'HEAD').stdout.strip()
    git('fetch', '-q', 'origin', 'main')
    upstream = git('rev-parse', 'origin/main').stdout.strip()
    in_rebase = os.path.isdir(os.path.join(REPO, '.git', 'rebase-merge')) or \
        os.path.isdir(os.path.join(REPO, '.git', 'rebase-apply'))
    fresh = head == upstream and not in_rebase
    print('git      :', 'up to date with origin/main' if fresh else
          f'NOT up to date (HEAD {head[:7]}, origin/main {upstream[:7]}{", rebase in progress" if in_rebase else ""}) '
          '— run: git rebase --abort; git checkout -f main; git reset --hard origin/main')
    ok &= fresh
    print('work dir :', os.path.abspath(FEED))
    print('Environment OK.' if ok else 'Environment check FAILED — fix the lines above before running the routine.')
    sys.exit(0 if ok else 1)


def cmd_today(_):
    print(datetime.now(KST).strftime('%Y-%m-%d'))


def cmd_paths(_):
    for n, p in [('feed', FEED)] + list(WORK.items()) + [('log', '/tmp/routine_log')]:
        print(f'{n:8s}: {os.path.abspath(p)}')


def cmd_workdir(args):
    d = work(args[0] if args else '')
    shutil.rmtree(d, ignore_errors=True)
    if '--remove' in args:
        print(f'Removed {d}')
        return
    os.makedirs(d)
    print(f'Empty work dir: {d}')


def cmd_agent_init(args):
    name = args[0] if args else ''
    d = work(name)
    os.makedirs(d, exist_ok=True)
    try:
        os.remove(os.path.join(d, 'DONE'))
    except FileNotFoundError:
        pass
    save(os.path.join(d, 'entries.json'), [])
    if name in NOTE_FILE:
        open(os.path.join(d, NOTE_FILE[name]), 'w', encoding='utf-8', newline='\n').close()
    print(f'{name} work started: {d}')


def cmd_agent_note(args):
    if len(args) != 2 or args[0] not in NOTE_FILE:
        sys.exit('usage: agent-note updates|free "one line"')
    with open(os.path.join(work(args[0]), NOTE_FILE[args[0]]), 'a', encoding='utf-8') as f:
        f.write(args[1].strip() + '\n')
    print('Noted.')


def cmd_agent_count(args):
    name = args[0] if args else 'updates'
    e = load(os.path.join(work(name), 'entries.json'), [])
    key = {'updates': 'service', 'free': 'slug', 'report': 'role'}[name]
    print('Entries per ' + key + ':', dict(Counter(x.get(key) for x in e)) or 'none')
    print('Total:', len(e))


def cmd_agent_finish(args):
    name = args[0] if args else ''
    d = work(name)
    e = load(os.path.join(d, 'entries.json'), [])
    if name == 'free':
        c = Counter(x['status'] for x in e)
        lines = [f'Free tools agent: checked {len(e)} services — ' + ', '.join(f'{k} {v}' for k, v in sorted(c.items()))]
        un = [x['slug'] for x in e if x['status'] == 'unverified']
        if un:
            lines.append('Unverified: ' + ', '.join(un))
        cand = open(os.path.join(d, 'candidates.txt'), encoding='utf-8').read().strip() \
            if os.path.exists(os.path.join(d, 'candidates.txt')) else ''
        if cand:
            lines.append('New service candidates (not added):\n' + cand)
        report = '\n'.join(lines)
    elif name == 'report':
        report = f'Weekly report agent: wrote {len(e)} reports — ' + ', '.join(x['role'] for x in e)
    else:
        # 업데이트 작업: 보고 내용(서비스별 모드·저장 개수·읽지 못한 출처)은 작성자가 준다
        report = (open(args[args.index('--file') + 1], encoding='utf-8-sig').read() if '--file' in args
                  else sys.stdin.read()).strip()
        if not report:
            sys.exit('give the report text on stdin or with --file PATH')
    with open(os.path.join(d, 'REPORT.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(report + '\n')
    with open(os.path.join(d, 'DONE'), 'w') as f:
        f.write('done')
    print(report)


def cmd_agent_status(args):
    name = args[0] if args else ''
    d = work(name)
    label = {'updates': 'Updates agent', 'free': 'Free-tools agent', 'report': 'Weekly report agent'}[name]
    if name == 'free' and not os.path.isdir(d):
        print('No free-tools agent today.')
    elif os.path.exists(os.path.join(d, 'DONE')):
        print(f'{label} finished.')
        rp = os.path.join(d, 'REPORT.txt')
        if os.path.exists(rp):
            print(open(rp, encoding='utf-8').read().rstrip())
    else:
        print(f'{label} still running.')


def done_with_entries(name):
    d = WORK[name]
    return os.path.exists(os.path.join(d, 'DONE')) and load(os.path.join(d, 'entries.json'), [])


def cmd_apply_updates(_):
    rc = 0
    rejected = os.path.join(WORK['updates'], 'MERGE_REJECTED')
    if done_with_entries('updates'):
        rc = py('service_updates.py', 'merge', os.path.join(WORK['updates'], 'entries.json'))
        if rc:      # 병합이 거부되면 출처 확인 기록도 남기지 않는다 (save-source-state가 본다)
            open(rejected, 'w').close()
    else:
        print('No service updates to merge today.')
    rc = py('validate_data.py') or rc
    sys.exit(rc)


def cmd_save_source_state(_):
    if os.path.exists(os.path.join(WORK['updates'], 'MERGE_REJECTED')):
        print('Service updates were REJECTED — source state not saved (checked again tomorrow).')
        return
    if os.path.exists(os.path.join(WORK['updates'], 'DONE')):
        rc = py('detect_source_changes.py', 'commit', '--failed', os.path.join(WORK['updates'], 'failed_sources.txt'))
        if rc == 0:
            open(os.path.join(WORK['updates'], 'STATE_SAVED'), 'w').close()
        else:
            print('Source state NOT saved. If it says source_state.next.json was not found, the updates work '
                  'folder was cleared after `detect_source_changes.py check` — run that check again, then this.')
        sys.exit(rc)
    print('Updates work did not finish — source state not saved (checked again tomorrow).')


def cmd_apply_free(_):
    if done_with_entries('free'):
        f = os.path.join(WORK['free'], 'entries.json')
        sys.exit(py('free_tools.py', 'merge', f) or py('free_tools.py', 'validate'))
    print('No free-tools results to merge today.')


def cmd_apply_report(_):
    if done_with_entries('report'):
        f = os.path.join(WORK['report'], 'entries.json')
        sys.exit(py('weekly_report.py', 'merge', f) or py('weekly_report.py', 'validate'))
    print('No weekly report this week.')


def cmd_undo_data(args):
    if not args or args[0] not in ('updates', 'free', 'reports'):
        sys.exit('usage: undo-data updates|free|reports')
    path = 'data/' + args[0]
    subprocess.run(['git', 'checkout', '--', path], cwd=REPO, capture_output=True)
    subprocess.run(['git', 'clean', '-fdq', path], cwd=REPO)
    print(f'Restored {path}.')
    py('validate_data.py')


def cmd_publish_end(_):
    try:
        os.remove(os.path.join(FEED, 'PUBLISH_PHASE'))
    except FileNotFoundError:
        pass
    print('Publish mode ended.')


def git(*a):
    return subprocess.run(['git'] + list(a), cwd=REPO, capture_output=True, text=True)


def preflight(args):
    """푸시 전 검사 — 루틴 단계를 건너뛴 결과가 사이트에 올라가지 않게 한다. 문제 목록을 돌려준다."""
    problems = []
    digest = load(DIGEST, None)
    if digest is None:
        problems.append('no /tmp/feed/digest.json — PHASE 1 (digest-add) was not run')
    arts = load(ARTICLES, None)
    if arts is None:
        problems.append('no /tmp/feed/articles.json — PHASE 2 (publish-init / article-add) was not run')
    elif not os.path.exists(ARTICLES_SIG) or open(ARTICLES_SIG).read().strip() != file_sig(ARTICLES):
        problems.append('/tmp/feed/articles.json was not written by `routine_steps.py article-add` '
                        '(edited by hand or another tool) — save every article with article-add')
    if digest is not None and arts is not None and len(arts) < len(digest):
        problems.append(f'digest has {len(digest)} articles but only {len(arts)} were saved with article-add')
    if not os.path.exists(os.path.join(WORK['updates'], 'DONE')):
        problems.append('updates work not finished (no /tmp/updates/DONE) — do the UPDATES WORK '
                        '(routine/updates_agent_prompt.txt) up to agent-finish')
    upd = WORK['updates']
    if os.path.exists(os.path.join(upd, 'DONE')) and not os.path.exists(os.path.join(upd, 'MERGE_REJECTED')) \
            and not os.path.exists(os.path.join(upd, 'STATE_SAVED')):
        problems.append('source state not saved — run `routine_steps.py apply-updates` then `save-source-state` '
                        '(if it says source_state.next.json was not found, run detect_source_changes.py check again first)')
    rest = open_shortlist()
    if rest:
        problems.append(f'{len(rest)} ★ feed-scan items were never judged (digest-add or skip) — '
                        'run `routine_steps.py review`')
    cands = load(os.path.join(FEED, 'candidates.json'), [])
    if digest is not None and len(cands) >= 60 and len(digest) < 4 and '--few-ok' not in args:
        problems.append(f'only {len(digest)} articles from {len(cands)} feed-scan candidates — check every '
                        'source in the FEED SCAN output (all languages) per R2; if the day really has so few, '
                        'rerun with --few-ok "<reason>"')
    return problems


# 다른 파일에서 다시 만들어지는 파일 — 충돌하면 위쪽(main) 것을 받고 스크립트로 다시 만든다
GENERATED = ('data/index.json', 'data/updates/index.json', 'data/updates/latest.json')


def resolve_generated_conflicts():
    """rebase 충돌이 생성 파일에서만 났으면 다시 만들어 이어 간다. 해결하면 True."""
    for _ in range(10):
        if not os.path.isdir(os.path.join(REPO, '.git', 'rebase-merge')) and \
                not os.path.isdir(os.path.join(REPO, '.git', 'rebase-apply')):
            return True
        conflicted = [f for f in git('diff', '--name-only', '--diff-filter=U').stdout.split() if f]
        other = [f for f in conflicted if f not in GENERATED and not f.startswith('data/updates/feed/')]
        if other:
            print('Conflict in files that cannot be regenerated:', ', '.join(other))
            return False
        if conflicted:
            git('checkout', '--ours', '--', *conflicted)       # rebase 중 'ours' = 이미 main에 있는 쪽
            py('service_updates.py', 'rebuild')
            subprocess.run([PY, '-c', 'import sys; sys.path.insert(0, "scripts"); import feed_data; '
                            'feed_data.write_index()'], cwd=REPO)
            git('add', 'data')
            print('Regenerated after a rebase conflict:', ', '.join(conflicted))
        r = subprocess.run(['git', '-c', 'core.editor=true', 'rebase', '--continue'], cwd=REPO,
                           capture_output=True, text=True)
        if r.returncode and 'nothing to commit' not in (r.stdout + r.stderr):
            if not git('diff', '--name-only', '--diff-filter=U').stdout.strip():
                return False
    return False


def cmd_push_local(args):
    """토큰 없이 이 컴퓨터의 git 로그인으로 main에 올린다 (Antigravity 등 로컬 실행용)."""
    branch = git('rev-parse', '--abbrev-ref', 'HEAD').stdout.strip()
    if branch != 'main':
        sys.exit(f'Not on main (on "{branch}") — refusing to push.')
    problems = preflight(args)
    if problems:
        print('PUSH REFUSED — the routine is not finished:')
        for p in problems:
            print('  - ' + p)
        print('Fix these (run the missing steps), then run push-local again.')
        sys.exit(1)
    # 이 컴퓨터의 git 사용자로 커밋한다 — Claude 루틴 지침의 `git config user.*`가 실수로 실행돼
    # 저장소에 'Claude Daily Routine'이 남아 있으면 지운다
    if git('config', '--local', 'user.email').stdout.strip() == 'claude-routine@anthropic.com':
        git('config', '--local', '--unset', 'user.email')
        git('config', '--local', '--unset', 'user.name')
        print('Removed the Claude routine git identity from this repository (using your own).')
    git('add', 'data', 'scripts/keyword_rules.json')
    stat = git('diff', '--cached', '--stat').stdout
    print('Staged changes:\n' + (stat or '(none)'))
    if not stat.strip():
        print('No changes to commit.')
        return
    msg = 'Daily AI news feed: ' + datetime.now(KST).strftime('%Y.%m.%d')
    if '--few-ok' in args and args.index('--few-ok') + 1 < len(args):
        msg += '\n\nFew articles today: ' + args[args.index('--few-ok') + 1]
    r = git('commit', '-m', msg)
    if r.returncode:
        sys.exit('Commit failed:\n' + r.stdout + r.stderr)
    for attempt in (1, 2):
        r = git('pull', '--rebase', 'origin', 'main')
        if r.returncode and not resolve_generated_conflicts():
            git('rebase', '--abort')
            sys.exit('Pull failed (rebase aborted, nothing pushed — the commit is still on local main):\n'
                     + r.stdout + r.stderr)
        r = git('push', 'origin', 'main')
        if not r.returncode:
            print('✅ Pushed to main:', git('log', '--oneline', '-1').stdout.strip())
            return
        print(f'Push attempt {attempt} failed:\n' + r.stderr)
    sys.exit('Push failed twice — not forcing. Report this.')


if __name__ == '__main__':
    cmds = {'init': cmd_init, 'sources': cmd_sources, 'digest-add': cmd_digest_add,
            'digest-verify': cmd_digest_verify, 'publish-init': cmd_publish_init,
            'digest-list': cmd_digest_list, 'keywords': cmd_keywords,
            'article-add': cmd_article_add, 'articles-verify': cmd_articles_verify,
            'env-check': cmd_env_check, 'today': cmd_today, 'paths': cmd_paths, 'workdir': cmd_workdir,
            'agent-init': cmd_agent_init, 'agent-note': cmd_agent_note, 'agent-count': cmd_agent_count,
            'agent-finish': cmd_agent_finish, 'agent-status': cmd_agent_status,
            'apply-updates': cmd_apply_updates, 'save-source-state': cmd_save_source_state,
            'apply-free': cmd_apply_free, 'apply-report': cmd_apply_report, 'undo-data': cmd_undo_data,
            'publish-end': cmd_publish_end, 'push-local': cmd_push_local,
            'skip': cmd_skip, 'review': cmd_review}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit('usage: routine_steps.py ' + '|'.join(cmds))
    cmds[sys.argv[1]](sys.argv[2:])
