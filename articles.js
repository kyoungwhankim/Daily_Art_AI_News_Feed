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
            id:          'industry-fb9b4156-2026-04',
            tab:         'industry',
            headline:    '구글 임원 "스튜디오 90%, AI 쓰면서도 공개 안 해"',
            summary:     '구글 클라우드 잭 뷰저 이사가 게임스컴 설문을 인용해 \'스튜디오 10곳 중 9곳이 AI 사용 중\'이라고 밝혔다. 대부분의 스튜디오는 여론 반발을 우려해 이 사실을 공개하지 않는다.',
            body:        '<p>구글 클라우드의 게임 부문 총괄 이사 잭 뷰저(Jack Buser)가 "지금 플레이어들이 즐기는 게임 대부분은 이미 AI로 만들어진 것"이라고 밝혀 업계의 이목을 집중시켰다.</p><p>뷰저는 게임스컴(Gamescom) 현장에서 진행된 설문 결과를 인용, "게임 개발자 10명 중 9명이 \'AI 도구를 사용 중\'이라고 답했다"고 밝혔다. 그러나 GDC의 공식 개발자 조사에선 AI 사용률이 약 36%로 집계되는 등 공개 수치와 실제 현황 사이에 큰 괴리가 있다는 게 그의 주장이다.</p><p>왜 스튜디오들은 침묵할까. 뷰저에 따르면 많은 기업들이 여론 반발과 브랜드 이미지 훼손을 우려해 AI 도입 사실을 대외적으로 밝히지 않는다. \'AI가 인간의 창의성을 대체한다\'는 인식이 게이머 사이에 확산되면서, 스튜디오들은 조용히, 그러나 적극적으로 AI를 도입하는 이중적 행보를 보이고 있다.</p><p>실제 사례로 뷰저는 캡콤을 언급했다. 캡콤은 구글의 AI 도구(Gemini, Nano Banana Pro 등)를 활용해 오픈 월드를 채우는 배경 아트와 소품 등 보조 에셋을 AI로 제작하고 있다. 핵심 캐릭터와 스토리 관련 자산은 여전히 인간 아티스트가 담당하지만, 반복적이고 대량으로 필요한 배경 요소에는 AI가 빠르게 투입되고 있다.</p><p>뷰저는 AI의 핵심 가치로 개발 속도 혁신을 꼽았다. "과거엔 게임 1개 제작에 7년이 걸렸지만, 이제 같은 시간에 5개를 만들 수 있다"는 것이다. 한편 모건 스탠리는 AI 기반 비용 절감이 게임 산업에 연간 최대 220억 달러(약 30조 원)의 추가 수익을 창출할 수 있다고 전망한 바 있다.</p><p>원문: <a href="https://futurism.com/artificial-intelligence/google-exec-video-games-secretly-ai">Futurism</a></p>',
            source:      'Futurism',
            publishedAt: '2026.04.26',
            hue:         20,
            url:         'https://futurism.com/artificial-intelligence/google-exec-video-games-secretly-ai',
        },
        
    /* ---- art ---- */
        {
            id:          'art-b05348a3-2026-04',
            tab:         'art',
            headline:    '세계 최초 AI 아트 전문 미술관, LA에서 6월 개관',
            summary:     '레픽 아나돌의 \'데이터랜드\'가 6월 20일 LA 다운타운에서 개관을 앞두고 있으며, 생성 AI 예술의 윤리적 가능성을 탐구한다고 밝혔다.',
            body:        '<p>세계 최초의 AI 아트 전문 미술관 \'데이터랜드(Dataland)\'가 오는 6월 20일 LA 다운타운에 문을 연다!</p><p>터키계 미국인 아티스트 레픽 아나돌이 공동 설립한 이 미술관은 프랭크 게리가 설계한 \'더 그랜드 LA\' 복합단지 내 3만 5,000 제곱피트 공간에 5개의 몰입형 갤러리를 갖추고 있다.</p><p>단순한 AI 생성 이미지를 넘어 \'책임감 있는 AI 예술\'이란 무엇인지를 묻는 실험적 공간이어서 주목된다.</p><p>개관 첫 전시는 아나돌의 \'머신 드림스: 레인포레스트(Machine Dreams: Rainforest)\'로, 전 세계 16개 열대우림에서 직접 수집한 수백만 건의 자연 이미지와 사운드를 기반으로 만든 거대 언어 모델(LNM)을 활용한 몰입형 시청각 설치 작품이다. 스미소니언, 코넬 조류연구소, 게티 등 권위 있는 기관들과의 데이터 파트너십도 맺었다.</p><p>미술관은 지속 가능성에도 집중했다. 오리건주 구글 클라우드 서버를 활용해 87% 탄소 제로 재생에너지로 운영되며, 방문객 한 명이 경험 전체에 사용하는 전력은 스마트폰 충전 한 번에 해당하는 수준이라고 아나돌은 설명했다. AI 아트에 대한 저작권·편향성 논란이 이어지는 가운데, 데이터랜드는 허가 기반 데이터셋과 완전한 투명성을 통해 새로운 기준을 제시하겠다고 강조했다.</p><p>원문: <a href="https://www.npr.org/2026/04/25/nx-s1-5799511/dataland-refik-anadol-los-angeles-ai-art-museum">NPR</a></p>',
            source:      'NPR',
            publishedAt: '2026.04.26',
            hue:         270,
            image:       'https://npr.brightspotcdn.com/dims3/default/strip/false/crop/11656x8742+0+0/resize/1100/quality/50/format/jpeg/?url=http%3A%2F%2Fnpr-brightspot.s3.amazonaws.com%2Fa6%2F13%2F20c3e7b74ac9a20ecb24e002dcdc%2Fgallery-c-infinity-room-9.jpg',
            url:         'https://www.npr.org/2026/04/25/nx-s1-5799511/dataland-refik-anadol-los-angeles-ai-art-museum',
            urls: [
                { label: '공식 사이트', href: 'https://dataland.art/' },
            ],
        },
        {
            id:          'art-50937f7b-2026-04',
            tab:         'art',
            headline:    '오픈소스 AI 창작 도구 ComfyUI, 5억 달러 가치로 3천만 달러 조달',
            summary:     '생성 AI 출력물을 노드 방식으로 세밀하게 제어하는 ComfyUI가 시리즈 B로 3천만 달러를 유치하며 5억 달러 기업 가치를 인정받았다.',
            body:        '<p>크리에이터들이 AI 이미지·영상·오디오를 정밀하게 제어할 수 있게 해주는 ComfyUI가 시리즈 B 투자로 3천만 달러를 조달하며 5억 달러 기업 가치를 인정받았다!</p><p>이번 라운드는 Craft Ventures가 주도했고, Pace Capital·Chemistry·TruArrow 등이 참여했다. ComfyUI는 2023년 오픈소스 프로젝트로 시작해 2024년 말 시리즈 A로 1,900만 달러를 조달한 데 이어 이번에도 빠른 성장을 보여줬다.</p><p>미드저니나 ChatGPT 같은 단일 프롬프트 기반 툴이 60~80% 정도의 완성도에 그치는 반면, ComfyUI의 노드 기반 인터페이스는 생성 과정의 각 단계를 분리해 원하는 요소만 수정할 수 있어 \'AI 슬롭\' 넘쳐나는 시대에 특히 주목받고 있다.</p><p>현재 400만 명 이상의 사용자를 보유한 ComfyUI는 VFX, 애니메이션, 광고, 산업 디자인 등 다양한 전문 분야에서 쓰이고 있으며, 스튜디오 구인 공고에 \'ComfyUI 아티스트·엔지니어\'라는 직함이 등장할 만큼 크리에이티브 산업의 핵심 도구로 자리 잡았다. CEO 요란 옌은 "AI 슬롭이 범람하는 세상에서 인간 개입 방식의 ComfyUI 접근법이 결국 주목받게 될 것"이라고 강조했다.</p><p>원문: <a href="https://techcrunch.com/2026/04/24/comfyui-hits-500m-valuation-as-creators-seek-more-control-over-ai-generated-media/">TechCrunch</a></p>',
            source:      'TechCrunch',
            publishedAt: '2026.04.26',
            hue:         210,
            image:       'https://techcrunch.com/wp-content/uploads/2026/04/ComfyUI-Co-founders-1.png?w=1024',
            url:         'https://techcrunch.com/2026/04/24/comfyui-hits-500m-valuation-as-creators-seek-more-control-over-ai-generated-media/',
            urls: [
                { label: '공식 사이트', href: 'https://www.comfy.org/' },
            ],
        },
      
  ],
};
