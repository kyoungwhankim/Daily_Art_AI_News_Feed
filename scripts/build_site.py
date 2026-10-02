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
    _site/sitemap.xml, feed.xml, 404.html
    _site/app.css, config.js, data/ ... 기존 파일 복사

레포의 index.html(브라우저 Babel 버전)은 로컬 미리보기용으로 그대로 둔다.
--no-bundle 은 esbuild 없이 기존 index.html 방식(app.jsx + Babel)으로 만든다 (로컬 확인용).
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

SITE_URL = os.environ.get(
    'SITE_URL', 'https://kyoungwhankim.github.io/Daily_Art_AI_News_Feed').rstrip('/')
SITE_NAME = 'AI Art Daily'
SITE_TAGLINE = '한국어 큐레이션'
SITE_DESC = ('게임 제작과 아트 분야의 AI 뉴스를 매일 골라 한국어로 정리합니다. '
             '게임 제작 속 AI, AI 도입 뉴스, 아트 전반 AI 뉴스.')
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
STATIC_FILES = ['app.css', 'config.js', '.nojekyll']


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

THEME_BOOT = ("<script>document.documentElement.classList.add('js');"
              "try{document.documentElement.dataset.theme="
              "localStorage.getItem('aiad:theme')||'light'}catch(e){}</script>")


def head(root: str, title: str, desc: str, canonical: str, og_type='website',
         image=None, extra='') -> str:
    img = image or ''
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(title)}</title>
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
<link rel="stylesheet" href="{root}app.css?v={{CSS_V}}" />
<link rel="stylesheet" href="{root}static.css?v={{STATIC_V}}" />
{extra}
</head>
"""


def header(root: str) -> str:
    return f"""<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="{root}">
      <span class="brand-name">{esc(SITE_NAME)}</span>
      <small>{esc(SITE_TAGLINE)}</small>
    </a>
    <nav class="static-nav">
      {''.join(f'<a href="{href(root, tab_path(t))}">{esc(label)}</a>' for t, label, _ in TABS)}
    </nav>
  </div>
</header>
"""


def footer() -> str:
    return """<footer class="site-footer">
  <div class="meta-line">AI Art Daily · 매일 오전 업데이트</div>
  <div>큐레이션 · 한국어 번역</div>
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

def build_article(a: dict, related: list, subcats: dict) -> str:
    root = '../../'
    url = abs_url(article_path(a))
    desc = a['summary']
    shown = {k for k, _ in subcats[a['tab']]}
    kws = [k for k in a.get('keywords', []) if k in shown]
    ld = {
        '@context': 'https://schema.org',
        '@type': 'NewsArticle',
        'headline': a['headline'][:110],
        'description': desc,
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
    extra = ('<script type="application/ld+json">'
             + json.dumps(ld, ensure_ascii=False).replace('</', '<\\/') + '</script>')
    links = ''.join(
        f'<a href="{esc(u["href"])}" target="_blank" rel="noopener noreferrer">{esc(u.get("label") or "관련 링크")} ↗</a>'
        for u in a.get('urls', []) if u.get('href'))
    hero = (f'<img class="static-hero" src="{esc(a["image"])}" alt="{esc(a["headline"])}" '
            f'loading="eager" referrerpolicy="no-referrer" onerror="this.remove()" />'
            if a.get('image') else '')
    tags = ''.join(f'<a class="modal-keyword" href="{href(root, kw_path(a["tab"], k))}">#{esc(k)}</a>'
                   for k in kws)
    rel = ''.join(article_item(root, r) for r in related)
    return (head(root, f"{a['headline']} | {SITE_NAME}", desc, url, 'article', a.get('image'), extra)
            + f"""<body>
<div class="page">
{header(root)}
<main class="static-main">
  <article class="static-article">
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
    <p class="static-open"><a class="chip" href="{root}?article={esc(a['id'])}">피드에서 보기</a></p>
  </article>
  {f'<section class="static-related"><h2>같은 주제의 다른 기사</h2><ul class="static-list">{rel}</ul></section>' if rel else ''}
</main>
{footer()}
</div>
</body>
</html>
""")


def build_listing(path: str, title: str, desc: str, items: list,
                  tab: str, subcats: dict, active_kw=None) -> str:
    root = '../' * path.count('/')
    chips = ''
    if subcats.get(tab):
        chip_all = (f'<a class="chip subcat{"" if active_kw else " active"}" '
                    f'href="{href(root, tab_path(tab))}">전체</a>')
        chips = '<div class="subcats">' + chip_all + ''.join(
            f'<a class="chip subcat{" active" if k == active_kw else ""}" href="{href(root, kw_path(tab, k))}">'
            f'{esc(k)} <span class="subcat-count">{n}</span></a>'
            for k, n in subcats[tab]) + '</div>'
    return (head(root, f'{title} | {SITE_NAME}', desc, abs_url(path))
            + f"""<body>
<div class="page">
{header(root)}
<main class="static-main">
  <h1 class="feed-title">{esc(title)}</h1>
  <p class="feed-sub">{esc(desc)} · {len(items)}개 기사</p>
  {chips}
  {grouped_list(root, items)}
</main>
{footer()}
</div>
</body>
</html>
""")


def build_index(src: str, items: list, bundle: bool, react_tags: str, app_v: str) -> str:
    with open(src, encoding='utf-8') as f:
        page = f.read()
    meta = f"""<meta name="description" content="{esc(SITE_DESC)}" />
<link rel="canonical" href="{esc(SITE_URL + '/')}" />
<link rel="alternate" type="application/rss+xml" title="{esc(SITE_NAME)}" href="{esc(abs_url('feed.xml'))}" />
<meta property="og:site_name" content="{esc(SITE_NAME)}" />
<meta property="og:locale" content="ko_KR" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{esc(SITE_NAME)} — {esc(SITE_TAGLINE)}" />
<meta property="og:description" content="{esc(SITE_DESC)}" />
<meta property="og:url" content="{esc(SITE_URL + '/')}" />
<meta name="twitter:card" content="summary" />
<script type="application/ld+json">{json.dumps({'@context': 'https://schema.org', '@type': 'WebSite', 'name': SITE_NAME, 'url': SITE_URL + '/', 'inLanguage': 'ko', 'description': SITE_DESC}, ensure_ascii=False)}</script>
"""
    page = page.replace('</title>\n', '</title>\n' + meta + THEME_BOOT + '\n'
                        + '<link rel="stylesheet" href="static.css?v={STATIC_V}" />\n', 1)
    if bundle:
        page = re.sub(r'<script src="https://unpkg\.com/[^"]+"[^>]*></script>\n', '', page)
        page = re.sub(r'<script type="text/babel" src="app\.jsx[^"]*"></script>',
                      f'<script src="app.js?v={app_v}"></script>', page)
        page = page.replace('<script src="config.js"></script>',
                            react_tags + '<script src="config.js"></script>')
    # React가 렌더링하면 사라지는, 검색엔진·JS 미실행 환경용 최신 기사 목록
    fallback = ('<div class="static-main static-fallback">'
                f'<h1 class="feed-title">{esc(SITE_NAME)}</h1><p class="feed-sub">{esc(SITE_DESC)}</p>'
                '<nav class="static-nav">' + ''.join(
                    f'<a href="{href("", tab_path(t))}">{esc(label)}</a>' for t, label, _ in TABS)
                + '</nav>' + grouped_list('', items) + '</div>')
    page = page.replace('<div id="root"></div>', f'<div id="root">{fallback}</div>', 1)
    return page


def build_sitemap(articles: list, listing_paths: list) -> str:
    latest = iso_date(articles[0]['publishedAt']) if articles else ''
    rows = [f'<url><loc>{esc(SITE_URL + "/")}</loc><lastmod>{latest}</lastmod></url>']
    rows += [f'<url><loc>{esc(abs_url(p))}</loc><lastmod>{latest}</lastmod></url>' for p in listing_paths]
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
{footer()}
</div>
</body>
</html>
""")


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(feed_data.REPO, '_site'))
    ap.add_argument('--no-bundle', action='store_true')
    args = ap.parse_args()
    repo, out = feed_data.REPO, args.out

    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    for name in STATIC_FILES + ['static.css']:
        src = os.path.join(repo, name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(out, name))
    shutil.copytree(os.path.join(repo, 'data'), os.path.join(out, 'data'))

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
        return text.replace('{CSS_V}', css_v).replace('{STATIC_V}', static_v)

    write(out, 'index.html', fin(build_index(os.path.join(repo, 'index.html'),
                                         articles[:HOME_LIST], bundle, react_tags, app_v)))

    by_tab = defaultdict(list)
    for a in articles:
        by_tab[a['tab']].append(a)
    for a in articles:
        same = [r for r in by_tab[a['tab']] if r['id'] != a['id']]
        kws = set(a.get('keywords', []))
        related = sorted(same, key=lambda r: -len(kws & set(r.get('keywords', []))))
        related = [r for r in related if kws & set(r.get('keywords', []))][:5] or same[:5]
        write(out, article_path(a) + 'index.html', fin(build_article(a, related, subcats)))

    listing_paths = []
    for tab, label, desc in TABS:
        p = tab_path(tab)
        listing_paths.append(p)
        write(out, p + 'index.html', fin(build_listing(p, label, desc, by_tab[tab], tab, subcats)))
        for k, _ in subcats[tab]:
            p = kw_path(tab, k)
            listing_paths.append(p)
            items = [a for a in by_tab[tab] if k in a.get('keywords', [])]
            write(out, p + 'index.html', fin(build_listing(
                p, f'{k} — {label}', f'{label} 중 {k} 관련 기사', items, tab, subcats, k)))

    write(out, 'sitemap.xml', build_sitemap(articles, listing_paths))
    write(out, 'feed.xml', build_feed(articles))
    write(out, '404.html', fin(build_404()))

    print(f'Built {out}: {len(articles)} article pages, {len(listing_paths)} listing pages, '
          f'bundle={"esbuild" if bundle else "babel"}')


if __name__ == '__main__':
    main()
