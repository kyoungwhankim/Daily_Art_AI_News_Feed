#!/usr/bin/env python3
"""run_report_agent.py — 금주 리포트 작성을 위해 Gemini 4 Argon (High) 에이전트 세션을 실행하고 완료를 기다린다.

사용법:
  python3 scripts/run_report_agent.py [YYYY-MM-DD]

동작:
  1. /tmp/report/context.json 이 없으면 `weekly_report.py context` 를 먼저 실행한다.
  2. 로컬 Antigravity Language Server 에 연결해 `Gemini 4 Argon (High)` (MODEL_PLACEHOLDER_M417) 모델로
     새 에이전트 대화를 시작하고 `routine/report_agent_prompt.txt` 지침을 전달한다.
  3. `/tmp/report/DONE` 이 생성되고 9개 직군 리포트가 `/tmp/report/entries.json` 에 저장될 때까지 대기한다.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = '/tmp/report'
KST = timezone(timedelta(hours=9))
ARGON_HIGH_MODEL = 'MODEL_PLACEHOLDER_M417'   # Gemini 4 Argon (High)


def call_ls_rpc(ls_address: str, csrf_token: str, method: str, payload: dict, timeout: int = 30) -> dict:
    url = f'http://{ls_address}/exa.language_server_pb.LanguageServerService/{method}'
    body = json.dumps(payload).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Connect-Protocol-Version': '1',
        'x-codeium-csrf-token': csrf_token,
    }
    req = urllib.request.Request(url, data=body, headers=headers, method='POST')
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode('utf-8')
        return json.loads(raw) if raw else {}


def discover_ls() -> tuple[str, str]:
    """환경변수 또는 실행 중인 Antigravity language_server 프로세스에서 주소와 CSRF 토큰을 찾는다."""
    addr = os.environ.get('ANTIGRAVITY_LS_ADDRESS', '').strip()
    token = os.environ.get('ANTIGRAVITY_CSRF_TOKEN', '').strip()
    if addr and token:
        return addr, token

    if os.name == 'nt':
        ps = (
            "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'language_server*.exe' } | "
            "ForEach-Object { "
            "$p = $_.ProcessId; $c = $_.CommandLine; "
            "$ports = (Get-NetTCPConnection -OwningProcess $p -State Listen -ErrorAction SilentlyContinue).LocalPort; "
            "Write-Output \"$p|$c|$($ports -join ',')\" }"
        )
        r = subprocess.run(['powershell', '-NoProfile', '-Command', ps], capture_output=True, text=True)
        for line in r.stdout.splitlines():
            parts = line.strip().split('|')
            if len(parts) < 3:
                continue
            cmd, ports_str = parts[1], parts[2]
            m = re.search(r'--csrf_token[=\s]+([0-9a-fA-F-]+)', cmd)
            if not m or not ports_str:
                continue
            cand_token = m.group(1)
            for port in ports_str.split(','):
                port = port.strip()
                if not port.isdigit():
                    continue
                cand_addr = f'127.0.0.1:{port}'
                try:
                    call_ls_rpc(cand_addr, cand_token, 'GetUserStatus', {}, timeout=3)
                    return cand_addr, cand_token
                except Exception:
                    continue
    raise RuntimeError('Could not connect to Antigravity Language Server (set ANTIGRAVITY_LS_ADDRESS / ANTIGRAVITY_CSRF_TOKEN)')


def load_entries_count() -> int:
    try:
        with open(os.path.join(WORK, 'entries.json'), encoding='utf-8') as f:
            return len(json.load(f))
    except Exception:
        return 0


def main():
    date_arg = None
    for a in sys.argv[1:]:
        if re.match(r'^\d{4}-\d{2}-\d{2}$', a):
            date_arg = a

    ctx_path = os.path.join(WORK, 'context.json')
    if not os.path.exists(ctx_path):
        cmd = [sys.executable, os.path.join(REPO, 'scripts', 'weekly_report.py'), 'context']
        if date_arg:
            cmd.append(date_arg)
        subprocess.run(cmd, cwd=REPO, check=True)

    with open(ctx_path, encoding='utf-8') as f:
        ctx = json.load(f)
    report_date = ctx.get('date') or date_arg or datetime.now(KST).strftime('%Y-%m-%d')
    expected_roles = len(ctx.get('roles') or []) or 9

    done_path = os.path.join(WORK, 'DONE')
    try:
        os.remove(done_path)
    except FileNotFoundError:
        pass

    ls_address, csrf_token = discover_ls()
    prompt_path = os.path.join(REPO, 'routine', 'report_agent_prompt.txt').replace('\\', '/')
    repo_norm = REPO.replace('\\', '/')
    work_norm = os.path.abspath(WORK).replace('\\', '/')

    prompt = (
        f"Today is {report_date} (weekly report date). "
        f"Repository path (`REPO_DIR`): `{repo_norm}`. "
        f"Work directory (`/tmp/report`): `{work_norm}`. "
        f"Read `{prompt_path}` and `{repo_norm}/routine/antigravity_prompt.txt` (W1–W5 rules for Windows PowerShell), "
        f"then follow `{prompt_path}` from STEP 1 to FINISH to write all 9 role reports (5-minute continuous prose commentary, "
        f"2,000–3,000 chars each, at most 2 core points / 1–4 refs) and refine Sections 2 & 3 of each `routine/role_knowledge/<role>.md`. "
        f"Note: `/tmp/report/context.md` is already generated at `{work_norm}/context.md`, so after `agent-init report` you can read `{work_norm}/context.md` directly."
    )

    start_req = {
        'source': 'CORTEX_TRAJECTORY_SOURCE_AGENT_API',
        'trajectoryType': 'CORTEX_TRAJECTORY_TYPE_CASCADE',
        'customAgentSpec': {
            'codingAgent': {'googleMode': True},
            'commandExecutionPolicy': 'eager',
            'enforcedWorkspaceValidation': False,
            'cascadeConfig': {
                'plannerConfig': {
                    'planModel': ARGON_HIGH_MODEL,
                }
            },
        },
    }
    start_resp = call_ls_rpc(ls_address, csrf_token, 'StartCascade', start_req)
    cascade_id = start_resp.get('cascadeId', '')
    if not cascade_id:
        sys.exit(f'Failed to start Gemini 4 Argon (High) report agent: {start_resp}')

    call_ls_rpc(ls_address, csrf_token, 'UpdateConversationAnnotations', {
        'cascadeId': cascade_id,
        'title': f'Weekly Report ({report_date}) — Gemini 4 Argon (High)',
        'titleGenerationMethod': 'TITLE_GENERATION_METHOD_AGENT_API',
    })
    call_ls_rpc(ls_address, csrf_token, 'SendUserCascadeMessage', {
        'cascadeId': cascade_id,
        'items': [{'text': prompt}],
    })
    print(f'Started Gemini 4 Argon (High) report agent: conversationId={cascade_id} for {report_date}', flush=True)

    t0 = time.time()
    last_count = -1
    nudges = 0
    while time.time() - t0 < 2700:   # 최대 45분 대기
        time.sleep(10)
        cnt = load_entries_count()
        if cnt != last_count:
            print(f'  [{int(time.time() - t0)}s] saved reports: {cnt}/{expected_roles}', flush=True)
            last_count = cnt
        if os.path.exists(done_path) and cnt >= expected_roles:
            print(f'Report agent finished ({cnt}/{expected_roles} reports).', flush=True)
            rp = os.path.join(WORK, 'REPORT.txt')
            if os.path.exists(rp):
                print(open(rp, encoding='utf-8').read().rstrip(), flush=True)
            sys.exit(0)
        try:
            traj = call_ls_rpc(ls_address, csrf_token, 'GetCascadeTrajectory', {'cascadeId': cascade_id})
            status = traj.get('status', '')
            if status in ('CASCADE_RUN_STATUS_IDLE', 'CASCADE_RUN_STATUS_COMPLETED', 'CASCADE_RUN_STATUS_DONE'):
                if os.path.exists(done_path) and cnt >= expected_roles:
                    sys.exit(0)
                if cnt >= expected_roles and not os.path.exists(done_path):
                    subprocess.run([sys.executable, os.path.join(REPO, 'scripts', 'routine_steps.py'),
                                    'agent-finish', 'report'], cwd=REPO, check=True)
                    sys.exit(0)
                if nudges < 3:
                    nudges += 1
                    print(f'  Agent idle at {cnt}/{expected_roles} reports; sending continuation nudge ({nudges}/3)...', flush=True)
                    call_ls_rpc(ls_address, csrf_token, 'SendUserCascadeMessage', {
                        'cascadeId': cascade_id,
                        'items': [{'text': f'Continue writing the remaining role reports ({cnt}/{expected_roles} saved so far) and finish with `python scripts/run.py scripts/routine_steps.py agent-finish report`.'}],
                    })
                else:
                    sys.exit(f'Report agent stopped early after {nudges} nudges ({cnt}/{expected_roles} reports saved).')
        except Exception:
            pass

    sys.exit(f'Timed out waiting for report agent ({load_entries_count()}/{expected_roles} reports saved).')


if __name__ == '__main__':
    main()
