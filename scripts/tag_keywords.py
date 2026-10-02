"""
tag_keywords.py — 지난 기사에 키워드를 일괄로 붙이는 관리용 도구 (루틴은 쓰지 않는다).

키워드는 고정 목록(data/keywords.json)으로 관리하고, 매일 루틴은 프롬프트의
KEYWORD LIST를 보고 새 기사의 keywords를 직접 고른다. 키워드를 새로 추가할 때만
이 도구로 지난 기사에 그 키워드를 붙인다.

사용법:
    python3 scripts/tag_keywords.py LABEL [--tab TAB] [--apply]

    LABEL   추가할 키워드 (data/keywords.json의 해당 탭 목록에 먼저 넣어 둔다)
    --tab   대상 탭 (생략하면 LABEL이 목록에 있는 모든 탭)
    --apply 실제로 파일에 쓴다. 없으면 붙을 기사 목록만 출력한다.

규칙은 scripts/keyword_rules.json. 규칙이 맞은 기사에 LABEL을 더하고
(기존 keywords는 유지), 탭 목록 순서로 정렬한다. 결과는 반드시 눈으로 확인한다.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feed_data  # noqa: E402

RULES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'keyword_rules.json')
ASCII_RE = re.compile(r'^[\x00-\x7f]+$')


def _term_pattern(term: str) -> str:
    if ASCII_RE.match(term):
        return r'(?<![A-Za-z0-9])' + re.escape(term) + r'(?![A-Za-z0-9])'
    return re.escape(term)


def load_rules(path: str = RULES_PATH) -> list:
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
    text = _plain((body or '').split('</p>', 1)[0])
    m = re.search(r'(.+?(?:요|다|\.))(?:\s|$)', text)
    return m.group(1) if m else text


def matches(article: dict, rule: dict) -> bool:
    """target은 제목+요약, company/product는 제목+요약+본문 첫 문장에서 찾는다."""
    text = f"{article.get('headline', '')} {article.get('summary', '')}"
    if rule['kind'] != 'target':
        text += ' ' + _first_sentence(article.get('body', ''))
    for ex in rule['exclude']:
        text = ex.sub(' ', text)
    return bool(rule['match'].search(text))


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
    ap = argparse.ArgumentParser()
    ap.add_argument('label')
    ap.add_argument('--tab', choices=feed_data.TABS)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    lists = feed_data.keyword_lists()
    tabs = [args.tab] if args.tab else [t for t in feed_data.TABS
                                        if args.label in lists.get(t, [])]
    missing = [t for t in tabs if args.label not in lists.get(t, [])]
    if not tabs or missing:
        sys.exit(f'"{args.label}" is not in the keyword list of '
                 f'{missing or "any tab"} — add it to data/keywords.json first.')
    rule = next((r for r in load_rules() if r['label'] == args.label), None)
    if rule is None:
        sys.exit(f'No rule for "{args.label}" in scripts/keyword_rules.json — '
                 f'add one, or tag the articles by hand.')

    hits = 0
    for name in feed_data.date_files():
        day = feed_data.read_day(name)
        new_day = []
        for a in day:
            kws = a.get('keywords', [])
            if a['tab'] in tabs and args.label not in kws and matches(a, rule):
                hits += 1
                print(f'  + [{a["tab"]}] {a["publishedAt"]} {a["headline"][:60]}')
                order = lists[a['tab']]
                kws = [k for k in order if k in set(kws) | {args.label}]
            new_day.append(with_keywords(a, kws))
        if args.apply and new_day != day:
            feed_data.write_day(name, new_day)
    if args.apply:
        feed_data.write_index()
    print(f'{"Tagged" if args.apply else "Would tag"} {hits} article(s) '
          f'with "{args.label}".')


if __name__ == '__main__':
    main()
