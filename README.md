# Art AI News Feed

A daily, curated stream of AI-generated art and AI-in-art news in Korean.

Static site — no backend, no login. Hosted on GitHub Pages. The whole app is React rendered in the browser; updating the site means editing one JavaScript file and pushing.

Daily updates are produced by a Claude Code Routine that runs in the cloud each morning, researches news, writes Korean translations, and pushes the change to `main` automatically. Manual editing still works the same way it always did — pick whichever path fits the day.

## Live site

Edit `articles.js`, commit, push. GitHub Pages auto-rebuilds in ~60 seconds.

## File structure

| File | Purpose |
|---|---|
| `index.html` | Entry point (served by GitHub Pages) |
| `app.css` | All styling |
| `app.jsx` | App logic — tabs, search, modal, bookmarks, theme, URL sync, date grouping |
| `articles.js` | **The article database — edited daily** |
| `scripts/fetch_article.py` | Routine helper — fetches a candidate URL, extracts og:image / lazy-load fallbacks, related links, and clean body text |
| `scripts/update_articles_js.py` | Routine helper — inserts new article objects into `articles.js` and skips URLs already present (URL dedup) |
| `scripts/push_to_main.py` | Routine helper — verifies branch, commits, pushes directly to `main` via token URL, syncs the tracking ref |
| `assets/logo.png` | DX mascot |
| `assets/news/` | Drop thumbnail images here (path referenced by `image` field) |
| `fonts/` | NEXON Lv2 Gothic (Light, Regular, Medium, Bold) |
| `.nojekyll` | Tells GitHub Pages to skip Jekyll processing — required so `_`-prefixed paths and dotfiles serve correctly |

## Daily workflow

### Automated (Claude Code Routine)

A scheduled cloud routine handles the full pipeline every morning:

1. **Discovery (Phase 1)** — `WebSearch` with `site:` filters across the source whitelist, plus an optional RSS pass, builds a candidate URL list per section.
2. **Fetch & write (Phase 2)** — For every candidate, `scripts/fetch_article.py` extracts image/links/body. The routine reads the body for an explicit publication date and only keeps articles dated **today or yesterday in KST** (a calendar-day rule that absorbs the timezone gap with US/EU publishers). Korean headline, summary, and a 600–800 character translated body are written into a JSON entry.
3. **Update** — `scripts/update_articles_js.py` reads `articles.json`, dedupes against URLs already present in `articles.js`, generates unique slug ids, and inserts the new entries directly after each tab's section comment marker.
4. **Push** — `scripts/push_to_main.py` commits inside the main working directory (signing only works there in the routine environment), pushes directly to `main` via a token URL (the default `origin` proxy denies pushes), and re-syncs the local tracking ref.

The routine never creates branches or pull requests — every change lands on `main` so GitHub Pages picks it up immediately.

### Manual

The original workflow still works for ad-hoc edits:

1. On github.com, edit `articles.js`.
2. Add new entries inside the `articles: [ ... ]` array (order doesn't matter — feed is sorted by `publishedAt`).
3. Commit. Wait ~60 seconds. Refresh the site.

## Article schema

```js
{
  id:          'unique-slug',                 // any unique string; used in URLs (?article=<id>)
  tab:         'games',                       // must match a tab id from tabs[] — 'games' | 'industry' | 'art'
  headline:    '한국어 제목',
  summary:     '한 줄 요약',
  body:        '<p>본문 첫 문단</p><p>두 번째 문단…</p>',  // HTML — rendered in modal when card is clicked
  source:      '출처명',                       // outlet name (Korean for Korean outlets, English otherwise)
  publishedAt: '2026.04.25',                  // 'YYYY.MM.DD' format with dots — sorts the feed and labels date headers
  hue:         30,                            // 0–360 integer — fallback gradient thumbnail color
  url:         'https://...',                 // primary source link (required)

  // optional —
  image:       'assets/news/example.jpg',     // overrides the hue gradient when present; falls back to gradient if missing/broken
  urls: [                                     // additional related links shown in the modal
    { label: '관련 보도', href: 'https://...' },
    { label: '공식 발표', href: 'https://...' },
  ],
}
```

### Field notes

- **`publishedAt`** — Treated as the **upload date** (when the article was added to the site), not necessarily the original article's publish date. Displayed verbatim. Format must be `YYYY.MM.DD` with dots. The routine fills this with the current KST date automatically.
- **`body`** — HTML string. Wrap each paragraph in `<p>...</p>`. Allowed tags: `<p>`, `<h2>`, `<h3>`, `<blockquote>`, `<strong>`, `<em>`, `<a>`, `<ul>/<li>`, `<ol>/<li>`. End with `<p>원문: <a href="...">출처</a></p>`. The routine produces 5 paragraphs total: a 3-paragraph casual opening (what / context / why it matters) followed by a 2-paragraph condensed Korean translation, plus the attribution line.
- **`image`** — Local path (`assets/news/foo.jpg`) or external URL. If the image fails to load, the card silently falls back to the `hue` gradient — no broken-image icons. The routine prefers og:image, falls through twitter:image / lazy-load img tags / large `width=` images, and finally falls back to a WebFetch hero-image scan when curl cannot extract anything.
- **`urls`** — Array of `{label, href}`. Omit the field entirely if there are no extras (don't write `urls: []`).

## Tabs

Defined at the top of `articles.js`:

```js
tabs: [
  { id: 'games',    label: '게임 제작 속 AI' },
  { id: 'industry', label: 'AI 도입 뉴스' },
  { id: 'art',      label: '아트 전반 AI 뉴스' },
],
```

Every article's `tab` must match one of these `id`s. Adding a new tab is just adding to the array.

## Features

- **Tabs with counts and "new" indicator** — A small dot appears on a tab when it has articles published in the last 3 days (auto-detected from `publishedAt`).
- **Search (⌘K / Ctrl+K)** — Substring match against headline, summary, source.
- **Date grouping** — Feed is grouped by date with sticky section headers. The most recent date gets a "오늘" featured layout (one large card + two compact rows) when 3+ articles exist for it.
- **Modal reading view** — Click any card to open a half-width centered modal with the full `body`, related articles, and any `urls`. Reading progress bar at the top.
- **Shareable article links** — Opening any article syncs `?article=<id>` into the URL via `pushState`. Pasting that URL opens directly to the article. Browser back/forward navigates between modal and feed.
- **Bookmarks** — Per-browser, stored in `localStorage`. No login, no sync across devices.
- **Theme** — Light/dark toggle, also persisted to `localStorage`.
- **Image fallback** — Broken image URLs degrade gracefully to the hue gradient.

## What "today" means

`app.jsx` reads the visitor's system date at load time. Articles with `publishedAt` matching that date get the "오늘" group + featured layout. Yesterday's articles get an "어제" header. Older entries get standard `M월 D일 (요일)` headers.

The routine itself uses a separate calendar-day rule: it only keeps articles whose stated publication date is **today or yesterday in KST** (the routine's wall clock). This deliberately accepts US/EU "yesterday" articles as eligible for "today's" upload, because those publishers' yesterday is often Korea's today. The URL dedup in `scripts/update_articles_js.py` prevents the same article from being uploaded on consecutive days.

## Routine setup notes

The routine relies on one secret: a GitHub Personal Access Token (`GITHUB_TOKEN`) with `Contents: Read and write` permission scoped to this repository. It is stored as an environment variable in the routine configuration — not in any committed file.

`scripts/` runs both inside the routine's cloud environment and locally. To test a script outside the routine, set `REPO_PATH` to point at your local clone:

```sh
REPO_PATH=/path/to/Daily_Art_AI_News_Feed python3 scripts/update_articles_js.py
```

## Bookmarks & theme storage

Stored per-browser in `localStorage` under keys `aiad:saved` and `aiad:theme`. There is no server-side account system. Clearing browser data resets both.
