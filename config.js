/* AI Art Daily — site config (탭 정의) */
/* 기사 데이터는 data/index.json + data/articles/YYYY-MM-DD.json 에 날짜별로 나뉘어 있다. */
window.AIAD = {
  tabs: [
    { id: 'games', label: '게임 제작 속 AI', desc: '게임 아트 리소스 제작에 사용되는 AI 관련 뉴스들을 매일 업데이트합니다.' },
    { id: 'industry', label: 'AI 도입 뉴스', desc: '게임 스튜디오들의 AI 도입과 관련된 뉴스들을 매일 업데이트합니다.' },
    { id: 'art', label: '아트 전반 AI 뉴스', desc: '게임 제작과 무관하게 모든 아트 관련 AI 뉴스들을 매일 업데이트합니다.' },
  ],

  // 사이드바 '뉴스 › 업데이트' — 공식 업데이트를 모아 볼 아트 관련 AI 서비스 회사 (분류 순서 = 필터 순서)
  updateSources: [
    { category: '이미지', name: 'Midjourney', url: 'https://updates.midjourney.com/' },
    { category: '이미지', name: 'OpenAI', url: 'https://openai.com/news/' },
    { category: '이미지', name: 'Google DeepMind', url: 'https://deepmind.google/blog/' },
    { category: '이미지', name: 'Black Forest Labs', url: 'https://bfl.ai/blog' },
    { category: '이미지', name: 'Stability AI', url: 'https://stability.ai/news' },
    { category: '이미지', name: 'Krea', url: 'https://www.krea.ai/blog' },
    { category: '이미지', name: 'Topaz Labs', url: 'https://www.topazlabs.com/news' },
    { category: '이미지', name: 'Microsoft AI', url: 'https://microsoft.ai/news/' },
    { category: '영상', name: 'Runway', url: 'https://runwayml.com/news' },
    { category: '영상', name: 'Luma AI', url: 'https://lumalabs.ai/news' },
    { category: '영상', name: 'Pika', url: 'https://pika.art/blog' },
    { category: '영상', name: 'MiniMax', url: 'https://www.minimax.io/news' },
    { category: '영상', name: 'PixVerse', url: 'https://pixverse.ai/en/blog' },
    { category: '영상', name: 'Hedra', url: 'https://www.hedra.com/blog' },
    { category: '영상', name: 'Synthesia', url: 'https://www.synthesia.io/blog' },
    { category: '3D', name: 'Meshy', url: 'https://www.meshy.ai/blog' },
    { category: '3D', name: 'Hyper3D Rodin', url: 'https://hyper3d.ai/blog' },
    { category: '3D', name: 'CSM', url: 'https://www.csm.ai/blog' },
    { category: '3D', name: 'World Labs', url: 'https://www.worldlabs.ai/blog' },
    { category: '게임 에셋', name: 'Scenario', url: 'https://www.scenario.com/blog' },
    { category: '게임 에셋', name: 'Layer AI', url: 'https://www.layer.ai/blog' },
    { category: '모션', name: 'Rokoko', url: 'https://www.rokoko.com/insights' },
    { category: '모션', name: 'Reallusion', url: 'https://magazine.reallusion.com/' },
    { category: '모션', name: 'Autodesk', url: 'https://adsknews.autodesk.com/en/news/' },
    { category: '음악·음성', name: 'ElevenLabs', url: 'https://elevenlabs.io/blog' },
    { category: '음악·음성', name: 'Suno', url: 'https://suno.com/blog' },
    { category: '도구', name: 'ComfyUI', url: 'https://docs.comfy.org/changelog' },
    { category: '도구', name: 'NVIDIA', url: 'https://blogs.nvidia.com/' },
    { category: '도구', name: 'Hugging Face', url: 'https://huggingface.co/blog' },
    { category: '도구', name: 'fal.ai', url: 'https://blog.fal.ai/' },
    { category: '도구', name: 'Figma', url: 'https://www.figma.com/blog/' },
    { category: '도구', name: 'Blender', url: 'https://www.blender.org/news/' },
    { category: '도구', name: 'Anthropic', url: 'https://www.anthropic.com/news' },
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
   *   keywords:    ['3D', 'Blender'],      // 서브 카테고리 — 그 탭의 data/keywords.json 목록에 있는 값만
   *   url:         'https://...',          // 원문 링크
   *   urls: [                              // optional — 추가 관련 링크
   *     { label: '관련 보도', href: 'https://...' },
   *     { label: '공식 발표', href: 'https://...' },
   *   ],
   * }
   */
};
