#!/usr/bin/env python3
"""config.js의 updateSources(업데이트 수집 출처)가 지금 열리는지 확인한다.

    python3 scripts/check_update_sources.py           # 전체
    python3 scripts/check_update_sources.py Kling Veo # 이름으로 골라서

각 서비스의 notice(공지)·dev(개발자 변경 기록) 주소에 요청을 보내 HTTP 상태를 보여 준다.
403은 대개 사이트가 자동 접속을 막은 것이라 브라우저로는 열린다 — 수집은 다른 출처로 해야 한다.
node가 있어야 한다 (config.js를 그대로 읽는다).
"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = 'Mozilla/5.0 (compatible; AIArtDaily-update-check)'


def load_sources():
    js = "global.window={};require(process.argv[1]);console.log(JSON.stringify(window.AIAD.updateSources))"
    out = subprocess.run(['node', '-e', js, os.path.join(REPO, 'config.js')],
                         check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def status(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return str(r.status)
    except urllib.error.HTTPError as e:
        return str(e.code)
    except Exception as e:  # 연결 실패, 시간 초과 등
        return type(e).__name__


def main(names):
    sources = load_sources()
    if names:
        sources = [s for s in sources if s['name'] in names]
    jobs = [(s, kind, u) for s in sources for kind in ('notice', 'dev') for u in s.get(kind, [])]
    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(lambda j: status(j[2]), jobs))
    bad = blocked = 0
    cur = None
    for (s, kind, url), st in zip(jobs, results):
        if s['name'] != cur:
            cur = s['name']
            print(f"\n{s['category']} › {s['name']}" + (f" ({s['maker']})" if s.get('maker') else ''))
        ok = st.startswith('2')
        mark = 'OK ' if ok else '-- ' if st == '403' else '!! '
        blocked += st == '403'
        bad += not ok and st != '403'
        print(f"  {mark} {st:>5}  {kind:<6} {url}")
    no_dev = [s['name'] for s in sources if not s.get('dev')]
    print(f"\n{len(jobs)}개 주소 중 실패 {bad}개 · 자동 접속 막힘(403) {blocked}개 · 개발자 변경 기록 없음: {', '.join(no_dev) or '-'}")
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
