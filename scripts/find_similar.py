#!/usr/bin/env python3
"""
find_similar.py — 새 기사가 이미 게시한 기사와 '같은 소식'인지 확인할 후보를 찾는다.

update_articles.py의 중복 검사는 URL만 비교한다. 같은 소식을 다른 매체가 쓴 기사는 URL이 달라
통과하므로, 루틴은 기사를 digest에 저장하기 전에 이 스크립트로 최근 기사 중 비슷한 것을 찾아
같은 소식이면 건너뛴다.

    python3 scripts/find_similar.py --title "한국어 제목" [--text "원문 제목·요약 등 영어 텍스트"] [--days 21]
                                    [--digest /tmp/feed/digest.json]

    --digest를 주면 오늘 이미 모은 기사(아직 게시 전)와도 비교한다 — 두 섹션이 같은 소식을 고르는 경우.

비교: 제목(과 예전 기사의 요약)의 글자 묶음(2글자씩), 고유명사·숫자 토큰(QSSR, Capcom, PS5, 1000 …),
조사를 뗀 한국어 낱말이 얼마나 겹치는지.
점수가 높은 순으로 최대 5건을 보여 준다. 판단은 사람(루틴)이 한다 — 같은 회사의 다른 소식일 수 있다.

출력:
    SIMILAR: <점수> | <게시일> | <탭> | <제목> | <URL>
    LIKELY_SAME: ...   (점수 0.35 이상 — 같은 소식일 가능성이 높다)
    (없으면) NO_SIMILAR
"""

import argparse
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feed_data  # noqa: E402

STOP = {'ai', 'the', 'a', 'an', 'of', 'and', 'for', 'to', 'in', 'on', 'with', 'is', 'are', 'new', 'its', 'by',
        'at', 'as', 'from', 'that', 'this', 'it', 'be', 'or', 'not', 'how', 'why', 'what', 'will', 'can',
        'game', 'games', 'gaming', 'studio', 'studios', 'model', 'models', 'tool', 'tools', 'video', 'image',
        '생성형', '게임', '공개', '도입', '출시', '발표', '기능', '모델', '개발', '사용', '위한', '통해', '대한'}
THRESHOLD = 0.22
LIKELY = 0.35      # 이 점수 이상이면 같은 소식일 가능성이 높다 — 루틴은 같은 사건이 아님을 확인할 때만 저장한다


def bigrams(s: str) -> set:
    s = re.sub(r'[\s\W_]+', '', s.lower())
    return {s[i:i + 2] for i in range(len(s) - 1)}


# 한국어 낱말 끝의 조사·어미 — '개발사는'과 '개발사가'를 같은 낱말로 본다
JOSA = re.compile(r'(으로써|으로서|에서는|에게서|까지는|부터는|으로|에서|에게|까지|부터|보다|처럼|만큼|이라|이다|하는|했다|한다|은|는|이|가|을|를|에|의|도|로|와|과|만|께)$')


def tokens(s: str) -> set:
    out = set()
    s = re.sub(r'(\d),(\d{3})', r'\1\2', s)          # 1,000 → 1000
    for w in re.findall(r'[A-Za-z][A-Za-z0-9.+-]*[A-Za-z0-9]|\d+[A-Za-z]+|[A-Za-z]+\d+|\d{3,}|[가-힣]{2,}', s):
        w = w.lower().strip('.')
        if re.fullmatch(r'[가-힣]+', w):
            stem = JOSA.sub('', w)
            if len(stem) >= 2:
                w = stem
        if w in STOP or len(w) < 2:
            continue
        out.add(w)
    return out


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--title', required=True, help='새 기사의 한국어 제목')
    ap.add_argument('--text', default='', help='원문 제목·요약 등 추가 텍스트 (영어 고유명사 비교용)')
    ap.add_argument('--days', type=int, default=21, help='비교할 최근 기간 (일)')
    ap.add_argument('--digest', help='오늘 모은 기사 파일 (PHASE 1 digest.json)')
    args = ap.parse_args()

    since = dt.date.today() - dt.timedelta(days=args.days)
    new_bi = bigrams(args.title)
    new_tok = tokens(args.title + ' ' + args.text)
    candidates = []
    if args.digest and os.path.exists(args.digest):
        with open(args.digest, encoding='utf-8') as f:
            for d in json.load(f):
                candidates.append({'headline': d.get('title_ko', ''), 'summary': ' '.join(d.get('summary_ko', [])),
                                   'publishedAt': 'TODAY (digest)', 'tab': f"section {d.get('section')}",
                                   'url': d.get('source_url', '')})
    for name in feed_data.date_files():
        day = feed_data.filename_to_date(name)
        if dt.date(*map(int, day.split('.'))) < since:
            continue
        candidates += feed_data.read_day(name)
    found = []
    for a in candidates:
        old_tok = tokens(a['headline'] + ' ' + a.get('summary', ''))
        shared = new_tok & old_tok
        # 제목끼리, 그리고 새 제목과 예전 기사의 제목+요약을 비교해 더 높은 쪽을 쓴다
        bi = max(jaccard(new_bi, bigrams(a['headline'])),
                 jaccard(new_bi, bigrams(a['headline'] + a.get('summary', ''))) * 1.2)
        # 낱말 겹침: 새 기사 낱말 중 예전 기사에도 있는 비율 (예전 기사가 길어도 점수가 깎이지 않게)
        cover = len(shared) / len(new_tok) if new_tok else 0.0
        score = 0.5 * bi + 0.5 * max(jaccard(new_tok, old_tok), cover * 0.8)
        # 이름이 흔치 않은 고유명사(영문)나 숫자(금액·수치)가 둘 이상 겹치면 같은 소식일 가능성이 크다
        rare = {t for t in shared if re.search(r'[a-z0-9]', t)}
        if len(rare) >= 2:
            score += 0.15
        # 한국어 핵심 낱말이 넷 이상 겹치면 같은 사건일 가능성이 크다
        if len(shared - rare) >= 4:
            score += 0.1
        if score >= THRESHOLD:
            found.append((round(score, 2), a, sorted(shared)))
    found.sort(key=lambda x: -x[0])
    if not found:
        print('NO_SIMILAR')
        return
    for score, a, shared in found[:5]:
        tag = 'LIKELY_SAME' if score >= LIKELY else 'SIMILAR'
        print(f"{tag}: {score} | {a['publishedAt']} | {a['tab']} | {a['headline']} | {a['url']}")
        print(f"         공통 단어: {', '.join(shared[:10]) or '-'}")


if __name__ == '__main__':
    main()
