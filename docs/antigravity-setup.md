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
3. **루틴 전용 클론 — Antigravity scratch 폴더에** — Automation은 프로젝트가 아니라 Antigravity 전용 작업 공간
   `C:\Users\<사용자>\.gemini\antigravity\scratch`에서 돕니다. 그 밖의 폴더(예: `D:\GitRepos\...`)는 승인 없이
   접근하지 못해, 저장소도 이 안에 둡니다. 매일 `git reset --hard`로 main에 맞추므로 평소 작업 폴더로 쓰지 마세요.
   ```powershell
   cd $HOME\.gemini\antigravity\scratch
   git clone https://github.com/kyoungwhankim/Daily_Art_AI_News_Feed.git
   ```
4. **GitHub 로그인 확인** — 아래가 비밀번호 창 없이 성공해야 합니다. 처음엔 Git Credential Manager 창이 뜨면 브라우저로 로그인하세요. 토큰을 프롬프트에 넣을 필요는 없습니다.
   ```powershell
   cd $HOME\.gemini\antigravity\scratch\Daily_Art_AI_News_Feed
   git push --dry-run origin main
   git config --local --list
   ```
   마지막 줄 결과에 `user.name=Claude Daily Routine`이 있으면 `git config --unset user.name`, `git config --unset user.email`로 지우세요 (커밋이 내 계정으로 찍히게).
5. **환경 점검** — "Environment OK."가 나와야 합니다.
   ```powershell
   python scripts/routine_steps.py env-check
   ```
6. **자동 승인** — 아무도 보지 않는 실행이라, 터미널 명령·파일 쓰기·웹 접근을 매번 승인하라고 하면 거기서 멈춥니다. Automation을 만들 때 Review permissions 화면과 Antigravity 설정의 실행 정책을 자동 진행으로 맞춰 주세요. 이 루틴은 저장소 폴더와 작업 파일 폴더 `C:\tmp`(feed·updates·free·report — 매일 비우고 새로 쓰는 임시 파일) 아래만 씁니다.
7. **수동 시험은 같은 폴더에서** — Automation 전에 일반 대화로 시험할 때도 Prompt의 경로(scratch 폴더)를 그대로 씁니다. 다른 폴더에서 시험하면 시험 결과가 그 폴더에 남아, Automation과 다른 상태가 됩니다.
8. **매일 오전 9시에 컴퓨터가 켜져 있고 Antigravity가 실행 중**이어야 합니다 (절전 모드 해제).
9. **실행 로그** — 루틴은 모든 스크립트 출력을 `C:\tmp\routine_log\YYYY-MM-DD.txt`에 UTF-8로 남깁니다 (`scripts/run.py`).
   Antigravity 화면의 터미널 출력은 Windows 코드 페이지 때문에 한글이 `?�`로 깨질 수 있지만, 이 파일은 깨지지 않습니다.
   문제가 생기면 이 파일을 보내 주세요. 터미널 화면까지 UTF-8로 보고 싶으면 Windows 설정 → 시간 및 언어 → 언어 및 지역 →
   관리 언어 설정 → 시스템 로캘 변경 → "Beta: 세계 언어 지원을 위해 Unicode UTF-8 사용"을 켜고 재부팅합니다
   (아주 오래된 한국어 프로그램 일부는 글자가 깨질 수 있습니다).

## 2. New Automation 입력값

| 항목 | 값 |
|---|---|
| Name | AI News Daily |
| Trigger | Daily, around 9:00 AM |
| Time Zone | Asia/Seoul |
| Model | Pro |
| Prompt | 아래 3번 |

## 3. Prompt

> ⚠️ **반드시 줄바꿈 없는 한 줄로 붙여 넣으세요.** Windows의 Antigravity Automation은 Prompt를 에이전트에 넘길 때 첫 줄바꿈 이후를 잘라 버립니다. 여러 줄로 쓰면 첫 문장만 전달되어 Step 1(저장소 이동·최신화)이 빠지고, 에이전트가 엉뚱한 폴더나 옛 상태의 저장소로 실행됩니다 (10-28, 10-30에 실제로 발생). 메모장에 먼저 붙여서 한 줄인지 확인한 뒤 옮기면 안전합니다. 명령은 `|`나 `;`로 잇지 않고 (1)~(7) 번호로 나눴습니다 — PowerShell에서 `|`는 파이프로 오해될 수 있습니다.

```text
You run the AI Art Daily daily routine (Korean AI news digest, GitHub repository kyoungwhankim/Daily_Art_AI_News_Feed); this run is unattended, so never stop to ask anything. STEP 1: in PowerShell run these commands one at a time: (1) Set-Location C:\Users\<사용자>\.gemini\antigravity\scratch\Daily_Art_AI_News_Feed (2) git rebase --abort (an error here is fine) (3) git fetch origin main (4) git checkout -f main (5) git reset --hard origin/main (6) git log --oneline -1 (7) git log --oneline -1 origin/main. Lines (6) and (7) must show the same commit, otherwise stop and report. Use ONLY this folder: never search for or use another copy of the repository on this computer. STEP 2: read routine/antigravity_prompt.txt in that folder in full and follow it exactly from SETUP to FINISH. STEP 3: if your context is ever summarized, re-read routine/antigravity_prompt.txt and continue from the step you were on; never start over.
```

`<사용자>`는 Windows 사용자 폴더 이름으로 바꿉니다 (PowerShell에서 `$HOME`이 가리키는 폴더). 바꾼 뒤 Run Now로 돌려, 맨 처음 실행되는 명령이 이 `Set-Location`이고 환경 점검의 `repo :` 줄이 scratch 경로인지 확인하세요.

## 4. 처음 돌릴 때

- **Run Now로 지켜보기** — 승인 창에서 멈추지 않는지, 기사 품질이 괜찮은지 확인하세요.
- **푸시 없이 시험하려면** — 3번 프롬프트 끝에 이 줄을 붙여서 Run Now 하세요. 시험이 끝나면 `git reset --hard origin/main`으로 지워집니다.
  `TEST RUN: do not run push-local or any git commit / push. Instead run "git status --short" and stop after FINISH.`
- **Claude 루틴과 동시에 돌리지 않기** — 둘 다 돌면 같은 소식이 다른 매체 기사로 두 번 올라갈 수 있습니다. 옮기기로 하면 Claude 루틴을 끄세요.
- **확인되지 않은 점** — Antigravity가 대화를 언제 요약하는지, 컴퓨터가 꺼져 있던 날 실행을 건너뛰는지 따라잡는지는 공식 문서에 없습니다. Gemini Pro가 긴 지침을 끝까지 지키는지도 첫 실행으로 확인해야 합니다. 마지막 보고에 "규칙이 안 맞았던 단계"를 적게 해 두었으니, 그 줄을 보고 지침을 고치면 됩니다.
