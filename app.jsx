/* AI Art Daily — hi-fi prototype */

const { useState, useEffect, useMemo, useRef, useCallback } = React;
const { tabs: TABS, updateSources: UPDATE_SOURCES = [] } = window.AIAD;

/* ---------- data loading ---------- */
// 기사 데이터는 날짜별 파일로 나뉘어 있다: data/index.json → data/articles/YYYY-MM-DD.json
// 날짜 파일은 index의 rev(내용 해시)로 캐시를 구분하므로, 바뀐 날짜 파일만 새로 받는다.
const DATA_BASE = '/data/';   // 사이트 최상위 기준 (/topics/... 페이지에서도 같은 데이터를 읽는다)
async function fetchJson(url, init) {
  const r = await fetch(url, init);
  if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
  return r.json();
}
async function loadArticles() {
  const [index, keywords] = await Promise.all([
    fetchJson(`${DATA_BASE}index.json`, { cache: 'no-cache' }),
    fetchJson(`${DATA_BASE}keywords.json`, { cache: 'no-cache' }),   // 탭별 서브 카테고리 키워드 목록
  ]);
  const days = await Promise.all(
    index.dates.map(d => fetchJson(`${DATA_BASE}${d.file}?v=${d.rev}`))
  );
  return { articles: days.flat(), keywordTabs: keywords.tabs };   // index는 최신순 → 기사도 최신 날짜부터
}

/* ---------- page address (탭·서브 카테고리 ↔ 주소) ---------- */
// 배포 사이트의 /topics/<tab>/, /topics/<tab>/<키워드>/, /articles/<id>/ 는 검색엔진용 HTML을 담은 같은 앱 페이지다.
// /articles/<id>/ 는 그 기사의 탭 화면 위에 기사 창을 연다 (링크 복사·공유 주소).
// 주소 → 앱 상태, 앱 상태 → 주소를 맞춰서, 어떤 주소로 들어와도 같은 카드 화면이 열린다.
// 키워드 주소 이름 규칙은 scripts/build_site.py의 kw_slug()와 같아야 한다.
function kwSlug(label) {
  return label.replace(/[\s·/]+/g, '-').replace(/^-+|-+$/g, '').toLowerCase();
}
function parseRoute(pathname) {
  const parts = pathname.split('/').filter(Boolean).map(p => { try { return decodeURIComponent(p); } catch { return p; } });
  if (parts[0] === 'topics' && TABS.some(t => t.id === parts[1])) {
    return { home: false, tab: parts[1], kwSlug: parts[2] || null, articleId: null };
  }
  if (parts[0] === 'articles' && parts[1]) {
    return { home: false, tab: null, kwSlug: null, articleId: parts[1] };
  }
  if (parts[0] === 'updates') {
    return { home: false, tab: null, kwSlug: null, articleId: null, updates: true,
             updCat: parts[1] || null, updCompany: parts[2] || null };
  }
  return { home: true, tab: null, kwSlug: null, articleId: null };
}
function articlePath(id) {
  return `/articles/${encodeURIComponent(id)}/`;
}
function routePath(home, tab, keyword) {
  if (home) return '/';
  return keyword ? `/topics/${tab}/${encodeURIComponent(kwSlug(keyword))}/` : `/topics/${tab}/`;
}
const INITIAL_ROUTE = parseRoute(window.location.pathname);

/* ---------- app install (PWA) ---------- */
// 안드로이드·데스크톱 크롬: 브라우저가 주는 설치 이벤트를 받아 헤더의 "앱 설치" 버튼으로 연다.
// 아이폰·아이패드 사파리: 설치 이벤트가 없어서 "공유 → 홈 화면에 추가" 안내를 한 번 보여 준다.
function isStandalone() {
  return (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) || window.navigator.standalone === true;
}
function useInstallPrompt() {
  const [evt, setEvt] = useState(null);
  useEffect(() => {
    const onPrompt = e => { e.preventDefault(); setEvt(e); };
    const onInstalled = () => setEvt(null);
    window.addEventListener('beforeinstallprompt', onPrompt);
    window.addEventListener('appinstalled', onInstalled);
    return () => {
      window.removeEventListener('beforeinstallprompt', onPrompt);
      window.removeEventListener('appinstalled', onInstalled);
    };
  }, []);
  const install = evt ? () => { evt.prompt(); evt.userChoice.finally(() => setEvt(null)); } : null;
  return install;
}
function IosInstallHint() {
  const isIos = /iphone|ipad|ipod/i.test(navigator.userAgent) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  const [show, setShow] = useState(() => {
    try { return isIos && !isStandalone() && !localStorage.getItem('aiad:ios-hint-done'); } catch { return false; }
  });
  if (!show) return null;
  const close = () => { try { localStorage.setItem('aiad:ios-hint-done', '1'); } catch {} setShow(false); };
  return (
    <div className="install-hint" role="dialog" aria-label="홈 화면에 추가">
      <span>홈 화면에 추가하면 앱처럼 쓸 수 있어요 — 사파리의 <b>공유</b> 버튼 → <b>홈 화면에 추가</b></span>
      <button type="button" onClick={close} aria-label="닫기">✕</button>
    </div>
  );
}

/* ---------- date helpers ---------- */
const TODAY = (() => { const d = new Date(); d.setHours(0, 0, 0, 0); return d; })();
const KOR_DAY = ['일','월','화','수','목','금','토'];

function parseDate(s) {
  if (!s) return new Date(0);
  const [y, m, d] = s.split(/[-./]/).map(Number);
  return new Date(y, (m || 1) - 1, d || 1);
}
function daysAgo(iso) {
  const d = parseDate(iso);
  return Math.round((TODAY - d) / 86400000);
}
function fmtKoreanDate(iso) {
  const d = parseDate(iso);
  return `${d.getMonth() + 1}월 ${d.getDate()}일 ${KOR_DAY[d.getDay()]}요일`;
}
function dateLabel(iso) {
  const ago = daysAgo(iso);
  if (ago === 0) return { main: '오늘', sub: fmtKoreanDate(iso), pin: 'TODAY' };
  if (ago === 1) return { main: '어제', sub: fmtKoreanDate(iso), pin: null };
  return { main: fmtKoreanDate(iso), sub: null, pin: null };
}
function relativeKor(iso) {
  const ago = daysAgo(iso);
  if (ago === 0) return '오늘';
  if (ago === 1) return '어제';
  if (ago < 7) return `${ago}일 전`;
  return `${Math.floor(ago / 7)}주 전`;
}

/* ---------- helpers ---------- */
function highlight(text, q) {
  if (!q) return text;
  const parts = text.split(new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'));
  return parts.map((p, i) =>
    p.toLowerCase() === q.toLowerCase() ? <mark key={i}>{p}</mark> : <React.Fragment key={i}>{p}</React.Fragment>
  );
}

function tabCounts(articles) {
  const counts = {};
  TABS.forEach(t => counts[t.id] = 0);
  articles.forEach(a => { counts[a.tab] = (counts[a.tab] || 0) + 1; });
  return counts;
}
// 서브 카테고리: data/keywords.json의 탭별 목록 (목록 순서) 중
// 탭 안에서 MIN_SUBCAT_ARTICLES개 이상 기사에 붙은 키워드만 (5개 이하는 너무 지엽적이라 숨김)
const MIN_SUBCAT_ARTICLES = 6;
function subCategoriesFor(keywordTabs, articles, tabId) {
  const counts = new Map();
  articles.forEach(a => {
    if (a.tab !== tabId) return;
    (a.keywords || []).forEach(k => counts.set(k, (counts.get(k) || 0) + 1));
  });
  return ((keywordTabs && keywordTabs[tabId]) || [])
    .map(k => ({ label: k.label, count: counts.get(k.label) || 0 }))
    .filter(k => k.count >= MIN_SUBCAT_ARTICLES);
}

function isArticleNew(a) {
  return daysAgo(a.publishedAt) <= 2;      // auto: today, yesterday, 2 days ago
}
function tabHasNew(tabId, articles) {
  return articles.some(a => a.tab === tabId && isArticleNew(a));
}

/* ---------- thumb ---------- */
function Thumb({ hue, image, alt, children }) {
  const [failed, setFailed] = useState(false);
  const bg = `linear-gradient(135deg, oklch(0.88 0.06 ${hue}) 0%, oklch(0.78 0.09 ${(hue + 40) % 360}) 100%)`;
  const showImg = image && !failed;
  return (
    <div className="thumb">
      {showImg ? (
        <img
          className="thumb-img"
          src={image}
          alt={alt || ''}
          loading="lazy"
          onError={() => setFailed(true)}
        />
      ) : (
        <div className="thumb-bg" style={{ background: bg }} />
      )}
      {children}
    </div>
  );
}

/* ---------- card ---------- */
function ArticleCard({ article, onOpen, query, variant }) {
  const cls = `card${variant ? ' ' + variant : ''}`;
  return (
    <button className={cls} onClick={() => onOpen(article)}>
      <Thumb hue={article.hue} image={article.image} alt={article.headline} />
      <div className="card-body">
        <h3 className="card-headline">{highlight(article.headline, query)}</h3>
        <p className="card-summary">{highlight(article.summary, query)}</p>
        <div className="card-foot">
          <span className="source">{article.source}</span>
          <span>{article.publishedAt}</span>
        </div>
      </div>
    </button>
  );
}

/* ---------- date section ---------- */
function DateSection({ iso, items, onOpen, query, isToday }) {
  const lbl = dateLabel(iso);
  return (
    <section className="date-section">
      <div className="date-header">
        <div className="date-label">
          {lbl.pin && <span className="pin">{lbl.pin}</span>}
          <span>{lbl.main}</span>
          {lbl.sub && <span className="iso">· {lbl.sub}</span>}
        </div>
        <div className="date-count">{items.length}개 기사</div>
      </div>
      {isToday && items.length > 1 ? (
        <div className="grid today-grid">
          <ArticleCard variant="feature" article={items[0]} onOpen={onOpen} query={query} />
          {items.slice(1, 3).map(a => (
            <ArticleCard key={a.id} article={a} onOpen={onOpen} query={query} />
          ))}
          {items.length > 3 && (
            <div style={{ gridColumn: '1 / -1' }}>
              <div className="grid">
                {items.slice(3).map(a => (
                  <ArticleCard key={a.id} article={a} onOpen={onOpen} query={query} />
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="grid">
          {items.map(a => (
            <ArticleCard key={a.id} article={a} onOpen={onOpen} query={query} />
          ))}
        </div>
      )}
    </section>
  );
}

/* ---------- header ---------- */
function Header({ query, onQuery, theme, onToggleTheme, onShowHome, onMenu }) {
  const inputRef = useRef(null);
  const install = useInstallPrompt();
  // 좁은 화면에선 검색창을 숨겨 두고, 돋보기 버튼을 누르면 헤더 아래 한 줄로 펼친다
  const [searchOpen, setSearchOpen] = useState(false);
  const openSearch = () => { setSearchOpen(true); setTimeout(() => inputRef.current && inputRef.current.focus(), 0); };
  const closeSearch = () => { setSearchOpen(false); onQuery(''); };
  useEffect(() => {
    const onKey = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        inputRef.current && inputRef.current.focus();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  return (
    <header className={`site-header ${searchOpen ? 'searching' : ''}`}>
      <div className="header-inner">
        <button type="button" className="menu-btn" aria-label="메뉴" onClick={onMenu}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M4 7h16M4 12h16M4 17h16" /></svg>
        </button>
        <div className="brand" onClick={() => { onQuery(''); onShowHome && onShowHome(); window.scrollTo({ top: 0, behavior: 'smooth' }); }}>
          <span className="brand-name">AI Art Daily</span>
          <small>한국어 큐레이션</small>
        </div>
        <div className="header-actions">
          <label className="search">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="7" />
              <path d="m20 20-3.5-3.5" />
            </svg>
            <input
              ref={inputRef}
              value={query}
              onChange={e => onQuery(e.target.value)}
              onKeyDown={e => { if (e.key === 'Escape' && searchOpen) closeSearch(); }}
              type="search"
              enterKeyHint="search"
              placeholder="기사 · 출처 · 키워드 검색"
            />
            {!query && <span className="kbd">⌘ K</span>}
          </label>
          <button type="button" className="icon-btn search-toggle"
            aria-label={searchOpen ? '검색 닫기' : '검색'} aria-expanded={searchOpen}
            onClick={searchOpen ? closeSearch : openSearch}>
            {searchOpen ? (
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 6l12 12M18 6L6 18" /></svg>
            ) : (
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></svg>
            )}
          </button>
          {install && (
            <button className="icon-btn" title="앱 설치" aria-label="앱 설치" onClick={install}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 3v12" /><path d="m7 10 5 5 5-5" /><path d="M5 21h14" />
              </svg>
            </button>
          )}
          <button className="icon-btn" title={theme === 'dark' ? '라이트 모드' : '다크 모드'} onClick={onToggleTheme}>
            {theme === 'dark' ? (
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
              </svg>
            ) : (
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                <path d="M20 14a8 8 0 1 1-10-10 7 7 0 0 0 10 10z" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}

/* ---------- tabs ---------- */
function Tabs({ active, onChange, articles, viewHome, subcats, keyword, onKeyword }) {
  const counts = useMemo(() => tabCounts(articles), [articles]);
  return (
    <nav className="tabs-wrap">
      <div className="tabs-inner">
        <div className="tabs-meta">
          {`카테고리 · ${TABS.length}개 채널`}
        </div>
          <div className="tabs">
            {TABS.map(t => (
              <button
                key={t.id}
                className={`tab ${t.id === active && !viewHome ? 'active' : ''}`}
                onClick={() => onChange(t.id)}
              >
                {t.label}
                <span className="count">{counts[t.id] || 0}</span>
                {tabHasNew(t.id, articles) && t.id !== active && <span className="new-dot" />}
              </button>
            ))}
          </div>
        {subcats && (
          <SubCategoryBar items={subcats} total={counts[active] || 0} active={keyword} onChange={onKeyword} />
        )}
      </div>
    </nav>
  );
}

/* ---------- sub-categories ---------- */
function SubCategoryBar({ items, total, active, onChange }) {
  if (!items.length) return null;
  return (
    <div className="subcats" role="tablist" aria-label="서브 카테고리">
      <button
        role="tab"
        aria-selected={!active}
        className={`chip subcat ${!active ? 'active' : ''}`}
        onClick={() => onChange(null)}
      >
        전체 <span className="subcat-count">{total}</span>
      </button>
      {items.map(it => (
        <button
          key={it.label}
          role="tab"
          aria-selected={active === it.label}
          className={`chip subcat ${active === it.label ? 'active' : ''}`}
          onClick={() => onChange(active === it.label ? null : it.label)}
        >
          {it.label} <span className="subcat-count">{it.count}</span>
        </button>
      ))}
    </div>
  );
}

/* ---------- feed meta ---------- */
function FeedMeta({ activeTab, count, query, keyword }) {
  const today = `${TODAY.getFullYear()}년 ${TODAY.getMonth() + 1}월 ${TODAY.getDate()}일 (${KOR_DAY[TODAY.getDay()]})`;
  let title, sub;
  if (query) {
    title = `\u201c${query}\u201d 검색 결과`;
    sub = `${count}개 기사`;
  } else {
    const t = TABS.find(t => t.id === activeTab);
    title = t.label;
    sub = keyword ? `${today} · ${keyword} · ${count}개 기사` : `${today} · ${count}개 기사`;
  }
  const activeDesc = !query
    ? (TABS.find(t => t.id === activeTab) || {}).desc
    : null;
  return (
    <div className="feed-meta">
      <div>
        <h1 className="feed-title">{title}</h1>
        <div className="feed-sub">{sub}</div>
        {activeDesc && <p className="feed-desc">{activeDesc}</p>}
      </div>
      {!query && (
        <div className="feed-toolbar"></div>
      )}
    </div>
  );
}

/* ---------- modal ---------- */
function ArticleModal({ article, onClose, onOpen, allArticles, onSelectKeyword }) {
  const bodyRef = useRef(null);
  const [progress, setProgress] = useState(0);
  const [copied, setCopied] = useState(false);

  const copyLink = () => {
    // 공유용 주소는 기사별 정적 페이지 (배포 사이트에서 scripts/build_site.py가 만든다 — 링크 미리보기·검색 노출용)
    const link = window.location.origin + articlePath(article.id);   // 열면 카드 화면 위에 이 기사 창이 뜬다
    const done = () => { setCopied(true); setTimeout(() => setCopied(false), 1600); };
    const fallback = () => {
      try {
        const ta = document.createElement('textarea');
        ta.value = link;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.focus();
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        done();
      } catch (e) { /* no-op */ }
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(link).then(done, fallback);
    } else {
      fallback();
    }
  };

  useEffect(() => {
    const onKey = e => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    document.body.classList.add('no-scroll');
    return () => {
      window.removeEventListener('keydown', onKey);
      document.body.classList.remove('no-scroll');
    };
  }, [onClose]);

  const onScroll = () => {
    const el = bodyRef.current;
    if (!el) return;
    const max = el.scrollHeight - el.clientHeight;
    setProgress(max > 0 ? Math.min(100, (el.scrollTop / max) * 100) : 0);
  };

  const related = allArticles
    .filter(a => a.tab === article.tab && a.id !== article.id)
    .slice(0, 3);

  const heroBg = `linear-gradient(135deg, oklch(0.85 0.08 ${article.hue}) 0%, oklch(0.7 0.12 ${(article.hue + 40) % 360}) 100%)`;
  const [heroFailed, setHeroFailed] = useState(false);
  useEffect(() => { setHeroFailed(false); }, [article && article.id]);

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-progress" style={{ width: `${progress}%` }} />
        <button className="modal-close" onClick={onClose} aria-label="닫기">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>

        <div className="modal-hero">
          {article.image && !heroFailed ? (
            <img
              className="thumb-img"
              src={article.image}
              alt={article.headline}
              onError={() => setHeroFailed(true)}
            />
          ) : (
            <div className="thumb-bg" style={{ background: heroBg }} />
          )}
        </div>

        <div className="modal-body" ref={bodyRef} onScroll={onScroll}>
          <h1 className="modal-headline">{article.headline}</h1>
          <div className="modal-meta">
            <span>{article.source}</span>
            <span style={{ color: 'var(--muted-2)' }}>·</span>
            <span>{article.publishedAt}</span>
            <a href={article.url} target="_blank" rel="noopener noreferrer">
              원문 보기
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M7 17 17 7" /><path d="M8 7h9v9" />
              </svg>
            </a>
            <button type="button" className={`modal-copy ${copied ? 'copied' : ''}`} onClick={copyLink}>
              {copied ? (
                <>
                  복사됨
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M20 6 9 17l-5-5" />
                  </svg>
                </>
              ) : (
                <>
                  링크 복사
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="9" y="9" width="11" height="11" rx="2" /><path d="M5 15V5a2 2 0 0 1 2-2h10" />
                  </svg>
                </>
              )}
            </button>
            {Array.isArray(article.urls) && article.urls.filter(u => u && u.href).map((u, i) => (
              <a key={i} href={u.href} target="_blank" rel="noopener noreferrer">
                {u.label || '관련 링크'}
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M7 17 17 7" /><path d="M8 7h9v9" />
                </svg>
              </a>
            ))}
          </div>
          {(() => {
            const kws = article.keywords || [];
            return kws.length > 0 && (
              <div className="modal-keywords">
                {kws.map(k => (
                  <button key={k} type="button" className="modal-keyword" onClick={() => onSelectKeyword(article.tab, k)}>
                    #{k}
                  </button>
                ))}
              </div>
            );
          })()}
          <div className="modal-article">
            <p style={{ fontSize: 18, lineHeight: 1.7, color: 'var(--ink)' }}>{article.summary}</p>
            <div dangerouslySetInnerHTML={{ __html: article.body || '' }} />
          </div>

          {related.length > 0 && (
            <div className="modal-foot-related">
              <h4>같은 주제의 다른 기사</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {related.map(r => (
                  <button
                    key={r.id}
                    onClick={() => onOpen(r)}
                    style={{
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      gap: 16, padding: '12px 0',
                      background: 'transparent', border: 0, borderTop: '1px solid var(--hairline)',
                      cursor: 'pointer', textAlign: 'left', fontFamily: 'inherit', color: 'inherit',
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--ink)', lineHeight: 1.4 }}>
                        {r.headline}
                      </div>
                      <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 4 }}>
                        {r.source} · {r.publishedAt}
                      </div>
                    </div>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--muted)" strokeWidth="2">
                      <path d="M9 6l6 6-6 6" />
                    </svg>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ---------- date grouped feed with pagination ---------- */
function DateGroupedFeed({ articles, onOpen, query, expandAll }) {
  const [showAllState, setShowAll] = useState(false);
  const showAll = showAllState || expandAll;   // 서브 카테고리 선택 시에는 지난 기사까지 모두 표시

  // group by publishedAt
  const groups = useMemo(() => {
    const map = new Map();
    articles.forEach(a => {
      const k = a.publishedAt || '0000.00.00';
      if (!map.has(k)) map.set(k, []);
      map.get(k).push(a);
    });
    return [...map.entries()]
      .sort(([a], [b]) => b.localeCompare(a))
      .map(([iso, items]) => ({ iso, items }));
  }, [articles]);

  const recent = groups.filter(g => daysAgo(g.iso) <= 6);
  const older = groups.filter(g => daysAgo(g.iso) > 6);
  const olderCount = older.reduce((n, g) => n + g.items.length, 0);

  const visibleGroups = showAll ? groups : recent;

  return (
    <>
      {visibleGroups.map(g => (
        <DateSection
          key={g.iso}
          iso={g.iso}
          items={g.items}
          onOpen={onOpen}
          query={query}
          isToday={daysAgo(g.iso) === 0}
        />
      ))}
      {!showAll && older.length > 0 && (
        <div className="show-older">
          <button onClick={() => setShowAll(true)}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 5v14M5 12h14" />
            </svg>
            지난 기사 더 보기
            <span className="older-meta">+{olderCount}건 · {older.length}일치</span>
          </button>
        </div>
      )}
    </>
  );
}

/* ---------- empty + skeleton ---------- */
function EmptyState({ message, sub }) {
  return (
    <div className="empty">
      <div className="empty-art">∅</div>
      <h3>{message || '아직 새로운 소식이 없어요'}</h3>
      <p>{sub || '이 카테고리에 새 기사가 도착하면\u00a0바로 알려드릴게요.'}</p>
    </div>
  );
}
function SkeletonCard() {
  return (
    <div className="card skeleton" style={{ cursor: 'default' }}>
      <div className="thumb"><div className="thumb-bg" /></div>
      <div className="card-body">
        <div className="skel-line short" style={{ height: 10 }} />
        <div className="skel-line" style={{ height: 18, width: '92%' }} />
        <div className="skel-line" style={{ height: 18, width: '70%' }} />
        <div style={{ marginTop: 12 }}>
          <div className="skel-line" style={{ height: 10, width: '40%' }} />
        </div>
      </div>
    </div>
  );
}

/* ---------- home view ---------- */
function HomeView({ onSelectTab, onOpenArticle, articles }) {
  const today = `${TODAY.getFullYear()}년 ${TODAY.getMonth() + 1}월 ${TODAY.getDate()}일 (${KOR_DAY[TODAY.getDay()]})`;
  const latest = useMemo(() => {
    return [...articles]
      .sort((a, b) => (b.publishedAt || '').localeCompare(a.publishedAt || ''))
      .slice(0, 10);
  }, [articles]);
  const tickerItems = useMemo(() => [...latest, ...latest], [latest]);
  const tabLabelOf = (id) => (TABS.find(t => t.id === id) || {}).label || '';
  return (
    <div className="home">
      <aside className="home-hero">
        <div className="home-eyebrow">
          <span className="home-eyebrow-line" aria-hidden="true" />
          <span className="home-eyebrow-text">AI ART DAILY</span>
          <span className="home-eyebrow-date">{today}</span>
        </div>
        <h1 className="home-title">아트 제작자를 위한<br/>AI 뉴스 큐레이션</h1>
        <p className="home-lede">
          매일 쏟아지는 AI 뉴스 중 게임·아트 제작 현장에 실제로 영향을 주는 소식만 골라
          한국어로 정리합니다.
        </p>
      </aside>

      <section className="home-main">
        <div className="home-section-head">
          <span className="home-section-eyebrow">
            <span className="home-section-kind">CHANNELS</span>
            <span className="home-section-rule" aria-hidden="true" />
            <span className="home-section-count">{String(TABS.length).padStart(2, '0')}</span>
          </span>
          <h2 className="home-section-title">카테고리 채널</h2>
          <div className="home-section-sub">관심 분야를 골라 오늘의 큐레이션을 확인하세요</div>
        </div>
        <ul className="home-grid">
          {TABS.map((t, i) => (
            <li key={t.id} className="home-card-wrap">
              <button className="home-card" onClick={() => onSelectTab(t.id)}>
                <div className="home-card-num">{String(i + 1).padStart(2, '0')}</div>
                <div className="home-card-body">
                  <div className="home-card-title">{t.label}</div>
                  <p className="home-card-desc">{t.desc}</p>
                </div>
              </button>
            </li>
          ))}
        </ul>
        <div className="home-grid-note">
          <span className="home-grid-note-dot" aria-hidden="true" />
          <div className="home-grid-note-body">
            <strong>카테고리 확장 예정</strong>
            <span>새로운 아이디어는 언제든 환영입니다.</span>
          </div>
        </div>
      </section>

      <section className="home-ticker" aria-label="최신 뉴스">
        <div className="home-ticker-head">
          <span className="home-ticker-eyebrow">
            <span className="home-ticker-pulse" aria-hidden="true" />
            LATEST
          </span>
          <span className="home-ticker-title">가장 최근 큐레이션된 10개 기사</span>
        </div>
        <div className="home-ticker-track-wrap">
          <ul className="home-ticker-track">
            {tickerItems.map((a, i) => (
              <li key={`${a.id}-${i}`} className="home-ticker-card">
                <button className="home-ticker-btn" onClick={() => onOpenArticle(a)}>
                  <span className="home-ticker-cat">{tabLabelOf(a.tab)}</span>
                  <span className="home-ticker-headline">{a.headline}</span>
                  <span className="home-ticker-meta">
                    <span className="home-ticker-source">{a.source}</span>
                    <span className="home-ticker-dot" aria-hidden="true" />
                    <span className="home-ticker-date">{a.publishedAt}</span>
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  );
}

/* ---------- sidebar (대분류: 뉴스 · 업데이트) ---------- */
// 좁은 화면의 서랍을 손가락으로 끌어 여닫는다.
// 닫혀 있을 땐 화면 아무 곳에서나 오른쪽으로, 열려 있을 땐 서랍이나 바깥을 왼쪽으로 스와이프한다.
// 가로로 넘기는 영역(탭·칩 줄, 하단 띠)이나 기사 창 위에서는 그 영역의 스와이프가 먼저다.
// 끄는 동안 서랍이 손가락을 따라오고, 놓았을 때 절반 넘게 끌었거나 빠르게 튕기면 여닫힌다.
const DRAWER_EDGE = 28;   // 이 안쪽에서 시작하면 가로 스크롤 영역 위여도 서랍을 연다 (px)
function inHorizontalScroller(el) {
  for (; el && el !== document.body; el = el.parentElement) {
    if (el.classList.contains('home-ticker') || el.classList.contains('modal-backdrop')) return true;
    const ox = getComputedStyle(el).overflowX;
    if ((ox === 'auto' || ox === 'scroll') && el.scrollWidth > el.clientWidth) return true;
  }
  return false;
}
function useDrawerSwipe(asideRef, backdropRef, open, onOpen, onClose) {
  const st = useRef({ open, onOpen, onClose });
  st.current.open = open; st.current.onOpen = onOpen; st.current.onClose = onClose;
  useEffect(() => {
    const mq = window.matchMedia('(max-width: 1024px)');
    let g = null;   // 진행 중인 제스처
    const paint = (x, w) => {
      const a = asideRef.current, b = backdropRef.current;
      a.style.transition = 'none'; a.style.transform = `translateX(${x}px)`;
      b.style.transition = 'none'; b.style.opacity = String(1 + x / w);
    };
    const reset = () => {
      for (const el of [asideRef.current, backdropRef.current]) {
        if (el) { el.style.transition = ''; el.style.transform = ''; el.style.opacity = ''; }
      }
    };
    const onStart = e => {
      g = null;
      if (!mq.matches || e.touches.length !== 1 || !asideRef.current) return;
      const t = e.touches[0];
      const wasOpen = st.current.open;
      if (wasOpen ? !(asideRef.current.contains(e.target) || backdropRef.current.contains(e.target)) : (t.clientX > DRAWER_EDGE && inHorizontalScroller(e.target))) return;
      g = { wasOpen, x0: t.clientX, y0: t.clientY, t0: Date.now(), drag: false, x: 0, w: asideRef.current.offsetWidth };
    };
    const onMove = e => {
      if (!g) return;
      const t = e.touches[0], dx = t.clientX - g.x0, dy = t.clientY - g.y0;
      if (!g.drag) {
        if (Math.abs(dx) < 8 && Math.abs(dy) < 8) return;
        // 세로로 움직이거나 반대 방향이면 평소 스크롤로 둔다
        if (Math.abs(dx) <= Math.abs(dy) || (g.wasOpen ? dx > 0 : dx < 0)) { g = null; return; }
        g.drag = true;
      }
      e.preventDefault();
      g.dx = dx;
      g.x = Math.max(-g.w, Math.min(0, (g.wasOpen ? 0 : -g.w) + dx));
      paint(g.x, g.w);
    };
    const onEnd = () => {
      if (!g || !g.drag) { g = null; return; }
      const v = g.dx / Math.max(1, Date.now() - g.t0);   // px/ms
      const next = v > 0.3 ? true : v < -0.3 ? false : (1 + g.x / g.w) > 0.5;
      g = null;
      reset();
      if (next !== st.current.open) (next ? st.current.onOpen : st.current.onClose)();
    };
    document.addEventListener('touchstart', onStart, { passive: true });
    document.addEventListener('touchmove', onMove, { passive: false });
    document.addEventListener('touchend', onEnd);
    document.addEventListener('touchcancel', onEnd);
    return () => {
      document.removeEventListener('touchstart', onStart);
      document.removeEventListener('touchmove', onMove);
      document.removeEventListener('touchend', onEnd);
      document.removeEventListener('touchcancel', onEnd);
    };
  }, []);
}

// 뉴스 › 게임 제작 속 AI / AI 도입 뉴스 / 아트 전반 AI 뉴스 (지금 피드),  업데이트 (AI 서비스 회사 공식 업데이트)
// 서브 섹션(뉴스의 탭, 업데이트의 분야)을 누르면 그 아래 서브 카테고리(키워드, 회사)가 펼쳐진다.
// 펼쳐지는 건 지금 선택된 서브 섹션 하나뿐이라, 다른 서브 섹션을 고르면 이전 것은 접힌다.
// 이미 펼쳐진 메뉴(서브 섹션, 뉴스·업데이트)를 다시 누르면 접힌다.
function Sidebar({ section, viewHome, activeTab, open, onOpen, onClose, onNewsHome, onTab, onUpdates, counts,
                   subcats, keyword, onKeyword, updCat, onUpdCat, updCompany, onUpdCompany }) {
  const [newsOpen, setNewsOpen] = useState(true);
  const [updOpen, setUpdOpen] = useState(true);
  const newsActive = section === 'news';
  const asideRef = useRef(null), backdropRef = useRef(null);
  useDrawerSwipe(asideRef, backdropRef, open, onOpen, onClose);
  const current = newsActive ? (viewHome ? null : `news:${activeTab}`) : (updCat ? `upd:${updCat}` : null);
  const [folded, setFolded] = useState(null);       // 다시 눌러 접은 서브 섹션
  useEffect(() => { setFolded(null); }, [current]);
  const isOpen = key => current === key && folded !== key;
  const toggle = (key, go) => { if (isOpen(key)) setFolded(key); else { setFolded(null); go(); } };
  return (
    <>
      <div ref={backdropRef} className={`sidebar-backdrop ${open ? 'open' : ''}`} onClick={onClose} />
      <aside ref={asideRef} className={`sidebar ${open ? 'open' : ''}`} aria-label="카테고리">
        <div className="side-drawer-head">
          <span className="brand-name">AI Art Daily</span>
          <button type="button" className="side-close" aria-label="메뉴 닫기" onClick={onClose}>✕</button>
        </div>
        <nav className="side-nav">
          <div className="side-group">
            <div className={`side-group-head ${newsActive && viewHome ? 'active' : ''}`}>
              <button type="button" className="side-group-link" onClick={() => {
                if (newsActive && viewHome && newsOpen) setNewsOpen(false);
                else { setNewsOpen(true); onNewsHome(); }
              }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M4 5h13v14H6a2 2 0 0 1-2-2z" /><path d="M17 9h3v8a2 2 0 0 1-2 2" /><path d="M8 9h5M8 13h5" />
                </svg>
                <span>뉴스</span>
              </button>
              <button type="button" className="side-caret-btn" aria-label={newsOpen ? '접기' : '펼치기'} aria-expanded={newsOpen} onClick={() => setNewsOpen(o => !o)}>
                <svg className={`side-caret ${newsOpen ? 'open' : ''}`} width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2"><path d="m6 9 6 6 6-6" /></svg>
              </button>
            </div>
            {newsOpen && (
              <ul className="side-list">
                {TABS.map(t => {
                  const here = newsActive && !viewHome && activeTab === t.id;
                  const opened = isOpen(`news:${t.id}`);
                  return (
                    <li key={t.id}>
                      <button type="button"
                        className={`side-item ${here && !keyword ? 'active' : ''} ${opened ? 'expanded' : ''}`}
                        aria-expanded={opened}
                        onClick={() => toggle(`news:${t.id}`, () => onTab(t.id))}>
                        <span>{t.label}</span>
                        {counts[t.id] > 0 && <span className="side-count">{counts[t.id]}</span>}
                      </button>
                      {opened && subcats.length > 0 && (
                        <ul className="side-sublist">
                          {subcats.map(c => (
                            <li key={c.label}>
                              <button type="button" className={`side-subitem ${keyword === c.label ? 'active' : ''}`}
                                onClick={() => onKeyword(keyword === c.label ? null : c.label)}>
                                <span>{c.label}</span>
                                <span className="side-count">{c.count}</span>
                              </button>
                            </li>
                          ))}
                        </ul>
                      )}
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
          <div className="side-group">
            <div className={`side-group-head ${section === 'updates' && !updCat ? 'active' : ''}`}>
              <button type="button" className="side-group-link" onClick={() => {
                if (section === 'updates' && !updCat && updOpen) setUpdOpen(false);
                else { setUpdOpen(true); onUpdates(); }
              }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1" />
                </svg>
                <span>업데이트</span>
                <span className="side-badge">NEW</span>
              </button>
              <button type="button" className="side-caret-btn" aria-label={updOpen ? '접기' : '펼치기'} aria-expanded={updOpen} onClick={() => setUpdOpen(o => !o)}>
                <svg className={`side-caret ${updOpen ? 'open' : ''}`} width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2"><path d="m6 9 6 6 6-6" /></svg>
              </button>
            </div>
            {updOpen && (
              <ul className="side-list">
                {UPDATE_CATS.map(c => {
                  const here = section === 'updates' && updCat === c.slug;
                  const opened = isOpen(`upd:${c.slug}`);
                  return (
                    <li key={c.slug}>
                      <button type="button" className={`side-item ${here && !updCompany ? 'active' : ''} ${opened ? 'expanded' : ''}`}
                        aria-expanded={opened} onClick={() => toggle(`upd:${c.slug}`, () => onUpdCat(c.slug))}>
                        <span>{c.label}</span>
                        <span className="side-count">{UPDATE_COMPANIES.filter(x => x.catSlug === c.slug).length}</span>
                      </button>
                      {opened && (
                        <ul className="side-sublist">
                          {UPDATE_COMPANIES.filter(x => x.catSlug === c.slug).map(co => (
                            <li key={co.slug}>
                              <button type="button" className={`side-subitem ${updCompany === co.slug ? 'active' : ''}`}
                                onClick={() => onUpdCompany(c.slug, co.slug)}>
                                <span>{co.name}</span>
                              </button>
                            </li>
                          ))}
                        </ul>
                      )}
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </nav>
      </aside>
    </>
  );
}

/* ---------- 업데이트 (아트 관련 AI 서비스 회사의 공식 업데이트) ---------- */
// 구조: 분야(위쪽 탭·사이드바) › 회사(칩) › 그 회사의 업데이트 (최신순)
// 주소: /updates/  /updates/<분야>/  /updates/<분야>/<회사>/
const UPDATE_CAT_SLUG = {
  '이미지': 'image', '영상': 'video', '3D': '3d', '게임 에셋': 'game-assets',
  '모션': 'motion', '음악·음성': 'audio', '도구': 'tools',
};
const UPDATE_CATS = [...new Set(UPDATE_SOURCES.map(s => s.category))]
  .map(label => ({ label, slug: UPDATE_CAT_SLUG[label] || kwSlug(label) }));
const UPDATE_COMPANIES = UPDATE_SOURCES.map(s => ({
  ...s, slug: kwSlug(s.name), catSlug: UPDATE_CAT_SLUG[s.category] || kwSlug(s.category),
}));
function updatesPath(cat, company) {
  if (cat && company) return `/updates/${cat}/${company}/`;
  if (cat) return `/updates/${cat}/`;
  return '/updates/';
}

// 아직 공지 수집이 연결되지 않아, 화면 흐름을 보기 위한 예시 항목을 회사마다 만든다.
// 실제 데이터가 붙으면 같은 형식({ company, date, title, summary, url, kind })으로 바뀐다.
const SAMPLE_KINDS = {
  'image':       [['모델', '새 이미지 모델 버전 공개'], ['기능', '편집·인페인팅 기능 개선'], ['요금', '요금제와 사용량 정책 변경'], ['API', 'API에 새 해상도 옵션 추가']],
  'video':       [['모델', '새 영상 생성 모델 공개'], ['기능', '영상 길이 연장과 카메라 제어 추가'], ['기능', '오디오 동시 생성 지원'], ['API', 'API 요청 한도 상향']],
  '3d':          [['모델', '3D 생성 모델 업데이트'], ['기능', '자동 리깅·텍스처 기능 추가'], ['연동', '게임 엔진 플러그인 업데이트'], ['기능', '내보내기 형식 추가']],
  'game-assets': [['기능', '게임 에셋 스타일 학습 기능 개선'], ['연동', '엔진 연동 워크플로우 추가'], ['모델', '새 생성 모델 지원'], ['기능', '팀 협업 기능 추가']],
  'motion':      [['기능', '모션 캡처 정확도 개선'], ['연동', 'DCC 툴 연동 업데이트'], ['기능', '얼굴·손 추적 기능 추가'], ['요금', '라이선스 정책 변경']],
  'audio':       [['모델', '새 음성·음악 모델 공개'], ['기능', '언어·보이스 추가'], ['API', 'API 지연 시간 개선'], ['기능', '편집 기능 추가']],
  'tools':       [['기능', '새 버전 릴리스'], ['연동', '새 모델·노드 지원 추가'], ['기능', '성능 개선과 버그 수정'], ['API', '개발자 도구 업데이트']],
};
function sampleUpdatesFor(c) {
  const kinds = SAMPLE_KINDS[c.catSlug] || SAMPLE_KINDS.tools;
  const seed = [...c.slug].reduce((n, ch) => n + ch.charCodeAt(0), 0);
  return kinds.map(([kind, title], i) => {
    const d = new Date(TODAY); d.setDate(d.getDate() - ((seed % 5) + i * (6 + (seed % 7))));
    return {
      id: `${c.slug}-${i}`, company: c, kind, sample: true,
      date: `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`,
      title: `${c.name} — ${title}`,
      summary: '예시 항목이에요. 공지 수집이 연결되면 회사의 공식 업데이트를 한국어로 요약해 이 자리에 보여 드려요.',
      url: c.url,
    };
  });
}
const ALL_UPDATES = UPDATE_COMPANIES.flatMap(sampleUpdatesFor)
  .sort((a, b) => b.date.localeCompare(a.date) || a.company.name.localeCompare(b.company.name));

function UpdatesNav({ cat, company, onCat, onCompany }) {
  const companies = cat ? UPDATE_COMPANIES.filter(c => c.catSlug === cat) : [];
  return (
    <nav className="tabs-wrap">
      <div className="tabs-inner">
        <div className="tabs-meta">업데이트 · {UPDATE_CATS.length}개 분야 · {UPDATE_COMPANIES.length}곳</div>
        <div className="tabs">
          <button className={`tab ${!cat ? 'active' : ''}`} onClick={() => onCat(null)}>
            전체 <span className="count">{UPDATE_COMPANIES.length}</span>
          </button>
          {UPDATE_CATS.map(c => (
            <button key={c.slug} className={`tab ${cat === c.slug ? 'active' : ''}`} onClick={() => onCat(c.slug)}>
              {c.label} <span className="count">{UPDATE_COMPANIES.filter(x => x.catSlug === c.slug).length}</span>
            </button>
          ))}
        </div>
        {cat && (
          <div className="subcats" role="tablist" aria-label="회사">
            <button className={`chip subcat ${!company ? 'active' : ''}`} onClick={() => onCompany(null)}>전체</button>
            {companies.map(c => (
              <button key={c.slug} className={`chip subcat ${company === c.slug ? 'active' : ''}`} onClick={() => onCompany(c.slug)}>
                {c.name}
              </button>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
}

function UpdateRow({ u, showCompany, onCompany }) {
  return (
    <li className="update-row">
      <div className="update-date">{u.date}</div>
      <div className="update-main">
        <div className="update-head">
          {showCompany && (
            <button type="button" className="update-company" onClick={() => onCompany(u.company)}>{u.company.name}</button>
          )}
          <span className="update-cat">{u.kind}</span>
          {u.sample && <span className="update-sample">예시</span>}
        </div>
        <h3 className="update-title">{u.title}</h3>
        <p className="update-summary">{u.summary}</p>
        <a className="update-link" href={u.url} target="_blank" rel="noopener noreferrer">공식 공지 보기 ↗</a>
      </div>
    </li>
  );
}

function UpdatesView({ cat, company, onCat, onCompany }) {
  const catObj = UPDATE_CATS.find(c => c.slug === cat) || null;
  const comp = UPDATE_COMPANIES.find(c => c.slug === company && c.catSlug === cat) || null;
  const items = ALL_UPDATES.filter(u => (!cat || u.company.catSlug === cat) && (!comp || u.company.slug === comp.slug));
  const title = comp ? comp.name : catObj ? catObj.label : '업데이트';
  const desc = comp
    ? `${comp.name}의 공식 업데이트를 최신순으로 모아 보여 드려요.`
    : catObj
      ? `${catObj.label} 분야 AI 서비스들의 공식 업데이트예요. 회사를 고르면 그 회사 소식만 볼 수 있어요.`
      : '아트 관련 AI 서비스 회사들의 공식 업데이트를 분야·회사별로 모아 보여 드려요.';
  return (
    <>
      <UpdatesNav cat={cat} company={comp ? comp.slug : null} onCat={onCat} onCompany={slug => onCompany(cat, slug)} />
      <div className="feed-meta">
        <div>
          <h1 className="feed-title">{title}</h1>
          <div className="feed-sub">
            {comp ? `${catObj.label} · 업데이트 ${items.length}건` : `업데이트 ${items.length}건 · 최신순`}
          </div>
          <p className="feed-desc">{desc}</p>
        </div>
        {comp && (
          <a className="chip update-official" href={comp.url} target="_blank" rel="noopener noreferrer">공식 업데이트 페이지 ↗</a>
        )}
      </div>
      <main className="feed">
        <div className="updates-notice">준비 중이에요 — 지금 보이는 업데이트는 화면 구성을 보기 위한 <b>예시</b>예요.</div>
        <ol className="updates-list">
          {items.map(u => (
            <UpdateRow key={u.id} u={u} showCompany={!comp} onCompany={c => onCompany(c.catSlug, c.slug)} />
          ))}
        </ol>
      </main>
    </>
  );
}

/* ---------- App ---------- */
function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem('aiad:theme') || 'light');
  const accent = '#c2410c';

  const [activeTab, setActiveTab] = useState(INITIAL_ROUTE.tab || 'games');
  const [viewHome, setViewHome] = useState(INITIAL_ROUTE.home);
  const [section, setSection] = useState(INITIAL_ROUTE.updates ? 'updates' : 'news');   // 사이드바: 'news' | 'updates'
  const [sideOpen, setSideOpen] = useState(false);    // 좁은 화면에서 사이드바 서랍 (✕나 바깥을 눌러야만 닫힌다)
  const [updCat, setUpdCat] = useState(INITIAL_ROUTE.updCat || null);          // 업데이트 › 분야 (slug)
  const [updCompany, setUpdCompany] = useState(INITIAL_ROUTE.updCompany || null); // 업데이트 › 분야 › 회사 (slug)
  const goUpdates = (cat, company) => {
    setSection('updates'); setUpdCat(cat || null); setUpdCompany(company || null);
    window.scrollTo({ top: 0 });
  };
  const [query, setQuery] = useState('');
  const [keyword, setKeyword] = useState(null);       // 선택된 서브 카테고리 (null = 전체)
  const [articles, setArticles] = useState([]);
  const [keywordTabs, setKeywordTabs] = useState(null);
  const [dataState, setDataState] = useState('loading');   // 'loading' | 'ready' | 'error'
  const [open, setOpen] = useState(null);

  // load the date-split article files once
  useEffect(() => {
    let cancelled = false;
    loadArticles()
      .then(({ articles: list, keywordTabs }) => {
        if (cancelled) return;
        setArticles(list);
        setKeywordTabs(keywordTabs);
        // /topics/<tab>/<키워드>/ 로 들어온 경우 → 그 서브 카테고리 선택
        const route = parseRoute(window.location.pathname);
        if (route.kwSlug) {
          const hit = ((keywordTabs || {})[route.tab] || []).find(k => kwSlug(k.label) === route.kwSlug);
          if (hit) setKeyword(hit.label);
        }
        // /articles/<id>/ (또는 예전 ?article=<id>) 로 들어온 경우 → 그 기사의 탭 위에 기사 창
        let id = route.articleId;
        try { id = id || new URLSearchParams(window.location.search).get('article'); } catch {}
        const found = id ? list.find(a => a.id === id) : null;
        if (found) {
          setActiveTab(found.tab);
          setViewHome(false);
          setOpen(found);
          const url = new URL(window.location.href);
          url.searchParams.delete('article');
          window.history.replaceState({}, '', articlePath(found.id) + url.search);
        }
        setDataState('ready');
      })
      .catch(err => {
        console.error('Failed to load articles', err);
        if (!cancelled) setDataState('error');
      });
    return () => { cancelled = true; };
  }, []);
  const articlesRef = useRef(articles);
  articlesRef.current = articles;
  const keywordTabsRef = useRef(keywordTabs);
  keywordTabsRef.current = keywordTabs;
  const [loading, setLoading] = useState(false);

  // 기사 창 열기/닫기 — 열면 주소가 /articles/<id>/ 가 되고, 닫으면 원래 화면 주소로 돌아간다
  const openArticle = (a) => {
    setOpen(a);
    if (window.location.pathname === articlePath(a.id)) return;
    const st = window.history.state;
    if (st && st.modal) {
      // 기사 창 안에서 다른 기사로 이동 → 같은 기록을 바꿔서, 닫으면 바로 원래 화면으로 돌아가게
      window.history.replaceState({ modal: true }, '', articlePath(a.id) + window.location.search);
    } else {
      window.history.pushState({ modal: true }, '', articlePath(a.id) + window.location.search);
    }
  };
  const closeArticle = useCallback(() => {
    if (window.history.state && window.history.state.modal) {
      window.history.back();          // 앱에서 연 기사 창 → 이전 주소로 (popstate가 창을 닫는다)
    } else {
      setOpen(null);                  // 공유 링크로 바로 들어온 경우 → 아래 effect가 탭 주소로 바꾼다
    }
  }, []);

  // back/forward → 탭·서브 카테고리와 기사 창을 주소에 맞춘다
  useEffect(() => {
    function onPop() {
      const route = parseRoute(window.location.pathname);
      setSection(route.updates ? 'updates' : 'news');
      if (route.updates) { setOpen(null); setUpdCat(route.updCat || null); setUpdCompany(route.updCompany || null); return; }
      if (route.articleId) {
        const found = articlesRef.current.find(a => a.id === route.articleId);
        if (found) { setActiveTab(found.tab); setViewHome(false); }
        setOpen(found || null);
        return;
      }
      setOpen(null);
      setViewHome(route.home);
      if (!route.home) {
        setActiveTab(route.tab);
        setQuery('');
        const hit = ((keywordTabsRef.current || {})[route.tab] || []).find(k => kwSlug(k.label) === route.kwSlug);
        setKeyword(hit ? hit.label : null);
      }
    }
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  // 북마크 기능을 없애며 예전에 저장해 둔 목록을 지운다
  useEffect(() => { try { localStorage.removeItem('aiad:saved'); } catch (e) {} }, []);

  // theme
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.setProperty('--accent', accent);
    localStorage.setItem('aiad:theme', theme);
  }, [theme]);

  // simulate loading on tab switch (briefly)
  useEffect(() => {
    setLoading(true);
    const t = setTimeout(() => setLoading(false), 280);
    return () => clearTimeout(t);
  }, [activeTab, keyword]);

  const toggleTheme = () => {
    setTheme(t => t === 'dark' ? 'light' : 'dark');
  };

  // 서브 카테고리 목록 (현재 탭)
  const subcats = useMemo(() => subCategoriesFor(keywordTabs, articles, activeTab), [keywordTabs, articles, activeTab]);
  const activeKeyword = subcats.some(c => c.label === keyword) ? keyword : null;
  const showSubcats = !viewHome && !query.trim() && dataState === 'ready';
  const goTab = (id) => { setActiveTab(id); setKeyword(null); setViewHome(false); setQuery(''); };

  // 탭·서브 카테고리를 바꾸면 주소도 /topics/... 로 바꾼다 (공유·새로고침해도 같은 화면).
  // 저장한 기사·검색 화면은 주소를 바꾸지 않는다. 데이터가 오기 전에는 들어온 주소를 그대로 둔다.
  // 기사 창이 열려 있는 동안은 /articles/<id>/ 를 유지한다.
  useEffect(() => {
    if (dataState !== 'ready' || open) return;
    const onArticle = window.location.pathname.startsWith('/articles/');
    if (section !== 'updates' && !onArticle && query.trim()) return;
    const path = section === 'updates' ? updatesPath(updCat, updCompany) : routePath(viewHome, activeTab, activeKeyword);
    if (path === window.location.pathname) return;
    if (onArticle) window.history.replaceState({}, '', path + window.location.search);   // 공유 링크로 들어와 창을 닫음
    else window.history.pushState({}, '', path + window.location.search);
  }, [dataState, open, section, updCat, updCompany, viewHome, query, activeTab, activeKeyword]);

  // filter pipeline
  let visible = articles;
  if (query.trim()) {
    const q = query.trim().toLowerCase();
    visible = visible.filter(a =>
      a.headline.toLowerCase().includes(q) ||
      a.summary.toLowerCase().includes(q) ||
      a.source.toLowerCase().includes(q)
    );
  } else {
    visible = visible.filter(a => a.tab === activeTab);
    if (activeKeyword) visible = visible.filter(a => (a.keywords || []).includes(activeKeyword));
  }

  if (false) {
    visible = [...visible];
  }

  // groupByDate flag
  const groupByDate = true;

  return (
    <div className="page">
      <Header
        query={query}
        onQuery={(v) => { setQuery(v); if (v) { setSection('news'); setViewHome(false); } }}
        theme={theme}
        onToggleTheme={toggleTheme}
        onShowHome={() => { setSection('news'); setViewHome(true); setQuery(''); }}
        onMenu={() => setSideOpen(true)}
      />
      <div className="layout">
      <Sidebar
        section={section}
        viewHome={viewHome}
        activeTab={activeTab}
        open={sideOpen}
        onOpen={() => setSideOpen(true)}
        onClose={() => setSideOpen(false)}
        counts={tabCounts(articles)}
        onNewsHome={() => { setSection('news'); setViewHome(true); setQuery(''); window.scrollTo({ top: 0 }); }}
        onTab={(id) => { setSection('news'); goTab(id); window.scrollTo({ top: 0 }); }}
        onUpdates={() => goUpdates(null, null)}
        updCat={updCat}
        onUpdCat={(cat) => goUpdates(cat, null)}
        updCompany={updCompany}
        onUpdCompany={(cat, company) => goUpdates(cat, company)}
        subcats={subcats}
        keyword={activeKeyword}
        onKeyword={(k) => { setKeyword(k); window.scrollTo({ top: 0 }); }}
      />
      <div className="layout-main">
      {section === 'updates' ? (
        <UpdatesView
          cat={updCat}
          company={updCompany}
          onCat={(cat) => goUpdates(cat, null)}
          onCompany={(cat, company) => goUpdates(cat, company)}
        />
      ) : (<>
      {!viewHome && (
        <Tabs
          active={activeTab}
          onChange={goTab}
          articles={articles}
          viewHome={viewHome}
          subcats={showSubcats ? subcats : null}
          keyword={activeKeyword}
          onKeyword={setKeyword}
        />
      )}
      
      {!viewHome && (
        <FeedMeta
          activeTab={activeTab}
          count={visible.length}
          query={query.trim()}
          keyword={activeKeyword}
        />
      )}
      <main className="feed">
        {viewHome ? (
          <HomeView
            onSelectTab={(id) => { goTab(id); window.scrollTo({ top: 0 }); }}
            onOpenArticle={openArticle}
            articles={articles}
          />
        ) : dataState === 'error' ? (
          <EmptyState message="기사를 불러오지 못했어요" sub="잠시 후 새로고침해 주세요." />
        ) : (loading || dataState === 'loading') ? (
          <div className="grid">
            {[0,1,2,3,4,5].map(i => <SkeletonCard key={i} />)}
          </div>
        ) : visible.length === 0 ? (
          query ? (
            <EmptyState message={`\u201c${query}\u201d에 대한 결과가 없어요`} sub="다른 키워드를 시도해 보세요." />
          ) : (
            <EmptyState />
          )
        ) : (groupByDate && !query) ? (
          <DateGroupedFeed
            articles={visible}
            onOpen={openArticle}
            query={query.trim()}
            expandAll={!!activeKeyword}
          />
        ) : (
          <div className="grid">
            {visible.map(a => (
              <ArticleCard
                key={a.id}
                article={a}
                onOpen={openArticle}
                query={query.trim()}
              />
            ))}
          </div>
        )}
      </main>
      </>)}

      <footer className="site-footer">
        <div className="meta-line">AI Art Daily · 매일 오전 업데이트</div>
        <div>큐레이션 · 한국어 번역</div>
      </footer>
      </div>
      </div>
      <IosInstallHint />

      {open && (
        <ArticleModal
          article={open}
          onClose={closeArticle}
          onOpen={openArticle}
          allArticles={articles}
          onSelectKeyword={(tab, k) => {
            setOpen(null); goTab(tab); setKeyword(k); window.scrollTo({ top: 0 });
            if (window.history.state && window.history.state.modal) window.history.replaceState({}, '', window.location.href);
          }}
        />
      )}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
