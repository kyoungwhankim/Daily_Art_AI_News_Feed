"""
add_keyword.py — 탭의 키워드 목록(data/keywords.json)에 새 키워드를 추가하고
                 지난 기사 중 맞는 것에도 붙인다. 루틴이 PHASE 2 STEP 4에서 쓴다.

사용법:
    python3 scripts/add_keyword.py --tab TAB --label LABEL --kind KIND \
        --match "검색어1,검색어2" [--desc "언제 붙이는지"] [--dry-run]

    --kind   target(제작 대상) | topic(주제) | company(회사) | product(프로그램·서비스)
    --match  지난 기사에서 찾을 이름·표기 (쉼표로 구분, 영문/한글 표기 모두).
             영문/숫자만으로 된 값은 대소문자 무시 + 단어 경계로 찾는다.

동작:
    1. 같은 탭에 이미 있는 label(대소문자 무시)이면 거부한다.
    2. data/keywords.json의 그 탭 목록 끝에 추가하고, /tmp/feed/keywords.json도 갱신한다.
    3. 같은 탭의 지난 기사 중 제목·요약에 --match 값이 있는 기사에 label을 붙인다.
    4. 규칙을 scripts/keyword_rules.json에 남긴다 (다음 관리 작업용).
    5. 붙은 기사 목록을 출력한다.

사이트는 탭 안에서 6개 이상 기사에 붙은 키워드만 서브 카테고리로 보여준다.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feed_data  # noqa: E402
import tag_keywords  # noqa: E402

TMP_KEYWORDS = '/tmp/feed/keywords.json'
KINDS = ('target', 'topic', 'company', 'product')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tab', required=True, choices=feed_data.TABS)
    ap.add_argument('--label', required=True)
    ap.add_argument('--kind', required=True, choices=KINDS)
    ap.add_argument('--match', required=True)
    ap.add_argument('--desc', default='')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    label = args.label.strip()
    terms = [t.strip() for t in args.match.split(',') if t.strip()]
    if not label or not terms:
        sys.exit('REJECTED: --label and --match must not be empty.')

    spec = feed_data.read_keyword_spec()
    rows = spec['tabs'][args.tab]
    if any(r['label'].lower() == label.lower() for r in rows):
        sys.exit(f'REJECTED: "{label}" is already in the {args.tab} list — '
                 f'use the existing label.')

    entry = {'label': label, 'kind': args.kind}
    if args.desc.strip():
        entry['desc'] = args.desc.strip()
    rule = {'label': label, 'kind': args.kind, 'match': terms}
    pattern = re.compile('|'.join(tag_keywords._term_pattern(t) for t in terms),
                         re.IGNORECASE)

    tagged = []
    order = [r['label'] for r in rows] + [label]
    for name in feed_data.date_files():
        day = feed_data.read_day(name)
        new_day = []
        for a in day:
            kws = a.get('keywords', [])
            if (a['tab'] == args.tab and label not in kws and pattern.search(
                    f"{a.get('headline', '')} {a.get('summary', '')}")):
                kws = [k for k in order if k in set(kws) | {label}]
                tagged.append(a)
            new_day.append(tag_keywords.with_keywords(a, kws))
        if not args.dry_run and new_day != day:
            feed_data.write_day(name, new_day)

    if not args.dry_run:
        rows.append(entry)
        feed_data.write_keyword_spec(spec)
        feed_data.write_index()
        if os.path.exists(TMP_KEYWORDS):
            with open(TMP_KEYWORDS, 'w') as f:
                json.dump(feed_data.keyword_lists(), f, ensure_ascii=False)
        with open(tag_keywords.RULES_PATH, encoding='utf-8') as f:
            rules = json.load(f)
        if not any(r['label'] == label for r in rules['keywords']):
            rules['keywords'].append(rule)
            lines = ['{', '  "_comment": ' + json.dumps(
                rules['_comment'], ensure_ascii=False, indent=4
            ).replace('\n', '\n  ') + ',', '  "keywords": [']
            lines += ['    ' + json.dumps(k, ensure_ascii=False)
                      + (',' if i < len(rules['keywords']) - 1 else '')
                      for i, k in enumerate(rules['keywords'])]
            lines += ['  ]', '}']
            with open(tag_keywords.RULES_PATH, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines) + '\n')

    verb = 'Would add' if args.dry_run else 'Added'
    print(f'{verb} keyword "{label}" ({args.kind}) to {args.tab}; '
          f'tagged {len(tagged)} past article(s):')
    for a in tagged:
        print(f'  + {a["publishedAt"]} {a["headline"][:60]}')
    print(f'The chip appears on the site once {args.tab} has 6+ articles '
          f'with "{label}" (now {len(tagged)} past + today\'s).')


if __name__ == '__main__':
    main()
