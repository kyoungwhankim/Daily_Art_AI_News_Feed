"""
build_site.py — 배포용 정적 사이트를 _site/ 에 만든다 (GitHub Actions가 실행).

사용법:
    python3 scripts/build_site.py [--out _site] [--no-bundle]

만드는 것:
    _site/index.html              피드 앱 (검색엔진용 메타 정보 + 최신 기사 목록을 HTML에 미리 넣음)
    _site/app.js                  app.jsx를 미리 변환한 번들 (esbuild, 브라우저에서 Babel을 돌리지 않음)
    _site/articles/<id>/          기사별 정적 페이지 (제목·본문·OG·canonical·NewsArticle 구조화 데이터)
    _site/topics/<tab>/           탭별 기사 목록
    _site/topics/<tab>/<키워드>/   서브 카테고리별 기사 목록 (탭 안에서 6개 이상인 키워드만)
    _site/sitemap.xml, feed.xml, 404.html, robots.txt (사이트가 도메인 최상위일 때)
    _site/manifest.webmanifest, sw.js, icons/   PWA (홈 화면에 설치, 오프라인 열람)
    _site/app.css, config.js, data/ ... 기존 파일 복사

레포의 index.html(브라우저 Babel 버전)은 로컬 미리보기용으로 그대로 둔다.
--no-bundle 은 esbuild 없이 기존 index.html 방식(app.jsx + Babel)으로 만든다 (로컬 확인용).
--redirect-site DIR 은 예전 GitHub Pages 주소용 안내 사이트를 DIR에 만든다 — 어떤 경로로 들어와도
같은 경로의 새 주소(SITE_URL)로 넘겨 준다.
"""

import argparse
import base64
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feed_data  # noqa: E402
import service_updates  # noqa: E402
import free_tools  # noqa: E402

SITE_URL = os.environ.get(
    'SITE_URL', 'https://ai-art-news.pages.dev').rstrip('/')
# PREVIEW=1 이면 미리보기 배포용: 모든 페이지 noindex, robots.txt 전체 차단, 사이트맵 없음
PREVIEW = os.environ.get('PREVIEW') == '1'
# 예전 주소 (GitHub Pages). --redirect-site 로 이 주소용 "주소가 바뀌었어요" 안내 사이트를 만든다.
OLD_SITE_PATH = '/Daily_Art_AI_News_Feed'
SITE_NAME = 'AI Art Daily'
SITE_DESC = ('게임 제작과 아트 분야의 AI 뉴스를 매일 골라 한국어로 정리합니다. '
             '게임 제작 속 AI, AI 도입 뉴스, 아트 전반 AI 뉴스.')
# 개인정보처리방침 (privacy/ 페이지). 내용을 바꾸면 PRIVACY_DATE도 고친다.
PRIVACY_OWNER = '김경환'          # 개인정보 보호책임자 (contact/ 페이지에도 쓴다)
CONTACT_EMAIL = 'kyoungwhankim.dev@gmail.com'
PRIVACY_DATE = '2026년 10월 7일'
TABS = [
    ('games', '게임 제작 속 AI', '게임 아트 리소스 제작에 사용되는 AI 관련 뉴스들을 매일 업데이트합니다.'),
    ('industry', 'AI 도입 뉴스', '게임 스튜디오들의 AI 도입과 관련된 뉴스들을 매일 업데이트합니다.'),
    ('art', '아트 전반 AI 뉴스', '게임 제작과 무관하게 모든 아트 관련 AI 뉴스들을 매일 업데이트합니다.'),
]
TAB_LABEL = {t: label for t, label, _ in TABS}
MIN_SUBCAT_ARTICLES = 6          # app.jsx와 같은 기준
HOME_LIST = 30                   # index.html에 미리 넣는 최신 기사 수
FEED_ITEMS = 50
KST = timezone(timedelta(hours=9))

REACT_PROD = [
    'https://unpkg.com/react@18.3.1/umd/react.production.min.js',
    'https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js',
]
ESBUILD = 'esbuild@0.24.2'
STATIC_FILES = ['app.css', 'config.js', '.nojekyll', 'manifest.webmanifest', 'ads.txt', 'favicon.ico']


# ---------- helpers ----------

def esc(s) -> str:
    return html.escape(str(s or ''), quote=True)


def plain(h: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h or '')).strip()


def kw_slug(label: str) -> str:
    """서브 카테고리 주소용 이름: 공백·가운뎃점·슬래시는 '-', 영문은 소문자."""
    return re.sub(r'[\s·/]+', '-', label).strip('-').lower()


def iso_date(published_at: str) -> str:
    """'2026.10.02' → '2026-10-02'"""
    return published_at.replace('.', '-')


def kor_date(published_at: str) -> str:
    y, m, d = (int(x) for x in published_at.split('.'))
    return f'{y}년 {m}월 {d}일'


def article_path(a: dict) -> str:
    return f"articles/{a['id']}/"


def tab_path(tab: str) -> str:
    return f'topics/{tab}/'


def kw_path(tab: str, label: str) -> str:
    return f'topics/{tab}/{kw_slug(label)}/'


def href(root: str, path: str) -> str:
    """root(현재 페이지에서 사이트 최상위까지의 상대 경로) + path, 주소용으로 인코딩."""
    return root + urllib.request.quote(path, safe='/-_.~')


def abs_url(path: str = '') -> str:
    return f"{SITE_URL}/{urllib.request.quote(path, safe='/-_.~')}"


def write(out: str, rel: str, text: str) -> None:
    path = os.path.join(out, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def sri(url: str) -> str:
    with urllib.request.urlopen(url, timeout=60) as r:
        data = r.read()
    return 'sha384-' + base64.b64encode(hashlib.sha384(data).digest()).decode()


def file_hash(path: str) -> str:
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:10]


# ---------- data ----------

def load():
    articles = []
    for name in reversed(feed_data.date_files()):            # 최신 날짜부터
        articles += feed_data.read_day(name)
    lists = feed_data.keyword_lists()
    subcats = {}
    for tab, _, _ in TABS:
        counts = defaultdict(int)
        for a in articles:
            if a['tab'] == tab:
                for k in a.get('keywords', []):
                    counts[k] += 1
        subcats[tab] = [(k, counts[k]) for k in lists.get(tab, [])
                        if counts[k] >= MIN_SUBCAT_ARTICLES]
    return articles, subcats


# ---------- page shell ----------

# PWA: 앱 설치 정보 + 오프라인 캐시(service worker) 등록 — 피드 앱 페이지 공통
PWA_HEAD = """<link rel="manifest" href="/manifest.webmanifest" />
<meta name="theme-color" content="#444444" />
<link rel="icon" href="/icons/icon.svg" type="image/svg+xml" />
<link rel="icon" href="/icons/favicon-32.png" sizes="32x32" type="image/png" />
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-title" content="AI Art Daily" />
<meta name="apple-mobile-web-app-status-bar-style" content="default" />
<script>if ('serviceWorker' in navigator) addEventListener('load', function () { navigator.serviceWorker.register('/sw.js'); });</script>
"""

THEME_BOOT = ("<script>document.documentElement.classList.add('js');"
              "try{document.documentElement.dataset.theme="
              "localStorage.getItem('aiad:theme')||'light'}catch(e){}</script>")


ADS_SCRIPT = ('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
              '?client=ca-pub-7751014405174019" crossorigin="anonymous"></script>\n')


def no_ads(h: str) -> str:
    """내용이 거의 없는 화면(404·설정·로그인 전 나만의 피드)에서는 광고 스크립트를 뺀다.
    애드센스 정책: 게시자 콘텐츠가 없는 화면에 광고를 게재하면 안 된다.
    (소유권 확인용 google-adsense-account 메타 태그는 남긴다.)"""
    return h.replace(ADS_SCRIPT, '', 1)


def head(root: str, title: str, desc: str, canonical: str, og_type='website',
         image=None, extra='') -> str:
    img = image or ''
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="google-adsense-account" content="ca-pub-7751014405174019" />
{ADS_SCRIPT}<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}" />
<link rel="canonical" href="{esc(canonical)}" />
<link rel="alternate" type="application/rss+xml" title="{esc(SITE_NAME)}" href="{esc(abs_url('feed.xml'))}" />
<meta property="og:site_name" content="{esc(SITE_NAME)}" />
<meta property="og:locale" content="ko_KR" />
<meta property="og:type" content="{og_type}" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:url" content="{esc(canonical)}" />
{f'<meta property="og:image" content="{esc(img)}" />' if img else ''}
<meta name="twitter:card" content="{'summary_large_image' if img else 'summary'}" />
<meta name="twitter:title" content="{esc(title)}" />
<meta name="twitter:description" content="{esc(desc)}" />
{f'<meta name="twitter:image" content="{esc(img)}" />' if img else ''}
{THEME_BOOT}
<link rel="icon" href="/icons/icon.svg" type="image/svg+xml" />
<link rel="icon" href="/icons/favicon-32.png" sizes="32x32" type="image/png" />
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png" />
<link rel="stylesheet" href="{root}app.css?v={{CSS_V}}" />
<link rel="stylesheet" href="{root}static.css?v={{STATIC_V}}" />
{extra}
</head>
"""


def header(root: str) -> str:
    return f"""<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="{root}">
      <img class="brand-mark" src="{root}icons/logo.svg" alt="" aria-hidden="true" />
      <span class="brand-name">{esc(SITE_NAME)}</span>
    </a>
    <nav class="static-nav">
      {''.join(f'<a href="{href(root, tab_path(t))}">{esc(label)}</a>' for t, label, _ in TABS)}
    </nav>
  </div>
</header>
"""


def footer(root: str = '/') -> str:
    return f"""<footer class="site-footer">
  <div class="meta-line">AI Art Daily · 매일 오전 업데이트</div>
  <div>큐레이션 · 한국어 번역 · <a href="{root}about/">소개</a> · <a href="{root}contact/">문의</a> · <a href="{root}privacy/">개인정보처리방침</a></div>
</footer>
"""


def article_item(root: str, a: dict) -> str:
    return (f'<li><a href="{href(root, article_path(a))}">{esc(a["headline"])}</a>'
            f'<span class="static-item-meta">{esc(a["source"])} · {esc(a["publishedAt"])}</span>'
            f'<p>{esc(a["summary"])}</p></li>')


def grouped_list(root: str, items: list) -> str:
    out, cur = [], None
    for a in items:
        if a['publishedAt'] != cur:
            if cur is not None:
                out.append('</ul>')
            cur = a['publishedAt']
            out.append(f'<h2 class="static-date">{esc(kor_date(cur))}</h2><ul class="static-list">')
        out.append(article_item(root, a))
    if cur is not None:
        out.append('</ul>')
    return '\n'.join(out)


# ---------- pages ----------

def article_page(a: dict, related: list, subcats: dict):
    """기사 페이지의 (검색엔진용 본문 HTML, NewsArticle 구조화 데이터).

    배포 사이트의 /articles/<id>/ 는 피드 앱 페이지라, 방문자에게는 그 기사의 탭 화면 위에
    기사 창이 열리고 이 본문은 숨겨진다 (app.jsx parseRoute).
    """
    root = '/'
    url = abs_url(article_path(a))
    shown = {k for k, _ in subcats[a['tab']]}
    kws = [k for k in a.get('keywords', []) if k in shown]
    ld = {
        '@context': 'https://schema.org',
        '@type': 'NewsArticle',
        'headline': a['headline'][:110],
        'description': a['summary'],
        'datePublished': f"{iso_date(a['publishedAt'])}T09:00:00+09:00",
        'inLanguage': 'ko',
        'mainEntityOfPage': url,
        'articleSection': TAB_LABEL[a['tab']],
        'keywords': a.get('keywords', []),
        'isBasedOn': a['url'],
        'publisher': {'@type': 'Organization', 'name': SITE_NAME, 'url': SITE_URL + '/'},
    }
    if a.get('image'):
        ld['image'] = [a['image']]
    links = ''.join(
        f'<a href="{esc(u["href"])}" target="_blank" rel="noopener noreferrer">{esc(u.get("label") or "관련 링크")} ↗</a>'
        for u in a.get('urls', []) if u.get('href'))
    hero = (f'<img class="static-hero" src="{esc(a["image"])}" alt="{esc(a["headline"])}" '
            f'loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()" />'
            if a.get('image') else '')
    tags = ''.join(f'<a class="modal-keyword" href="{href(root, kw_path(a["tab"], k))}">#{esc(k)}</a>'
                   for k in kws)
    rel = ''.join(article_item(root, r) for r in related)
    html_ = f"""<article class="static-article">
    <nav class="static-crumb"><a href="{href(root, tab_path(a['tab']))}">{esc(TAB_LABEL[a['tab']])}</a></nav>
    <h1 class="modal-headline">{esc(a['headline'])}</h1>
    <div class="modal-meta">
      <span>{esc(a['source'])}</span><span>·</span><time datetime="{iso_date(a['publishedAt'])}">{esc(a['publishedAt'])}</time>
      <a href="{esc(a['url'])}" target="_blank" rel="noopener noreferrer">원문 보기 ↗</a>{links}
    </div>
    {f'<div class="modal-keywords">{tags}</div>' if tags else ''}
    {hero}
    <div class="modal-article">
      <p class="static-lead">{esc(a['summary'])}</p>
      {a.get('body', '')}
    </div>
  </article>
  {f'<section class="static-related"><h2>같은 주제의 다른 기사</h2><ul class="static-list">{rel}</ul></section>' if rel else ''}"""
    return html_, ld


def listing_fallback(title: str, desc: str, items: list, tab: str,
                     subcats: dict, active_kw=None) -> str:
    """탭·서브 카테고리 페이지의 검색엔진용 목록 (앱이 뜨면 숨겨진다)."""
    root = '/'
    chips = ''
    if subcats.get(tab):
        chip_all = (f'<a class="chip subcat{"" if active_kw else " active"}" '
                    f'href="{href(root, tab_path(tab))}">전체</a>')
        chips = '<div class="subcats">' + chip_all + ''.join(
            f'<a class="chip subcat{" active" if k == active_kw else ""}" href="{href(root, kw_path(tab, k))}">'
            f'{esc(k)} <span class="subcat-count">{n}</span></a>'
            for k, n in subcats[tab]) + '</div>'
    return (f'<h1 class="feed-title">{esc(title)}</h1>'
            f'<p class="feed-sub">{esc(desc)} · {len(items)}개 기사</p>'
            + chips + grouped_list(root, items))


def build_shell(src: str, path: str, title: str, desc: str, fallback: str,
                bundle: bool, react_tags: str, app_v: str, ld: dict,
                og_type: str = 'website', image=None) -> str:
    """피드 앱 페이지 (첫 화면, /topics/... 페이지 공통).

    레포의 index.html을 바탕으로 메타 정보·검색엔진용 목록을 넣는다. 방문자에게는
    앱이 주소를 읽어 같은 탭·서브 카테고리의 카드 화면을 띄운다 (app.jsx parseRoute).
    """
    with open(src, encoding='utf-8') as f:
        page = f.read()
    url = abs_url(path) if path else SITE_URL + '/'
    ld_json = json.dumps(ld, ensure_ascii=False).replace('</', '<\\/')
    img_meta = (f'<meta property="og:image" content="{esc(image)}" />\n'
                f'<meta name="twitter:image" content="{esc(image)}" />\n') if image else ''
    meta = f"""<meta name="description" content="{esc(desc)}" />
<link rel="canonical" href="{esc(url)}" />
<link rel="alternate" type="application/rss+xml" title="{esc(SITE_NAME)}" href="{esc(abs_url('feed.xml'))}" />
<meta property="og:site_name" content="{esc(SITE_NAME)}" />
<meta property="og:locale" content="ko_KR" />
<meta property="og:type" content="{og_type}" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:url" content="{esc(url)}" />
{img_meta}<meta name="twitter:card" content="{'summary_large_image' if image else 'summary'}" />
<meta name="twitter:title" content="{esc(title)}" />
<meta name="twitter:description" content="{esc(desc)}" />
<script type="application/ld+json">{ld_json}</script>
"""
    page = re.sub(r'<title>[^<]*</title>\n', lambda m: f'<title>{esc(title)}</title>\n' + meta + PWA_HEAD + THEME_BOOT + '\n'
                  + '<link rel="stylesheet" href="/static.css?v={STATIC_V}" />\n', page, count=1)
    # 어떤 경로의 페이지에서도 같은 파일을 읽도록 사이트 최상위 기준 주소로
    page = re.sub(r'(href|src)="(app\.css|config\.js|app\.jsx)', r'\1="/\2', page)
    if bundle:
        page = re.sub(r'<script src="https://unpkg\.com/[^"]+"[^>]*></script>\n', '', page)
        page = re.sub(r'<script type="text/babel" src="/app\.jsx[^"]*"></script>',
                      f'<script src="/app.js?v={app_v}"></script>', page)
        page = page.replace('<script src="/config.js"></script>',
                            react_tags + '<script src="/config.js"></script>')
    nav = ('<nav class="static-nav">' + ''.join(
        f'<a href="{href("/", tab_path(t))}">{esc(label)}</a>' for t, label, _ in TABS) + '</nav>')
    page = page.replace('<div id="root"></div>',
                        f'<div id="root"><div class="static-main static-fallback">{nav}{fallback}</div></div>', 1)
    return page


def build_sitemap(articles: list, listing_paths: list, dated_paths=()) -> str:
    """dated_paths: [(경로, 'YYYY.MM.DD')] — 업데이트 페이지처럼 페이지마다 최근 날짜가 다른 목록."""
    latest = iso_date(articles[0]['publishedAt']) if articles else ''
    rows = [f'<url><loc>{esc(SITE_URL + "/")}</loc><lastmod>{latest}</lastmod></url>']
    rows += [f'<url><loc>{esc(abs_url(p))}</loc><lastmod>{latest}</lastmod></url>' for p in listing_paths]
    rows += [f'<url><loc>{esc(abs_url(p))}</loc><lastmod>{iso_date(d)}</lastmod></url>' for p, d in dated_paths]
    rows += [f'<url><loc>{esc(abs_url(article_path(a)))}</loc>'
             f'<lastmod>{iso_date(a["publishedAt"])}</lastmod></url>' for a in articles]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + '\n'.join(rows) + '\n</urlset>\n')


def build_feed(articles: list) -> str:
    def rfc822(pa):
        y, m, d = (int(x) for x in pa.split('.'))
        return datetime(y, m, d, 9, 0, tzinfo=KST).strftime('%a, %d %b %Y %H:%M:%S +0900')
    items = []
    for a in articles[:FEED_ITEMS]:
        link = abs_url(article_path(a))
        items.append(
            f'<item><title>{esc(a["headline"])}</title><link>{esc(link)}</link>'
            f'<guid isPermaLink="true">{esc(link)}</guid><pubDate>{rfc822(a["publishedAt"])}</pubDate>'
            f'<category>{esc(TAB_LABEL[a["tab"]])}</category>'
            f'<description>{esc(a["summary"])}</description></item>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
            f'<title>{esc(SITE_NAME)}</title><link>{esc(SITE_URL + "/")}</link>'
            f'<description>{esc(SITE_DESC)}</description><language>ko</language>'
            + ''.join(items) + '</channel></rss>\n')


UPDATES_LIST = 100   # 분야·전체 업데이트 페이지의 검색엔진용 목록에 넣을 최근 항목 수 (서비스 페이지는 전부)


def update_item(root: str, e: dict, svc: dict, show_service: bool) -> str:
    """업데이트 한 건 (검색엔진용). 월 단위 항목(dateMonthOnly)은 날짜를 쓰지 않는다."""
    meta = [svc['name']] if show_service else []
    meta.append(e['kind'])
    if not e.get('dateMonthOnly'):
        meta.append(e['date'])
    det = ''.join(f'<li>{esc(d)}</li>' for d in e.get('details', []))
    who = (f'<a href="{href(root, "updates/" + svc["catSlug"] + "/" + svc["slug"] + "/")}">{esc(svc["name"])}</a> — '
           if show_service else '')
    return (f'<li>{who}<a href="{esc(e["url"])}" rel="noopener">{esc(e["title"])}</a>'
            f'<span class="static-item-meta">{esc(" · ".join(meta))}</span>'
            f'<p>{esc(e["summary"])}</p>' + (f'<ul>{det}</ul>' if det else '') + '</li>')


def updates_fallback(title: str, desc: str, entries: list, by_slug: dict, links: list, show_service=True) -> str:
    root = '/'
    nav = ('<div class="subcats">' + ''.join(
        f'<a class="chip subcat" href="{href(root, p)}">{esc(t)}</a>' for t, p in links) + '</div>') if links else ''
    return (f'<h1 class="feed-title">{esc(title)}</h1><p class="feed-sub">{esc(desc)} · 업데이트 {len(entries)}건</p>'
            + nav + '<ul class="static-list">'
            + ''.join(update_item(root, e, by_slug[e['service']], show_service) for e in entries) + '</ul>')


# ---------- 무료로 써보기 (/free/, /free/<분야>/) ----------
# 주소 규칙·분야 slug는 app.jsx FREE_CAT_SLUG와 같아야 한다.
FREE_CAT_SLUG = {'이미지': 'image', '영상': 'video', '3D': '3d', '게임 에셋': 'game-assets',
                 '애니메이션·모션': 'motion', '음악·음성': 'audio', '디자인·도구': 'tools'}
FREE_TYPE_LABEL = {'plan': '무료 플랜', 'trial': '기간제 체험', 'credits': '가입 크레딧', 'free': '무료 서비스'}


def free_item(t: dict, d: dict) -> str:
    gone = d.get('status') in ('ended', 'paid') or d.get('type') == 'none'
    if gone:
        return ''
    offer = d.get('offer') or '조사 중'
    meta = [t['category']]
    if d.get('type') in FREE_TYPE_LABEL:
        meta.append(FREE_TYPE_LABEL[d['type']])
    if d.get('checked'):
        meta.append(d['checked'] + ' 확인')
    url = d.get('try_url') or t['url']
    rel = 'noopener'
    lim = f'<p>{esc(d["limits"])}</p>' if d.get('limits') else ''
    return (f'<li><a href="{esc(url)}" rel="{rel}">{esc(t["name"])}</a> — {esc(offer)}'
            f'<span class="static-item-meta">{esc(" · ".join(meta))}</span>{lim}</li>')


def free_fallback(title: str, desc: str, tools: list, data: dict, links: list) -> str:
    nav = ('<div class="subcats">' + ''.join(
        f'<a class="chip subcat" href="{href("/", p)}">{esc(t)}</a>' for t, p in links) + '</div>') if links else ''
    trials = ''.join(free_item(t, data.get(t['slug'], {})) for t in tools if t['kind'] == 'trial')
    frees = ''.join(free_item(t, data.get(t['slug'], {})) for t in tools if t['kind'] == 'free')
    out = f'<h1 class="feed-title">{esc(title)}</h1><p class="feed-sub">{esc(desc)}</p>' + nav
    if trials:
        out += f'<h2>무료 체험 · 무료 플랜</h2><ul class="static-list">{trials}</ul>'
    if frees:
        out += f'<h2>무료 서비스</h2><ul class="static-list">{frees}</ul>'
    return out


# ---------- 아티스트 브리핑 — 직군별 추천 (/for/, /for/<직군>/) ----------
# 고르는 기준은 app.jsx roleArticles·roleUpdates와 같아야 한다 (config.js roles 주석 참고).
ROLE_LIST = 30   # 직군 페이지의 검색엔진용 목록에 넣을 최근 기사·업데이트 수


def load_roles() -> list:
    js = "global.window={};require(process.argv[1]);console.log(JSON.stringify(window.AIAD.roles||[]))"
    out = subprocess.run(['node', '-e', js, os.path.join(feed_data.REPO, 'config.js')],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def compile_terms(terms: list) -> list:
    out = []
    for t in terms:
        if re.fullmatch(r'[\x00-\x7f]+', t):
            out.append((t, re.compile(r'(?<![a-z0-9])' + re.escape(t.lower()) + r'(?![a-z0-9])'), None))
        else:
            out.append((t, None, re.sub(r'\s+', '', t.lower())))
    return out


def term_hits(compiled: list, text: str) -> set:
    low = (text or '').lower()
    flat = re.sub(r'\s+', '', low)
    return {t for t, rx, ko in compiled if (rx.search(low) if rx else ko in flat)}


def role_articles(role: dict, articles: list) -> list:
    ct, tags = compile_terms(role.get('terms', [])), set(role.get('tags', []))
    out = []
    for a in articles:
        h = term_hits(ct, a['headline'])
        s = term_hits(ct, a['summary']) - h
        score = 3 * len(tags & set(a.get('keywords', []))) + 3 * len(h) + 2 * len(s)
        if score < 3:
            score += len(term_hits(ct, html.unescape(re.sub(r'<[^>]+>', ' ', a.get('body', '')))) - h - s)
        if score >= 3:
            out.append(a)
    return out


def role_updates(role: dict, entries: list) -> list:
    ct, svc = compile_terms(role.get('terms', [])), set(role.get('services', []))
    return [e for e in entries if e['service'] in svc or term_hits(ct, e['title'])
            or len(term_hits(ct, e['summary'] + ' ' + ' '.join(e.get('details') or []))) >= 2]


def role_fallback(role: dict, news: list, upd: list, by_slug: dict, roles: list) -> str:
    root = '/'
    nav = '<div class="subcats">' + ''.join(
        f'<a class="chip subcat{" active" if r["id"] == role["id"] else ""}" href="{href(root, "for/" + r["id"] + "/")}">'
        f'{esc(r["label"])}</a>' for r in roles) + '</div>'
    return (f'<h1 class="feed-title">{esc(role["label"])} 브리핑 — 추천 뉴스·업데이트</h1>'
            f'<p class="feed-sub">{esc(role["desc"])} · 키워드: {esc(", ".join(role["terms"][:12]))}</p>' + nav
            + f'<h2 class="static-date">추천 뉴스 ({len(news)}건 중 최근 {min(len(news), ROLE_LIST)}건)</h2>'
            + grouped_list(root, news[:ROLE_LIST])
            + f'<h2 class="static-date">추천 업데이트 ({len(upd)}건 중 최근 {min(len(upd), ROLE_LIST)}건)</h2>'
            + '<ul class="static-list">'
            + ''.join(update_item(root, e, by_slug[e['service']], True) for e in upd[:ROLE_LIST]) + '</ul>')


def build_redirect_site(out: str) -> None:
    """예전 주소(GitHub Pages)용: index.html·404.html이 같은 경로의 새 주소로 넘겨 준다."""
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    new = SITE_URL + '/'
    old_path = json.dumps(OLD_SITE_PATH)
    page = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(SITE_NAME)} — 주소가 바뀌었어요</title>
<link rel="canonical" href="{esc(new)}" />
<script>
(function () {{
  var old = {old_path}, p = location.pathname;
  if (p.indexOf(old) === 0) p = p.slice(old.length) || '/';
  location.replace({json.dumps(SITE_URL)} + p + location.search + location.hash);
}})();
</script>
<meta http-equiv="refresh" content="3; url={esc(new)}" />
</head>
<body style="font-family: system-ui, sans-serif; padding: 40px;">
<p>{esc(SITE_NAME)}의 주소가 바뀌었어요: <a href="{esc(new)}">{esc(new)}</a></p>
</body>
</html>
"""
    write(out, 'index.html', page)
    write(out, '404.html', page)
    print(f'Built redirect site {out} → {new}')


# 문의 양식: 서버 없이 메일 작성 창을 연다 (받는 사람·제목·본문이 채워진 상태)
#   기본 메일 앱(mailto: — Outlook·메일 앱 등 컴퓨터에 설정된 앱), Outlook 웹, Gmail 웹
CONTACT_JS = r"""
(function () {
  var MAIL = '__MAIL__';
  var form = document.getElementById('contact-form'), st = document.getElementById('cf-status');
  function say(t, ok) { st.textContent = t; st.className = 'cf-status ' + (ok ? 'ok' : 'err'); }
  function compose() {
    var f = new FormData(form), msg = (f.get('message') || '').trim();
    if (msg.length < 5) { say('내용을 적어 주세요.'); return null; }
    var name = (f.get('name') || '').trim();
    var subject = '[AI Art Daily 문의] ' + f.get('topic');
    var body = msg + (name ? '\n\n— ' + name : '');
    say('메일 작성 창을 열었어요. 내용을 확인하고 보내기를 눌러 주세요.', true);
    return { s: encodeURIComponent(subject), b: encodeURIComponent(body), to: encodeURIComponent(MAIL) };
  }
  document.querySelectorAll('[data-send]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var c = compose(); if (!c) return;
      var kind = btn.getAttribute('data-send');
      if (kind === 'app') location.href = 'mailto:' + MAIL + '?subject=' + c.s + '&body=' + c.b;
      else if (kind === 'outlook') window.open('https://outlook.live.com/mail/0/deeplink/compose?to=' + c.to + '&subject=' + c.s + '&body=' + c.b, '_blank', 'noopener');
      else if (kind === 'gmail') window.open('https://mail.google.com/mail/?view=cm&fs=1&to=' + c.to + '&su=' + c.s + '&body=' + c.b, '_blank', 'noopener');
    });
  });
})();
"""


def build_contact() -> str:
    root = '/' + SITE_URL.split('/', 3)[3] + '/' if SITE_URL.count('/') >= 3 else '/'
    js = CONTACT_JS.replace('__MAIL__', CONTACT_EMAIL)
    return (head(root, f'문의 | {SITE_NAME}', f'{SITE_NAME}에 문의하거나 뉴스 피드 개선 아이디어를 보내 주세요.', abs_url('contact/'))
            + f"""<body>
<div class="page">
{header(root)}
<main class="static-main static-doc">
  <h1 class="feed-title">문의</h1>
  <p class="feed-sub">기사 내용 정정, 저작권, 제휴, 개인정보 관련 문의를 받아요.
  <strong>뉴스 피드를 더 좋게 만들 아이디어도 언제든 환영해요</strong> — 보고 싶은 주제, 추가했으면 하는 AI 서비스, 불편한 점 무엇이든 편하게 보내 주세요.</p>

  <form class="contact-form" id="contact-form" novalidate>
    <div class="cf-row">
      <label>문의 종류
        <select name="topic">
          <option>뉴스 피드 개선 아이디어</option>
          <option>기사 내용 정정</option>
          <option>저작권</option>
          <option>제휴</option>
          <option>개인정보·계정</option>
          <option>기타</option>
        </select>
      </label>
      <label><b class="cf-l">이름 <span>(선택)</span></b><input name="name" maxlength="50" autocomplete="name" /></label>
    </div>
    <label>내용<textarea name="message" rows="7" maxlength="3000" placeholder="자유롭게 적어 주세요."></textarea></label>
    <div class="cf-foot">
      <span class="cf-status" id="cf-status" role="status">버튼을 누르면 받는 사람·제목·내용이 채워진 메일 작성 창이 열려요.</span>
      <div class="cf-btns">
        <button type="button" class="chip active" data-send="app">메일 앱으로 보내기</button>
        <button type="button" class="chip" data-send="outlook">Outlook 웹</button>
        <button type="button" class="chip" data-send="gmail">Gmail</button>
      </div>
    </div>
  </form>

  <dl class="static-contact">
    <dt>관리자</dt><dd>{esc(PRIVACY_OWNER)}</dd>
    <dt>이메일</dt><dd><a href="mailto:{esc(CONTACT_EMAIL)}">{esc(CONTACT_EMAIL)}</a></dd>
  </dl>
</main>
{footer(root)}
</div>
<script>{js}</script>
</body>
</html>
""")


def build_about() -> str:
    root = '/' + SITE_URL.split('/', 3)[3] + '/' if SITE_URL.count('/') >= 3 else '/'
    mail = f'<a href="mailto:{esc(CONTACT_EMAIL)}">{esc(CONTACT_EMAIL)}</a>'
    tabs = ''.join(f'<li><a href="{href(root, tab_path(t))}"><strong>{esc(label)}</strong></a> — {esc(desc)}</li>'
                   for t, label, desc in TABS)
    return (head(root, f'소개 | {SITE_NAME}',
                 f'{SITE_NAME}가 무엇을 다루고, 기사를 어떻게 고르고 쓰는지 소개합니다.',
                 abs_url('about/'))
            + f"""<body>
<div class="page">
{header(root)}
<main class="static-main static-doc">
  <h1 class="feed-title">소개</h1>
  <p class="feed-sub">{SITE_NAME}는 게임과 아트를 만드는 사람들을 위한 한국어 AI 뉴스 사이트예요.
  매일 아침, 아트 작업에 영향을 주는 AI 소식을 골라 한국어로 정리합니다.</p>

  <h2>운영 목적</h2>
  <p>AI는 하루가 다르게 발전하고, 새 도구와 소식이 매일 쏟아집니다. 그런데 정작 현업 아티스트들은 정보의 홍수
  속에서 내 작업에 정말 필요한 양질의 정보를 찾기가 점점 어려워지고 있어요. 바쁜 작업 틈틈이 수많은 해외 매체와
  서비스 공지를 일일이 확인하기는 쉽지 않으니까요.</p>
  <p>{SITE_NAME}는 그런 아쉬움에서 출발했습니다. 믿을 수 있는 출처의 새 AI 소식을 매일 골라, 아티스트 각자의
  <strong>직무와 관심사에 맞게 큐레이션</strong>해 전하는 것이 이 서비스의 목표예요. 넘쳐나는 정보를 쫓는 대신,
  꼭 알아야 할 소식만 짧은 시간에 확인하고 다시 작업에 집중할 수 있도록 돕고 싶습니다.</p>

  <h2>무엇을 다루나요</h2>
  <ul>
    {tabs}
    <li><a href="{root}updates/"><strong>업데이트</strong></a> — 이미지·영상·3D·음악 등 아트 AI 서비스 50여 곳의
      공식 업데이트 소식을 서비스별로 모아요.</li>
    <li><a href="{root}for/"><strong>아티스트 브리핑</strong></a> — 3D·2D·애니메이터·VFX·사운드 등 직군별로
      꼭 볼 만한 뉴스와 도구를 묶어 보여 줘요.</li>
    <li><a href="{root}free/"><strong>AI 무료로 써보기</strong></a> — 아트 AI 서비스를 무료로 써 볼 수 있는
      방법(무료 플랜·체험·가입 크레딧)을 매주 확인해 정리해요.</li>
  </ul>

  <h2>기사를 고르는 기준</h2>
  <ul>
    <li><strong>믿을 수 있는 출처만</strong> — AI 회사·게임 엔진·스튜디오의 공식 발표와, 한국·미국·일본·중국·유럽의
      게임·아트·기술 전문 매체 약 80곳을 출처 목록으로 정해 두고 그 안에서 고릅니다.</li>
    <li><strong>새 소식만</strong> — 발행일이 오늘이나 어제인 기사만 다루고, 이미 소개한 소식을 다른 매체가
      다시 보도한 경우에는 새로 밝혀진 사실이 없으면 싣지 않아요.</li>
    <li><strong>아트 작업과 관련 있는 것</strong> — 이미지·영상·3D·애니메이션·사운드 제작 도구, 스튜디오의 AI 도입,
      창작자와 저작권 이슈처럼 만드는 사람에게 의미 있는 소식을 우선합니다. 단순 주가·투자 소식이나
      창작과 관계없는 AI 뉴스는 다루지 않아요.</li>
  </ul>

  <h2>기사를 쓰는 방식</h2>
  <ul>
    <li>원문을 읽고 핵심을 한국어로 새로 씁니다. 원문을 그대로 옮기거나 통째로 번역하지 않아요.</li>
    <li>무슨 일이 있었는지, 구체적으로 무엇이 바뀌는지, 그리고 <strong>아트 작업에 왜 중요한지</strong>를 함께 적어요.</li>
    <li>모든 기사에 원문 매체 이름, 발행일, 원문 링크를 밝히고, 더 자세한 내용은 원문에서 보도록 안내합니다.
      대표 이미지는 원문 매체가 공유용으로 제공하는 이미지를 출처와 함께 씁니다.</li>
    <li>서비스 업데이트와 무료 이용 정보는 각 서비스의 공식 페이지(요금제·도움말·공식 블로그)에서 확인한 내용만
      싣고, 확인하지 못한 정보는 '확인 필요'로 표시해요.</li>
  </ul>

  <h2>AI 활용과 운영</h2>
  <p>기사 수집과 한국어 요약에는 AI 도구를 활용합니다. 어떤 출처를 쓸지, 어떤 소식을 싣고 뺄지, 기사를
  어떤 형식과 기준으로 쓸지는 운영자가 정하고 계속 다듬어요. 사실과 다른 내용이나 잘못된 번역을 발견하면
  <a href="{root}contact/">문의</a>로 알려 주세요. 확인한 뒤 바로 고칩니다.</p>

  <h2>운영자</h2>
  <dl class="static-contact">
    <dt>운영</dt><dd>{esc(PRIVACY_OWNER)}</dd>
    <dt>이메일</dt><dd>{mail}</dd>
    <dt>문의</dt><dd><a href="{root}contact/">문의 페이지</a> · <a href="{root}privacy/">개인정보처리방침</a></dd>
  </dl>
</main>
{footer(root)}
</div>
</body>
</html>
""")


def build_privacy() -> str:
    root = '/' + SITE_URL.split('/', 3)[3] + '/' if SITE_URL.count('/') >= 3 else '/'
    mail = f'<a href="mailto:{esc(CONTACT_EMAIL)}">{esc(CONTACT_EMAIL)}</a>'
    return (head(root, f'개인정보처리방침 | {SITE_NAME}',
                 f'{SITE_NAME}의 개인정보 수집·이용, 쿠키와 광고, 이용자 권리에 대한 안내입니다.',
                 abs_url('privacy/'))
            + f"""<body>
<div class="page">
{header(root)}
<main class="static-main static-doc">
  <h1 class="feed-title">개인정보처리방침</h1>
  <p class="feed-sub">시행일: {PRIVACY_DATE}</p>

  <p>{SITE_NAME}(이하 '사이트')는 「개인정보 보호법」 등 관련 법령을 지키며, 이용자의 개인정보를 필요한 만큼만
  처리합니다. 이 방침은 사이트가 어떤 정보를 왜 처리하는지, 이용자가 어떤 권리를 갖는지 설명합니다.</p>

  <h2>1. 처리하는 개인정보</h2>
  <p>사이트의 기사와 업데이트 소식은 회원가입이나 로그인 없이 누구나 볼 수 있으며, 이때 이름·이메일 같은
  정보를 받지 않습니다. 다만 아래 정보가 처리될 수 있습니다.</p>
  <ul>
    <li><strong>접속 기록</strong> — IP 주소, 브라우저·기기 정보, 접속 시각, 요청한 페이지.
      사이트를 전송하는 호스팅 서비스(Cloudflare)가 보안과 서비스 운영을 위해 자동으로 기록합니다.</li>
    <li><strong>광고 쿠키</strong> — 사이트에 표시되는 Google 애드센스 광고가 쿠키와 기기 식별자를 사용합니다
      (아래 4항).</li>
    <li><strong>Google 계정 로그인 정보</strong> (로그인 기능을 이용하는 경우에만) — 이메일 주소, 이름,
      프로필 사진 주소, 계정 고유 식별자, 그리고 이용자가 직접 저장한 관심 분야 설정('나만의 피드')·저장한 기사와
      업데이트 목록·마지막 방문일(새 소식 표시용).
      비밀번호는 사이트가 받지 않으며 Google이 직접 인증합니다.</li>
  </ul>

  <h2>2. 이용 목적과 보유 기간</h2>
  <ul>
    <li>접속 기록: 서비스 제공, 장애·부정 이용 대응, 통계. 호스팅 서비스의 보관 기준에 따라 보관 후 삭제됩니다.</li>
    <li>로그인 정보: 로그인 상태 유지와 '나만의 피드' 제공. 이용자가 계정 삭제를 요청하면 지체 없이 삭제합니다.</li>
    <li>광고 쿠키: 광고 표시와 광고 성과 측정 (Google의 정책에 따름).</li>
  </ul>
  <p>법령에 따라 보관해야 하는 경우를 빼고는 목적을 이룬 개인정보를 바로 파기합니다.</p>

  <h2>3. 제3자 제공과 처리 위탁</h2>
  <p>사이트는 이용자의 개인정보를 다른 곳에 팔거나 제공하지 않습니다. 서비스 운영을 위해 아래 업체의 서비스를
  이용하며, 이 과정에서 정보가 해외에서 처리될 수 있습니다.</p>
  <table class="static-table">
    <thead><tr><th>업체</th><th>하는 일</th><th>처리되는 정보</th><th>위치</th></tr></thead>
    <tbody>
      <tr><td>Cloudflare, Inc.</td><td>사이트 호스팅·전송</td><td>접속 기록</td><td>미국 등 전 세계 데이터센터</td></tr>
      <tr><td>Google LLC</td><td>광고(애드센스), Google 계정 로그인</td><td>광고 쿠키, 로그인 시 계정 정보</td><td>미국 등</td></tr>
      <tr><td>Supabase, Inc.</td><td>로그인 처리, '나만의 피드' 설정 저장</td><td>로그인 정보, 관심 분야 설정, 저장한 글 목록, 마지막 방문일</td><td>대한민국(서울) 리전</td></tr>
    </tbody>
  </table>
  <p>정보는 사이트 이용 시점에 암호화된 통신(HTTPS)으로 전송되며, 위 보유 기간 동안 처리됩니다.
  해외 처리를 원하지 않으면 로그인 기능을 이용하지 않거나 계정 삭제를 요청할 수 있습니다.</p>

  <h2>4. 쿠키와 광고</h2>
  <ul>
    <li>Google을 포함한 제3자 광고 업체는 쿠키를 사용해 이용자가 이 사이트나 다른 웹사이트를 방문한 기록을 바탕으로
      광고를 게재합니다.</li>
    <li>Google은 광고 쿠키를 사용해 이용자의 사이트 방문 기록에 기반한 광고를 이용자에게 보여 줄 수 있습니다.</li>
    <li>맞춤 광고는 <a href="https://adssettings.google.com" rel="noopener">Google 광고 설정</a>에서 끌 수 있고,
      제3자 업체의 맞춤 광고 쿠키는 <a href="https://www.aboutads.info/choices/" rel="noopener">aboutads.info</a>에서
      끌 수 있습니다.</li>
    <li>Google의 정보 처리 방식은 <a href="https://policies.google.com/technologies/partner-sites?hl=ko" rel="noopener">Google 파트너 사이트 정책</a>에서 볼 수 있습니다.</li>
    <li>브라우저 설정에서 쿠키를 거부할 수 있으며, 이 경우 일부 기능(로그인 등)을 이용하지 못할 수 있습니다.</li>
  </ul>

  <h2>5. 브라우저에 저장하는 정보</h2>
  <p>화면 테마(라이트·다크) 선택, 앱 설치 안내 표시 여부, 마지막 방문일(새 소식 표시용), 로그인 상태를 이용자의 브라우저 저장소(localStorage)에
  저장하고, 빠른 로딩을 위해 페이지 파일을 브라우저에 캐시합니다. 이 정보는 사이트 서버로 보내지지 않으며,
  브라우저의 사이트 데이터 삭제로 지울 수 있습니다.</p>

  <h2>6. 이용자의 권리</h2>
  <p>이용자는 언제든지 자신의 개인정보 열람, 정정, 삭제, 처리 정지를 요청할 수 있습니다. 아래 문의처로
  연락하면 지체 없이 처리하고 결과를 알려 드립니다. 로그인한 이용자는 계정 메뉴의 '관심사 설정'에서 저장한 정보를
  고치고, '회원 탈퇴'로 계정과 저장한 정보를 바로 삭제할 수 있습니다.</p>

  <h2>7. 안전성 확보 조치</h2>
  <p>모든 통신은 HTTPS로 암호화하고, 로그인 정보는 이용자 본인만 읽고 쓸 수 있도록 접근 권한을 제한하며,
  관리용 권한은 운영자만 사용합니다.</p>

  <h2>8. 만 14세 미만 아동</h2>
  <p>사이트는 만 14세 미만 아동의 개인정보를 알면서 수집하지 않습니다. 만 14세 미만이라면 로그인 기능을
  이용하지 말아 주세요.</p>

  <h2>9. 개인정보 보호책임자와 문의</h2>
  <ul>
    <li>개인정보 보호책임자: {esc(PRIVACY_OWNER)}</li>
    <li>문의: {mail}</li>
  </ul>
  <p>개인정보 침해에 대한 신고나 상담은 아래 기관에도 할 수 있습니다.</p>
  <ul>
    <li>개인정보침해신고센터 (국번 없이 118, <a href="https://privacy.kisa.or.kr" rel="noopener">privacy.kisa.or.kr</a>)</li>
    <li>개인정보분쟁조정위원회 (1833-6972, <a href="https://www.kopico.go.kr" rel="noopener">www.kopico.go.kr</a>)</li>
    <li>대검찰청 (국번 없이 1301, <a href="https://www.spo.go.kr" rel="noopener">www.spo.go.kr</a>)</li>
    <li>경찰청 (국번 없이 182, <a href="https://ecrm.police.go.kr" rel="noopener">ecrm.police.go.kr</a>)</li>
  </ul>

  <h2>10. 방침의 변경</h2>
  <p>이 방침이 바뀌면 시행일과 함께 이 페이지에 알립니다.</p>
</main>
{footer(root)}
</div>
</body>
</html>
""")


def build_404() -> str:
    root = '/' + SITE_URL.split('/', 3)[3] + '/' if SITE_URL.count('/') >= 3 else '/'
    return (head(root, f'페이지를 찾을 수 없어요 | {SITE_NAME}', SITE_DESC, SITE_URL + '/')
            .replace('<link rel="canonical"', '<meta name="robots" content="noindex" />\n<link rel="canonical"')
            + f"""<body>
<div class="page">
{header(root)}
<main class="static-main">
  <h1 class="feed-title">페이지를 찾을 수 없어요</h1>
  <p class="feed-sub"><a href="{root}">첫 화면으로 돌아가기</a></p>
</main>
{footer(root)}
</div>
</body>
</html>
""")


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(feed_data.REPO, '_site'))
    ap.add_argument('--no-bundle', action='store_true')
    ap.add_argument('--redirect-site', metavar='DIR')
    args = ap.parse_args()
    if args.redirect_site:
        build_redirect_site(args.redirect_site)
        return
    repo, out = feed_data.REPO, args.out

    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    for name in STATIC_FILES + ['static.css']:
        src = os.path.join(repo, name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(out, name))
    shutil.copytree(os.path.join(repo, 'data'), os.path.join(out, 'data'),
                    ignore=shutil.ignore_patterns('source_state.json'))   # 업데이트 수집용 내부 파일
    shutil.copytree(os.path.join(repo, 'icons'), os.path.join(out, 'icons'))

    articles, subcats = load()

    # app 번들 (esbuild) — 브라우저에서 Babel을 돌리지 않게
    bundle = not args.no_bundle
    react_tags, app_v = '', ''
    if bundle:
        subprocess.run(['npx', '--yes', ESBUILD, os.path.join(repo, 'app.jsx'),
                        '--loader:.jsx=jsx', '--jsx-factory=React.createElement',
                        '--jsx-fragment=React.Fragment', '--target=es2019', '--minify',
                        f'--outfile={os.path.join(out, "app.js")}'], check=True)
        app_v = file_hash(os.path.join(out, 'app.js'))
        react_tags = ''.join(f'<script src="{u}" integrity="{sri(u)}" crossorigin="anonymous"></script>\n'
                             for u in REACT_PROD)
    else:
        shutil.copy2(os.path.join(repo, 'app.jsx'), os.path.join(out, 'app.jsx'))

    css_v = file_hash(os.path.join(repo, 'app.css'))
    static_v = file_hash(os.path.join(repo, 'static.css'))

    def fin(text: str) -> str:
        text = text.replace('{CSS_V}', css_v).replace('{STATIC_V}', static_v)
        # index.html(앱 화면 틀)의 app.css?v=고정값도 내용 해시로 — 서비스 워커가 예전 CSS를 계속 쓰지 않게
        return re.sub(r'app\.css\?v=[^"\']+', f'app.css?v={css_v}', text)

    def shell(path, title, desc, fallback, ld, og_type='website', image=None):
        return fin(build_shell(os.path.join(repo, 'index.html'), path, title, desc,
                               fallback, bundle, react_tags, app_v, ld, og_type, image))

    home_fallback = (f'<h1 class="feed-title">{esc(SITE_NAME)}</h1><p class="feed-sub">{esc(SITE_DESC)}</p>'
                     + grouped_list('/', articles[:HOME_LIST]))
    write(out, 'index.html', shell('', SITE_NAME, SITE_DESC, home_fallback,
                                   {'@context': 'https://schema.org', '@type': 'WebSite', 'name': SITE_NAME,
                                    'url': SITE_URL + '/', 'inLanguage': 'ko', 'description': SITE_DESC}))

    by_tab = defaultdict(list)
    for a in articles:
        by_tab[a['tab']].append(a)
    for a in articles:
        same = [r for r in by_tab[a['tab']] if r['id'] != a['id']]
        kws = set(a.get('keywords', []))
        related = sorted(same, key=lambda r: -len(kws & set(r.get('keywords', []))))
        related = [r for r in related if kws & set(r.get('keywords', []))][:5] or same[:5]
        body, ld = article_page(a, related, subcats)
        write(out, article_path(a) + 'index.html', shell(
            article_path(a), f"{a['headline']} | {SITE_NAME}", a['summary'], body, ld,
            'article', a.get('image')))

    def collection(path, name, desc):
        return {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': name,
                'description': desc, 'url': abs_url(path), 'inLanguage': 'ko',
                'isPartOf': {'@type': 'WebSite', 'name': SITE_NAME, 'url': SITE_URL + '/'}}

    listing_paths = []
    for tab, label, desc in TABS:
        p = tab_path(tab)
        listing_paths.append(p)
        write(out, p + 'index.html', shell(
            p, f'{label} | {SITE_NAME}', desc,
            listing_fallback(label, desc, by_tab[tab], tab, subcats), collection(p, label, desc)))
        for k, _ in subcats[tab]:
            p = kw_path(tab, k)
            listing_paths.append(p)
            items = [a for a in by_tab[tab] if k in a.get('keywords', [])]
            kdesc = f'{label} 중 {k} 관련 기사'
            write(out, p + 'index.html', shell(
                p, f'{k} — {label} | {SITE_NAME}', kdesc,
                listing_fallback(f'{k} — {label}', kdesc, items, tab, subcats, k),
                collection(p, f'{k} — {label}', kdesc)))

    # service worker — 앱 화면을 이루는 파일을 미리 저장. 파일 내용이 바뀌면 VERSION이 바뀌어 새로 설치된다
    with open(os.path.join(out, 'index.html'), encoding='utf-8') as f:
        home = f.read()
    precache = ['/'] + [u for u in re.findall(r'(?:href|src)="(/(?:app\.js|app\.css|static\.css|config\.js)[^"]*)"', home)]
    precache += ['/manifest.webmanifest', '/icons/icon-192.png'] + (REACT_PROD if bundle else [])
    precache = list(dict.fromkeys(precache))
    with open(os.path.join(repo, 'sw.js'), encoding='utf-8') as f:
        sw = f.read()
    version = hashlib.md5(json.dumps(precache).encode()
                          + open(os.path.join(repo, 'sw.js'), 'rb').read()).hexdigest()[:10]
    # 아이콘·로고 주소에 내용 해시를 붙인다 — 바꾸면 브라우저 탭 아이콘·오프라인 캐시가 새 파일을 받는다
    icon_names = ['icon.svg', 'favicon-32.png', 'apple-touch-icon.png', 'icon-192.png', 'icon-512.png', 'logo.svg']
    icon_v = hashlib.md5(b''.join(open(os.path.join(repo, 'icons', n), 'rb').read() for n in icon_names)).hexdigest()[:8]
    version = hashlib.md5((version + icon_v).encode()).hexdigest()[:10]
    write(out, 'sw.js', sw.replace('__VERSION__', version)
          .replace('__PRECACHE__', json.dumps(precache, ensure_ascii=False)))

    # 사이드바 대분류 '업데이트' 페이지: /updates/, /updates/<분야>/, /updates/<분야>/<서비스>/
    # 검색엔진용으로 실제 업데이트 목록을 담는다 (앱이 뜨면 숨겨진다). 주소 규칙은 app.jsx와 같아야 한다.
    services = service_updates.load_services()
    by_slug = {sv['slug']: sv for sv in services}
    all_upd = service_updates.sorted_entries(
        [e for sv in services for e in service_updates.read_service(sv['slug'])])
    cats = []
    for sv in services:
        if sv['catSlug'] not in [c for c, _ in cats]:
            cats.append((sv['catSlug'], sv['category']))
    cat_links = [(label, f'updates/{slug}/') for slug, label in cats]
    upd_desc = '아트 관련 AI 서비스들의 공식 업데이트(새 모델·기능·API 변경)를 분야·서비스별로 한국어로 정리했어요.'
    upd_dated = []

    def upd_page(path_, title, desc, entries, links, show_service=True, limit=None):
        shown = entries[:limit] if limit else entries
        write(out, path_ + 'index.html', shell(
            path_, f'{title} | {SITE_NAME}', desc,
            updates_fallback(title, desc, shown, by_slug, links, show_service),
            collection(path_, title, desc)))
        if entries:
            upd_dated.append((path_, entries[0]['date']))

    upd_page('updates/', 'AI 서비스 업데이트', upd_desc, all_upd, cat_links, limit=UPDATES_LIST)
    for slug, label in cats:
        svs = [sv for sv in services if sv['catSlug'] == slug]
        entries = [e for e in all_upd if by_slug[e['service']]['catSlug'] == slug]
        upd_page(f'updates/{slug}/', f'{label} AI 서비스 업데이트',
                 f'{label} 분야 AI 서비스({", ".join(sv["name"] for sv in svs[:6])} 등)의 공식 업데이트를 최신순으로 정리했어요.',
                 entries, [(sv['name'], f'updates/{slug}/{sv["slug"]}/') for sv in svs], limit=UPDATES_LIST)
        for sv in svs:
            entries = [e for e in all_upd if e['service'] == sv['slug']]
            who = f'{sv["maker"]} {sv["name"]}' if sv.get('maker') else sv['name']
            upd_page(f'updates/{slug}/{sv["slug"]}/', f'{who} 업데이트',
                     f'{who}의 공식 업데이트(새 모델·기능·API·개발자 변경 기록)를 최신순으로 한국어로 정리했어요.',
                     entries, [(label, f'updates/{slug}/')], show_service=False)

    # 무료로 써보기: /free/, /free/<분야>/ (검색엔진용 목록 — 앱이 뜨면 숨겨진다)
    ftools = free_tools.load_tools()
    if ftools:
        fdata = free_tools.load_data()
        for t in ftools:
            t['catSlug'] = FREE_CAT_SLUG.get(t['category'], free_tools.kw_slug(t['category']))
        fcats = []
        for t in ftools:
            if t['catSlug'] not in [c for c, _ in fcats]:
                fcats.append((t['catSlug'], t['category']))
        flinks = [(label, f'free/{slug}/') for slug, label in fcats]
        fdesc = ('이미지·영상·3D·애니메이션·음악 등 아트 AI 서비스의 무료 체험·무료 플랜과 무료 서비스를 모았어요. '
                 '매주 공식 가격 페이지를 확인해 갱신해요.')
        write(out, 'free/index.html', shell(
            'free/', f'AI 무료로 써보기 | {SITE_NAME}', fdesc,
            free_fallback('AI 무료로 써보기', fdesc, ftools, fdata.get('tools', {}), flinks),
            collection('free/', 'AI 무료로 써보기', fdesc)))
        listing_paths.append('free/')
        for slug, label in fcats:
            ts = [t for t in ftools if t['catSlug'] == slug]
            d = (f'{label} AI 서비스({", ".join(t["name"] for t in ts[:5])} 등)를 무료로 써 보는 방법 — '
                 '무료 크레딧·무료 체험·무료 플랜을 매주 확인해 정리했어요.')
            title = f'무료 {label} AI 서비스'
            write(out, f'free/{slug}/index.html', shell(
                f'free/{slug}/', f'{title} | {SITE_NAME}', d,
                free_fallback(title, d, ts, fdata.get('tools', {}), [('전체', 'free/')]),
                collection(f'free/{slug}/', title, d)))
            listing_paths.append(f'free/{slug}/')

    # 아티스트 브리핑 (직군별 추천)
    roles = load_roles()
    if roles:
        role_desc = '게임 아트 직군(3D·2D·애니메이터·리거·VFX·테크니컬 아티스트·사운드 등)별로 관심 가질 AI 뉴스와 서비스 업데이트를 모았어요.'
        write(out, 'for/index.html', shell(
            'for/', f'아티스트 브리핑 | {SITE_NAME}', role_desc,
            '<h1 class="feed-title">아티스트 브리핑</h1>'
            f'<p class="feed-sub">{esc(role_desc)}</p><ul class="static-list">' + ''.join(
                f'<li><a href="{href("/", "for/" + r["id"] + "/")}">{esc(r["label"])}</a><p>{esc(r["desc"])}</p></li>'
                for r in roles) + '</ul>',
            collection('for/', '아티스트 브리핑', role_desc)))
        listing_paths.append('for/')
        for r in roles:
            p = f'for/{r["id"]}/'
            news, upd = role_articles(r, articles), role_updates(r, all_upd)
            d = f'{r["label"]}를 위한 AI 뉴스와 서비스 업데이트 — {r["desc"]}'
            write(out, p + 'index.html', shell(
                p, f'{r["label"]} 브리핑 | {SITE_NAME}', d,
                role_fallback(r, news, upd, by_slug, roles), collection(p, f'{r["label"]} 브리핑', d)))
            listing_paths.append(p)

    # 나만의 피드 (/me/) — 로그인 회원 화면이라 검색엔진에는 내보내지 않는다
    me_desc = '로그인하면 내 직군·관심 주제·관심 서비스·키워드에 맞는 뉴스와 업데이트만 모아 볼 수 있어요.'
    write(out, 'me/index.html', no_ads(shell('me/', f'나만의 피드 | {SITE_NAME}', me_desc,
                                      f'<h1 class="feed-title">나만의 피드</h1><p class="feed-sub">{esc(me_desc)}</p>',
                                      collection('me/', '나만의 피드', me_desc))
          .replace('<title>', '<meta name="robots" content="noindex" />\n<title>', 1)))

    st_desc = '계정 정보, 나만의 피드 관심사, 회원 탈퇴를 관리해요.'
    write(out, 'settings/index.html', no_ads(shell('settings/', f'설정 | {SITE_NAME}', st_desc,
                                            f'<h1 class="feed-title">설정</h1><p class="feed-sub">{esc(st_desc)}</p>',
                                            collection('settings/', '설정', st_desc))
          .replace('<title>', '<meta name="robots" content="noindex" />\n<title>', 1)))

    icon_re = re.compile(r'(/icons/(?:' + '|'.join(re.escape(n) for n in icon_names) + r'))(?=["\'])')
    for dp, _, fs in os.walk(out):
        for fn in fs:
            if fn.endswith('.html') or fn == 'manifest.webmanifest':
                fp = os.path.join(dp, fn)
                with open(fp, encoding='utf-8') as fh:
                    txt = fh.read()
                new = icon_re.sub(lambda m: m.group(1) + '?v=' + icon_v, txt)
                if new != txt:
                    with open(fp, 'w', encoding='utf-8') as fh:
                        fh.write(new)

    write(out, 'sitemap.xml', build_sitemap(articles, listing_paths + ['about/', 'contact/', 'privacy/'], upd_dated))
    write(out, 'feed.xml', build_feed(articles))
    write(out, '404.html', fin(no_ads(build_404())))
    write(out, 'about/index.html', fin(build_about()))
    write(out, 'privacy/index.html', fin(build_privacy()))
    write(out, 'contact/index.html', fin(build_contact()))
    if PREVIEW:
        write(out, 'robots.txt', 'User-agent: *\nDisallow: /\n')
        os.remove(os.path.join(out, 'sitemap.xml'))
        for dp, _, fs in os.walk(out):
            for f in fs:
                if f.endswith('.html'):
                    fp = os.path.join(dp, f)
                    with open(fp, encoding='utf-8') as fh:
                        h = fh.read()
                    if 'name="robots"' not in h:
                        h = h.replace('<title>', '<meta name="robots" content="noindex" />\n<title>', 1)
                        with open(fp, 'w', encoding='utf-8') as fh:
                            fh.write(h)
    elif SITE_URL.count('/') == 2:     # 도메인 최상위 사이트일 때만 robots.txt가 의미 있다
        write(out, 'robots.txt', f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n')

    print(f'Built {out}: {len(articles)} article pages, {len(listing_paths)} listing pages, '
          f'bundle={"esbuild" if bundle else "babel"}{", PREVIEW (noindex)" if PREVIEW else ""}')


if __name__ == '__main__':
    main()
