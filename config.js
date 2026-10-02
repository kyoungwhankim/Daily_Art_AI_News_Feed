/* AI Art Daily — site config (탭 정의) */
/* 기사 데이터는 data/index.json + data/articles/YYYY-MM-DD.json 에 날짜별로 나뉘어 있다. */
window.AIAD = {
  tabs: [
    { id: 'games', label: '게임 제작 속 AI', desc: '게임 아트 리소스 제작에 사용되는 AI 관련 뉴스들을 매일 업데이트합니다.' },
    { id: 'industry', label: 'AI 도입 뉴스', desc: '게임 스튜디오들의 AI 도입과 관련된 뉴스들을 매일 업데이트합니다.' },
    { id: 'art', label: '아트 전반 AI 뉴스', desc: '게임 제작과 무관하게 모든 아트 관련 AI 뉴스들을 매일 업데이트합니다.' },
  ],

  /*
   * 날짜 파일(data/articles/*.json)의 기사 형식:
   * {
   *   id:          'unique-slug',          // any unique string
   *   tab:         'games',                // must match a tab id above
   *   headline:    '한국어 제목',
   *   summary:     '한 줄 요약',
   *   body:        '<p>본문 첫 문단</p><p>두 번째 문단…</p>',  // 카드 클릭 시 모달 본문 (HTML 허용)
   *   source:      '출처',
   *   publishedAt: '2026.04.25',           // 'YYYY.MM.DD' 형식, 사이트 업로드 날짜 (정렬·날짜 헤더에 사용; 화면에는 그대로 표시됨)
   *   hue:         30,                     // 0–360, 그라디언트 썸네일 색상
   *   image:       'assets/news/x.jpg',    // optional — 있으면 그라디언트 대신 이미지 사용
   *   keywords:    ['3D', 'Blender'],      // 서브 카테고리 (scripts/tag_keywords.py가 자동 생성)
   *   url:         'https://...',          // 원문 링크
   *   urls: [                              // optional — 추가 관련 링크
   *     { label: '관련 보도', href: 'https://...' },
   *     { label: '공식 발표', href: 'https://...' },
   *   ],
   * }
   */
};
