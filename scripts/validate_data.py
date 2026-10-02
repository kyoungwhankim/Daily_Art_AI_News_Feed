"""
validate_data.py — data/ 디렉터리가 사이트가 읽을 수 있는 상태인지 검사한다.

사용법:
    python3 scripts/validate_data.py

검사 항목:
    - data/index.json과 모든 날짜 파일이 올바른 JSON인지
    - index.json의 날짜 목록·기사 수·rev가 실제 파일과 일치하는지
    - 모든 기사에 필수 필드가 있고, tab이 유효하고, publishedAt이 파일 날짜와 같은지
    - id가 전체에서 중복되지 않는지
    - keywords가 문자열 배열이고 그 탭의 고정 목록(data/keywords.json)에 있는 값인지

통과하면 "✅ data/ is valid ..."를 출력하고 0으로, 실패하면 문제를 출력하고 1로 끝난다.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feed_data  # noqa: E402

REQUIRED = ('id', 'tab', 'headline', 'summary', 'body', 'source',
            'publishedAt', 'hue', 'keywords', 'url')


def main():
    problems = []

    try:
        with open(feed_data.INDEX_PATH, encoding='utf-8') as f:
            index = json.load(f)
    except Exception as e:  # noqa: BLE001
        print(f'❌ data/index.json is unreadable: {e}')
        sys.exit(1)

    try:
        expected = feed_data.build_index()
    except Exception as e:  # noqa: BLE001
        print(f'❌ A date file is unreadable: {e}')
        sys.exit(1)

    if index != expected:
        problems.append('data/index.json is out of date with data/articles/ '
                        '(run scripts/update_articles.py or feed_data.write_index())')

    try:
        keyword_lists = feed_data.keyword_lists()
    except Exception as e:  # noqa: BLE001
        print(f'❌ data/keywords.json is unreadable: {e}')
        sys.exit(1)
    seen_ids = set()
    total = 0
    for name in feed_data.date_files():
        day = feed_data.filename_to_date(name)
        articles = feed_data.read_day(name)
        if not isinstance(articles, list) or not articles:
            problems.append(f'{name}: must be a non-empty JSON array')
            continue
        for i, a in enumerate(articles):
            where = f'{name}[{i}]'
            missing = [k for k in REQUIRED if k not in a]
            if missing:
                problems.append(f'{where}: missing {missing}')
                continue
            if a['tab'] not in feed_data.TABS:
                problems.append(f'{where}: invalid tab {a["tab"]!r}')
            if a['publishedAt'] != day:
                problems.append(f'{where}: publishedAt {a["publishedAt"]} '
                                f'does not match file date {day}')
            kws = a['keywords']
            if not isinstance(kws, list) or not all(isinstance(k, str) for k in kws):
                problems.append(f'{where}: keywords must be a list of strings')
            else:
                unknown = set(kws) - set(keyword_lists.get(a['tab'], []))
                if unknown:
                    problems.append(f'{where}: keywords not in the {a["tab"]} '
                                    f'list {sorted(unknown)}')
            if a['id'] in seen_ids:
                problems.append(f'{where}: duplicate id {a["id"]}')
            seen_ids.add(a['id'])
            total += 1

    if problems:
        print('❌ data/ validation failed:')
        for p in problems:
            print('  -', p)
        sys.exit(1)
    print(f'✅ data/ is valid: {len(index["dates"])} date files, '
          f'{total} articles.')


if __name__ == '__main__':
    main()
