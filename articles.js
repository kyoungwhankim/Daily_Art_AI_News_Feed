/* AI Art Daily — article dataset */
window.AIAD = {
  tabs: [
    { id: 'games',    label: '게임 제작 속 AI' },
    { id: 'industry', label: 'AI 도입 뉴스' },
    { id: 'art',      label: '아트 전반 AI 뉴스' },
  ],

  /*
   * Each article shape:
   * {
   *   id:          'unique-slug',          // any unique string
   *   tab:         'games',                // must match a tab id above
   *   cat:         '게임 제작',             // small category label on card
   *   headline:    '한국어 제목',
   *   summary:     '한 줄 요약',
   *   body:        '<p>본문 첫 문단</p><p>두 번째 문단…</p>',  // ← 카드 클릭 시 모달에 보이는 한국어 번역 본문 (HTML 허용)
   *   source:      '출처',
   *   publishedAt: '2026-04-25',           // ISO date — used for sorting
   *   mark:        'NEWS',                 // small badge label
   *   date:        '2026.04.25',           // displayed date string
   *   isNew:       true,                   // optional — shows "NEW" pip
   *   hue:         30,                     // 0–360, gradient thumbnail color
   *   image:       'assets/news/x.jpg',    // optional — overrides gradient
   *   url:         'https://...',          // original source link
   * }
   */
  articles: [
    /* ---- games ---- */

    /* ---- industry ---- */

    /* ---- art ---- */

  ],
};
