# 로그인 · 나만의 피드 운영 안내

AI Art Daily의 로그인(Google)과 나만의 피드를 운영하면서 알아 둘 것을 모았다.
요금·한도 숫자는 2026년 10월 기준이고 자주 바뀌니, 결정하기 전에 꼭 공식 요금 페이지에서 다시 확인한다.

- Supabase 요금: https://supabase.com/pricing
- Supabase 사용량: 대시보드 → 프로젝트 → **Usage** (또는 Organization → Usage)

---

## 1. 지금 구성

| 구성 요소 | 어디에 | 하는 일 |
|---|---|---|
| Google Cloud 프로젝트 `AI Art Daily` | console.cloud.google.com | Google 로그인 화면(OAuth 클라이언트, 동의 화면) |
| Supabase 프로젝트 `abablvgtlhuvwdpxvoyu` (서울) | supabase.com 대시보드 | 로그인 처리, 회원 목록, `profiles` 표 |
| `config.js` → `auth` | 이 레포 | Supabase 주소와 **공개용** publishable 키 |
| `supabase/schema.sql` | 이 레포 | `profiles` 표, 본인만 읽고 쓰는 보안 규칙, 회원 탈퇴 함수 |
| `/me/` 나만의 피드, `/settings/` 설정 | 사이트 | 관심사 보기·수정, 계정 정보, 회원 탈퇴 |

로그인 흐름: 사이트의 로그인 버튼 → Google 계정 선택 → `https://abablvgtlhuvwdpxvoyu.supabase.co/auth/v1/callback` → 사이트로 돌아옴.

회원 한 명에 대해 저장되는 것:
- Supabase Auth(`auth.users`): Google 이메일, 이름, 프로필 사진 주소, 가입일, 마지막 로그인
- `profiles` 표: 직군, 관심 뉴스 주제, 관심 AI 서비스, 직접 키워드, 직군 추천 포함 여부
  - 저장한 글(`saved`, 기사·업데이트 id만, 최대 500개), 마지막 방문일(`seen_on`)
  - 용량을 아끼려고 이 두 칸은 기본값 없이 비워 둔다(null) — 쓰지 않는 회원은 자리를 차지하지 않는다.
    마지막 방문일은 관심사를 저장한 회원만, 하루 한 번만 기록한다.
  - 예상 용량: 회원 1명당 평균 약 2~3KB → 5만 명이어도 150MB 안팎 (무료 한도 500MB)

---

## 2. 비밀값 — 어디에 두고 무엇을 절대 공개하지 않는가

| 값 | 공개 여부 | 있는 곳 |
|---|---|---|
| Supabase Project URL | 공개 OK | `config.js` |
| Supabase publishable 키 (`sb_publishable_...`) | 공개 OK (브라우저용) | `config.js` |
| Supabase **secret 키** (`sb_secret_...`, 예전 service_role) | **절대 비공개** | Supabase 대시보드에만 |
| Supabase DB 비밀번호 | **절대 비공개** | 본인 보관 |
| Google OAuth **클라이언트 보안 비밀번호** (`GOCSPX-...`) | **절대 비공개** | Supabase → Authentication → Providers → Google 에만 |

- secret 키·DB 비밀번호·클라이언트 보안 비밀번호는 레포, 채팅, 이슈, 커밋 어디에도 넣지 않는다.
- 혹시 노출됐다면 바로 재발급한다.
  - Supabase secret 키: Project Settings → API Keys에서 새로 만들고 예전 키를 지운다.
  - Google 보안 비밀번호: Google Cloud → 클라이언트 → 보안 비밀번호 추가 → Supabase에 새 값 저장 → 예전 값 삭제.
- publishable 키가 공개돼도 안전한 이유는 `profiles` 표의 **행 단위 보안(RLS)** 때문이다. 각 회원은 자기 줄만 읽고 쓸 수 있다.
  **RLS를 끄면 누구나 모든 회원 데이터를 읽을 수 있으니 절대 끄지 않는다.** (Table Editor에서 표 옆에 "RLS enabled"가 보여야 한다.)

---

## 3. 무료 플랜 한도와 업그레이드 시점

### Supabase Free (현재)
| 항목 | 한도 | 이 사이트 기준 |
|---|---|---|
| 월간 활성 사용자(MAU) | 50,000명 | 한 달에 한 번이라도 로그인한 회원 수 |
| 데이터베이스 | 500MB | 회원 1명 ≈ 몇 KB → 수만 명도 여유 |
| 데이터 전송량(egress) | 월 5GB | 관심사 읽기·쓰기만 해서 매우 적음 |
| 활성 프로젝트 | 2개 | 지금 1개 사용 |
| 백업 | 없음 | 아래 "백업" 참고 |
| **비활성 일시정지** | **7일 동안 활동이 없으면 프로젝트가 멈춤** | 아래 참고 |

### ⚠️ 7일 일시정지 (무료 플랜에서 가장 먼저 겪을 수 있는 문제)
- 무료 프로젝트는 일주일 동안 사용이 없으면 자동으로 **일시정지(paused)** 된다. 멈추면 로그인과 나만의 피드가 동작하지 않는다(뉴스·업데이트는 그대로 보인다).
- 대처: Supabase 대시보드에서 프로젝트를 열고 **Restore project**를 누르면 몇 분 뒤 다시 켜진다. 데이터는 그대로 남아 있다.
- 예방: GitHub Actions 작업 **Supabase keep-alive**(`.github/workflows/supabase-keepalive.yml`)가 월·목요일 아침에 자동으로 돈다.
  - `keep_alive()` 함수(`supabase/schema.sql` 5번)를 불러 데이터베이스에 활동을 남긴다. 회원 데이터는 건드리지 않는다.
  - 함께 로그인 서버 상태, Google 로그인 켜짐 여부, 배포된 `config.js`의 Supabase 설정을 확인한다 (`scripts/check_supabase.py`).
  - 실패하면 GitHub 알림 메일이 오고 레포에 **"Supabase 점검 실패"** 이슈가 열린다. 다시 성공하면 이슈가 자동으로 닫힌다.
  - 공개 키만 쓰므로 Secret은 필요 없다. Actions 탭 → Supabase keep-alive → **Run workflow**로 바로 돌려 볼 수 있다.
  - 이미 멈춘 프로젝트를 되살리지는 못한다(무료 플랜은 대시보드에서 직접 Restore). 빨리 알아채는 게 목적이다.
- Pro 플랜은 일시정지가 없다.

### 업그레이드(Pro) 를 고려할 때
아래 중 하나라도 해당하면 Pro로 올린다.
- MAU가 **약 40,000명**(한도의 80%)을 넘기 시작할 때
- 데이터베이스가 **400MB** 근처일 때 (Usage 페이지에서 확인)
- 회원 데이터가 중요해져서 **자동 백업**이 필요할 때
- 일시정지가 한 번이라도 서비스에 문제가 됐을 때
- Google 로그인 화면의 "abablvgtlhuvwdpxvoyu.supabase.co(으)로 이동" 문구를 사이트 주소로 바꾸고 싶을 때(커스텀 도메인 — 유료 추가 기능)

### Supabase Pro (참고)
- 월 $25부터. MAU 100,000명, DB 8GB, 전송량 250GB 포함. 매일 자동 백업(7일 보관), 일시정지 없음.
- 포함량을 넘으면 사용량만큼 추가 요금(예: MAU 1명당 약 $0.00325).
- 커스텀 도메인(예: `auth.내도메인.com`)은 월 약 $10 추가 기능.
- 업그레이드 방법: 대시보드 → Organization → **Billing** → Change plan. 사이트 코드는 바꿀 필요 없다.
- 지출 상한(Spend Cap)을 켜 두면 포함량을 넘었을 때 요금 대신 서비스가 제한된다. 예상 못 한 청구가 걱정되면 켜 둔다.

### Google 쪽
- Google 로그인 자체는 무료이고 사용자 수 제한이 없다.
- OAuth 동의 화면이 **프로덕션(게시됨)** 상태여야 누구나 로그인할 수 있다. "테스트" 상태면 등록한 테스트 사용자 100명만 된다.
- 지금은 기본 권한(이메일·프로필)만 써서 Google 검수가 필요 없다. 다음을 하면 검수(며칠~몇 주)가 필요하다:
  - 동의 화면에 **로고**를 넣을 때
  - 이메일·프로필 외의 권한(Drive, Gmail 등)을 요청할 때

---

## 4. 회원 · 데이터 보기

- 회원 목록: Supabase → **Authentication → Users** (이메일, 가입일, 마지막 로그인)
- 회원별 관심사: Supabase → **Table Editor → profiles**
- 통계: Supabase → **SQL Editor**에서 실행

```sql
-- 전체 회원 수 / 최근 30일 로그인한 회원 수
select count(*) as 전체,
       count(*) filter (where last_sign_in_at > now() - interval '30 days') as 최근30일
from auth.users;

-- 관심사를 저장한 회원 수
select count(*) from public.profiles;

-- 직군별 회원 수
select coalesce(role, '(없음)') as 직군, count(*) from public.profiles group by 1 order by 2 desc;

-- 가장 많이 고른 뉴스 주제 20개
select t as 주제, count(*) from public.profiles, unnest(news_topics) t group by 1 order by 2 desc limit 20;

-- 가장 많이 고른 AI 서비스 20개
select s as 서비스, count(*) from public.profiles, unnest(services) s group by 1 order by 2 desc limit 20;

-- 직접 입력 키워드 상위 30개 (새 서브 카테고리·서비스 후보를 찾을 때)
select k as 키워드, count(*) from public.profiles, unnest(keywords) k group by 1 order by 2 desc limit 30;

-- 날짜별 가입자 수
select date(created_at) as 날짜, count(*) from auth.users group by 1 order by 1 desc limit 30;
```

---

## 5. 백업

- 무료 플랜에는 자동 백업이 없다. 회원 관심사를 잃고 싶지 않으면 한 달에 한 번 정도 내보낸다:
  Table Editor → `profiles` → **Export → CSV**.
- 회원 계정 자체(Google 로그인)는 회원이 다시 로그인하면 다시 생긴다. 잃으면 아쉬운 건 `profiles`(관심사)다.
- Pro로 올리면 매일 자동 백업된다.
- 백업 파일에는 개인정보(회원 id와 관심사)가 들어 있으니 안전한 곳에 보관한다.

---

## 6. 개인정보 · 회원 요청 처리

- 개인정보처리방침: `/privacy/` (scripts/build_site.py의 `build_privacy`). 저장하는 정보나 업체가 바뀌면 이 페이지와 시행일(`PRIVACY_DATE`)을 함께 고친다.
  - 예: 이메일 뉴스레터를 보내기 시작하거나, 회원에게서 새 정보를 받거나, Supabase 리전을 바꾸는 경우.
- 회원 탈퇴: 회원이 **설정 → 회원 탈퇴**로 직접 할 수 있다(`delete_my_account()` 함수가 계정과 관심사를 함께 지움).
- 메일로 삭제를 요청받으면: Supabase → Authentication → Users → 해당 회원 → **Delete user**. `profiles`는 계정과 함께 자동으로 지워진다.
- 메일로 열람을 요청받으면: SQL Editor에서 그 회원의 `profiles` 줄과 auth 정보(이메일·가입일)를 보내 준다.
  ```sql
  select u.email, u.created_at, u.last_sign_in_at, p.*
  from auth.users u left join public.profiles p on p.id = u.id
  where u.email = '회원@이메일';
  ```
- 개인정보 유출이 의심되면(예: secret 키 노출) 키를 바로 재발급하고, 법령(개인정보 보호법)에 따라 회원 통지와 신고(개인정보포털·KISA) 의무가 있는지 확인한다.
- 만 14세 미만은 로그인 기능을 쓰지 않도록 방침에 적어 두었다.

---

## 7. 바꿀 일이 생겼을 때

### 사이트 주소(도메인)를 바꾸면 — 예: `ai-art-news.pages.dev` → `내도메인.com`
1. Supabase → Authentication → **URL Configuration**: Site URL과 Redirect URLs에 새 주소 추가 (`https://내도메인.com/**`)
2. Google Cloud → 클라이언트: **승인된 JavaScript 원본**에 새 주소 추가
3. Google Cloud → 브랜딩: 홈페이지·개인정보처리방침 링크, **승인된 도메인**에 새 도메인 추가
4. 레포: `scripts/build_site.py`의 `SITE_URL`, `.github/workflows/deploy.yml`
5. 예전 주소는 한동안 함께 등록해 두고, 옮긴 뒤에 지운다.

### 관심사에 새 항목을 추가하려면 (예: 알림 받기 여부)
1. SQL Editor: `alter table public.profiles add column ... ;` (보안 규칙은 표 단위라 다시 만들 필요 없음)
2. `supabase/schema.sql`에도 같은 내용 반영
3. `app.jsx`의 `EMPTY_PROFILE`, `useProfile`의 select 목록, `ProfileForm` 양식에 추가
4. 개인정보처리방침의 "처리하는 개인정보"에 추가

### Supabase 키를 새 형식으로 바꾸거나 재발급하면
- `config.js`의 `supabaseAnonKey`만 새 publishable 키로 바꾸고 배포한다. 기존 로그인 회원은 다시 로그인해야 할 수 있다.

---

## 8. 문제가 생겼을 때

| 증상 | 확인할 곳 |
|---|---|
| "Supabase 점검 실패" 이슈가 열림 | 이슈 안의 로그에서 FAIL 줄 확인. 대부분 일시정지 → 대시보드에서 Restore project. `keep_alive` 404면 schema.sql 5번을 다시 실행 |
| 로그인 버튼이 안 보임 | `config.js`의 `supabaseUrl`·`supabaseAnonKey`가 비어 있지 않은지 |
| 로그인 누르면 오류 / 아무 일도 없음 | Supabase 프로젝트가 **일시정지**됐는지(대시보드 첫 화면), Providers → Google이 켜져 있는지 |
| Google 화면에 `redirect_uri_mismatch` | Google Cloud 클라이언트의 승인된 리디렉션 URI가 `https://abablvgtlhuvwdpxvoyu.supabase.co/auth/v1/callback`과 정확히 같은지 |
| Google 화면에 "확인되지 않은 앱" / 일부 사람만 로그인됨 | OAuth 동의 화면이 "프로덕션(게시됨)"인지 |
| 로그인 후 다른 주소로 가거나 `?error=` 가 붙음 | Supabase Redirect URLs에 지금 사이트 주소(`/**` 포함)가 있는지 |
| 관심사 저장 실패 | `profiles` 표가 있는지(schema.sql 실행 여부), RLS 정책이 지워지지 않았는지 |
| 회원 탈퇴 실패 | `delete_my_account` 함수가 있는지 (schema.sql을 다시 실행하면 만들어짐) |
| 갑자기 많은 회원이 로그아웃됨 | 키 재발급·JWT 설정 변경 여부 |

브라우저 개발자 도구(F12) → Console에 빨간 오류가 있으면 그 문구를 함께 보면 원인을 찾기 쉽다.

---

## 9. 정기 점검 (한 달에 한 번, 5분)

- [ ] Supabase **Usage**: MAU, DB 크기, egress가 한도의 80%를 넘지 않았는지
- [ ] Actions 탭에서 Supabase keep-alive 작업이 계속 성공하고 있는지 (GitHub은 레포에 60일 동안 활동이 없으면 정해진 시간 작업을 끈다 — 꺼졌으면 Actions 탭에서 다시 켠다)
- [ ] `profiles` CSV 백업 (무료 플랜일 때)
- [ ] Authentication → Users에서 이상하게 많은 가입(스팸)이 없는지
- [ ] 위 4장의 통계 쿼리로 인기 주제·서비스·직접 키워드 확인 → 서브 카테고리·업데이트 서비스 추가 아이디어로 활용
