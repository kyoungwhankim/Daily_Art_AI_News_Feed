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
