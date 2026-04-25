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
   *   isNew:       true,                   // optional — 최근 3일 이내면 'NEW' 표시
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
            id:          'industry-15ed0ad1-2026-04',
            tab:         'industry',
            headline:    '구글 임원, 게임사 10곳 중 9곳이 AI 이미 사용 중',
            summary:     '구글 클라우드 게임 총괄 잭 뷰저가 대형 스튜디오 대부분이 이미 AI를 게임 개발에 활용 중이라고 밝혔다.',
            body:        '<p>구글 클라우드의 게임 총괄 책임자 잭 뷰저가 현재 출시된 게임 대부분이 이미 AI의 도움을 받아 만들어졌다고 주장해 업계 주목을 받고 있다.</p><p>뷰저는 지난 게임즈컴에서 전 세계 스튜디오를 대상으로 실시한 설문 결과, 응답자의 약 90%가 AI를 사용하고 있다고 답했다고 전했다. 다른 기관 조사에서 나오는 40~50% 수치와의 차이는 공개 꺼림칙함 때문이라고 설명했다.</p><p>AI 사용이 논쟁적 주제인 만큼 많은 스튜디오가 공개적으로 밝히길 꺼리지만, 실제로는 이미 광범위하게 쓰인다는 점이 다시 확인됐다.</p><p>뷰저는 인터뷰에서 구글 클라우드의 Gemini 등 AI 도구들이 일부 스튜디오에서 개발 과정의 단조롭고 반복적인 작업을 줄이는 데 활용되고 있다고 설명했다.</p><p>그는 "플레이어들이 깨닫지 못하는 것은, 지금 즐기고 있는 게임들이 이미 AI로 만들어졌다는 사실"이라고 말했다. "게임즈컴에서 전 세계 스튜디오를 대상으로 설문했는데, 10명 중 약 9명이 \'AI를 사용한다\'고 답했다"고 덧붙였다.</p><p>캡콤의 사례도 소개됐다. 캡콤은 구글 AI 도구를 활용해 세계관 구성 요소 아이디어를 빠르게 생성하는 데 사용하고 있으며, 이를 통해 크리에이티브 팀이 주요 캐릭터와 핵심 장면 같은 높은 가치의 창작 작업에 집중할 수 있게 된다고 밝혔다. 다만 캡콤은 생성형 AI 에셋을 최종 게임에 포함시키지는 않겠다는 입장을 유지하고 있다.</p><p>뷰저는 또한 "플레이어들이 AI가 자신이 좋아하는 게임 일부에 사용됐음을 알게 되면 더 수용적인 태도를 보일 수 있다"고 제안했다. "이것이 실제로 더 빠르게 좋아하는 게임을 받을 수 있도록 도와준다는 걸 깨닫게 될 것이며, 한 게임을 7년 기다리는 일은 없어질 것"이라고 말했다.</p><p>한편 GDC 2026 게임 산업 현황 보고서에 따르면 업계 종사자의 52%가 생성형 AI에 부정적 입장을 취하고 있어, 실제 사용 현황과 업계 감정 사이의 간극이 크다는 점도 드러났다.</p><p>원문: <a href="https://www.videogameschronicle.com/news/their-favourite-games-were-already-built-with-ai-google-exec-says-almost-every-studio-uses-ai-but-not-all-disclose-it/">Video Games Chronicle</a></p>',
            source:      'Video Games Chronicle',
            publishedAt: '2026.04.25',
            isNew:       true,
            hue:         210,
            image:       'https://www.videogameschronicle.com/files/2025/09/resident-evil-requiem-pic7.jpg',
            url:         'https://www.videogameschronicle.com/news/their-favourite-games-were-already-built-with-ai-google-exec-says-almost-every-studio-uses-ai-but-not-all-disclose-it/',
        },
        {
            id:          'industry-b7862575-2026-04',
            tab:         'industry',
            headline:    '모건스탠리, AI 활용 시 게임 산업 연간 220억 달러 이익 가능',
            summary:     '모건스탠리 분석가들이 AI로 개발 비용을 최대 절반까지 줄이면 게임사들이 연 220억 달러 이익을 창출할 수 있다고 분석했다.',
            body:        '<p>월가의 대형 투자은행 모건스탠리가 AI 도구 활용이 게임 산업의 수익성을 획기적으로 끌어올릴 수 있다는 분석 보고서를 내놓았다.</p><p>분석에 따르면 게임사들이 AI로 개발 비용을 약 50% 줄인다면 연간 약 220억 달러(약 30조 원)의 이익 창출이 가능하다고 한다. 현재 글로벌 게임 소비자 지출이 연 2,750억 달러이며, 그 중 약 20%가 개발 및 운영에 재투자된다.</p><p>게임 개발에 드는 막대한 시간과 비용을 AI로 줄일 수 있다면, 업계 구조가 근본적으로 바뀔 수 있다는 전망이다.</p><p>로이터 보도에 따르면 모건스탠리 애널리스트들은 게임 환경 제작, 대화 생성, 소프트웨어 테스트 자동화 등에 AI를 활용하면 개발 기간과 비용을 크게 단축할 수 있어 마진이 개선될 것이라고 전망했다.</p><p>보고서는 Grand Theft Auto 시리즈 사례를 예로 들며, 타이틀 간 8년의 간격이 발생할 만큼 게임 개발이 얼마나 비용이 많이 들고 노동 집약적인지를 지적했다. AI를 통해 더 작은 팀이 협업하고, 출시 후 개선도 더 빠르게 진행할 수 있다는 것이 핵심 주장이다.</p><p>다만 모든 게임사가 같은 수준의 혜택을 누리지는 못할 것이라는 전망도 담겼다. 모건스탠리는 "독점 데이터, IP, 라이브 운영 기반을 보유한 플랫폼에 가치가 집중될 것"이라며, "유통, 데이터, 참여도를 통제하는 기업이 최대 수혜자가 될 수 있다"고 분석했다.</p><p>이번 보고서는 AI가 게임 산업의 비즈니스 모델 자체를 근본적으로 변화시킬 수 있음을 시사한다는 점에서 주목받고 있다. 소규모 팀도 대형 퍼블리셔와 경쟁할 수 있는 환경이 만들어질 수 있기 때문이다.</p><p>원문: <a href="https://www.pymnts.com/artificial-intelligence-2/2026/morgan-stanley-says-gaming-could-score-22-billion-with-ai/">PYMNTS</a></p>',
            source:      'PYMNTS',
            publishedAt: '2026.04.25',
            isNew:       true,
            hue:         220,
            image:       'https://www.pymnts.com/wp-content/uploads/2026/04/Morgan-Stanley-gaming-AI.png',
            url:         'https://www.pymnts.com/artificial-intelligence-2/2026/morgan-stanley-says-gaming-could-score-22-billion-with-ai/',
        },

    /* ---- art ---- */
        {
            id:          'art-4cd35d15-2026-04',
            tab:         'art',
            headline:    'OpenAI의 AI 영상 서비스 Sora, 내일(26일) 종료',
            summary:     'OpenAI가 AI 영상 생성 서비스 Sora 앱을 4월 26일 종료한다고 밝혔다. API는 9월 24일까지 운영 후 종료될 예정이다.',
            body:        '<p>OpenAI의 AI 영상 생성 서비스인 Sora가 내일(4월 26일) 공식 앱 서비스를 종료한다. 2025년 9월 출시 이후 약 반 년 만에 막을 내리는 것이다.</p><p>종료 배경에는 천문학적인 운영 비용(일부 추정치에 따르면 하루 최대 1,500만 달러)과 가입자 급감이 있다. 출시 초기 100만 명을 넘겼던 월간 사용자는 올해 1월 기준 전월 대비 45%나 감소했다.</p><p>AI 영상 생성 분야의 선구자였던 Sora의 폐막은 생성형 AI 업계 전반에 시사하는 바가 크다. 영상 생성이 텍스트 대비 약 2,000배 비싸다는 경제적 현실이 결국 걸림돌이 됐다.</p><p>OpenAI는 공식 X 계정을 통해 "Sora 앱을 종료한다. Sora로 창작하고, 공유하고, 커뮤니티를 만들어 준 모든 분께 감사드린다. 여러분이 Sora로 만들어낸 것들은 의미가 있었고, 이 소식이 실망스럽다는 걸 안다"고 전했다.</p><p>Sora 앱은 AI가 생성한 콘텐츠를 독점적으로 게시하는 소셜 미디어 형태의 서비스였다. 구독 없이도 누구나 매우 사실적인 AI 영상을 생성할 수 있어 큰 반향을 일으켰으며, 이로 인해 딥페이크 문제와 소위 \'AI 슬롭\'이라 불리는 저품질 AI 콘텐츠에 대한 우려도 함께 커졌다.</p><p>Sora 팀 리드 빌 피블스는 지난 10월에 이미 "현재 경제성은 완전히 지속 불가능하다"고 X에서 인정한 바 있다. 영상 생성은 수백 프레임을 노이즈 제거하고 렌더링해야 하기 때문에, 텍스트 생성 대비 에너지 소비량이 훨씬 높다.</p><p>이 결정은 디즈니에도 영향을 미쳤다. 디즈니는 Sora를 통해 약 10억 달러 규모의 투자를 계획했으나, 서비스 종료 발표 후 해당 계획이 무산된 것으로 알려졌다. API의 경우 9월 24일까지 운영이 유지되므로, API 사용자들은 그때까지 시간 여유가 있다.</p><p>현재 콘텐츠를 보존하고 싶은 사용자는 sora.chatgpt.com/exports/me에서 내보내기 기능을 이용해야 하며, OpenAI는 서비스 종료 이후 콘텐츠 복구를 보장하지 않는다고 밝혔다.</p><p>원문: <a href="https://www.liubknews.com/post/sora-ai-shuts-down-why-and-what-this-means-for-tech">Liubk News</a></p>',
            source:      'Liubk News',
            publishedAt: '2026.04.25',
            isNew:       true,
            hue:         270,
            image:       'https://static.wixstatic.com/media/f96851_56ddce71a8064e7f86804582b81e0dfd~mv2.png/v1/fill/w_638,h_634,al_c,q_90/f96851_56ddce71a8064e7f86804582b81e0dfd~mv2.png',
            url:         'https://www.liubknews.com/post/sora-ai-shuts-down-why-and-what-this-means-for-tech',
            urls: [
                { label: '공식 안내', href: 'https://help.openai.com/en/articles/20001152-what-to-know-about-the-sora-discontinuation' },
                { label: '관련 보도', href: 'https://the-decoder.com/openai-sets-two-stage-sora-shutdown-with-app-closing-april-2026-and-api-following-in-september/' },
            ],
        },
        {
            id:          'art-ebe9f929-2026-04',
            tab:         'art',
            headline:    'OpenAI, ChatGPT Images 2.0 공개—한번에 8장 일관성 유지',
            summary:     'OpenAI가 새로운 이미지 생성 모델 ChatGPT Images 2.0을 공개했다. 2K 해상도와 멀티언어 텍스트, 한 번에 최대 8장의 일관된 이미지 생성이 특징이다.',
            body:        '<p>OpenAI가 4월 21일 새 이미지 생성 모델 \'ChatGPT Images 2.0\'을 공개했다. 이전 모델보다 훨씬 정밀한 텍스트 렌더링과 다국어 지원, 그리고 \'생각하는 능력\'이 추가됐다.</p><p>가장 눈길을 끄는 기능은 한 번의 프롬프트로 최대 8장의 이미지를 생성하면서도 캐릭터와 오브젝트의 일관성을 유지한다는 점이다. 스토리보드나 브랜드 캠페인 제작에 특히 유용하다.</p><p>멀티언어 텍스트 렌더링 정확도가 95% 이상에 달하며, 사진·일러스트·망가·픽셀아트 등 다양한 스타일을 지원한다는 점에서 크리에이터들의 기대가 크다.</p><p>ChatGPT Images 2.0은 gpt-image-2 모델을 기반으로 하며, 최대 2K 해상도와 3:1(초광각)에서 1:3(초세로)에 이르는 다양한 화면비를 지원한다. 라틴어, 중국어, 일본어, 한국어, 아랍어 등 다양한 문자 체계에서 95% 이상의 텍스트 렌더링 정확도를 자랑한다.</p><p>\'생각 기능\'은 모델이 웹을 검색하고 여러 이미지를 생성한 뒤 결과물을 스스로 검토하는 능력을 부여한다. 이를 통해 다양한 크기의 마케팅 에셋, 여러 패널로 구성된 만화 스트립 등을 생성할 수 있다.</p><p>VentureBeat는 이 모델이 다국어 텍스트, 전체 인포그래픽, 슬라이드, 지도, 심지어 망가까지 "거의 완벽하게" 처리한다고 평가했다. 특히 소셜 미디어 비주얼, 마케팅 배너, 광고 소재 초안 작성 등에서 유용성이 두드러진다.</p><p>ChatGPT Plus, Pro, Business, Enterprise 구독자는 4월 21일부터 Images 2.0에 접근할 수 있으며, gpt-image-2 API도 함께 공개됐다. API 가격은 출력 품질과 해상도에 따라 달라진다. 출력의 배치 API 사용 시 50% 할인이 적용된다.</p><p>원문: <a href="https://openai.com/index/introducing-chatgpt-images-2-0/">OpenAI</a></p>',
            source:      'OpenAI',
            publishedAt: '2026.04.25',
            isNew:       true,
            hue:         265,
            url:         'https://openai.com/index/introducing-chatgpt-images-2-0/',
            urls: [
                { label: '관련 보도', href: 'https://venturebeat.com/technology/openais-chatgpt-images-2-0-is-here-and-it-does-multilingual-text-full-infographics-slides-maps-even-manga-seemingly-flawlessly' },
            ],
        },

  ],
};
