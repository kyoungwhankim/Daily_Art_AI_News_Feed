# Antigravity Automation으로 매일 루틴 돌리기 (Windows)

Claude 루틴과 같은 구조입니다. Automation에는 짧은 실행 프롬프트만 넣고, 실제 작업 지침은 repo에 둡니다.

| | 설정 화면에 넣는 프롬프트 | repo의 작업 지침 |
|---|---|---|
| Claude 루틴 | `routine/trigger_prompt.txt` 내용 | `routine/daily_feed_prompt.txt` (+ 에이전트 지침 3개) |
| Antigravity Automation | 아래 3번 | `routine/antigravity_prompt.txt` → 위 지침을 Windows 방식으로 따라 함 |

`antigravity_prompt.txt`는 기사 수집 규칙을 따로 들고 있지 않고, `daily_feed_prompt.txt`를 읽게 합니다. 그래서 출처·검사 규칙을 고치면 두 환경에 함께 적용됩니다. Windows에서 다르게 해야 하는 점(PowerShell 명령, 하위 에이전트 없이 순서대로 처리, 로컬 GitHub 로그인으로 푸시)만 이 파일에 있습니다.

## 1. 컴퓨터 준비 (한 번만)

1. **프로그램 설치**
   - Git for Windows — https://git-scm.com/download/win
   - Python 3.10 이상 — https://www.python.org/downloads/ (설치 화면에서 "Add python.exe to PATH" 체크)
   - Node.js LTS — https://nodejs.org/ (서비스 목록 `config.js`를 읽는 데 씀)
   - curl은 Windows 10/11에 기본으로 있습니다.
2. **UTF-8 모드 켜기** — 한국어가 깨지지 않게. PowerShell에서 한 번 실행하고 Antigravity를 다시 시작:
   ```powershell
   setx PYTHONUTF8 1
   ```
3. **루틴 전용 클론** — 매일 `git reset --hard`로 main에 맞추므로 평소 작업 폴더와 따로 둡니다.
   ```powershell
   cd $HOME
   git clone https://github.com/kyoungwhankim/Daily_Art_AI_News_Feed.git
   ```
   다른 위치에 두면 3번 프롬프트의 경로도 바꾸세요.
4. **GitHub 로그인 확인** — 아래가 비밀번호 창 없이 성공해야 합니다. 처음엔 Git Credential Manager 창이 뜨면 브라우저로 로그인하세요. 토큰을 프롬프트에 넣을 필요는 없습니다.
   ```powershell
   cd $HOME\Daily_Art_AI_News_Feed
   git push --dry-run origin main
   ```
5. **환경 점검** — "Environment OK."가 나와야 합니다.
   ```powershell
   python scripts/routine_steps.py env-check
   ```
6. **Antigravity에서 이 폴더 열기** — Automation이 이 폴더(워크스페이스)에서 돌게 합니다.
7. **자동 승인** — 아무도 보지 않는 실행이라, 터미널 명령·파일 쓰기·웹 접근을 매번 승인하라고 하면 거기서 멈춥니다. Automation을 만들 때 Review permissions 화면과 Antigravity 설정의 실행 정책을 자동 진행으로 맞춰 주세요. 이 루틴은 저장소 폴더와 `C:\tmp` 아래만 씁니다.
8. **매일 오전 9시에 컴퓨터가 켜져 있고 Antigravity가 실행 중**이어야 합니다 (절전 모드 해제).

## 2. New Automation 입력값

| 항목 | 값 |
|---|---|
| Name | AI News Daily |
| Trigger | Daily, around 9:00 AM |
| Time Zone | Asia/Seoul |
| Model | Pro |
| Prompt | 아래 3번 |

## 3. Prompt

```text
You run the AI Art Daily daily routine (Korean AI news digest, GitHub repository kyoungwhankim/Daily_Art_AI_News_Feed). The full instructions live in the repository. This run is unattended: never stop to ask anything.

Step 1 — In the PowerShell terminal, go to the repository and reset it to the latest main (one command per line):

Set-Location $HOME\Daily_Art_AI_News_Feed
git fetch origin main
git checkout main
git reset --hard origin/main

If the folder does not exist, stop and report that the repository is missing.

Step 2 — Read routine/antigravity_prompt.txt in full and follow it exactly, from SETUP to FINISH. It tells you how to run the main instructions (routine/daily_feed_prompt.txt) on this Windows computer.

Step 3 — If your context is ever summarized, re-read routine/antigravity_prompt.txt and continue from the step you were on (the work files show your progress). Never start over.
```

## 4. 처음 돌릴 때

- **Run Now로 지켜보기** — 승인 창에서 멈추지 않는지, 기사 품질이 괜찮은지 확인하세요.
- **푸시 없이 시험하려면** — 3번 프롬프트 끝에 이 줄을 붙여서 Run Now 하세요. 시험이 끝나면 `git reset --hard origin/main`으로 지워집니다.
  `TEST RUN: do not run push-local or any git commit / push. Instead run "git status --short" and stop after FINISH.`
- **Claude 루틴과 동시에 돌리지 않기** — 둘 다 돌면 같은 소식이 다른 매체 기사로 두 번 올라갈 수 있습니다. 옮기기로 하면 Claude 루틴을 끄세요.
- **확인되지 않은 점** — Antigravity가 대화를 언제 요약하는지, 컴퓨터가 꺼져 있던 날 실행을 건너뛰는지 따라잡는지는 공식 문서에 없습니다. Gemini Pro가 긴 지침을 끝까지 지키는지도 첫 실행으로 확인해야 합니다. 마지막 보고에 "규칙이 안 맞았던 단계"를 적게 해 두었으니, 그 줄을 보고 지침을 고치면 됩니다.
