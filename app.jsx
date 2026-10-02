/* AI Art Daily — hi-fi prototype */

const { useState, useEffect, useMemo, useRef, useCallback } = React;
const { tabs: TABS } = window.AIAD;

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
function ArticleCard({ article, onOpen, onToggleSave, isSaved, query, variant }) {
  const cls = `card${variant ? ' ' + variant : ''}`;
  return (
    <button className={cls} onClick={() => onOpen(article)}>
      <Thumb hue={article.hue} image={article.image} alt={article.headline}>
        <div
          className={`bookmark-btn ${isSaved ? 'saved' : ''}`}
          role="button"
          aria-label="저장"
          onClick={e => { e.stopPropagation(); onToggleSave(article.id); }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill={isSaved ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="1.8">
            <path d="M6 4h12v17l-6-4-6 4z" strokeLinejoin="round" />
          </svg>
        </div>
      </Thumb>
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
function DateSection({ iso, items, onOpen, onToggleSave, saved, query, isToday }) {
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
          <ArticleCard variant="feature" article={items[0]} onOpen={onOpen} onToggleSave={onToggleSave} isSaved={saved.includes(items[0].id)} query={query} />
          {items.slice(1, 3).map(a => (
            <ArticleCard key={a.id} article={a} onOpen={onOpen} onToggleSave={onToggleSave} isSaved={saved.includes(a.id)} query={query} />
          ))}
          {items.length > 3 && (
            <div style={{ gridColumn: '1 / -1' }}>
              <div className="grid">
                {items.slice(3).map(a => (
                  <ArticleCard key={a.id} article={a} onOpen={onOpen} onToggleSave={onToggleSave} isSaved={saved.includes(a.id)} query={query} />
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="grid">
          {items.map(a => (
            <ArticleCard key={a.id} article={a} onOpen={onOpen} onToggleSave={onToggleSave} isSaved={saved.includes(a.id)} query={query} />
          ))}
        </div>
      )}
    </section>
  );
}

/* ---------- header ---------- */
function Header({ query, onQuery, savedCount, onShowSaved, theme, onToggleTheme, onShowHome }) {
  const inputRef = useRef(null);
  const install = useInstallPrompt();
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
    <header className="site-header">
      <div className="header-inner">
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
              placeholder="기사 · 출처 · 키워드 검색"
            />
            {!query && <span className="kbd">⌘ K</span>}
          </label>
          {install && (
            <button className="icon-btn" title="앱 설치" aria-label="앱 설치" onClick={install}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 3v12" /><path d="m7 10 5 5 5-5" /><path d="M5 21h14" />
              </svg>
            </button>
          )}
          <button className="icon-btn" title="저장한 기사" onClick={onShowSaved}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path d="M6 4h12v17l-6-4-6 4z" strokeLinejoin="round" />
            </svg>
            {savedCount > 0 && <span className="badge-count">{savedCount}</span>}
          </button>
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
function Tabs({ active, onChange, articles, savedCount, viewSaved, onClearSaved, viewHome, subcats, keyword, onKeyword }) {
  const counts = useMemo(() => tabCounts(articles), [articles]);
  return (
    <nav className="tabs-wrap">
      <div className="tabs-inner">
        <div className="tabs-meta">
          {viewSaved ? '저장한 기사' : `카테고리 · ${TABS.length}개 채널`}
        </div>
        {viewSaved ? (
          <div className="tabs">
            <button className="tab active">
              저장된 기사 <span className="count">{savedCount}</span>
            </button>
            <button className="tab" onClick={onClearSaved}>
              <span style={{ color: 'var(--muted)' }}>← 전체 피드로 돌아가기</span>
            </button>
          </div>
        ) : (
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
        )}
        {!viewSaved && subcats && (
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
function FeedMeta({ activeTab, count, viewSaved, query, keyword }) {
  const today = `${TODAY.getFullYear()}년 ${TODAY.getMonth() + 1}월 ${TODAY.getDate()}일 (${KOR_DAY[TODAY.getDay()]})`;
  let title, sub;
  if (query) {
    title = `\u201c${query}\u201d 검색 결과`;
    sub = `${count}개 기사`;
  } else if (viewSaved) {
    title = '저장한 기사';
    sub = `${count}개 기사 · 북마크됨`;
  } else {
    const t = TABS.find(t => t.id === activeTab);
    title = t.label;
    sub = keyword ? `${today} · ${keyword} · ${count}개 기사` : `${today} · ${count}개 기사`;
  }
  const activeDesc = (!query && !viewSaved)
    ? (TABS.find(t => t.id === activeTab) || {}).desc
    : null;
  return (
    <div className="feed-meta">
      <div>
        <h1 className="feed-title">{title}</h1>
        <div className="feed-sub">{sub}</div>
        {activeDesc && <p className="feed-desc">{activeDesc}</p>}
      </div>
      {!viewSaved && !query && (
        <div className="feed-toolbar"></div>
      )}
    </div>
  );
}

/* ---------- modal ---------- */
function ArticleModal({ article, onClose, isSaved, onToggleSave, onOpen, allArticles, onSelectKeyword }) {
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
        <button
          className={`modal-save ${isSaved ? 'saved' : ''}`}
          onClick={() => onToggleSave(article.id)}
          aria-label="저장"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill={isSaved ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="1.8">
            <path d="M6 4h12v17l-6-4-6 4z" strokeLinejoin="round" />
          </svg>
        </button>
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
function DateGroupedFeed({ articles, onOpen, onToggleSave, saved, query, expandAll }) {
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
          onToggleSave={onToggleSave}
          saved={saved}
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

/* ---------- App ---------- */
function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem('aiad:theme') || 'light');
  const accent = '#c2410c';

  const [activeTab, setActiveTab] = useState(INITIAL_ROUTE.tab || 'games');
  const [viewHome, setViewHome] = useState(INITIAL_ROUTE.home);
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
  const [saved, setSaved] = useState(() => {
    try { return JSON.parse(localStorage.getItem('aiad:saved') || '[]'); } catch { return []; }
  });
  const [viewSaved, setViewSaved] = useState(false);
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
        setViewSaved(false);
        setQuery('');
        const hit = ((keywordTabsRef.current || {})[route.tab] || []).find(k => kwSlug(k.label) === route.kwSlug);
        setKeyword(hit ? hit.label : null);
      }
    }
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  // theme
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.setProperty('--accent', accent);
    localStorage.setItem('aiad:theme', theme);
  }, [theme]);

  // persist saved
  useEffect(() => {
    localStorage.setItem('aiad:saved', JSON.stringify(saved));
  }, [saved]);

  // simulate loading on tab switch (briefly)
  useEffect(() => {
    setLoading(true);
    const t = setTimeout(() => setLoading(false), 280);
    return () => clearTimeout(t);
  }, [activeTab, viewSaved, keyword]);

  const toggleSave = (id) => {
    setSaved(s => s.includes(id) ? s.filter(x => x !== id) : [...s, id]);
  };
  const toggleTheme = () => {
    setTheme(t => t === 'dark' ? 'light' : 'dark');
  };

  // 서브 카테고리 목록 (현재 탭)
  const subcats = useMemo(() => subCategoriesFor(keywordTabs, articles, activeTab), [keywordTabs, articles, activeTab]);
  const activeKeyword = subcats.some(c => c.label === keyword) ? keyword : null;
  const showSubcats = !viewHome && !viewSaved && !query.trim() && dataState === 'ready';
  const goTab = (id) => { setActiveTab(id); setKeyword(null); setViewSaved(false); setViewHome(false); setQuery(''); };

  // 탭·서브 카테고리를 바꾸면 주소도 /topics/... 로 바꾼다 (공유·새로고침해도 같은 화면).
  // 저장한 기사·검색 화면은 주소를 바꾸지 않는다. 데이터가 오기 전에는 들어온 주소를 그대로 둔다.
  // 기사 창이 열려 있는 동안은 /articles/<id>/ 를 유지한다.
  useEffect(() => {
    if (dataState !== 'ready' || open) return;
    const onArticle = window.location.pathname.startsWith('/articles/');
    if (!onArticle && (viewSaved || query.trim())) return;
    const path = routePath(viewHome, activeTab, activeKeyword);
    if (path === window.location.pathname) return;
    if (onArticle) window.history.replaceState({}, '', path + window.location.search);   // 공유 링크로 들어와 창을 닫음
    else window.history.pushState({}, '', path + window.location.search);
  }, [dataState, open, viewHome, viewSaved, query, activeTab, activeKeyword]);

  // filter pipeline
  let visible = articles;
  if (viewSaved) {
    visible = visible.filter(a => saved.includes(a.id));
  } else if (query.trim()) {
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
        onQuery={(v) => { setQuery(v); if (v) { setViewSaved(false); setViewHome(false); } }}
        savedCount={saved.length}
        onShowSaved={() => { setViewSaved(true); setViewHome(false); setQuery(''); }}
        theme={theme}
        onToggleTheme={toggleTheme}
        onShowHome={() => { setViewHome(true); setViewSaved(false); setQuery(''); }}
      />
      {!viewHome && (
        <Tabs
          active={activeTab}
          onChange={goTab}
          articles={articles}
          savedCount={saved.length}
          viewSaved={viewSaved}
          onClearSaved={() => setViewSaved(false)}
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
          viewSaved={viewSaved}
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
          viewSaved ? (
            <EmptyState message="저장한 기사가 없어요" sub="기사 카드의 북마크 아이콘을 눌러 나중에 읽을 기사를 모아보세요." />
          ) : query ? (
            <EmptyState message={`\u201c${query}\u201d에 대한 결과가 없어요`} sub="다른 키워드를 시도해 보세요." />
          ) : (
            <EmptyState />
          )
        ) : (groupByDate && !query && !viewSaved) ? (
          <DateGroupedFeed
            articles={visible}
            onOpen={openArticle}
            onToggleSave={toggleSave}
            saved={saved}
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
                onToggleSave={toggleSave}
                isSaved={saved.includes(a.id)}
                query={query.trim()}
              />
            ))}
          </div>
        )}
      </main>

      <IosInstallHint />
      <footer className="site-footer">
        <div className="meta-line">AI Art Daily · 매일 오전 업데이트</div>
        <div>큐레이션 · 한국어 번역</div>
      </footer>

      {open && (
        <ArticleModal
          article={open}
          onClose={closeArticle}
          isSaved={saved.includes(open.id)}
          onToggleSave={toggleSave}
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
