/* Hi-fi mock dataset for AI Art Daily — articles per tab */
window.AIAD = {
  tabs: [
    { id: 'games',     label: '게임 제작 속 AI' },
    { id: 'industry',  label: 'AI 도입 뉴스' },
    { id: 'art',       label: '아트 전반 AI 뉴스' },
    { id: 'tools',     label: '신규 도구' },
    { id: 'research',  label: '연구 & 논문' },
    { id: 'policy',    label: '정책 & 저작권' },
    { id: 'community', label: '커뮤니티' },
  ],
  articles: [
    /* ---- games ---- */
    { id: 'a1', tab: 'games', cat: '게임 제작',
      headline: '엔씨소프트, 사내 캐릭터 컨셉 아트 워크플로우에 생성형 AI 도입',
      summary: '엔씨소프트 아트 디렉터들이 초기 컨셉 단계에서 자체 학습한 생성형 AI 모델을 사용한다고 밝혔다. 회사는 최종 캐릭터 디자인은 모두 사내 아티스트가 완성한다는 점을 분명히 했다.',
      source: '연합뉴스', publishedAt: '2026-04-25', mark: '연', date: '2일 전', isNew: true, hue: 28,
      url: 'https://example.com/ncsoft-ai-concept'
    },
    { id: 'a2', tab: 'games', cat: 'AI 도입',
      headline: '유비소프트, 텍스트-투-3D 도구로 NPC 환경 자산 제작 시간 40% 단축',
      summary: '유비소프트 몬트리올이 GDC 2026에서 자체 개발한 텍스트-투-3D 파이프라인을 공개했다. 거리 소품과 인테리어 아트 작업이 주요 적용 분야다.',
      source: 'The Verge', publishedAt: '2026-04-24', mark: 'V', date: '3일 전', hue: 220,
      url: 'https://example.com/ubisoft-text-to-3d'
    },
    { id: 'a3', tab: 'games', cat: '인디 게임',
      headline: '인디 게임 \"파스텔 오디세이\", AI로 제작한 4,000여 장 배경 텍스처 화제',
      summary: '1인 개발자 김미래씨는 직접 학습시킨 LoRA 모델로 모든 배경을 제작했다. 출시 첫 주 스팀 일일 트렌드 12위에 올랐다.',
      source: '게임메카', publishedAt: '2026-04-21', mark: '메', date: '7일 전', hue: 310,
      url: 'https://example.com/pastel-odyssey'
    },
    { id: 'a4', tab: 'games', cat: '대기업 동향',
      headline: '넥슨, 라이브 서비스 게임 NPC 대화에 LLM 통합 테스트 시작',
      summary: '넥슨이 \"마비노기 모바일\"의 일부 NPC에 자체 학습 LLM을 적용한 폐쇄 베타를 진행 중이다. 컨텍스트 일관성과 한국어 자연스러움이 주요 평가 기준이다.',
      source: 'ZDNet Korea', publishedAt: '2026-04-23', mark: 'Z', date: '5일 전', isNew: true, hue: 165,
      url: 'https://example.com/nexon-llm-npc'
    },
    { id: 'a5', tab: 'games', cat: '아티스트 인터뷰',
      headline: '\"AI는 더 빠른 무드보드일 뿐\" — 펄어비스 컨셉 아트 디렉터 인터뷰',
      summary: '검은사막 IP의 컨셉 아트 디렉터 이수진씨가 사내 AI 도구가 어떻게 통합되는지 설명한다. 그는 \"최종 결과물의 품질과 책임은 여전히 인간 아티스트의 영역\"이라고 강조했다.',
      source: '게임포커스', publishedAt: '2026-04-19', mark: 'F', date: '9일 전', hue: 50,
      url: 'https://example.com/pearlabyss-interview'
    },
    { id: 'a6', tab: 'games', cat: '도구',
      headline: 'Unity, AI 텍스처 생성 패키지 \"Muse Texture\" 정식 출시',
      summary: '베타 6개월 만에 정식 출시된 Muse Texture는 PBR 머티리얼 4K 해상도까지 지원한다. 인디 개발자 라이선스는 월 $15부터 시작한다.',
      source: 'Wired', publishedAt: '2026-04-25', mark: 'W', date: '4일 전', hue: 200,
      url: 'https://example.com/unity-muse'
    },
    { id: 'a7', tab: 'games', cat: '커뮤니티',
      headline: '한국게임개발자협회, AI 활용 게임 출시 가이드라인 초안 공개',
      summary: 'KGDA가 회원사 대상으로 AI 생성 자산 표시 기준, 학습 데이터 출처, 크레딧 표기 방법 등을 담은 자율 가이드라인 초안을 회람했다. 의견 수렴 후 6월 확정 예정이다.',
      source: '연합뉴스', publishedAt: '2026-04-20', mark: '연', date: '8일 전', hue: 95,
      url: 'https://example.com/kgda-guideline'
    },

    /* ---- industry ---- */
    { id: 'b1', tab: 'industry', cat: '대기업 동향',
      headline: '디즈니, 단편 애니메이션 \"라이트하우스\"에 Runway Gen-4 부분 활용 공개',
      summary: '디즈니 단편 부서는 환경 매트 페인팅 일부와 군중 시뮬레이션에서 Runway 모델을 사용했다고 인정했다. 캐릭터 애니메이션은 전부 수작업이라고 강조했다.',
      source: 'The Verge', publishedAt: '2026-04-18', mark: 'V', date: '8일 전', hue: 30,
      url: 'https://example.com/disney-runway'
    },
    { id: 'b2', tab: 'industry', cat: 'IPO',
      headline: 'Stability AI 후속 \"Stability X\", 시리즈 C에서 12억 달러 조달',
      summary: '엔터프라이즈 미디어 워크플로우에 집중한 Stability X가 신규 라운드를 마감했다. 주요 투자자는 디즈니, 워너브러더스, 파라마운트 등 대형 스튜디오다.',
      source: 'Wired', publishedAt: '2026-04-25', mark: 'W', date: '1일 전', isNew: true, hue: 280,
      url: 'https://example.com/stability-x-series-c'
    },
    { id: 'b3', tab: 'industry', cat: '광고',
      headline: '제일기획, 첫 100% AI 제작 TVC 공개 — 4주 만에 6개 버전 양산',
      summary: '제일기획이 한 글로벌 자동차 브랜드를 위해 제작한 광고가 이번 주 방영됐다. 기존 12주 일정을 4주로 단축했지만 카피라이팅과 디렉팅은 인간 팀이 담당했다.',
      source: 'ZDNet Korea', publishedAt: '2026-04-22', mark: 'Z', date: '6일 전', hue: 0,
      url: 'https://example.com/cheil-ai-tvc'
    },
    { id: 'b4', tab: 'industry', cat: '플랫폼',
      headline: '넷플릭스, AI 생성 콘텐츠 표시 의무화 — 9월부터 전 콘텐츠 적용',
      summary: '넷플릭스는 작품의 일부라도 생성형 AI를 사용했을 경우 메타데이터에 표시하도록 제작사에 통보했다. 시청자는 작품 정보 화면에서 사용 범위를 확인할 수 있다.',
      source: 'The Verge', publishedAt: '2026-04-24', mark: 'V', date: '3일 전', hue: 350,
      url: 'https://example.com/netflix-ai-disclosure'
    },
    { id: 'b5', tab: 'industry', cat: '한국',
      headline: '삼성전자, 광고 제작에 자체 \"가우스 비주얼\" 도입 본격화',
      summary: '삼성전자가 사내 마케팅 부서에 가우스 비주얼 모델을 전사 배포한다. 제품 디자인 팀과 광고 에이전시 외주 비중을 조정한다는 보도다.',
      source: '연합뉴스', publishedAt: '2026-04-15', mark: '연', date: '12일 전', hue: 230,
      url: 'https://example.com/samsung-gauss'
    },
    { id: 'b6', tab: 'industry', cat: '글로벌',
      headline: 'Meta, 인스타그램 \"AI 크리에이터\" 검증 배지 도입',
      summary: 'Meta는 AI 도구로 콘텐츠를 만드는 크리에이터 계정에 별도 배지를 부여한다. 신뢰성과 출처 표시를 위한 조치라고 회사는 설명했다.',
      source: 'Wired', publishedAt: '2026-04-23', mark: 'W', date: '5일 전', isNew: true, hue: 190,
      url: 'https://example.com/meta-ai-badge'
    },

    /* ---- art ---- */
    { id: 'c1', tab: 'art', cat: '미술관',
      headline: '뉴욕현대미술관, 첫 AI 영구 컬렉션으로 \"잠재 공간\" 시리즈 6점 인수',
      summary: 'MoMA 큐레이터 팀은 작가가 자체 학습 모델을 공개한 점을 인수 결정의 핵심 근거로 들었다. 컬렉션은 가을 재개관과 함께 5층 미디어 갤러리에 전시된다.',
      source: 'ArtNews', publishedAt: '2026-04-22', mark: 'A', date: '5일 전', hue: 45,
      url: 'https://example.com/moma-latent-space'
    },
    { id: 'c2', tab: 'art', cat: '비엔날레',
      headline: '베니스 비엔날레 2026 한국관, AI와 전통 한국화의 대화 주제 선정',
      summary: '커미셔너로 선정된 정연주씨가 AI와 한국 산수화의 만남을 주제로 한국관을 큐레이션한다. 참여 작가 5명 중 3명이 AI 도구를 작업에 통합한다.',
      source: '연합뉴스', publishedAt: '2026-04-22', mark: '연', date: '6일 전', isNew: true, hue: 95,
      url: 'https://example.com/venice-korea-2026'
    },
    { id: 'c3', tab: 'art', cat: '경매',
      headline: '소더비 \"AI Art Now\" 경매, 총낙찰액 1,840만 달러로 신기록',
      summary: '경매에 오른 42점 중 38점이 낙찰됐고, 최고가는 익명 작가의 \"무한 회랑\" 시리즈로 280만 달러였다. 컬렉터 중 30%가 첫 미술품 구매자였다.',
      source: 'ArtNews', publishedAt: '2026-04-23', mark: 'A', date: '4일 전', hue: 320,
      url: 'https://example.com/sothebys-ai-auction'
    },
    { id: 'c4', tab: 'art', cat: '전시',
      headline: '국립현대미술관 서울, 기획전 \"기계의 눈으로 본 한국\" 4월 30일 개막',
      summary: 'MMCA는 한국 작가 12명의 AI 협업 작품을 선보인다. 백남준의 비디오 아트와 동시대 AI 작품의 대화를 시도하는 섹션이 핵심이다.',
      source: 'ArtNews', publishedAt: '2026-04-17', mark: 'A', date: '10일 전', hue: 165,
      url: 'https://example.com/mmca-machine-eye'
    },
    { id: 'c5', tab: 'art', cat: '비평',
      headline: '\"AI 아트의 새로움은 무엇인가?\" — 미술비평가 현시원 특별 기고',
      summary: '비평가 현시원이 최근 AI 아트 담론에서 빠진 \"매체 특정성\" 논의를 다시 끌어온다. 그는 도구가 아닌 모델 자체의 미학적 가능성을 살펴야 한다고 주장한다.',
      source: '아트인컬처', publishedAt: '2026-04-16', mark: 'I', date: '11일 전', hue: 5,
      url: 'https://example.com/hyun-essay'
    },
    { id: 'c6', tab: 'art', cat: '레지던시',
      headline: '리움미술관, AI 아티스트 레지던시 1기 5명 선정',
      summary: '리움이 처음 운영하는 AI 아트 레지던시 1기 작가 명단을 발표했다. 작가들은 6개월간 미술관 내 작업실과 GPU 클러스터를 사용한다.',
      source: '아트인컬처', publishedAt: '2026-04-21', mark: 'I', date: '7일 전', hue: 250,
      url: 'https://example.com/leeum-residency'
    },
    { id: 'c7', tab: 'art', cat: '갤러리',
      headline: '국제갤러리, AI 아티스트 듀오 \"Obvious\" 첫 한국 개인전 7월 개최',
      summary: '국제갤러리가 파리 기반 AI 아티스트 듀오 Obvious의 첫 한국 개인전을 발표했다. 신작 14점이 공개되며 일부는 한국 단원풍 학습 모델로 제작됐다.',
      source: 'ArtNews', publishedAt: '2026-04-14', mark: 'A', date: '13일 전', hue: 25,
      url: 'https://example.com/kukje-obvious'
    },
    { id: 'c8', tab: 'art', cat: '아티스트',
      headline: 'Refik Anadol, 광주비엔날레 위해 \"한국의 자연\" 데이터셋 구축',
      summary: 'Refik Anadol 스튜디오가 한국 환경부와 협업해 한국 식물·풍경 영상 데이터셋을 구축한다. 결과물은 9월 광주에서 첫 공개된다.',
      source: 'Wired', publishedAt: '2026-04-13', mark: 'W', date: '14일 전', hue: 130,
      url: 'https://example.com/anadol-korea'
    },
    { id: 'c9', tab: 'art', cat: '국내',
      headline: '갤러리현대, \"AI 시대의 한국화\" 단체전 6월 개막',
      summary: '갤러리현대가 한국화 작가 8명과 AI 협업 작품을 선보이는 단체전을 준비 중이다. 전통 화법과 디퓨전 모델의 시각적 만남이 주제다.',
      source: '아트인컬처', publishedAt: '2026-04-19', mark: 'I', date: '9일 전', hue: 60,
      url: 'https://example.com/gallery-hyundai'
    },

    /* ---- tools ---- */
    { id: 'd1', tab: 'tools', cat: '도구',
      headline: 'Adobe Firefly 4, 비디오 워크플로우용 \"키프레임 생성\" 베타 공개',
      summary: '키프레임 두 장과 텍스트 설명만으로 12초까지의 모션 시퀀스를 생성한다. 어도비는 광고와 모션 디자인 스튜디오를 우선 타깃으로 한다고 밝혔다.',
      source: 'ZDNet Korea', publishedAt: '2026-04-22', mark: 'Z', date: '6일 전', hue: 15,
      url: 'https://example.com/firefly-4'
    },
    { id: 'd2', tab: 'tools', cat: '오픈소스',
      headline: 'ComfyUI 4.0 출시 — 노드 그룹화와 협업 워크스페이스 도입',
      summary: '오픈소스 디퓨전 워크플로우 도구 ComfyUI가 메이저 업데이트를 공개했다. 팀 협업을 위한 클라우드 워크스페이스가 핵심 신기능이다.',
      source: 'The Verge', publishedAt: '2026-04-25', mark: 'V', date: '2일 전', isNew: true, hue: 200,
      url: 'https://example.com/comfyui-4'
    },
    { id: 'd3', tab: 'tools', cat: '3D',
      headline: 'Blender 4.5, AI 리토폴로지 도구 \"AutoMesh\" 실험적 도입',
      summary: '하이폴리 모델을 게임용 로우폴리로 자동 변환하는 도구가 베타 플래그로 추가됐다. UV 언랩과 노멀 베이크까지 한 번에 처리한다.',
      source: 'Wired', publishedAt: '2026-04-22', mark: 'W', date: '5일 전', hue: 280,
      url: 'https://example.com/blender-automesh'
    },
    { id: 'd4', tab: 'tools', cat: '한국',
      headline: '카카오, 한국어 특화 디자인 도구 \"칼라 스튜디오\" 공개 베타',
      summary: '카카오브레인이 한국어 프롬프트와 한국적 미감에 최적화된 이미지 생성 도구를 공개했다. 한복, 한옥, 한국 풍경 데이터셋이 핵심이다.',
      source: 'ZDNet Korea', publishedAt: '2026-04-21', mark: 'Z', date: '7일 전', hue: 320,
      url: 'https://example.com/kakao-kalla'
    },

    /* ---- research ---- */
    { id: 'e1', tab: 'research', cat: '연구',
      headline: 'KAIST, 한국화 화풍 보존을 위한 소규모 데이터 학습 모델 발표',
      summary: '연구팀은 단원 김홍도와 혜원 신윤복 작품 200여 점만으로 학습한 디퓨전 모델을 공개했다. 논문은 SIGGRAPH Asia 2026에 채택됐다.',
      source: 'ZDNet Korea', publishedAt: '2026-04-17', mark: 'Z', date: '10일 전', hue: 80,
      url: 'https://example.com/kaist-korean-paint'
    },
    { id: 'e2', tab: 'research', cat: '논문',
      headline: 'Stanford, 디퓨전 모델의 \"창의성\" 정량 평가 프레임워크 제안',
      summary: 'CHI 2026에서 발표될 이 논문은 모델 출력의 신규성·다양성·일관성을 동시에 측정한다. 8개 주요 모델을 비교한 결과도 함께 공개됐다.',
      source: 'Wired', publishedAt: '2026-04-23', mark: 'W', date: '4일 전', hue: 230,
      url: 'https://example.com/stanford-creativity'
    },
    { id: 'e3', tab: 'research', cat: '컨퍼런스',
      headline: 'NeurIPS 2026 워크숍, \"창작자 권리와 AI\" 트랙 신설',
      summary: 'NeurIPS가 처음으로 작가·아티스트·법학자가 함께하는 트랙을 마련한다. 키노트는 한국 한복판화 작가 강병인씨가 맡는다.',
      source: 'The Verge', publishedAt: '2026-04-22', mark: 'V', date: '6일 전', hue: 30,
      url: 'https://example.com/neurips-rights'
    },

    /* ---- policy ---- */
    { id: 'f1', tab: 'policy', cat: '정책',
      headline: '미국 저작권청, AI 학습 데이터 출처 공개 의무화 지침 초안 발표',
      summary: '저작권청은 모델 훈련에 사용된 저작물 목록을 일정 규모 이상 모델은 공개해야 한다는 가이드라인 초안을 4월 22일 공개했다. 업계 의견 수렴은 6월까지다.',
      source: 'Wired', publishedAt: '2026-04-22', mark: 'W', date: '4일 전', isNew: true, hue: 5,
      url: 'https://example.com/uscb-disclosure'
    },
    { id: 'f2', tab: 'policy', cat: '한국',
      headline: '문체부, AI 생성물 저작권 가이드라인 2차 개정안 행정예고',
      summary: '문체부는 \"인간 창작 기여도\"를 정량화하는 새 기준을 포함한 개정안을 4월 24일 행정예고했다. 의견 수렴은 5월 30일까지 진행된다.',
      source: '연합뉴스', publishedAt: '2026-04-25', mark: '연', date: '1일 전', isNew: true, hue: 350,
      url: 'https://example.com/mcst-guideline-v2'
    },
    { id: 'f3', tab: 'policy', cat: 'EU',
      headline: 'EU AI Act 시행령, 9월 1일 \"고위험 창작 도구\" 분류 발효',
      summary: 'EU 집행위가 시행령 최종안을 통과시켰다. 일부 영상·캐릭터 생성 도구가 고위험으로 분류돼 별도 등록 의무가 부여된다.',
      source: 'The Verge', publishedAt: '2026-04-24', mark: 'V', date: '3일 전', hue: 220,
      url: 'https://example.com/eu-ai-act-sept'
    },
    { id: 'f4', tab: 'policy', cat: '소송',
      headline: '뉴욕타임스 vs OpenAI 1심, \"학습은 변형적 사용\" 일부 인정',
      summary: '연방 지방법원이 학습 자체는 공정 이용 가능성이 있다고 판단하면서도, 출력 단계에서의 침해는 별도로 다투라고 결정했다. 양측 모두 항소 의사를 밝혔다.',
      source: 'Wired', publishedAt: '2026-04-25', mark: 'W', date: '2일 전', isNew: true, hue: 0,
      url: 'https://example.com/nyt-openai-ruling'
    },
    { id: 'f5', tab: 'policy', cat: '저작권',
      headline: 'C2PA 표준, 한국 주요 포털 4사 동시 도입 발표',
      summary: '네이버, 카카오, 줌, 다음이 콘텐츠 출처 인증 표준 C2PA를 6월부터 단계 도입한다. 이미지·영상·뉴스 콘텐츠가 우선 적용 대상이다.',
      source: 'ZDNet Korea', publishedAt: '2026-04-20', mark: 'Z', date: '8일 전', hue: 130,
      url: 'https://example.com/c2pa-korea'
    },

    /* ---- community ---- */
    { id: 'g1', tab: 'community', cat: '커뮤니티',
      headline: '아트스테이션, 작가별 AI 학습 옵트아웃 메타데이터 표준 도입',
      summary: '플랫폼은 모든 업로드 작품에 머신리딩 가능한 학습 거부 태그를 자동 추가한다. C2PA 콘텐츠 자격 증명과 호환된다.',
      source: 'ArtNews', publishedAt: '2026-04-16', mark: 'A', date: '11일 전', hue: 290,
      url: 'https://example.com/artstation-optout'
    },
    { id: 'g2', tab: 'community', cat: '국내',
      headline: '한국 일러스트레이터 1,200명, AI 학습 거부 공동 선언문 발표',
      summary: '한국일러스트레이션협회 주도로 1,200여 명이 동의한 공동 선언문이 발표됐다. 무단 학습 데이터 사용에 대한 법적 대응도 함께 예고됐다.',
      source: '연합뉴스', publishedAt: '2026-04-22', mark: '연', date: '6일 전', isNew: true, hue: 15,
      url: 'https://example.com/kor-illustrators'
    },
  ],

  /* full body for the modal — keyed by article id; one shared body for the prototype */
  body: `
    <p>엔씨소프트가 자사 게임 IP의 캐릭터 컨셉 아트 초기 단계에 사내 학습 생성형 AI 모델을 도입했다고 밝혔다. 회사는 새로운 워크플로우가 아티스트를 대체하는 것이 아니라, 초기 탐색 단계에서 더 많은 시각적 후보를 빠르게 검토하기 위한 것이라고 강조했다.</p>
    <p>아트 디렉터 박지우 상무는 "텍스트-투-이미지 도구는 우리에게 더 빠른 무드보드와 다양한 실루엣 옵션을 제공한다. 그러나 캐릭터의 최종 디자인, 표정, 동작은 여전히 사내 아티스트의 손을 거쳐 완성된다"고 설명했다.</p>
    <h3>사내 모델만 사용, 외부 데이터 학습 배제</h3>
    <p>엔씨소프트가 도입한 모델은 회사가 지난 10년간 축적한 자체 컨셉 아트 데이터셋을 기반으로 학습됐다. 외부에서 수집한 무단 데이터는 학습에 포함되지 않았으며, 사내 아티스트들의 동의를 거쳐 데이터셋이 구성됐다고 회사는 설명했다.</p>
    <blockquote>우리는 AI를 도구로 본다. 화가가 붓을 고르듯, 아티스트가 자신에게 맞는 도구를 선택할 수 있어야 한다.</blockquote>
    <h3>업계 반응과 우려</h3>
    <p>일러스트레이터 협회 일부 회원들은 여전히 우려를 표하고 있다. 한국일러스트레이션협회 김민수 사무국장은 "사내 데이터 사용이라고 해도, 향후 AI 도구가 인력 감축의 명분으로 사용될 수 있다는 우려가 있다"고 지적했다.</p>
    <p>엔씨소프트는 향후 1년간 아트 인력 규모를 유지할 계획이며, AI 도구 사용 가이드라인을 사내에 공개할 예정이라고 밝혔다. 회사는 또한 분기별로 사내 아티스트들과의 라운드테이블을 열어 도구 사용 방향을 함께 정해나가겠다고 덧붙였다.</p>
    <h3>한국 게임업계 전반의 흐름</h3>
    <p>엔씨소프트뿐 아니라 넥슨, 펄어비스, 크래프톤 등 주요 한국 게임사들도 사내 AI 도구 도입을 진행 중이거나 검토하고 있다. 한국게임개발자협회는 이번 주 회원사들을 대상으로 자율 가이드라인 초안을 회람했으며, 6월 중 최종안을 확정할 예정이다.</p>
    <p>이번 발표는 지난주 GDC 2026에서 유비소프트가 자체 텍스트-투-3D 파이프라인을 공개한 데 이어 나온 것으로, 글로벌 게임 산업 전반에서 생성형 AI 도구의 워크플로우 통합이 본격화되고 있음을 보여준다.</p>
  `
};
