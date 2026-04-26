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
        {
            id:          'games-3ba27897-2026-04',
            tab:         'games',
            headline:    'Reallusion, 2026 로드맵에서 \'하이브리드 AI\' 3D 캐릭터 제작 공개',
            summary:     'Reallusion이 Character Creator와 iClone에 AI 이미지-투-3D, 실시간 페이셜 모캡, RTX 렌더링을 결합한 2026 하이브리드 AI 로드맵을 공개했다.',
            body:        '<p>3D 캐릭터·애니메이션 툴 전문 기업 Reallusion이 2026년 기술 로드맵을 공개하며 AI와 전통 3D 워크플로를 결합한 \'하이브리드 미디어 창작\' 비전을 내세웠다.</p><p>핵심은 AI 이미지-투-3D 헤드 재구성 플러그인 Headshot 3, 웹캠·영상 기반 정밀 페이셜 모캡 AccuFace 2, NVIDIA와 협업한 RTX 패스 트레이스 렌더링, 그리고 AI 생성 3D 모델을 Character Creator 표준 토폴로지로 변환하는 CC Wrap이다.</p><p>AI 생성 캐릭터를 애니메이션 파이프라인에 손쉽게 통합할 수 있는 길이 열렸다는 점에서 게임·영상 제작자들의 기대를 모으고 있다.</p><p>Reallusion의 2026 로드맵은 AI 혁명이 크리에이티브 환경을 재편하는 시점에서 자사 도구를 하이브리드 미디어 창작의 최전선에 두겠다는 전략을 담고 있다. 생성 단계에 강력한 AI를 접목하는 동시에 전통 3D 워크플로의 한계를 계속 밀어붙이겠다는 것이다.</p><p>Headshot 3는 2D 사진 한 장으로 정확한 3D 두상을 재구성하는 독자 AI 모델을 탑재한다. 방대한 얼굴 스캔 데이터셋으로 훈련한 이 모델은 얼굴 랜드마크·깊이 단서·해부학적 특징을 더 정밀하게 해석해 토폴로지가 개선된 메시와 높은 정체성 보존력을 제공한다. 텍스트 프롬프트에서 4K AI 이미지 생성, 스플라인 기반 두상 정제, 내장 렌즈 교정 기능도 함께 제공된다.</p><p>AccuFace 2는 Character Creator 5의 HD 페이셜 프로파일에 맞춰 새로 훈련한 트래킹 시스템을 채택해, 섬세한 고주파 립싱크 디테일과 자연스러운 표정을 실시간으로 캡처한다. 라이브 웹캠 입력과 영상 기반 트래킹을 모두 지원한다.</p><p>RTX 렌더링은 NVIDIA와의 긴밀한 협업으로 개발됐으며, Character Creator와 iClone에 무료 업데이트로 제공된다. NVIDIA RTX GPU와 DLSS 기술을 활용해 시네마틱급 패스 트레이스 렌더링을 거의 실시간 속도로 구현한다. 디지털 휴먼 셰이더에 최적화되어 머리카락·피부·서브서페이스 스캐터링을 정밀하게 제어할 수 있다.</p><p>CC Wrap은 AI 생성 3D 모델이나 일반 3D 모델·의상 메시를 Character Creator 표준 토폴로지로 감싸는 도구다. AI가 생성한 정적 에셋을 전문 애니메이션 파이프라인에 통합하려는 업계의 요구를 직접 겨냥한 것으로, Reallusion 생태계 전반에서 재사용할 수 있는 게임 레디 캐릭터를 빠르게 제작할 수 있게 한다.</p><p>원문: <a href="https://www.cgchannel.com/2026/04/see-reallusions-2026-roadmap-redefining-3d-with-hybrid-ai/">CG Channel</a></p>',
            source:      'CG Channel',
            publishedAt: '2026.04.26',
            hue:         32,
            url:         'https://www.cgchannel.com/2026/04/see-reallusions-2026-roadmap-redefining-3d-with-hybrid-ai/',
            urls: [
                { label: '공식 발표', href: 'https://www.reallusion.com/character-creator/' },
                { label: '관련 정보', href: 'https://magazine.reallusion.com/2026/03/13/headshot-3-is-coming-pre-launch-offer-live-now/' },
            ],
        },
        {
            id:          'games-3c9fd8bd-2026-04',
            tab:         'games',
            headline:    'Autodesk, AI 모캡 전문사 Radical 핵심 기술 인수',
            summary:     'Autodesk가 AI 기반 모션 캡처 기업 RADiCAL의 핵심 기술과 IP를 인수해 Flow Studio에 통합할 계획이라고 밝혔다. 기존 서비스 포털은 7월 6일 종료된다.',
            body:        '<p>Autodesk가 AI 기반 모션 캡처 기업 RADiCAL의 핵심 기술과 IP를 완전 인수했다고 CG Channel이 4월 25일 보도했다.</p><p>Radical은 단안 카메라 영상에서 배우의 움직임을 추출해 FBX로 내보내는 Radical Core와, Blender·Maya·Unity·Unreal Engine 5로 애니메이션을 스트리밍하는 Radical Live를 서비스해왔다. Autodesk는 2022년 초기 지분 투자 이후 이번에 완전 인수를 완료했다.</p><p>인수한 기술이 Autodesk의 클라우드 기반 VFX·애니메이션 플랫폼 Flow Studio(구 Wonder Studio)와 결합될 예정이라는 점에서, 게임·영상 제작 파이프라인의 AI 모캡 접근성이 크게 높아질 것으로 보인다.</p><p>Radical은 2017년 설립 이후 단일 카메라 영상에서 AI로 모션 데이터를 추출하는 기술을 선보여 모캡 전문 스튜디오 없이도 애니메이션을 제작할 수 있는 길을 열었다. Autodesk는 2022년 투자 당시 \'클라우드 기반 엔드투엔드 제작 민주화의 최신 움직임\'이라고 평가하며 Maya 통합을 목표로 제시했다.</p><p>Radical LinkedIn 발표에 따르면 이번 인수는 실시간 모션 캡처, AI 보조 애니메이션, AI 보조 포즈 추정, 그리고 브라우저 기반 협업 3D 워크스페이스 역량 강화에 초점을 맞추고 있으며, Autodesk Flow Studio 로드맵과 전략적으로 연계될 예정이다.</p><p>다만 Autodesk는 해당 기술을 자사 제품에 어떻게 통합할지 구체적인 계획은 공개하지 않았다. 기존 Radical 사용자들은 7월 6일 서비스 포털 종료 전까지 처리된 FBX 파일과 원본 영상을 내려받아야 하며, 사용자 데이터는 Autodesk로 이전되지 않는다.</p><p>이번 인수로 Autodesk의 Flow Studio는 이미 AI 모캡 기능을 보유한 Wonder Studio 기반에 Radical의 기술이 더해지며, 게임·영상 업계에서 AI 기반 애니메이션 파이프라인을 한층 강화할 전망이다.</p><p>원문: <a href="https://www.cgchannel.com/2026/04/autodesk-acquires-core-tech-of-ai-motion-capture-firm-radical/">CG Channel</a></p>',
            source:      'CG Channel',
            publishedAt: '2026.04.26',
            hue:         28,
            url:         'https://www.cgchannel.com/2026/04/autodesk-acquires-core-tech-of-ai-motion-capture-firm-radical/',
        },
 
    /* ---- industry ---- */
        {
            id:          'industry-2fc08271-2026-04',
            tab:         'industry',
            headline:    '전문가들, 거의 모든 대형 게임 스튜디오가 AI 비공개 활용 중',
            summary:     '구글 클라우드 임원 잭 버서와 블룸버그 저널리스트 제이슨 슈라이어가 거의 모든 대형 게임 스튜디오가 생성 AI를 비공개로 사용하고 있다고 밝혔다.',
            body:        '<p>게임 업계 내부 사정에 밝은 전문가들이 입을 모았다. 거의 모든 대형 게임 스튜디오가 이미 생성 AI를 활발하게 쓰고 있다는 것이다. 다만 대부분의 스튜디오가 소비자와 팬들의 반발이 두려워 이를 공개하지 않고 있다는 점도 함께 지적됐다.</p><p>구글 클라우드 게임 담당 이사 잭 버서는 최근 인터뷰에서 게임즈컴 현장 설문 결과를 공개했다. 개발자 10명 중 9명이 AI를 쓰고 있다고 답했지만, 실제로 이를 공개하는 스튜디오는 극히 드물다. 버서는 캡콤을 사례로 들며 수천 개의 소소한 세계 디테일 브레인스토밍에 구글 AI 툴을 활용하고 있다고 구체적으로 언급했다.</p><p>블룸버그의 베테랑 게임 저널리스트 제이슨 슈라이어도 이를 확인했다. 현재 거의 모든 대형 스튜디오가 생성 AI 툴, 특히 Anthropic의 Claude를 사용하고 있으며, 공개 입장과 실제 개발 현장 사이의 간극이 점점 커지고 있다는 것이다.</p><p>버서는 게이머들이 \'지금 즐기고 있는 게임들이 이미 AI로 만들어진 것임을 알지 못한다\'고 말했다. 이미 출시된 고평가 게임들 중 상당수가 AI를 개발에 적극 활용했음에도 이를 공개한 스튜디오는 거의 없다. 버서는 불투명성이 오히려 AI에 대한 부정적 인식을 고착시킨다고 주장하며 보다 솔직한 공개가 필요하다고 강조했다.</p><p>한편 슈라이어는 스트림에서 \'모두가 하고 있다\'는 표현을 사용했다. 인사이더 게이밍의 톰 헨더슨도 캡콤, 유비소프트 등 대형 스튜디오들이 비공개로 AI를 활용하고 있음을 확인했다. AI를 쓴 게임이 이미 높은 평가를 받으며 출시된 상황에서, 업계의 투명성을 둘러싼 논의는 앞으로 더욱 뜨거워질 전망이다.</p><p>원문: <a href="https://www.newsweek.com/entertainment/video-games/experts-say-everyones-doing-it-when-it-comes-to-generative-ai-in-games-11878394">Newsweek</a></p>',
            source:      'Newsweek',
            publishedAt: '2026.04.26',
            isNew:       true,
            hue:         218,
            url:         'https://www.newsweek.com/entertainment/video-games/experts-say-everyones-doing-it-when-it-comes-to-generative-ai-in-games-11878394',
            urls: [
                { label: '관련 보도', href: 'https://www.pcgamer.com/software/ai/players-dont-realise-that-their-favourite-games-right-now-were-already-built-with-ai-says-google-exec-making-ai-tools/' },
                { label: '관련 보도', href: 'https://futurism.com/artificial-intelligence/google-exec-video-games-secretly-ai' },
            ],
        },
        {
            id:          'industry-15ed0ad1-2026-04',
            tab:         'industry',
            headline:    '구글 임원, 게임사 10곳 중 9곳이 AI 이미 사용 중',
            summary:     '구글 클라우드 게임 총괄 잭 뷰저가 대형 스튜디오 대부분이 이미 AI를 게임 개발에 활용 중이라고 밝혔다.',
            body:        '<p>구글 클라우드의 게임 총괄 책임자 잭 뷰저가 현재 출시된 게임 대부분이 이미 AI의 도움을 받아 만들어졌다고 주장해 업계 주목을 받고 있다.</p><p>뷰저는 지난 게임즈컴에서 전 세계 스튜디오를 대상으로 실시한 설문 결과, 응답자의 약 90%가 AI를 사용하고 있다고 답했다고 전했다. 다른 기관 조사에서 나오는 40~50% 수치와의 차이는 공개 꺼림칙함 때문이라고 설명했다.</p><p>AI 사용이 논쟁적 주제인 만큼 많은 스튜디오가 공개적으로 밝히길 꺼리지만, 실제로는 이미 광범위하게 쓰인다는 점이 다시 확인됐다.</p><p>뷰저는 인터뷰에서 구글 클라우드의 Gemini 등 AI 도구들이 일부 스튜디오에서 개발 과정의 단조롭고 반복적인 작업을 줄이는 데 활용되고 있다고 설명했다.</p><p>그는 "플레이어들이 깨닫지 못하는 것은, 지금 즐기고 있는 게임들이 이미 AI로 만들어졌다는 사실"이라고 말했다. "게임즈컴에서 전 세계 스튜디오를 대상으로 설문했는데, 10명 중 약 9명이 \'AI를 사용한다\'고 답했다"고 덧붙였다.</p><p>캡콤의 사례도 소개됐다. 캡콤은 구글 AI 도구를 활용해 세계관 구성 요소 아이디어를 빠르게 생성하는 데 사용하고 있으며, 이를 통해 크리에이티브 팀이 주요 캐릭터와 핵심 장면 같은 높은 가치의 창작 작업에 집중할 수 있게 된다고 밝혔다. 다만 캡콤은 생성형 AI 에셋을 최종 게임에 포함시키지는 않겠다는 입장을 유지하고 있다.</p><p>뷰저는 또한 "플레이어들이 AI가 자신이 좋아하는 게임 일부에 사용됐음을 알게 되면 더 수용적인 태도를 보일 수 있다"고 제안했다. "이것이 실제로 더 빠르게 좋아하는 게임을 받을 수 있도록 도와준다는 걸 깨닫게 될 것이며, 한 게임을 7년 기다리는 일은 없어질 것"이라고 말했다.</p><p>한편 GDC 2026 게임 산업 현황 보고서에 따르면 업계 종사자의 52%가 생성형 AI에 부정적 입장을 취하고 있어, 실제 사용 현황과 업계 감정 사이의 간극이 크다는 점도 드러났다.</p><p>원문: <a href="https://www.videogameschronicle.com/news/their-favourite-games-were-already-built-with-ai-google-exec-says-almost-every-studio-uses-ai-but-not-all-disclose-it/">Video Games Chronicle</a></p>',
            source:      'Video Games Chronicle',
            publishedAt: '2026.04.25',
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
            hue:         220,
            image:       'https://www.pymnts.com/wp-content/uploads/2026/04/Morgan-Stanley-gaming-AI.png',
            url:         'https://www.pymnts.com/artificial-intelligence-2/2026/morgan-stanley-says-gaming-could-score-22-billion-with-ai/',
        },
 
    /* ---- art ---- */
        {
            id:          'art-c5b2bc0b-2026-04',
            tab:         'art',
            headline:    'OpenAI 소라, 오늘부로 앱·웹 서비스 공식 종료 — 고비용 저수익',
            summary:     'OpenAI의 AI 영상 생성 서비스 소라(Sora)가 4월 26일부로 앱과 웹 서비스를 완전히 종료했다. 하루 운영비 약 13억 원에 비해 전체 누적 수익이 극히 저조했던 것이 주된 원인이다.',
            body:        '<p>오늘(4월 26일), OpenAI의 AI 영상 생성 서비스 소라(Sora)의 앱과 웹 서비스가 공식 종료됐다. 2024년 12월 일반 공개된 지 불과 다섯 달 만의 일이다. API 서비스는 2026년 9월 24일까지는 계속 운영될 예정이다.</p><p>소라의 하루 운영 비용은 약 100만 달러(약 13억 원)에 달했지만, 서비스 전체 누적 수익은 약 210만 달러에 불과했다. 최대 100만 명을 기록했던 이용자 수도 50만 명 아래로 줄어들었다. 디즈니는 소라 파트너십에 약 10억 달러를 약속했으나, 서비스 종료 소식을 발표 불과 1시간 전에 통보받은 것으로 알려졌다.</p><p>OpenAI는 소라에 투입되던 컴퓨팅 자원을 코딩 및 엔터프라이즈 제품 쪽으로 전환하기로 했다. 창작 도구 분야에서 한발 물러서며 수익성과 실용성을 우선시하는 전략이 확인된 셈이다.</p><p>소라는 2024년 2월 첫 공개 당시 텍스트 프롬프트로 놀랍도록 현실감 있는 영상을 만들어내며 큰 주목을 받았다. 그러나 높은 인프라 비용, 저작권 소송 리스크, 지속적인 이용자 감소가 발목을 잡았다. 출시 초기 iOS 앱 스토어 1위를 기록하며 첫 주에만 100만 이상 다운로드됐지만, 지속 이용률은 끝내 회복되지 않았다.</p><p>소라가 남긴 자리는 Kling 3.0(콰이쇼우), Google Veo 3.1, Runway Gen-4 Turbo 등 경쟁 서비스들이 빠르게 채워나가고 있다. 기존 소라 이용자들은 sora.chatgpt.com/exports/me에서 콘텐츠를 내려받을 수 있으며, 기한이 지나면 데이터는 영구 삭제된다. OpenAI는 소라의 기반이 된 월드모델 연구는 계속 유지한다는 방침이다.</p><p>원문: <a href="https://help.openai.com/en/articles/20001152-what-to-know-about-the-sora-discontinuation">OpenAI</a></p>',
            source:      'OpenAI',
            publishedAt: '2026.04.26',
            isNew:       true,
            hue:         272,
            url:         'https://help.openai.com/en/articles/20001152-what-to-know-about-the-sora-discontinuation',
            urls: [
                { label: '관련 보도', href: 'https://techcrunch.com/2026/03/29/why-openai-really-shut-down-sora/' },
            ],
        },
        {
            id:          'art-ddbc372e-2026-04',
            tab:         'art',
            headline:    'Adobe After Effects 26.2, AI 기반 오브젝트 매트 툴 도입',
            summary:     'Adobe가 After Effects 26.2를 출시하며 클릭 한 번으로 동영상 속 움직이는 피사체를 자동 마스킹하는 AI 오브젝트 매트 툴을 선보였다.',
            body:        '<p>Adobe가 After Effects 26.2를 공개하며 가장 주목할 신기능으로 AI 기반 \'오브젝트 매트 툴(Object Matte Tool)\'을 선보였다.</p><p>기존 Roto Brush처럼 피사체를 직접 칠할 필요 없이, 단 한 프레임에서 클릭하거나 드래그로 선택하면 AI가 자동으로 전체 영상에 걸쳐 마스크를 생성하고 추적한다. DaVinci Resolve의 Magic Mask나 Flame의 AI 마스크 도구와 어깨를 나란히 하는 기능이다.</p><p>VFX·모션 그래픽 업계에서 가장 많이 쓰이는 합성 도구인 After Effects에 AI 자동 마스킹이 추가됨으로써, 로토스코핑에 드는 시간이 크게 줄어들 것으로 기대된다.</p><p>After Effects 26.2의 주요 업데이트 내용을 살펴보면, 오브젝트 매트 툴 외에도 파라메트릭 3D 메시에 대한 디스플레이스먼트 지원이 추가됐다. 이는 After Effects 26.0에서 도입된 3D 프리미티브 생성 및 Substance 머티리얼 네이티브 지원 기능을 한층 확장한 것이다.</p><p>SVG 지원도 강화됐다. After Effects 26.0에서 처음 도입된 SVG 파일 가져오기 기능이 이번 버전에서 확장되어, SVG를 컴포지션으로 불러와 각 요소를 별도의 편집 가능한 쉐이프 레이어로 변환하거나, 단일 레이어 그래픽의 경우 풋티지로 가져올 수 있다.</p><p>타임라인에서 비례 스크러빙(Proportional Scrubbing)도 새롭게 지원된다. 여러 레이어에서 선택한 속성을 선택 순서에 따라 비례적으로 조정할 수 있어, 단 한 번의 드래그로 캐스케이드나 그라디언트 스타일의 애니메이션을 만들 수 있다.</p><p>Quick Apply 기능도 추가됐다. 단일 검색창에서 이펙트, 프리셋, 메뉴 커맨드를 빠르게 검색하고 검색 결과에서 바로 적용할 수 있다. After Effects 26.2는 Windows 11 및 macOS 14.0 이상에서 이용 가능하며, 월 34.49달러 또는 연 263.88달러의 구독 형태로 제공된다.</p><p>원문: <a href="https://www.cgchannel.com/2026/04/adobe-releases-after-effects-26-2/">CG Channel</a></p>',
            source:      'CG Channel',
            publishedAt: '2026.04.26',
            hue:         270,
            url:         'https://www.cgchannel.com/2026/04/adobe-releases-after-effects-26-2/',
            urls: [
                { label: '공식 릴리즈 노트', href: 'https://helpx.adobe.com/after-effects/using/whats-new.html' },
                { label: '오브젝트 매트 사용법', href: 'https://helpx.adobe.com/after-effects/using/object-matte.html' },
            ],
        },
        {
            id:          'art-29ddbb46-2026-04',
            tab:         'art',
            headline:    '구글 딥마인드 \'Vision Banana\', SAM 3·Depth Anything V3 능가',
            summary:     '구글 딥마인드가 이미지 생성 모델로 훈련한 Vision Banana가 세그멘테이션·깊이 추정 분야에서 기존 전문 모델들을 제로샷으로 능가했다고 발표했다.',
            body:        '<p>구글 딥마인드가 이미지 생성용으로 훈련한 모델이 세그멘테이션과 깊이 추정 같은 시각 인식 작업에서도 최고 수준의 성능을 보인다는 연구 결과를 발표했다.</p><p>연구진은 Nano Banana Pro 기반의 이미지 생성 모델을 경량 인스트럭션 튜닝만으로 변환해 만든 \'Vision Banana\'가 Meta의 SAM 3와 Depth Anything V3를 각각 세그멘테이션과 깊이 추정 벤치마크에서 제로샷으로 앞섰다고 밝혔다.</p><p>생성 AI 훈련이 시각 인식 능력도 함께 길러낸다는 이번 발견은, LLM 프리트레이닝이 언어 이해 능력을 발생시키는 것과 유사한 패러다임 전환을 시사해 비전 AI 연구 커뮤니티에 큰 반향을 일으키고 있다.</p><p>논문 제목 \'Image Generators are Generalist Vision Learners\'에서 알 수 있듯이, 핵심 아이디어는 이미지 생성 훈련이 LLM 프리트레이닝과 마찬가지로 강력한 범용 시각 표현을 자연스럽게 학습시킨다는 것이다. 연구진은 시각 태스크의 출력 공간을 RGB 이미지로 매개변수화함으로써 시각 인식을 이미지 생성으로 재프레이밍했다.</p><p>구체적인 벤치마크 결과를 보면, Vision Banana는 세 개의 세그멘테이션 벤치마크에서 SAM 3를 능가하고, 깊이 추정에서는 Depth Anything V3를 (δ1: 0.929 vs 0.918), 표면 법선 추정에서는 Lotus-2를 (평균 각도 오차: 18.928° vs 19.642°) 각각 제로샷 전이 조건에서 앞섰다. 단일 가중치 세트와 프롬프트만으로 여러 시각 태스크를 전환할 수 있다는 것도 주목할 만한 특징이다.</p><p>연구진은 이번 결과가 생성적 연구와 판별적 연구라는 두 흐름 사이의 오랜 구분을 재고하게 만든다고 지적했다. 다만 논문은 보다 다양한 데이터셋과 실제 환경에서의 강건성은 추가 연구가 필요하다고 인정하고 있으며, 이번 벤치마크가 좁은 범위의 시각 문제를 다루고 있다는 비판도 있다.</p><p>이번 연구에는 He Kaiming과 Xie Saining 등 컴퓨터 비전 분야 저명 연구자들이 참여했으며, 논문은 arXiv에 공개되어 있다.</p><p>원문: <a href="https://www.marktechpost.com/2026/04/25/google-deepmind-introduces-vision-banana-an-instruction-tuned-image-generator-that-beats-sam-3-on-segmentation-and-depth-anything-v3-on-metric-depth-estimation/">MarkTechPost</a></p>',
            source:      'MarkTechPost',
            publishedAt: '2026.04.26',
            hue:         265,
            image:       'https://cms.aidailypost.com/uploads/google_deepminds_vision_banana_outperforms_sam_3_depth_anything_v3_3de1493e75.webp',
            url:         'https://www.marktechpost.com/2026/04/25/google-deepmind-introduces-vision-banana-an-instruction-tuned-image-generator-that-beats-sam-3-on-segmentation-and-depth-anything-v3-on-metric-depth-estimation/',
            urls: [
                { label: '논문', href: 'https://deepmind.google/research/publications/240658/' },
                { label: '프로젝트 페이지', href: 'https://vision-banana.github.io/' },
            ],
        },
        {
            id:          'art-4cd35d15-2026-04',
            tab:         'art',
            headline:    'OpenAI의 AI 영상 서비스 Sora, 내일(26일) 종료',
            summary:     'OpenAI가 AI 영상 생성 서비스 Sora 앱을 4월 26일 종료한다고 밝혔다. API는 9월 24일까지 운영 후 종료될 예정이다.',
            body:        '<p>OpenAI의 AI 영상 생성 서비스인 Sora가 내일(4월 26일) 공식 앱 서비스를 종료한다. 2025년 9월 출시 이후 약 반 년 만에 막을 내리는 것이다.</p><p>종료 배경에는 천문학적인 운영 비용(일부 추정치에 따르면 하루 최대 1,500만 달러)과 가입자 급감이 있다. 출시 초기 100만 명을 넘겼던 월간 사용자는 올해 1월 기준 전월 대비 45%나 감소했다.</p><p>AI 영상 생성 분야의 선구자였던 Sora의 폐막은 생성형 AI 업계 전반에 시사하는 바가 크다. 영상 생성이 텍스트 대비 약 2,000배 비싸다는 경제적 현실이 결국 걸림돌이 됐다.</p><p>OpenAI는 공식 X 계정을 통해 "Sora 앱을 종료한다. Sora로 창작하고, 공유하고, 커뮤니티를 만들어 준 모든 분께 감사드린다. 여러분이 Sora로 만들어낸 것들은 의미가 있었고, 이 소식이 실망스럽다는 걸 안다"고 전했다.</p><p>Sora 앱은 AI가 생성한 콘텐츠를 독점적으로 게시하는 소셜 미디어 형태의 서비스였다. 구독 없이도 누구나 매우 사실적인 AI 영상을 생성할 수 있어 큰 반향을 일으켰으며, 이로 인해 딥페이크 문제와 소위 \'AI 슬롭\'이라 불리는 저품질 AI 콘텐츠에 대한 우려도 함께 커졌다.</p><p>Sora 팀 리드 빌 피블스는 지난 10월에 이미 "현재 경제성은 완전히 지속 불가능하다"고 X에서 인정한 바 있다. 영상 생성은 수백 프레임을 노이즈 제거하고 렌더링해야 하기 때문에, 텍스트 생성 대비 에너지 소비량이 훨씬 높다.</p><p>이 결정은 디즈니에도 영향을 미쳤다. 디즈니는 Sora를 통해 약 10억 달러 규모의 투자를 계획했으나, 서비스 종료 발표 후 해당 계획이 무산된 것으로 알려졌다. API의 경우 9월 24일까지 운영이 유지되므로, API 사용자들은 그때까지 시간 여유가 있다.</p><p>현재 콘텐츠를 보존하고 싶은 사용자는 sora.chatgpt.com/exports/me에서 내보내기 기능을 이용해야 하며, OpenAI는 서비스 종료 이후 콘텐츠 복구를 보장하지 않는다고 밝혔다.</p><p>원문: <a href="https://www.liubknews.com/post/sora-ai-shuts-down-why-and-what-this-means-for-tech">Liubk News</a></p>',
            source:      'Liubk News',
            publishedAt: '2026.04.25',
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
            hue:         265,
            url:         'https://openai.com/index/introducing-chatgpt-images-2-0/',
            urls: [
                { label: '관련 보도', href: 'https://venturebeat.com/technology/openais-chatgpt-images-2-0-is-here-and-it-does-multilingual-text-full-infographics-slides-maps-even-manga-seemingly-flawlessly' },
            ],
        },
 
  ],
};
