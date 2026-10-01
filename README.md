# Art AI News Feed

A daily, curated stream of AI-generated art and AI-in-art news in Korean.

Static site — no backend, no login. Hosted on GitHub Pages. The whole app is React rendered in the browser; updating the site means editing one JavaScript file and pushing.

Daily updates are produced by a Claude Code Routine that runs in the cloud each morning, researches news, writes Korean translations, and pushes the change to `main` automatically.

---

## 개요

Claude Routine을 사용해서 아트 전용 데일리 뉴스 피드를 만든다.

- Claude Routine: [claude.ai/code/routines](https://claude.ai/code/routines)
- 루틴 프롬프트 전문: [`routine/daily_feed_prompt.txt`](routine/daily_feed_prompt.txt)
  (루틴 설정 화면의 프롬프트와 이 파일을 항상 같은 내용으로 유지한다)

## 규칙

### 스케줄

매일 오전 9시 01분(KST) 실행. 피드 게시 완료까지 30분 안팎 소요.

### 내용

#### 3가지 섹션으로 분류

| 섹션 | 사이트 탭 (`tab`) |
|---|---|
| 게임 제작과 관련된 AI 뉴스 | `games` — 게임 제작 속 AI |
| 글로벌 스튜디오의 AI 도입 뉴스 | `industry` — AI 도입 뉴스 |
| 아트 전반 AI 뉴스 | `art` — 아트 전반 AI 뉴스 |

#### 뉴스 출처는 Whitelist 출처를 우선으로 탐색하되 새로운 뉴스가 없으면 검색 범위를 확장

- KST 기준 오늘 또는 어제 뉴스만 탐색. 섹션별 최대 5개. 뉴스가 없다면 억지로 게재할 필요 없음.
- 탐색 순서: 공통 + 섹션별 Primary → (없으면) 섹션별 Broadened → (그래도 없으면) 오픈 웹 검색
- 콘텐츠 팜, SEO 애그리게이터, 광고 위주 재게시 사이트는 제외.

### Whitelist

출처 목록은 루틴 프롬프트 안의 `WHITELIST_ARTICLES` 블록에 들어 있다
([`routine/daily_feed_prompt.txt`](routine/daily_feed_prompt.txt) PHASE 1 → Step 2).
출처를 바꾸려면 루틴 프롬프트의 이 블록을 수정하고, 이 레포의 사본도 같이 갱신한다.

- `[공통]` — 모든 섹션에 적용
- `[게임 제작]`, `[글로벌 스튜디오 AI 도입]`, `[아트 전반]` — 각각 `- Primary:` / `- Broadened:` 목록

## 클라우드 환경

### 네트워크 엑세스

전체 (인터넷을 자유롭게 검색하기 위함)

### 환경 변수

- `GITHUB_TOKEN=(개인용 엑세스 토큰(PAT))` — 레포 clone 및 `main` push용
  - 토큰 생성: [Fine-grained Personal Access Tokens](https://github.com/settings/personal-access-tokens)
  - 환경을 공유하면 PAT도 공유되는 문제가 발생. 환경은 개인만 사용하고 절대 공유 금지.
  - 이 작업을 위한 별도 토큰 생성. 토큰 분리.

## 루틴 구조

단일 루틴이 한 세션 안에서 다음 단계를 순서대로 수행한다.

### PHASE 1 — 조사 (RESEARCH)

1. **SETUP** — `/tmp/feed/` 초기화, 프롬프트에 내장된 Whitelist를 파싱해 `/tmp/feed/whitelist.json`으로 저장
2. **SECTION 1, 2, 3 — 뉴스 수집** — Whitelist 기반 검색, 각 기사를 curl로 페치해 og:image + 링크 + 본문 추출, JSON 객체로 `/tmp/feed/digest.json`에 누적 저장
3. **VERIFY DIGEST** — 섹션별 수집 건수 확인

### PHASE 2 — 게시 (PUBLISH)

1. **Step 0** — `/tmp/feed/PUBLISH_PHASE` 표시 파일 생성 (이후 컨텍스트 압축 차단, 아래 참고)
2. **SETUP** — 레포를 `/home/user/Daily_Art_AI_News_Feed`에 준비하고 `origin/main`으로 맞춤
3. **STEP 1~2** — `digest.json`을 읽어 섹션 → 탭(`games`/`industry`/`art`)으로 매핑. digest에 있는 기사만, 순서대로 처리 (웹 검색 금지)
4. **STEP 3** — 기사마다 `scripts/fetch_article.py`를 정확히 한 번 실행 (실패 시 WebFetch 1회)
5. **STEP 4** — 필드 매핑 후 `/tmp/feed/articles.json`에 저장 (본문 600–800자, 이미지 4단계 대체 등)
6. **UPDATE articles.js** — `scripts/update_articles_js.py`로 URL 중복 제거 후 탭별 위치에 삽입, 문법 검사
7. **COMMIT AND PUSH** — `scripts/push_to_main.py`로 `main`에 직접 push (새 브랜치·PR 금지)
8. **FINISH** — `PUBLISH_PHASE` 표시 파일 삭제

PHASE 2에서는 하위 에이전트(Task tool)를 쓰지 않는다. 기사마다 fetch 결과가 같은 세션에 보여야 하는 PRE-FLIGHT CHECK 때문이다.

### 컨텍스트 압축 규칙

- PHASE 1(조사) 중에는 압축을 허용한다. PHASE 2에 필요한 내용은 모두 `digest.json` 파일에 있으므로 압축돼도 잃지 않는다.
- PHASE 2(게시) 중에는 압축을 허용하지 않는다. 레포의 PreCompact 훅
  ([`.claude/hooks/block-compact-while-publishing.sh`](.claude/hooks/block-compact-while-publishing.sh),
  [`.claude/settings.json`](.claude/settings.json))이 `/tmp/feed/PUBLISH_PHASE`가 있는 동안 자동·수동 압축을 모두 막는다.
- 훅은 세션 시작 시 `main` 브랜치의 설정을 읽으므로, 훅을 바꾸면 `main`에 반영돼야 다음 실행부터 적용된다.

## 운영 노하우

### 타임아웃 방지

- 문제: HTML이나 긴 본문을 한 번에 쓰면 스트림 타임아웃 발생
- 해결: 각 기사를 소형 JSON 객체로 저장 → 마지막에 스크립트가 파일을 일괄 갱신

### 정보 품질 확보

- STEP A: 기사 URL을 curl로 직접 페칭 → og:image + 관련 링크 + 본문 텍스트 3,000자 추출
- STEP B: 추출된 본문(ARTICLE_TEXT)만 기반으로 요약 작성 — 검색 스니펫 기반 요약 금지
- 페이월/짧은 텍스트/무관한 기사는 스킵하고 다른 기사 탐색

### 중복 게시 방지

- "오늘 또는 어제" 규칙 때문에 같은 기사가 이틀 연속 잡힐 수 있다. `update_articles_js.py`가 `articles.js`에 이미 있는 URL은 건너뛴다.

## 아이디어

- 아트실에서 주로 사용하는 AI 제품과 관련된 뉴스들을 타겟해서 업데이트
  - ex. Stable Diffusion, MeshyAI, Nano Banana, etc
- 대부분 영문 뉴스라 긴 버전의 요약본을 함께 게재
  - 단, 가독성을 위해서 긴 버전의 요약본은 클릭해서 열어야 읽을 수 있도록 레이아웃 설정
- 수집되는 뉴스의 퀄리티가 괜찮으면 슬랙 채널 개설
- 데일리로 새로운 뉴스를 찾기 힘들면 위클리도 가능
  - 혹은 위클리로 가장 대중의 관심도가 높았던 뉴스만 별도 정리
