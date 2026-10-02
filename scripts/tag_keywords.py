"""
tag_keywords.py — 기사에 서브 카테고리 키워드(keywords)를 붙인다.

사용법:
    python3 scripts/tag_keywords.py          # 모든 날짜 파일을 다시 태깅 (사전을 고친 뒤 실행)
    python3 scripts/tag_keywords.py --check  # 파일은 그대로 두고, 다시 태깅하면 바뀔 기사 수만 출력

키워드 사전은 scripts/keywords.json. update_articles.py는 새 기사를 추가할 때
이 모듈의 tag()로 keywords를 자동으로 붙이므로 루틴은 따로 실행할 필요가 없다.

검사 범위:
    target(제작 대상)        제목 + 요약
    company/product(이름)   제목 + 요약 + 본문 첫 문장
"""

import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feed_data  # noqa: E402

KEYWORDS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'keywords.json')
MIN_ARTICLES = 6      # 사이트와 같은 기준 — 탭 안에서 6개 이상이어야 서브 카테고리
ASCII_RE = re.compile(r'^[\x00-\x7f]+$')


def _term_pattern(term: str) -> str:
    if ASCII_RE.match(term):
        return r'(?<![A-Za-z0-9])' + re.escape(term) + r'(?![A-Za-z0-9])'
    return re.escape(term)


def load_rules(path: str = KEYWORDS_PATH) -> list:
    with open(path, encoding='utf-8') as f:
        spec = json.load(f)
    rules = []
    for k in spec['keywords']:
        rules.append({
            'label': k['label'],
            'kind': k['kind'],
            'match': re.compile('|'.join(_term_pattern(t) for t in k['match']),
                                re.IGNORECASE),
            'exclude': [re.compile(re.escape(t), re.IGNORECASE)
                        for t in k.get('exclude', [])],
        })
    return rules


def _plain(html: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html or '')).strip()


def _first_sentence(body: str) -> str:
    first_p = (body or '').split('</p>', 1)[0]
    text = _plain(first_p)
    m = re.search(r'(.+?(?:요|다|\.))(?:\s|$)', text)
    return m.group(1) if m else text


def tag(article: dict, rules: list) -> list:
    """기사의 keywords 목록 (사전 순서)."""
    short = f"{article.get('headline', '')} {article.get('summary', '')}"
    long = f"{short} {_first_sentence(article.get('body', ''))}"
    out = []
    for r in rules:
        text = short if r['kind'] == 'target' else long
        for ex in r['exclude']:
            text = ex.sub(' ', text)
        if r['match'].search(text):
            out.append(r['label'])
    return out


def with_keywords(article: dict, keywords: list) -> dict:
    """keywords를 url 앞(필드 순서: ... hue, image?, keywords, url, urls?)에 넣은 사본."""
    out = {}
    for k, v in article.items():
        if k == 'keywords':
            continue
        if k == 'url':
            out['keywords'] = keywords
        out[k] = v
    if 'keywords' not in out:
        out['keywords'] = keywords
    return out


def main():
    check_only = '--check' in sys.argv[1:]
    rules = load_rules()
    changed = 0
    per_tab = {t: Counter() for t in feed_data.TABS}
    untagged = Counter()
    for name in feed_data.date_files():
        day = feed_data.read_day(name)
        new_day = []
        for a in day:
            kws = tag(a, rules)
            if a.get('keywords') != kws:
                changed += 1
            new_day.append(with_keywords(a, kws))
            per_tab[a['tab']].update(kws)
            if not kws:
                untagged[a['tab']] += 1
        if not check_only and new_day != day:
            feed_data.write_day(name, new_day)
    if not check_only:
        feed_data.write_index()

    verb = 'would change' if check_only else 'updated'
    print(f'{verb} keywords on {changed} article(s).')
    for t in feed_data.TABS:
        shown = [f'{k} {n}' for k, n in per_tab[t].most_common()
                 if n >= MIN_ARTICLES]
        print(f'  {t}: {len(shown)} sub-categories, '
              f'{untagged[t]} article(s) without keywords')
        print('    ' + ', '.join(shown))


if __name__ == '__main__':
    main()
