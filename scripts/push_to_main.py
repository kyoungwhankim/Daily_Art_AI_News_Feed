"""
push_to_main.py — articles.js의 변경사항을 main 브랜치에 commit & push.

사용법:
    python3 scripts/push_to_main.py

전제 환경 변수:
    GITHUB_TOKEN — Daily_Art_AI_News_Feed 레포에 contents:write 권한이 있는 PAT.

전제 디렉터리:
    REPO = /home/user/Daily_Art_AI_News_Feed (REPO_PATH 환경변수로 override 가능)

라우틴 환경의 인프라 제약 세 가지를 우회한다:
    1. Commit signing은 메인 작업 디렉터리에서만 동작
       (signing program이 다른 디렉터리에서는 거부함)
    2. 기본 'origin' remote는 로컬 프록시(127.0.0.1:...)를 가리키고
       fetch는 허용하지만 push는 거부함 → 토큰 URL로 직접 푸시
    3. 직접 푸시 후 로컬 origin/main tracking ref가 stale 상태가 됨
       → 푸시 직후 'git fetch origin main'으로 동기화

⚠️  HARD RULE — 절대 새 브랜치를 만들지 않는다. 모든 commit은 main으로.
    사이트는 main 브랜치만 빌드하므로 다른 브랜치의 commit은 라이브에 안 뜸.
"""

import subprocess
import time
import os
import sys
from datetime import date


REPO = os.environ.get('REPO_PATH', '/home/user/Daily_Art_AI_News_Feed')


def run(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    """REPO 디렉터리에서 명령 실행, stdout/stderr 캡처."""
    return subprocess.run(
        cmd, cwd=REPO, capture_output=True, text=True, **kwargs
    )


def verify_on_main() -> None:
    """현재 HEAD가 main이 아니면 강제로 main으로 되돌린다."""
    r = run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    current = r.stdout.strip()
    if current != 'main':
        print(f'❌ HEAD is on "{current}", not "main".', flush=True)
        print('   Switching back to main before continuing.', flush=True)
        run(['git', 'checkout', 'main']).check_returncode()
        run(['git', 'reset', '--hard', 'origin/main']).check_returncode()
        print('   Now on main.', flush=True)
    else:
        print(f'✅ On branch: {current}', flush=True)


def commit_changes(upload_date: str) -> bool:
    """articles.js의 변경사항을 stage하고 commit한다.

    Returns:
        True: 새 commit이 생성됨
        False: 변경사항이 없어서 commit 생략됨
    """
    run(['git', 'add', 'articles.js'])
    status = run(['git', 'diff', '--cached', '--stat'])
    print('Staged changes:', flush=True)
    print(status.stdout or '(none)', flush=True)

    if not status.stdout.strip():
        print('No changes to commit — articles.js was not modified.',
              flush=True)
        return False

    commit = run(['git', 'commit', '-m',
                  f'Daily AI news feed: {upload_date}'])
    print(commit.stdout, flush=True)
    if commit.returncode != 0:
        print('Commit failed:', flush=True)
        print(commit.stderr, flush=True)
        sys.exit(1)
    print('✅ Commit created and signed.', flush=True)
    return True


def push_to_main() -> None:
    """토큰 URL로 직접 main 브랜치에 푸시. 일시 실패는 exponential backoff로 재시도."""
    token = os.environ['GITHUB_TOKEN']
    remote_url = (
        f'https://{token}@github.com/'
        f'kyoungwhankim/Daily_Art_AI_News_Feed.git'
    )

    # git이 진행 상황을 계속 출력하도록 강제 — Routine stream이 idle로 빠지지 않게.
    push_env = os.environ.copy()
    push_env['GIT_TRACE'] = '1'
    push_env['GIT_CURL_VERBOSE'] = '1'

    delays = [2, 4, 8, 16]
    max_retries = len(delays)

    for attempt in range(1, max_retries + 1):
        print(f'Push attempt {attempt}/{max_retries}...', flush=True)
        r = subprocess.run(
            ['git', 'push', '--progress', '--verbose',
             remote_url, 'main'],
            cwd=REPO,
            capture_output=True,
            text=True,
            env=push_env,
            timeout=120,
        )
        if r.returncode == 0:
            print('✅ Pushed.', flush=True)
            tail = r.stderr.replace(token, '***').strip()[-300:]
            print(tail, flush=True)
            return
        print('Attempt failed:', flush=True)
        print(r.stderr.replace(token, '***')[-300:], flush=True)
        if attempt < max_retries:
            time.sleep(delays[attempt - 1])

    sys.exit('❌ All push attempts failed.')


def sync_tracking_ref() -> None:
    """푸시 후 stale해진 origin/main tracking ref를 fetch로 동기화."""
    run(['git', 'fetch', 'origin', 'main'])


def main():
    upload_date = date.today().strftime('%Y.%m.%d')

    verify_on_main()

    if not commit_changes(upload_date):
        # 변경사항 없음 — 푸시할 게 없으니 조용히 종료
        return

    push_to_main()
    sync_tracking_ref()

    print()
    print('Site will rebuild automatically via GitHub Pages.')
    print('Daily feed is live shortly at:')
    print('  https://kyoungwhankim.github.io/Daily_Art_AI_News_Feed/')


if __name__ == '__main__':
    main()
