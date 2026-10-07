-- AI Art Daily — 나만의 피드용 Supabase 설정
-- Supabase 대시보드 → SQL Editor → New query 에 이 파일 전체를 붙여 넣고 Run.
-- 여러 번 실행해도 안전하다 (이미 있으면 건너뛰거나 다시 만든다).

-- 1) 회원별 관심사 (한 사람당 한 줄)
create table if not exists public.profiles (
  id           uuid primary key references auth.users(id) on delete cascade,   -- 로그인 계정 (탈퇴하면 같이 지워진다)
  role         text check (role is null or char_length(role) <= 20),           -- 직군 id (config.js roles: 3d, 2d, animator ...)
  news_topics  text[] not null default '{}' check (cardinality(news_topics) <= 100),  -- 관심 뉴스 서브 카테고리 '탭|키워드' (예: games|3D)
  services     text[] not null default '{}' check (cardinality(services) <= 100),     -- 관심 AI 서비스 slug (예: midjourney)
  keywords     text[] not null default '{}' check (cardinality(keywords) <= 20),      -- 직접 입력한 키워드
  include_role boolean not null default true,                                   -- 직군 추천도 피드에 섞을지
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

-- 2) 본인 줄만 읽고 쓸 수 있게 (행 단위 보안)
alter table public.profiles enable row level security;
drop policy if exists "profiles: read own"   on public.profiles;
drop policy if exists "profiles: insert own" on public.profiles;
drop policy if exists "profiles: update own" on public.profiles;
drop policy if exists "profiles: delete own" on public.profiles;
create policy "profiles: read own"   on public.profiles for select to authenticated using ((select auth.uid()) = id);
create policy "profiles: insert own" on public.profiles for insert to authenticated with check ((select auth.uid()) = id);
create policy "profiles: update own" on public.profiles for update to authenticated using ((select auth.uid()) = id) with check ((select auth.uid()) = id);
create policy "profiles: delete own" on public.profiles for delete to authenticated using ((select auth.uid()) = id);
revoke all on public.profiles from anon;
grant select, insert, update, delete on public.profiles to authenticated;

-- 3) 수정 시각 자동 기록
create or replace function public.profiles_touch() returns trigger
language plpgsql set search_path = '' as $$
begin new.updated_at = now(); return new; end $$;
drop trigger if exists profiles_touch on public.profiles;
create trigger profiles_touch before update on public.profiles
  for each row execute function public.profiles_touch();

-- 4) 회원 탈퇴 (본인 계정만 지운다 — 관심사도 함께 지워진다)
create or replace function public.delete_my_account() returns void
language sql security definer set search_path = '' as $$
  delete from auth.users where id = auth.uid();
$$;
revoke all on function public.delete_my_account() from public, anon;
grant execute on function public.delete_my_account() to authenticated;

-- 5) 깨우기용 함수 (.github/workflows/supabase-keepalive.yml이 주 2회 부른다)
--    무료 플랜은 7일 동안 활동이 없으면 프로젝트가 일시정지된다. 회원 데이터는 건드리지 않고 1만 돌려준다.
create or replace function public.keep_alive() returns int
language sql stable set search_path = '' as $$ select 1 $$;
revoke all on function public.keep_alive() from public;
grant execute on function public.keep_alive() to anon, authenticated;

-- 6) 저장한 글 · 덜 보기 · 마지막 방문일 (나만의 피드)
--    용량을 아끼려고 기본값 없이 비워 둔다 — 쓰지 않는 회원은 자리를 차지하지 않는다 (null).
--    글은 내용을 복사하지 않고 기사·업데이트 id만 저장한다.
alter table public.profiles add column if not exists saved   text[];   -- 저장한 기사·업데이트 id (최근 저장 순)
alter table public.profiles add column if not exists muted   text[];   -- 덜 보기: 뉴스 주제 '탭|키워드' 또는 서비스 slug
alter table public.profiles add column if not exists seen_on date;     -- 마지막 방문일 ('지난 방문 이후 새 소식' 표시용)
alter table public.profiles drop constraint if exists profiles_saved_limit;
alter table public.profiles add constraint profiles_saved_limit
  check (saved is null or (cardinality(saved) <= 500 and octet_length(array_to_string(saved, '')) <= 500 * 60));
alter table public.profiles drop constraint if exists profiles_muted_limit;
alter table public.profiles add constraint profiles_muted_limit
  check (muted is null or (cardinality(muted) <= 50 and octet_length(array_to_string(muted, '')) <= 50 * 120));
