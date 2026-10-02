"""
feed_data.py — 날짜별 기사 데이터(data/)를 다루는 공통 함수.

레이아웃:
    data/index.json                  날짜 목록 (최신순) + 파일별 기사 수·리비전
    data/articles/YYYY-MM-DD.json    그날 게시된 기사 배열
    data/keywords.json               탭별 서브 카테고리 키워드 목록

    index.json 예:
    {
      "dates": [
        {"date": "2026.10.01", "file": "articles/2026-10-01.json",
         "count": 9, "rev": "3f2a9c01d4"},
        ...
      ]
    }

    rev는 파일 내용의 md5 앞 10자리. 사이트는 날짜 파일을 `?v=<rev>`로
    불러오므로 내용이 바뀐 파일만 브라우저 캐시가 갱신된다.
"""

import hashlib
import json
import os
import re

REPO = os.environ.get('REPO_PATH', '/home/user/Daily_Art_AI_News_Feed')
DATA_DIR = os.path.join(REPO, 'data')
ARTICLES_DIR = os.path.join(DATA_DIR, 'articles')
INDEX_PATH = os.path.join(DATA_DIR, 'index.json')
KEYWORDS_PATH = os.path.join(DATA_DIR, 'keywords.json')

TABS = ('games', 'industry', 'art')
FILE_RE = re.compile(r'^(\d{4})-(\d{2})-(\d{2})\.json$')


def date_to_filename(published_at: str) -> str:
    """'2026.10.01' → '2026-10-01.json'"""
    return published_at.replace('.', '-') + '.json'


def filename_to_date(name: str) -> str:
    """'2026-10-01.json' → '2026.10.01'"""
    m = FILE_RE.match(name)
    if not m:
        raise ValueError(f'Not a date file name: {name}')
    return '.'.join(m.groups())


def normalize_url(u: str) -> str:
    """URL dedup용 정규화 — scheme, www., 끝의 '/', fragment 차이를 무시한다."""
    u = (u or '').strip().split('#', 1)[0]
    u = re.sub(r'^https?://', '', u, flags=re.IGNORECASE)
    u = re.sub(r'^www\.', '', u, flags=re.IGNORECASE)
    host, _, rest = u.partition('/')
    return (host.lower() + ('/' + rest if rest else '')).rstrip('/')


def read_keyword_spec() -> dict:
    with open(KEYWORDS_PATH, encoding='utf-8') as f:
        return json.load(f)


def write_keyword_spec(spec: dict) -> None:
    """data/keywords.json을 한 키워드 한 줄 형식으로 쓴다."""
    lines = ['{', '  "_comment": ' + json.dumps(
        spec.get('_comment', []), ensure_ascii=False, indent=4
    ).replace('\n', '\n  ') + ',', '  "tabs": {']
    tabs = list(spec['tabs'].items())
    for ti, (tab, rows) in enumerate(tabs):
        lines.append(f'    "{tab}": [')
        lines += ['      ' + json.dumps(r, ensure_ascii=False)
                  + (',' if i < len(rows) - 1 else '')
                  for i, r in enumerate(rows)]
        lines.append('    ]' + (',' if ti < len(tabs) - 1 else ''))
    lines += ['  }', '}']
    with open(KEYWORDS_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def keyword_lists() -> dict:
    """탭별 키워드 label 목록 (표시 순서). {'games': ['3D', ...], ...}"""
    spec = read_keyword_spec()
    return {tab: [k['label'] for k in rows] for tab, rows in spec['tabs'].items()}


def date_files() -> list:
    """data/articles/ 안의 날짜 파일 이름 목록 (오래된 순)."""
    if not os.path.isdir(ARTICLES_DIR):
        return []
    return sorted(n for n in os.listdir(ARTICLES_DIR) if FILE_RE.match(n))


def read_day(name: str) -> list:
    with open(os.path.join(ARTICLES_DIR, name), encoding='utf-8') as f:
        return json.load(f)


def serialize_day(articles: list) -> str:
    return json.dumps(articles, ensure_ascii=False, indent=2) + '\n'


def write_day(name: str, articles: list) -> None:
    os.makedirs(ARTICLES_DIR, exist_ok=True)
    with open(os.path.join(ARTICLES_DIR, name), 'w', encoding='utf-8') as f:
        f.write(serialize_day(articles))


def file_rev(name: str) -> str:
    with open(os.path.join(ARTICLES_DIR, name), 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:10]


def build_index() -> dict:
    entries = []
    for name in reversed(date_files()):          # 최신순
        entries.append({
            'date': filename_to_date(name),
            'file': f'articles/{name}',
            'count': len(read_day(name)),
            'rev': file_rev(name),
        })
    return {'dates': entries}


def write_index() -> dict:
    index = build_index()
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
        f.write('\n')
    return index
