/* AI Art Daily — hi-fi prototype */

const { useState, useEffect, useMemo, useRef } = React;
const { tabs: TABS, articles: ARTICLES, body: ARTICLE_BODY } = window.AIAD;
const WHITELIST = window.AIAD_WHITELIST || { articleSources: [], githubRepos: [] };

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
            <ArticleCard key={a.id} variant="compact-row" article={a} onOpen={onOpen} onToggleSave={onToggleSave} isSaved={saved.includes(a.id)} query={query} />
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
function Header({ query, onQuery, savedCount, onShowSaved, theme, onToggleTheme }) {
  const inputRef = useRef(null);
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
        <div className="brand" onClick={() => { onQuery(''); window.scrollTo({ top: 0, behavior: 'smooth' }); }}>
          <img className="brand-mark" src="assets/logo.png" alt="DX" />
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
function Tabs({ active, onChange, articles, savedCount, viewSaved, onClearSaved, viewWhitelist, onShowWhitelist }) {
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
                className={`tab ${t.id === active && !viewWhitelist ? 'active' : ''}`}
                onClick={() => onChange(t.id)}
              >
                {t.label}
                <span className="count">{counts[t.id] || 0}</span>
                {tabHasNew(t.id, articles) && t.id !== active && <span className="new-dot" />}
              </button>
            ))}
            <span className="tab-spacer" aria-hidden="true" />
            <button
              className={`tab tab-utility ${viewWhitelist ? 'active' : ''}`}
              onClick={onShowWhitelist}
              title="스크래이핑 / Github 추적 대상 목록"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{marginRight:6}}>
                <path d="M12 2 4 6v6c0 5 3.5 8.5 8 10 4.5-1.5 8-5 8-10V6l-8-4z" />
                <path d="m9 12 2 2 4-4" />
              </svg>
              유용한 소스
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}

/* ---------- feed meta ---------- */
function FeedMeta({ activeTab, count, viewSaved, query }) {
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
    sub = `${today} · ${count}개 기사`;
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
function ArticleModal({ article, onClose, isSaved, onToggleSave, onOpen, allArticles }) {
  const bodyRef = useRef(null);
  const [progress, setProgress] = useState(0);

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
            {Array.isArray(article.urls) && article.urls.filter(u => u && u.href).map((u, i) => (
              <a key={i} href={u.href} target="_blank" rel="noopener noreferrer">
                {u.label || '관련 링크'}
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M7 17 17 7" /><path d="M8 7h9v9" />
                </svg>
              </a>
            ))}
          </div>
          <div className="modal-article">
            <p style={{ fontSize: 18, lineHeight: 1.7, color: 'var(--ink)' }}>{article.summary}</p>
            <div dangerouslySetInnerHTML={{ __html: article.body || ARTICLE_BODY || '' }} />
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
function DateGroupedFeed({ articles, onOpen, onToggleSave, saved, query }) {
  const [showAll, setShowAll] = useState(false);

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

/* ---------- whitelist view ---------- */
function WlSubgroup({ kind, title, count, items }) {
  return (
    <div className="wl-sub">
      <div className="wl-sub-head">
        <h3 className="wl-sub-title">{title}</h3>
        <span className="wl-sub-count">{String(count).padStart(2, '0')}</span>
        <span className="wl-sub-rule" aria-hidden="true" />
      </div>
      <ul className="wl-grid">
        {items.map(it => (
          <li key={it.url} className="wl-card">
            <a className={`wl-card-link wl-card-${kind}`} href={it.url} target="_blank" rel="noopener noreferrer">
              <div className="wl-card-name">{it.name}</div>
              {it.note ? <div className="wl-card-note">{it.note}</div> : null}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}

function groupBy(items) {
  const map = new Map();
  const order = [];
  for (const it of items) {
    const k = it.group || '기타';
    if (!map.has(k)) { map.set(k, []); order.push(k); }
    map.get(k).push(it);
  }
  return order.map(k => [k, map.get(k)]);
}

function WhitelistView() {
  const [wlQuery, setWlQuery] = useState('');
  const q = wlQuery.trim().toLowerCase();
  const matches = (it) => !q ||
    (it.name && it.name.toLowerCase().includes(q)) ||
    (it.note && it.note.toLowerCase().includes(q)) ||
    (it.group && it.group.toLowerCase().includes(q)) ||
    (it.url && it.url.toLowerCase().includes(q));

  const filteredRepos = (WHITELIST.githubRepos || []).filter(matches);
  const filteredSources = (WHITELIST.articleSources || []).filter(matches);
  const totalAll = (WHITELIST.githubRepos || []).length + (WHITELIST.articleSources || []).length;
  const totalShown = filteredRepos.length + filteredSources.length;

  const sections = [
    {
      key: 'repos',
      title: 'Github 레포지토리',
      sub: '변경점을 이벤트로 추적하는 레포',
      kind: 'repo',
      items: filteredRepos,
    },
    {
      key: 'sources',
      title: '뉴스 소스',
      sub: '기사 스크래이핑에 사용하는 원본 출처 도메인',
      kind: 'site',
      items: filteredSources,
    },
  ];

  return (
    <div className="whitelist">
      <div className="wl-search-bar">
        <div className="wl-search">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <circle cx="11" cy="11" r="7" />
            <path d="m20 20-3.5-3.5" />
          </svg>
          <input
            type="search"
            value={wlQuery}
            onChange={(e) => setWlQuery(e.target.value)}
            placeholder="레포·소스·카테고리 검색…"
            aria-label="유용한 소스 검색"
          />
          {wlQuery && (
            <button type="button" className="wl-search-clear" onClick={() => setWlQuery('')} aria-label="검색어 지우기">×</button>
          )}
        </div>
        <div className="wl-search-meta">
          {q ? `${totalShown}개 일치 · 전체 ${totalAll}개` : `전체 ${totalAll}개`}
        </div>
      </div>
      {q && totalShown === 0 ? (
        <div className="wl-empty">검색 결과가 없어요. 다른 키워드로 시도해보세요.</div>
      ) : (
        sections.map(g => (
          g.items.length === 0 ? null : (
            <section key={g.key} className="wl-group">
              <header className="wl-group-head">
                <div className="wl-group-eyebrow">
                  <span className="wl-group-kind">{g.kind === 'repo' ? 'GITHUB' : 'SOURCES'}</span>
                  <span className="wl-group-rule" aria-hidden="true" />
                  <span className="wl-group-count">{String(g.items.length).padStart(2, '0')}</span>
                </div>
                <h2 className="wl-group-title">{g.title}</h2>
                <div className="wl-group-sub">{g.sub}</div>
              </header>
              {groupBy(g.items).map(([sub, items]) => (
                <WlSubgroup key={sub} kind={g.kind} title={sub} count={items.length} items={items} />
              ))}
            </section>
          )
        ))
      )}
    </div>
  );
}

/* ---------- App ---------- */
function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem('aiad:theme') || 'light');
  const accent = '#c2410c';

  const [activeTab, setActiveTab] = useState('games');
  const [viewWhitelist, setViewWhitelist] = useState(false);
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(() => {
    try {
      const id = new URLSearchParams(window.location.search).get('article');
      if (!id) return null;
      return ARTICLES.find(a => a.id === id) || null;
    } catch { return null; }
  });
  const [saved, setSaved] = useState(() => {
    try { return JSON.parse(localStorage.getItem('aiad:saved') || '[]'); } catch { return []; }
  });
  const [viewSaved, setViewSaved] = useState(false);
  const [loading, setLoading] = useState(false);

  // sync ?article=<id> into the URL when modal opens/closes
  useEffect(() => {
    const url = new URL(window.location.href);
    const current = url.searchParams.get('article');
    const target = open ? open.id : null;
    if (current === target) return;
    if (target) url.searchParams.set('article', target);
    else url.searchParams.delete('article');
    window.history.pushState({ articleId: target }, '', url.toString());
  }, [open]);

  // back/forward → reopen or close modal to match URL
  useEffect(() => {
    function onPop() {
      const id = new URLSearchParams(window.location.search).get('article');
      if (!id) { setOpen(null); return; }
      const found = ARTICLES.find(a => a.id === id);
      setOpen(found || null);
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
  }, [activeTab, viewSaved]);

  const toggleSave = (id) => {
    setSaved(s => s.includes(id) ? s.filter(x => x !== id) : [...s, id]);
  };
  const toggleTheme = () => {
    setTheme(t => t === 'dark' ? 'light' : 'dark');
  };

  // filter pipeline
  let visible = ARTICLES;
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
        onQuery={(v) => { setQuery(v); if (v) setViewSaved(false); }}
        savedCount={saved.length}
        onShowSaved={() => { setViewSaved(true); setQuery(''); }}
        theme={theme}
        onToggleTheme={toggleTheme}
      />
      <Tabs
        active={activeTab}
        onChange={(id) => { setActiveTab(id); setViewSaved(false); setViewWhitelist(false); setQuery(''); }}
        articles={ARTICLES}
        savedCount={saved.length}
        viewSaved={viewSaved}
        onClearSaved={() => setViewSaved(false)}
        viewWhitelist={viewWhitelist}
        onShowWhitelist={() => { setViewWhitelist(true); setViewSaved(false); setQuery(''); }}
      />
      {!viewWhitelist && (
        <FeedMeta
          activeTab={activeTab}
          count={visible.length}
          viewSaved={viewSaved}
          query={query.trim()}
        />
      )}
      <main className="feed">
        {viewWhitelist ? (
          <WhitelistView />
        ) : loading ? (
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
            onOpen={setOpen}
            onToggleSave={toggleSave}
            saved={saved}
            query={query.trim()}
          />
        ) : (
          <div className="grid">
            {visible.map(a => (
              <ArticleCard
                key={a.id}
                article={a}
                onOpen={setOpen}
                onToggleSave={toggleSave}
                isSaved={saved.includes(a.id)}
                query={query.trim()}
              />
            ))}
          </div>
        )}
      </main>

      <footer className="site-footer">
        <div className="meta-line">AI Art Daily · 매일 오전 업데이트</div>
        <div>큐레이션 · 한국어 번역</div>
      </footer>

      {open && (
        <ArticleModal
          article={open}
          onClose={() => setOpen(null)}
          isSaved={saved.includes(open.id)}
          onToggleSave={toggleSave}
          onOpen={setOpen}
          allArticles={ARTICLES}
        />
      )}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
