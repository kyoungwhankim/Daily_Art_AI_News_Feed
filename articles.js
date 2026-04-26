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
   *   headline:    '한국어 제목',
   *   summary:     '한 줄 요약',
   *   body:        '<p>본문 첫 문단</p><p>두 번째 문단…</p>',  // 카드 클릭 시 모달 본문 (HTML 허용)
   *   source:      '출처',
   *   publishedAt: '2026.04.25',           // 'YYYY.MM.DD' 형식, 사이트 업로드 날짜 (정렬·날짜 헤더에 사용; 화면에는 그대로 표시됨)
   *   hue:         30,                     // 0–360, 그라디언트 썸네일 색상
   *   image:       'assets/news/x.jpg',    // optional — 있으면 그라디언트 대신 이미지 사용
   *   url:         'https://...',          // 원문 링크
   *   urls: [                              // optional — 추가 관련 링크
   *     { label: '관련 보도', href: 'https://...' },
   *     { label: '공식 발표', href: 'https://...' },
   *   ],
   * }
   */
  articles: [
    /* ---- games ---- */
        
    /* ---- industry ---- */
        {
            id:          'industry-ce8307d6-2026-04',
            tab:         'industry',
            headline:    '\'AI 없이 만든 게임\'이 새로운 프리미엄 마케팅 전략으로 부상',
            summary:     'GDC 2026 설문에서 게임 업계 종사자의 52%가 생성형 AI에 부정적 입장을 밝힌 가운데, 인디 개발사들이 \'AI 미사용\'을 핵심 차별화 요소로 내세우는 마케팅 트렌드가 확산하고 있다',
            body:        '<p>\'핸드메이드\', \'수제\', \'인간이 만든\'이라는 표현이 식품·패션 업계처럼 이제 게임 시장에서도 프리미엄 브랜드 신호가 되고 있습니다!</p><p>GDC 2026 보고서에 따르면 게임 업계 종사자의 52%가 생성형 AI를 부정적으로 바라보고 있습니다. 2024년 18%, 2025년 30%에서 급격히 상승한 수치예요. 한편 소형 게임 플랫폼 Playdate Catalog는 4월 중 AI 생성 아트·음악·텍스트 게임의 신규 등록을 전면 금지했고, Steam도 AI 사용 여부 공시를 의무화했습니다.</p><p>반면 AI를 적극 활용하는 대형 스튜디오는 여전히 공시를 꺼리는 경향이 있어, \'AI 공개\'와 \'AI 없음 마케팅\' 사이의 간극이 점점 벌어지고 있어요.</p><p>인디 개발자들은 AI를 쓰지 않는다는 사실을 윤리, 장인 정신, 노동 존중의 관점에서 적극 홍보하고 있습니다. 이는 자동화 중심 대형 스튜디오와 차별화하며, \'의도적으로 선택된 창작물\'이라는 인식을 주는 전략입니다. 실제로 일부 플레이어들은 AI 미사용 게임에서 더 높은 \'저작 의도\'를 느낀다고 응답했습니다.</p><p>현재 게임 업계는 AI 활용 증가와 그에 대한 반발이 동시에 진행 중입니다. 36%의 종사자는 이미 생성형 AI 도구를 사용하고 있지만, 지난 2년간 전체의 25% 이상이 정리해고를 경험했습니다. \'AI 프리\'가 마케팅 전략으로 자리 잡는 현상은 이 갈등을 단적으로 보여줍니다.</p><p>원문: <a href="https://www.wokewaves.com/posts/ai-free-games-2026-trend">Woke Waves</a></p>',
            source:      'Woke Waves',
            publishedAt: '2026.04.26',
            hue:         130,
            image:       'https://cdn.prod.website-files.com/65c66d9aede3cf8a571e64b2/69ec212efd964447a2cd8c97_Woke%20Waves%20photo%20template%20(1420%20x%20680%20px)%20(1420%20x%20680%20px)%20(42)%20(1).jpg',
            url:         'https://www.wokewaves.com/posts/ai-free-games-2026-trend',
        },
        
    /* ---- art ---- */
        {
            id:          'art-ce2af83f-2026-04',
            tab:         'art',
            headline:    '세계 최초 AI 아트 전문 뮤지엄 \'Dataland\', 6월 LA 개관',
            summary:     '터키계 미국인 아티스트 리픽 아나돌이 로스앤젤레스에 AI 전용 미술관 Dataland를 설립해 오는 6월 20일 개관 예정이라고 밝혔다',
            body:        '<p>드디어 AI 아트만을 위한 세계 최초의 전문 미술관이 탄생합니다! 미국 로스앤젤레스에서 역사적인 일이 일어나고 있어요.</p><p>세계적인 AI 아티스트 리픽 아나돌과 공동 설립자 에프순 에르클르치가 LA 다운타운 더 그랜드 LA에 AI 아트 전문 뮤지엄 \'Dataland\'를 세웠습니다. 개관일은 2026년 6월 20일이고, 3만 5,000평방피트 규모에 5개의 완전 몰입형 360도 갤러리로 구성됩니다.</p><p>AI 작품이 독립된 기관을 갖게 됐다는 것은 AI 아트가 주류 예술계에서 정식으로 인정받기 시작했다는 중요한 신호예요.</p><p>첫 번째 전시 \'Machine Dreams: Rainforest\'는 수백만 장의 자연 이미지와 사운드를 기반으로 한 몰입형 시청각 체험입니다. 아나돌과 에르클르치가 아마존 우림을 직접 방문한 경험에서 영감을 받아 제작됐으며, 인간과 기계 지능이 맺는 관계를 자연의 언어로 표현합니다. 아나돌은 이 프로젝트를 두고 \'내 평생의 여정\'이라고 밝혔습니다.</p><p>Dataland는 민간 자본으로 운영되며, 프랭크 게리가 설계한 LA 그랜드 애비뉴 문화 지구 복합시설에 자리합니다. \'세계 최초 AI 아트 전문 뮤지엄\'이라는 타이틀을 내걸고 창작과 기술의 경계를 탐구하는 새로운 문화 공간으로 주목받고 있습니다.</p><p>원문: <a href="https://www.kunm.org/npr-news/2026-04-25/new-museum-dedicated-to-ai-promises-an-ethical-approach">NPR</a></p>',
            source:      'NPR',
            publishedAt: '2026.04.26',
            hue:         270,
            image:       'https://npr.brightspotcdn.com/dims4/default/9f69b34/2147483647/strip/true/resize/880x%5E/quality/90/?url=https%3A%2F%2Fnpr.brightspotcdn.com%2Fdims3%2Fdefault%2Fstrip%2Ffalse%2Fcrop%2F11656x8742%200%200%2Fresize%2F11656x8742%21%2F%3Furl%3Dhttp%3A%2F%2Fnpr-brightspot.s3.amazonaws.com%2Fa6%2F13%2F20c3e7b74ac9a20ecb24e002dcdc%2Fgallery-c-infinity-room-9.jpg',
            url:         'https://www.kunm.org/npr-news/2026-04-25/new-museum-dedicated-to-ai-promises-an-ethical-approach',
        },
        {
            id:          'art-a83a1059-2026-04',
            tab:         'art',
            headline:    '루마 Uni-1, \'생각하고 상상하는\' 새로운 AI 이미지 모델 등장',
            summary:     '루마 AI가 언어로 사고하고 픽셀로 상상하는 멀티모달 추론 이미지 모델 Uni-1을 출시해 AI 이미지 생성의 새로운 패러다임을 제시했다',
            body:        '<p>AI 이미지 생성 모델이 이제 \'생각하면서\' 그림을 그립니다. 루마 AI가 기존 확산 모델과는 전혀 다른 방식의 새 모델을 선보였어요.</p><p>루마 AI의 Uni-1은 자기회귀 트랜스포머 아키텍처를 기반으로 텍스트와 이미지를 순차적으로 처리합니다. 모델은 먼저 프롬프트를 분해하고, 구도와 공간 관계를 계획한 뒤에야 이미지를 생성합니다. \'언어로 생각하고 픽셀로 상상한다\'는 표현이 딱 맞는 접근 방식이죠.</p><p>레퍼런스 이미지를 기반으로 인물 정체성을 보존하며 생성하는 기능, 다양한 편집과 반복 작업 지원, 루마 에이전트와의 통합이 핵심 강점입니다. 단순한 텍스트-이미지 변환을 넘어 복잡한 창작 워크플로에 맞는 도구를 지향합니다.</p><p>실제 기업 활용 사례도 주목받고 있습니다. Uni-1이 통합된 루마 에이전트는 어드버스, 마즈다 같은 브랜드가 제품 이미지 한 장과 간단한 브리프만으로 광고 캠페인 전체를 40시간, 2만 달러 이하에 완성할 수 있도록 지원했습니다. 기존 1,500만 달러짜리 캠페인을 대체한 셈입니다.</p><p>루마에 따르면 Uni-1은 스타일, 편집, 레퍼런스 기반 생성 분야에서 인간 선호도 평가 1위를 기록했습니다. 텍스트-이미지 변환 부문에서는 2위에 올랐습니다.</p><p>원문: <a href="https://www.progressiverobot.com/2026/04/25/uni-1-by-luma/">Progressive Robot</a></p>',
            source:      'Progressive Robot',
            publishedAt: '2026.04.26',
            hue:         215,
            image:       'https://www.progressiverobot.com/wp-content/smush-webp/2026/04/uni-1-by-luma-featured-16x9-1.jpg.webp',
            url:         'https://www.progressiverobot.com/2026/04/25/uni-1-by-luma/',
        },
        {
            id:          'art-54604698-2026-04',
            tab:         'art',
            headline:    'xAI 그록 이매진, 완벽한 입술 싱크·음향으로 업그레이드',
            summary:     'xAI의 이미지-투-비디오 생성 도구 그록 이매진이 자연스러운 입술 움직임과 선명한 오디오 싱크를 갖춘 최신 업데이트를 선보이며 소셜미디어에서 폭발적 반응을 얻었다',
            body:        '<p>AI 영상 생성의 \'불쾌한 골짜기\'를 드디어 넘었습니다! 일론 머스크가 직접 올린 영상 하나가 AI 창작 커뮤니티를 뒤흔들었어요.</p><p>xAI의 그록 이매진이 업데이트되면서 입술과 발화 내용이 실제 사람처럼 자연스럽게 일치하는 수준에 도달했습니다. 머스크는 X에 \'New Grok Imagine model just dropped with much better lip sync & sound. Nothing in this video is real\'이라는 글과 함께 데모 영상을 게시했고, 영상은 순식간에 수백만 건의 조회수를 기록했습니다.</p><p>진짜인지 가짜인지 구분하기 어려울 만큼 자연스러운 동영상이 손쉽게 만들어지게 됐다는 점에서 창작의 가능성과 딥페이크 위험에 대한 논쟁이 동시에 불거졌어요.</p><p>이번 업데이트는 더 큰 학습 데이터셋, 정제된 확산 기법, X 사용자들의 실시간 피드백을 반영해 이루어졌습니다. 물리 시뮬레이션 개선과 프롬프트 일치도 향상도 함께 적용됐습니다. Grok 4.3 Beta 기반으로 구동되며, X 프리미엄 및 슈퍼그록 구독자라면 바로 이용할 수 있습니다.</p><p>사용자들은 역사적 인물의 연설부터 포토리얼리스틱 캐릭터 영상까지 다양한 콘텐츠를 쏟아내고 있습니다. 창작 가능성에 열광하는 반응과 함께, 영상 미디어의 진위 판별이 점점 어려워진다는 우려도 함께 제기되고 있습니다.</p><p>원문: <a href="https://www.eyerys.com/articles/news/grok-imagine-upgrade-brings-sharper-audio-and-flawless-lip-sync-image-video">Eyerys</a></p>',
            source:      'Eyerys',
            publishedAt: '2026.04.26',
            hue:         335,
            image:       'https://www.eyerys.com/sites/default/files/grok-592.avif',
            url:         'https://www.eyerys.com/articles/news/grok-imagine-upgrade-brings-sharper-audio-and-flawless-lip-sync-image-video',
        },
        {
            id:          'art-c95c17e9-2026-04',
            tab:         'art',
            headline:    '오픈AI 소라(Sora) 앱·웹, 오늘부로 공식 서비스 종료',
            summary:     '오픈AI가 AI 영상 생성 서비스 소라의 앱과 웹 플랫폼을 2026년 4월 26일 오늘부로 종료했으며, API는 9월까지 유지된다고 밝혔다',
            body:        '<p>화제를 모았던 AI 영상 생성 서비스 소라가 오늘 드디어 막을 내립니다. 불과 15개월 만의 일이에요.</p><p>오픈AI는 소라의 앱과 웹 플랫폼(sora.chatgpt.com)을 4월 26일 종료하고, API 접근권은 9월 24일까지 유지한다고 발표했습니다. 사용자들은 Sora 라이브러리에서 직접 기존 콘텐츠를 내보낼 수 있으며, 기한 내 내보내기하지 않으면 데이터는 영구 삭제됩니다.</p><p>2024년 12월 화려하게 출시된 소라가 채 1년 반을 못 채우고 종료되는 건데요, AI 영상 생성 시장의 냉혹한 현실을 보여주는 사례로 주목받고 있어요.</p><p>종료의 주된 이유는 지속 불가능한 운영 비용입니다. 최대 하루 1,500만 달러에 달하는 추론 비용에 비해 6개월간 총 앱 수익은 210만 달러에 그쳤습니다. 월간 다운로드 수도 고점 대비 66% 급감했으며, 디즈니와 추진하던 10억 달러 규모의 라이선스 계약도 최종 발표 1시간 전에 취소 통보를 받았습니다.</p><p>오픈AI는 컴퓨팅 자원을 기업용 코딩 도구와 통합 데스크톱 앱으로 재배치하기로 했습니다. 소라는 \'세계 시뮬레이션\' 연구 프로젝트 형태로 계속 이어지지만, 소비자 서비스로서의 소라는 오늘로 역사 속으로 사라집니다.</p><p>원문: <a href="https://www.liubknews.com/post/sora-ai-shuts-down-why-and-what-this-means-for-tech">LiubkNews</a></p>',
            source:      'LiubkNews',
            publishedAt: '2026.04.26',
            hue:         8,
            url:         'https://www.liubknews.com/post/sora-ai-shuts-down-why-and-what-this-means-for-tech',
            urls: [
                { label: '공식 발표', href: 'https://help.openai.com/en/articles/20001152-what-to-know-about-the-sora-discontinuation' },
            ],
        },
        
 
  ],
};
