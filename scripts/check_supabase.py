#!/usr/bin/env python3
"""Supabase(로그인 · 나만의 피드)가 살아 있는지 확인하고, 무료 플랜 일시정지를 막는다.

    python3 scripts/check_supabase.py

config.js의 auth(공개 주소와 publishable 키)만 쓴다 — 비밀키는 필요 없다.
1. keep_alive() 함수를 불러 데이터베이스에 활동을 남긴다 (7일 무활동 일시정지 방지)
2. 로그인 서버 상태와 Google 로그인이 켜져 있는지 확인한다
3. 배포된 사이트의 config.js에 Supabase 주소와 키가 들어 있는지 확인한다
하나라도 실패하면 종료 코드 1로 끝난다.
"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = os.environ.get('SITE_URL', 'https://ai-art-news.pages.dev').rstrip('/')
UA = 'Mozilla/5.0 (compatible; AIArtDaily-supabase-check)'


def load_auth():
    js = "global.window={};require(process.argv[1]);console.log(JSON.stringify(window.AIAD.auth||{}))"
    out = subprocess.run(['node', '-e', js, os.path.join(REPO, 'config.js')],
                         check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def request(url, key=None, body=None):
    headers = {'User-Agent': UA}
    if key:
        headers.update({'apikey': key, 'Authorization': f'Bearer {key}'})
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace')
    except Exception as e:  # 연결 실패, 시간 초과 등
        return 0, str(e)


def main():
    auth = load_auth()
    url, key = (auth.get('supabaseUrl') or '').rstrip('/'), auth.get('supabaseAnonKey') or ''
    if not url or not key:
        print('FAIL config.js auth에 supabaseUrl/supabaseAnonKey가 없다')
        return 1

    checks = []

    code, body = request(f'{url}/rest/v1/rpc/keep_alive', key, {})
    checks.append(('데이터베이스 깨우기 (keep_alive)', code == 200 and body.strip() == '1',
                   f'{code} {body[:200]}'))

    code, body = request(f'{url}/auth/v1/health', key)
    checks.append(('로그인 서버 상태', code == 200, f'{code} {body[:200]}'))

    code, body = request(f'{url}/auth/v1/settings', key)
    try:
        google = bool(json.loads(body).get('external', {}).get('google'))
    except ValueError:
        google = False
    checks.append(('Google 로그인 켜짐', code == 200 and google, f'{code} google={google}'))

    code, body = request(f'{SITE_URL}/config.js')
    checks.append(('배포된 config.js에 Supabase 설정', code == 200 and url in body and key in body,
                   f'{code} {SITE_URL}/config.js'))

    failed = 0
    for name, ok, detail in checks:
        print(f"{'OK  ' if ok else 'FAIL'} {name} — {detail}")
        failed += not ok
    if failed:
        print('\n일시정지됐다면: Supabase 대시보드에서 프로젝트를 열고 Restore project를 누른다.'
              '\n자세한 내용: docs/login-operations.md 8장 "문제가 생겼을 때"')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
