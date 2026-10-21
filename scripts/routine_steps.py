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
  python3 scripts/routine_steps.py publish-init      PHASE 2 시작: 게시 모드 + articles.json 비우기
  python3 scripts/routine_steps.py digest-list       PHASE 2 STEP 1: digest 목록 (섹션 → 탭)
  python3 scripts/routine_steps.py keywords          PHASE 2 SETUP: 탭별 키워드 목록 → /tmp/feed/keywords.json
  python3 scripts/routine_steps.py article-add <<'PYEOF' ... PYEOF    게시용 기사 하나 저장 (검사 포함)
  python3 scripts/routine_steps.py articles-verify   VERIFY ARTICLES

digest-add / article-add 는 표준 입력으로 파이썬 딕셔너리 리터럴 하나를 받는다
(세 따옴표 문자열·이어 붙인 문자열·주석 가능, 코드 실행은 안 됨 — ast.literal_eval).
"""
import ast
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEED = '/tmp/feed'
DIGEST = os.path.join(FEED, 'digest.json')
ARTICLES = os.path.join(FEED, 'articles.json')
KEYWORDS = os.path.join(FEED, 'keywords.json')
SOURCES = os.path.join(REPO, 'routine', 'sources.txt')
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
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_literal():
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


def placeholder(v):
    return not v or (isinstance(v, str) and v.strip().startswith('['))


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
    print('Initialized.')


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


def cmd_digest_add(_):
    a = read_literal()
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
    reject(problems)
    a.setdefault('image_url', '')
    a.setdefault('extra_links', [])
    if placeholder(a['image_url']):
        a['image_url'] = ''
    digest = load(DIGEST, [])
    digest.append(a)
    save(DIGEST, digest)
    print(f"Saved article {len(digest)} (up to 60): {a['title_ko'][:40]}...")


def cmd_digest_verify(_):
    arts = load(DIGEST, [])
    for sec in (1, 2, 3):
        titles = [a['title_ko'] for a in arts if a['section'] == sec]
        print(f'Section {sec}: {len(titles)} articles')
        for t in titles:
            print(f'  - {t[:50]}')
    print(f'Total: {len(arts)} articles collected today.')


# ---------------------------------------------------------------- PHASE 2
def cmd_publish_init(_):
    os.makedirs(FEED, exist_ok=True)
    open(os.path.join(FEED, 'PUBLISH_PHASE'), 'w').close()
    save(ARTICLES, [])
    print('PHASE 2 started — context compaction is now blocked.')
    print('Initialized.')


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


def cmd_article_add(_):
    a = read_literal()
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


if __name__ == '__main__':
    cmds = {'init': cmd_init, 'sources': cmd_sources, 'digest-add': cmd_digest_add,
            'digest-verify': cmd_digest_verify, 'publish-init': cmd_publish_init,
            'digest-list': cmd_digest_list, 'keywords': cmd_keywords,
            'article-add': cmd_article_add, 'articles-verify': cmd_articles_verify}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit('usage: routine_steps.py ' + '|'.join(cmds))
    cmds[sys.argv[1]](sys.argv[2:])
