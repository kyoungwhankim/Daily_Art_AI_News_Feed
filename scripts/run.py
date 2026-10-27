#!/usr/bin/env python3
"""run.py — 루틴 스크립트를 실행하고 출력을 UTF-8 로그 파일에도 남긴다 (Windows·Antigravity용).

    python scripts/run.py scripts/scan_feeds.py
    python scripts/run.py scripts/routine_steps.py article-add --file C:\\tmp\\feed\\input.txt

Windows의 백그라운드 PowerShell은 파이썬의 UTF-8 출력을 옛 코드 페이지로 읽어 한국어·일본어가 '?�'로
깨진 채 화면과 로그에 남는다. 이 래퍼는 스크립트(와 그 스크립트가 부르는 다른 스크립트)의 출력을
그대로 받아, 날짜별 로그 파일 /tmp/routine_log/YYYY-MM-DD.txt (Windows에서는 C:\\tmp\\routine_log)에
UTF-8로 덧붙인다. 화면에 보이는 글자가 깨져도 로그 파일은 깨지지 않는다. 종료 코드는 스크립트 것을 그대로 돌려준다.
"""
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

LOG_DIR = '/tmp/routine_log'
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    now = datetime.now(timezone(timedelta(hours=9)))
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, now.strftime('%Y-%m-%d') + '.txt')
    env = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
    cmd = [sys.executable] + sys.argv[1:]
    proc = subprocess.run(cmd, cwd=REPO, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = proc.stdout.decode('utf-8', errors='replace')
    with open(log_path, 'a', encoding='utf-8', newline='\n') as f:
        f.write(f"\n===== {now:%H:%M:%S} $ python {' '.join(sys.argv[1:])}  (exit {proc.returncode})\n")
        f.write(text)
    out = sys.stdout
    if hasattr(out, 'reconfigure'):
        out.reconfigure(encoding='utf-8', errors='replace')
    out.write(text)
    out.flush()
    sys.exit(proc.returncode)


if __name__ == '__main__':
    main()
