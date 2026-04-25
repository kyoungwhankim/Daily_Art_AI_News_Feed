# Art AI News Feed

A daily, curated stream of AI-generated art and AI-in-art news in Korean.

## Live site

Edit `articles.js` and push to update. GitHub Pages auto-rebuilds in ~60 seconds.

## File structure

| File | Purpose |
|---|---|
| `index.html` | Entry point (served by GitHub Pages) |
| `app.css` | All styling |
| `app.jsx` | App logic (search, tabs, modal, bookmarks, theme) |
| `articles.js` | **The article database — edit this daily** |
| `assets/logo.png` | DX mascot |
| `fonts/` | NEXON Lv2 Gothic |
| `.nojekyll` | Tells GitHub Pages to skip Jekyll processing |

## Daily workflow

1. On github.com, edit `articles.js`.
2. Add a new entry at the top of the `articles: [ ... ]` array, following the shape of the existing items.
3. Commit. Wait ~60 seconds. Refresh the site.

### Article fields

```js
{
  id: 'unique-slug',         // any unique string
  tab: 'news',               // must match a tab id from tabs[]
  headline: '제목',
  summary: '한 줄 요약',
  source: '출처',
  publishedAt: '2026-04-25', // ISO date — used for sorting
  mark: 'NEWS',              // small badge label
  date: '2026.04.25',        // displayed date
  isNew: true,               // optional — shows the "NEW" pip
  hue: 30,                   // 0–360, color of the gradient thumbnail
  image: 'assets/news/x.jpg',// optional — overrides the gradient
  url: 'https://...'         // link out
}
```

## Tabs

Tabs are defined at the top of `articles.js` under `tabs: [...]`. Each article must have a `tab` field matching one of the tab `id`s.

## Bookmarks & theme

Stored in each visitor's `localStorage` — no login, no server. Per-browser only.
