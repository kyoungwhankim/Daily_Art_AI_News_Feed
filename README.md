# Art AI News Feed

A daily, curated stream of AI-generated art and AI-in-art news in Korean.

Static site — no backend, no login. Hosted on Cloudflare Pages (https://ai-art-news.pages.dev), deployed by GitHub Actions. Updating the site means adding a date file under `data/articles/` and pushing; the Action builds the site (feed app + per-article pages for search engines) and deploys it.

Daily updates are produced by a Claude Code Routine that runs in the cloud each morning, researches news, writes Korean translations, and pushes the change to `main` automatically.

---

## 파일 구조

| 경로 | 내용 |
|---|---|
| `index.html`, `app.jsx`, `app.css` | 사이트 (React, 브라우저에서 Babel로 실행) |
| `config.js` | 탭 정의 (`window.AIAD.tabs`) |
| `data/index.json` | 날짜 파일 목록 (최신순) — `date`, `file`, `count`, `rev`(내용 해시) |
| `data/articles/YYYY-MM-DD.json` | 그날 게시된 기사 배열 (기사 형식은 `config.js` 주석 참고) |
| `scripts/update_articles.py` | 루틴이 새 기사를 오늘 날짜 파일에 추가하고 `index.json`을 다시 만든다 |
| `scripts/validate_data.py` | `data/` 검사 (JSON 형식, index 일치, 필수 필드, id 중복) |
| `scripts/feed_data.py` | 위 두 스크립트의 공통 함수 |
| `data/keywords.json` | 탭별 서브 카테고리 키워드 목록 (아래 참고) |
| `scripts/add_keyword.py` | 탭 목록에 키워드를 추가하고 지난 기사에도 붙인다 (루틴이 필요할 때 사용) |
| `scripts/tag_keywords.py`, `scripts/keyword_rules.json` | 지난 기사에 키워드를 일괄로 붙이는 관리 도구 / 키워드별 검색 규칙 |
| `scripts/fetch_article.py`, `scripts/push_to_main.py` | 루틴용 기사 가져오기 / main push |
| `routine/daily_feed_prompt.txt` | 루틴 프롬프트 전문 |
| `routine/updates_agent_prompt.txt` | 루틴이 따로 띄우는 업데이트 수집 에이전트의 프롬프트 (아래 '서비스 업데이트') |
| `data/updates/services/<서비스>/YYYY-MM-DD.json` | 서비스가 그날 발표한 공식 업데이트 배열 (서비스별·발표 날짜별 원본) |
| `data/updates/feed/<분야>.json`, `data/updates/index.json` | 사이트가 읽는 분야별 업데이트 목록과 색인 — `service_updates.py`가 자동 생성 |
| `scripts/service_updates.py` | 업데이트 데이터 저장·합치기·검사 (`save`, `merge`, `state`, `rebuild`, `validate`) |
| `scripts/read_source.py` | 업데이트 출처(RSS·변경 기록 페이지) 하나를 읽어 텍스트로 보여 줌 |
| `scripts/check_update_sources.py` | `config.js`의 업데이트 출처 주소가 열리는지 확인 |
| `scripts/build_site.py`, `static.css` | 배포용 정적 사이트 생성 (기사별 페이지, 목록, 사이트맵, RSS) — GitHub Actions가 실행 |
| `.github/workflows/deploy.yml` | main push 시 사이트를 만들어 Cloudflare Pages에 배포 (예전 GitHub Pages 주소는 안내 페이지) |

피드 앱은 `data/index.json`을 받은 뒤 날짜 파일들을 병렬로 불러온다. 날짜 파일은 `?v=<rev>`로 요청하므로 내용이 바뀐 날짜만 브라우저 캐시가 갱신된다.
`fetch`를 쓰므로 `file://`로 직접 열면 동작하지 않는다 — 로컬에서는 `python3 -m http.server`로 띄워서 확인한다.

## 배포 (GitHub Actions → Cloudflare Pages)

사이트 주소: **https://ai-art-news.pages.dev** (Cloudflare Pages 프로젝트 `ai-art-news`)

main에 push되면 `.github/workflows/deploy.yml`이 실행된다: `validate_data.py` → `build_site.py` → Cloudflare Pages 배포. 만든 파일(`_site/`)은 레포에 커밋하지 않는다. PR에서는 빌드만 확인한다.

- `claude/**` 브랜치에 push하면 같은 빌드를 **미리보기 주소 https://preview.ai-art-news.pages.dev** 에만 배포한다 (모든 페이지 noindex, robots.txt 전체 차단, 실제 사이트·예전 주소는 건드리지 않음).
- 필요한 레포 Secrets: `CLOUDFLARE_API_TOKEN`(권한: Account / Cloudflare Pages / Edit), `CLOUDFLARE_ACCOUNT_ID`
- 예전 주소(`kyoungwhankim.github.io/Daily_Art_AI_News_Feed/`)는 GitHub Pages(Source: GitHub Actions)에 안내 페이지만 배포한다 — 어떤 경로로 들어와도 같은 경로의 새 주소로 넘겨 준다 (`build_site.py --redirect-site`).
- 배포 사이트에서 만들어지는 것:
  - `index.html` — 피드 앱. 설명·OG 메타 정보와 최신 기사 30건 목록을 HTML에 미리 넣고, `app.jsx`는 esbuild로 미리 변환한 `app.js` + React production 빌드를 쓴다 (브라우저 Babel 없음)
  - `articles/<id>/` — 기사별 페이지. 피드 앱과 같은 페이지라 방문자에게는 그 기사의 탭 카드 화면 위에 기사 창이 열리고, 검색엔진·링크 미리보기용 본문·OG·NewsArticle 구조화 데이터는 HTML에 들어 있다. 앱에서 기사 창을 열면 주소가 이 경로가 되고, "링크 복사"도 이 주소를 복사한다 (예전 `?article=<id>` 링크는 이 주소로 바뀐다)
  - `topics/<tab>/`, `topics/<tab>/<키워드>/` — 탭별·서브 카테고리별 페이지 (6개 이상 키워드만). 피드 앱과 같은 페이지라 방문자에게는 그 탭·서브 카테고리가 선택된 카드 화면이 열리고, 검색엔진용 기사 목록은 HTML에 들어 있다. 앱에서 탭·서브 카테고리를 바꾸면 주소도 이 경로로 바뀐다
  - `sitemap.xml`, `feed.xml`(RSS, 최신 50건), `robots.txt`, `404.html`
  - PWA: `manifest.webmanifest`, `sw.js`(레포의 `sw.js`에 캐시 목록·버전을 채워 냄), `icons/` — 휴대폰 홈 화면에 앱처럼 설치하고, 한 번 연 화면과 기사 데이터는 오프라인에서도 열린다. 안드로이드·데스크톱 크롬에서는 헤더에 "앱 설치" 버튼이 뜨고, 아이폰·아이패드 사파리에는 "공유 → 홈 화면에 추가" 안내가 한 번 뜬다. 아이콘 원본은 `icons/icon.svg`
- 레포의 `index.html`은 브라우저 Babel 방식 그대로라 `python3 -m http.server`로 바로 미리 볼 수 있다. 배포본을 확인하려면 `python3 scripts/build_site.py` 후 `_site/`를 띄운다 (`npx`로 esbuild를 받으므로 Node가 필요, `--no-bundle`이면 불필요).
- 사이트 주소는 `build_site.py`의 `SITE_URL` (워크플로의 `SITE_URL` 환경 변수로도 지정).
- 검색 등록: 구글 Search Console, 네이버 서치어드바이저에 `https://ai-art-news.pages.dev` 등록 후 `sitemap.xml`(네이버는 `feed.xml` RSS도) 제출.

## 서브 카테고리 (키워드)

메뉴에서 메인 탭을 누르면 바로 아래 줄에 서브 카테고리(키워드) 칩이 나오고, 칩을 누르면 그 키워드가 붙은 기사만 보인다. `전체`는 탭의 모든 기사.

- **키워드 목록:** [`data/keywords.json`](data/keywords.json)에 탭별로 들어 있다 (표시 순서 = 목록 순서).
  - 처음 목록(2026.10.02): 게임 제작 속 AI 22개, AI 도입 뉴스 18개, 아트 전반 AI 뉴스 27개
  - 종류: 제작 대상(3D, 애니메이션 …), 주제(AI 도입 뉴스 전용: AI 사용 논란, 고용·노조 …), 회사, 프로그램·서비스
- 사이트는 탭 안에서 **6개 이상** 기사에 붙은 키워드만 칩으로 보여준다 (5개 이하는 지엽적이라 숨김 — 기사가 쌓이면 자동으로 나타남).
- 모든 기사에 `keywords` 배열이 있다 (해당 없음이면 `[]` — `전체`에서만 보인다).
- **매일 루틴:**
  - PHASE 2 SETUP Step 3에서 레포의 목록을 읽어 출력하고, STEP 4에서 기사마다 그 탭의 목록 안에서 키워드를 고른다.
  - 목록에 없는 회사·프로그램·서비스·제작 대상(AI 도입 뉴스는 주제 포함)이 기사의 주된 대상이고 앞으로도 반복될 일반적인 대상이면 `scripts/add_keyword.py`로 추가한다. 한 번 실행에 최대 2개, 기존 키워드의 변형(PlayStation → Sony 등)은 추가하지 않는다.
  - `add_keyword.py`는 목록에 추가하고, 같은 탭의 지난 기사 중 제목·요약에 그 이름이 있는 기사에도 붙이며, 규칙을 `scripts/keyword_rules.json`에 남긴다.
  - 저장 스크립트가 목록에 없는 값을 `REJECTED`로 막고, `update_articles.py`는 목록에 없는 값을 버리며, `validate_data.py`가 최종 확인한다.
- **수동 관리:** 키워드를 직접 추가할 때도 `add_keyword.py`를 쓴다. 이미 있는 키워드를 지난 기사에 더 붙이려면 `python3 scripts/tag_keywords.py <키워드> [--tab TAB]`로 미리 보고 `--apply`로 반영.
- 처음 태깅: 제작 대상·회사·프로그램은 규칙 기반, AI 도입 뉴스의 주제 키워드는 기사 제목·요약을 읽고 직접 붙였다.

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

## 서비스 업데이트 (사이드바 '업데이트')

아트 관련 AI 서비스의 **공식** 업데이트(공지·변경 기록·개발자 변경 기록)를 분야 › 서비스별로 모은다.

- **수집 대상**: `config.js`의 `updateSources` — 서비스마다 `notice`(공지 출처), `dev`(개발자 변경 기록), `match`(회사의 여러 제품이 섞인 출처에서 이 제품 글로 볼 단어).
  모으는 분야는 `routine/updates_agent_prompt.txt` 맨 위의 `CATEGORIES` (지금은 `이미지`). 분야를 늘리려면 거기에 분야 이름을 더한다.
- **수집 방식**: 뉴스 루틴이 PHASE 0에서 업데이트 에이전트를 백그라운드로 띄운다. 에이전트는 서비스마다
  - 저장된 항목이 없으면 **BACKFILL** — 서비스 시작부터 오늘까지 전체 기록
  - 있으면 **INCREMENTAL** — 마지막 날짜 이후 새 항목

  을 한국어로 정리해 `/tmp/updates/entries.json`에 저장한다(`service_updates.py save`가 항목마다 검사). 뉴스 PHASE 2가 `service_updates.py merge`로 `data/updates/`에 합치고 뉴스와 함께 push한다.
- **파일**: 원본은 `data/updates/services/<서비스>/<발표 날짜>.json`. 같은 서비스·같은 날짜·같은 url은 한 항목(중복 기준)이다. `feed/`·`index.json`은 생성 파일이라 직접 고치지 않는다 — 원본을 고쳤다면 `python3 scripts/service_updates.py rebuild`.
- **항목 형식**: `service`, `date`(발표 날짜 `YYYY.MM.DD`), `kind`(모델·기능·API·앱·연동·요금·정책·종료), `title`, `summary`, `details`(선택), `url`, `source`(`notice`/`dev`) — 자세한 규칙은 `scripts/service_updates.py` 맨 위 설명.
- **월 단위 항목**: 출처에 월까지만 있고 본문에서도 정확한 날을 못 찾은 항목은 `date`를 그 달 1일로, `dateMonthOnly: true`를 붙여 저장한다. 화면에는 날짜 없이 그 달 1일 항목 다음(전달 말일 항목 앞)에 보인다.
- **화면**: 수집된 분야는 실제 항목을, 아직 수집하지 않는 분야는 '예시' 항목을 보여 준다.
- **검색 노출**: `/updates/`, `/updates/<분야>/`, `/updates/<분야>/<서비스>/` 페이지는 빌드 때 실제 업데이트 목록(분야·전체는 최근 100건, 서비스는 전부)을 담고 사이트맵에 들어간다.
- **출처 점검**: `python3 scripts/check_update_sources.py` — GitHub Actions(`check-update-sources.yml`)가 매주 월요일에 돌려서, 열리지 않는 출처가 생기면 실패로 알려 준다.

## 루틴 구조

하나의 루틴이 한 세션 안에서 다음 단계를 순서대로 수행한다. 서비스 업데이트만 별도 에이전트가 맡는다.

### PHASE 0 — 업데이트 에이전트 시작

레포를 준비하고, Agent(Task) 도구로 업데이트 수집 에이전트(`routine/updates_agent_prompt.txt`)를 **백그라운드로** 띄운 뒤 바로 PHASE 1로 넘어간다.
PHASE 1이 끝나면 에이전트가 끝났는지(`/tmp/updates/DONE`) 확인하고, 끝날 때까지 기다린 다음 PHASE 2를 시작한다.

### 실행 규칙 (EXECUTION RULES)

프롬프트 맨 앞의 R1~R6은 아래 단계들을 "적힌 그대로" 실행하도록 강제한다. 단계의 조건 자체는 바꾸지 않는다.
(Sonnet 5.5 시험 실행에서 스크립트 생략·기사 일괄 저장·검증 생략 등이 관찰되어 추가)

- R1: 모든 코드 블록을 그대로 실행 (자리표시자만 채움, 대체·생략 금지)
- R2: 섹션별로 공통 + Primary 출처를 빠짐없이 확인한 뒤에만 Broadened/오픈 웹 여부 판단
- R3: PHASE 1 STEP A는 프롬프트 내 curl 스크립트, PHASE 2 STEP 3은 `scripts/fetch_article.py`를 기사마다 다시 실행
- R4: 기사 하나씩 처리 (여러 기사를 한 번에 저장 금지)
- R5: VERIFY DIGEST / VERIFY ARTICLES 필수
- R6: 저장 스크립트의 검사(본문 600–800자: 공백 포함, 태그·원문 줄 제외 등)가 `REJECTED`를 출력하면 다시 작성

### PHASE 1 — 조사 (RESEARCH)

1. **SETUP** — `/tmp/feed/` 초기화, 프롬프트에 내장된 Whitelist를 파싱해 `/tmp/feed/whitelist.json`으로 저장
2. **SECTION 1, 2, 3 — 뉴스 수집** — Whitelist 기반 검색, 각 기사를 curl로 페치해 og:image + 링크 + 본문 추출, JSON 객체로 `/tmp/feed/digest.json`에 누적 저장
3. **VERIFY DIGEST** — 섹션별 수집 건수 확인

### PHASE 2 — 게시 (PUBLISH)

1. **Step 0** — `/tmp/feed/PUBLISH_PHASE` 표시 파일 생성 (이후 컨텍스트 압축 차단, 아래 참고)
2. **SETUP** — 레포를 `/home/user/Daily_Art_AI_News_Feed`에 준비하고 `origin/main`으로 맞춤, 키워드 목록(`data/keywords.json`)을 읽어 `/tmp/feed/keywords.json`으로 저장
3. **STEP 1~2** — `digest.json`을 읽어 섹션 → 탭(`games`/`industry`/`art`)으로 매핑. digest에 있는 기사만, 순서대로 처리 (웹 검색 금지)
4. **STEP 3** — 기사마다 `scripts/fetch_article.py`를 정확히 한 번 실행 (실패 시 WebFetch 1회)
5. **STEP 4** — 필드 매핑 후 `/tmp/feed/articles.json`에 저장 (본문 600–800자, 이미지 4단계 대체, 목록 안에서 keywords 선택·필요 시 키워드 추가 등)
6. **UPDATE THE FEED DATA** — `scripts/update_articles.py`로 URL 중복 제거 후 오늘 날짜 파일에 추가, `scripts/validate_data.py`로 검사
7. **MERGE SERVICE UPDATES** — 업데이트 에이전트 결과를 `scripts/service_updates.py merge`로 `data/updates/`에 합치고 다시 검사 (뉴스가 없는 날도 실행)
8. **COMMIT AND PUSH** — `scripts/push_to_main.py`로 `main`에 직접 push (새 브랜치·PR 금지)
9. **FINISH** — `PUBLISH_PHASE` 표시 파일 삭제

PHASE 2에서는 하위 에이전트(Task tool)를 쓰지 않는다 (업데이트 에이전트는 PHASE 0에서만 띄우고 PHASE 2 전에 끝나 있다). 기사마다 fetch 결과가 같은 세션에 보여야 하는 PRE-FLIGHT CHECK 때문이다.

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

- "오늘 또는 어제" 규칙 때문에 같은 기사가 이틀 연속 잡힐 수 있다. `update_articles.py`가 `data/articles/`의 모든 날짜 파일에 이미 있는 URL은 건너뛴다 (scheme·`www.`·끝 `/`·`#` 차이는 같은 URL로 본다).

## 아이디어

- 아트실에서 주로 사용하는 AI 제품과 관련된 뉴스들을 타겟해서 업데이트
  - ex. Stable Diffusion, MeshyAI, Nano Banana, etc
- 대부분 영문 뉴스라 긴 버전의 요약본을 함께 게재
  - 단, 가독성을 위해서 긴 버전의 요약본은 클릭해서 열어야 읽을 수 있도록 레이아웃 설정
- 수집되는 뉴스의 퀄리티가 괜찮으면 슬랙 채널 개설
- 데일리로 새로운 뉴스를 찾기 힘들면 위클리도 가능
  - 혹은 위클리로 가장 대중의 관심도가 높았던 뉴스만 별도 정리
