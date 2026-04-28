/* Whitelist — 스크래핑/추적 대상 목록 (단순 데이터 파일) */
window.AIAD_WHITELIST = {
  /* 기사 소스 — 카테고리별 출처 도메인 (중복 제거) */
  articleSources: [
    /* ── 공통 (AI 뉴스레터 / 빅랩 / 일반 기술 매체) ── */
    { name: 'The Rundown AI',        url: 'https://www.therundown.ai',                  note: 'AI 데일리 뉴스레터', group: '공통' },
    { name: "Ben's Bites",           url: 'https://bensbites.com',                      note: 'AI 데일리 뉴스레터', group: '공통' },
    { name: 'The Neuron Daily',      url: 'https://www.theneurondaily.com',             note: 'AI 데일리 뉴스레터', group: '공통' },
    { name: 'MarkTechPost',          url: 'https://www.marktechpost.com',               note: 'AI · 머신러닝 기술 매체', group: '공통' },
    { name: 'Creative Bloq',         url: 'https://www.creativebloq.com',               note: '디자인 · 크리에이티브', group: '공통' },
    { name: 'OpenAI News',           url: 'https://openai.com/news',                    note: 'OpenAI 공식 발표', group: '공통' },
    { name: 'OpenAI Developers Blog',url: 'https://developers.openai.com/blog',         note: 'OpenAI 개발자 블로그', group: '공통' },
    { name: 'DeepMind Blog',         url: 'https://deepmind.google/blog',               note: 'Google DeepMind 리서치', group: '공통' },
    { name: 'Google AI Blog',        url: 'https://blog.google/technology/ai',          note: 'Google AI 발표', group: '공통' },
    { name: 'Runway Research',       url: 'https://runwayml.com/research',              note: 'Runway 리서치', group: '공통' },
    { name: 'Hugging Face Blog',     url: 'https://huggingface.co/blog',                note: '오픈소스 AI 허브', group: '공통' },
    { name: 'Towards Data Science',  url: 'https://towardsdatascience.com',             note: '데이터 사이언스 · ML', group: '공통' },
    { name: 'The Verge',             url: 'https://www.theverge.com',                   note: '테크 · 컬처 매체', group: '공통' },

    /* ── 게임 제작 (엔진 · 3D · 생성형 툴 · VFX) ── */
    { name: 'Game Developer',        url: 'https://www.gamedeveloper.com',              note: '게임 개발 전문 매체', group: '게임 제작 속 AI' },
    { name: 'Unreal Engine Blog',    url: 'https://www.unrealengine.com/blog',          note: 'Unreal Engine 공식', group: '게임 제작 속 AI' },
    { name: 'Unity Blog',            url: 'https://unity.com/blog',                     note: 'Unity 공식', group: '게임 제작 속 AI' },
    { name: 'VentureBeat — Games',   url: 'https://venturebeat.com/games',              note: '게임 · 비즈니스', group: '게임 제작 속 AI' },
    { name: 'NVIDIA Blog',           url: 'https://blogs.nvidia.com',                   note: 'GPU · AI 인프라', group: '게임 제작 속 AI' },
    { name: 'Stability AI News',     url: 'https://stability.ai/news-updates',          note: 'Stability AI 공식', group: '게임 제작 속 AI' },
    { name: 'Runway Blog',           url: 'https://runwayml.com/blog',                  note: '비디오 생성 AI', group: '게임 제작 속 AI' },
    { name: 'Adobe Business — AI',   url: 'https://business.adobe.com/ai.html',         note: 'Adobe 엔터프라이즈 AI', group: '게임 제작 속 AI' },
    { name: 'Midjourney',            url: 'https://www.midjourney.com',                 note: '이미지 생성 AI', group: '게임 제작 속 AI' },
    { name: 'Meshy Blog',            url: 'https://www.meshy.ai/blog',                  note: '3D 에셋 생성 AI', group: '게임 제작 속 AI' },
    { name: 'Luma Labs',             url: 'https://lumalabs.ai',                        note: '3D · 비디오 생성 AI', group: '게임 제작 속 AI' },
    { name: 'ElevenLabs Blog',       url: 'https://elevenlabs.io/blog',                 note: '음성 생성 AI', group: '게임 제작 속 AI' },
    { name: 'CG Channel',            url: 'https://www.cgchannel.com',                  note: 'VFX · 3D 그래픽스', group: '게임 제작 속 AI' },
    { name: 'fxguide',               url: 'https://www.fxguide.com',                    note: 'VFX 전문 매체', group: '게임 제작 속 AI' },
    { name: 'befores & afters',      url: 'https://beforesandafters.com',               note: 'VFX · 애니메이션', group: '게임 제작 속 AI' },
    { name: 'SideFX News',           url: 'https://www.sidefx.com/news',                note: 'Houdini 공식', group: '게임 제작 속 AI' },
    { name: 'Autodesk Blogs',        url: 'https://www.autodesk.com/blogs',             note: 'Maya · 3ds Max · AI', group: '게임 제작 속 AI' },
    { name: 'TechCrunch',            url: 'https://techcrunch.com',                     note: '테크 · 스타트업', group: '게임 제작 속 AI' },
    { name: 'Ars Technica',          url: 'https://arstechnica.com',                    note: '테크 · 사이언스', group: '게임 제작 속 AI' },
    { name: 'WIRED',                 url: 'https://www.wired.com',                      note: '테크 · 컬처', group: '게임 제작 속 AI' },
    { name: 'Papers with Code',      url: 'https://paperswithcode.com',                 note: '논문 · 구현체 큐레이션', group: '게임 제작 속 AI' },

    /* ── 글로벌 스튜디오 AI 도입 (게임 산업 · 비즈니스) ── */
    { name: 'GDC',                   url: 'https://gdconf.com/news-insights/',          note: 'Game Developers Conference', group: 'AI 도입 뉴스' },
    { name: 'GamesIndustry.biz',     url: 'https://www.gamesindustry.biz',              note: '게임 산업 비즈니스', group: 'AI 도입 뉴스' },
    { name: 'PocketGamer.biz',       url: 'https://www.pocketgamer.biz',                note: '모바일 게임 비즈니스', group: 'AI 도입 뉴스' },
    { name: 'Kotaku',                url: 'https://kotaku.com',                         note: '게임 컬처 매체', group: 'AI 도입 뉴스' },
    { name: 'Polygon',               url: 'https://www.polygon.com',                    note: '게임 · 엔터테인먼트', group: 'AI 도입 뉴스' },
    { name: 'IGN',                   url: 'https://www.ign.com',                        note: '게임 미디어', group: 'AI 도입 뉴스' },
    { name: 'Eurogamer',             url: 'https://www.eurogamer.net',                  note: '유럽 게임 매체', group: 'AI 도입 뉴스' },
    { name: 'Rock Paper Shotgun',    url: 'https://www.rockpapershotgun.com',           note: 'PC 게임 매체', group: 'AI 도입 뉴스' },
    { name: 'PC Gamer',              url: 'https://www.pcgamer.com',                    note: 'PC 게임 매체', group: 'AI 도입 뉴스' },
    { name: 'GamesRadar',            url: 'https://www.gamesradar.com',                 note: '게임 미디어', group: 'AI 도입 뉴스' },
    { name: 'Bloomberg',             url: 'https://www.bloomberg.com',                  note: '비즈니스 · 산업', group: 'AI 도입 뉴스' },
    { name: 'Reuters',               url: 'https://www.reuters.com',                    note: '글로벌 통신사', group: 'AI 도입 뉴스' },

    /* ── 아트 전반 (음악 · 영상 · 사운드 · 리서치) ── */
    { name: 'VentureBeat — AI',      url: 'https://venturebeat.com/ai',                 note: 'AI 산업 동향', group: '아트 전반 AI 뉴스' },
    { name: 'Adobe Research',        url: 'https://research.adobe.com',                 note: 'Adobe 리서치', group: '아트 전반 AI 뉴스' },
    { name: 'Suno Blog',             url: 'https://suno.ai/blog',                       note: '음악 생성 AI', group: '아트 전반 AI 뉴스' },
    { name: 'MusicTech',             url: 'https://musictech.com',                      note: '음악 제작 매체', group: '아트 전반 AI 뉴스' },
    { name: 'Sound on Sound',        url: 'https://www.soundonsound.com',               note: '음악 · 사운드 엔지니어링', group: '아트 전반 AI 뉴스' },
    { name: 'No Film School',        url: 'https://nofilmschool.com',                   note: '영상 제작', group: '아트 전반 AI 뉴스' },
    { name: 'The Next Web',          url: 'https://thenextweb.com',                     note: '테크 · 컬처', group: '아트 전반 AI 뉴스' },
  ],

  /* Github 레포지토리 — 새 커밋·릴리즈를 추적하는 오픈소스 레포
     group: 카테고리   tier: ⭐⭐⭐ 10k+  ·  ⭐⭐ 1k–10k  ·  ⭐ <1k */
  githubRepos: [
    /* ── 3D Mesh / Shape Generation ── */
    { name: 'Tencent-Hunyuan/Hunyuan3D-2',      url: 'https://github.com/Tencent-Hunyuan/Hunyuan3D-2',      note: 'Tencent 3D 생성',          group: '3D Mesh / Shape Generation', tier: '⭐⭐⭐' },
    { name: 'microsoft/TRELLIS',                url: 'https://github.com/microsoft/TRELLIS',                note: 'MS 3D 생성 파운데이션',     group: '3D Mesh / Shape Generation', tier: '⭐⭐⭐' },
    { name: 'openai/shap-e',                    url: 'https://github.com/openai/shap-e',                    note: 'OpenAI 3D 생성',           group: '3D Mesh / Shape Generation', tier: '⭐⭐⭐' },

    { name: 'ashawkey/stable-dreamfusion',      url: 'https://github.com/ashawkey/stable-dreamfusion',      note: 'DreamFusion 구현',          group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: 'threestudio-project/threestudio',  url: 'https://github.com/threestudio-project/threestudio',  note: 'Text-to-3D 프레임워크',     group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: 'openai/point-e',                   url: 'https://github.com/openai/point-e',                   note: 'OpenAI 포인트 클라우드',    group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: 'VAST-AI-Research/TripoSR',         url: 'https://github.com/VAST-AI-Research/TripoSR',         note: 'Fast image→3D',             group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: 'microsoft/TRELLIS.2',              url: 'https://github.com/microsoft/TRELLIS.2',              note: 'TRELLIS 후속',              group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: 'xxlong0/Wonder3D',                 url: 'https://github.com/xxlong0/Wonder3D',                 note: '단일 이미지→3D',            group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: 'TencentARC/InstantMesh',           url: 'https://github.com/TencentARC/InstantMesh',           note: '단일 이미지→3D 메시',       group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: 'nv-tlabs/GET3D',                   url: 'https://github.com/nv-tlabs/GET3D',                   note: 'NVIDIA 3D GAN',             group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: 'dreamgaussian/dreamgaussian',      url: 'https://github.com/dreamgaussian/dreamgaussian',      note: 'Gaussian splat 생성',       group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: 'AiuniAI/Unique3D',                 url: 'https://github.com/AiuniAI/Unique3D',                 note: '단일 이미지→3D',            group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: 'Tencent-Hunyuan/Hunyuan3D-2.1',    url: 'https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1',    note: 'Hunyuan3D 2.1',             group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: 'deepseek-ai/DreamCraft3D',         url: 'https://github.com/deepseek-ai/DreamCraft3D',         note: 'DeepSeek 3D 생성',          group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: 'wgsxm/PartCrafter',                url: 'https://github.com/wgsxm/PartCrafter',                note: '파트 단위 3D 생성',         group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: 'buaacyw/MeshAnything',             url: 'https://github.com/buaacyw/MeshAnything',             note: '아티스트 스타일 메시',      group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: '3DTopia/LGM',                      url: 'https://github.com/3DTopia/LGM',                      note: 'Large Gaussian Model',      group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: 'SUDO-AI-3D/zero123plus',           url: 'https://github.com/SUDO-AI-3D/zero123plus',           note: '뷰 합성 모델',              group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: 'nywang16/Pixel2Mesh',              url: 'https://github.com/nywang16/Pixel2Mesh',              note: '이미지→메시',               group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: 'thu-ml/prolificdreamer',           url: 'https://github.com/thu-ml/prolificdreamer',           note: 'VSD 기반 3D',               group: '3D Mesh / Shape Generation', tier: '⭐⭐' },
    { name: 'guochengqian/Magic123',            url: 'https://github.com/guochengqian/Magic123',            note: '단일 이미지→3D',            group: '3D Mesh / Shape Generation', tier: '⭐⭐' },

    { name: 'bytedance/MVDream',                url: 'https://github.com/bytedance/MVDream',                note: '멀티뷰 디퓨전',              group: '3D Mesh / Shape Generation', tier: '⭐' },
    { name: 'buaacyw/MeshAnythingV2',           url: 'https://github.com/buaacyw/MeshAnythingV2',           note: 'MeshAnything v2',            group: '3D Mesh / Shape Generation', tier: '⭐' },
    { name: 'hustvl/GaussianDreamer',           url: 'https://github.com/hustvl/GaussianDreamer',           note: 'Gaussian 기반 3D',           group: '3D Mesh / Shape Generation', tier: '⭐' },
    { name: 'bytedance/ImageDream',             url: 'https://github.com/bytedance/ImageDream',             note: '이미지 컨디션 3D',           group: '3D Mesh / Shape Generation', tier: '⭐' },
    { name: 'Gorilla-Lab-SCUT/Fantasia3D',      url: 'https://github.com/Gorilla-Lab-SCUT/Fantasia3D',      note: '디스엔탱글 3D 생성',         group: '3D Mesh / Shape Generation', tier: '⭐' },
    { name: 'jiawei-ren/dreamgaussian4d',       url: 'https://github.com/jiawei-ren/dreamgaussian4d',       note: '4D Gaussian 생성',           group: '3D Mesh / Shape Generation', tier: '⭐' },
    { name: 'bytedance/MVDream-threestudio',    url: 'https://github.com/bytedance/MVDream-threestudio',    note: 'MVDream + threestudio',      group: '3D Mesh / Shape Generation', tier: '⭐' },
    { name: 'NIRVANALAN/LN3Diff',               url: 'https://github.com/NIRVANALAN/LN3Diff',               note: '잠재 3D 디퓨전',             group: '3D Mesh / Shape Generation', tier: '⭐' },
    { name: 'sail-sg/TreeMeshGPT',              url: 'https://github.com/sail-sg/TreeMeshGPT',              note: '트리 구조 메시 GPT',         group: '3D Mesh / Shape Generation', tier: '⭐' },

    /* ── Texture / Material Generation ── */
    { name: 'TEXTurePaper/TEXTurePaper',        url: 'https://github.com/TEXTurePaper/TEXTurePaper',        note: 'TEXTure 공식',               group: 'Texture / Material Generation', tier: '⭐' },
    { name: 'OpenTexture/Paint3D',              url: 'https://github.com/OpenTexture/Paint3D',              note: '3D 메시 텍스처링',           group: 'Texture / Material Generation', tier: '⭐' },
    { name: 'sakalond/StableGen',               url: 'https://github.com/sakalond/StableGen',               note: 'Blender 통합 텍스처',        group: 'Texture / Material Generation', tier: '⭐' },
    { name: 'daveredrum/Text2Tex',              url: 'https://github.com/daveredrum/Text2Tex',              note: '텍스트→텍스처',              group: 'Texture / Material Generation', tier: '⭐' },
    { name: 'zzzyuqing/DreamMat',               url: 'https://github.com/zzzyuqing/DreamMat',               note: 'PBR 머티리얼 생성',          group: 'Texture / Material Generation', tier: '⭐' },
    { name: 'Night1099/COMFYUI-PBRFusion4',     url: 'https://github.com/Night1099/COMFYUI-PBRFusion4',     note: 'ComfyUI PBR 노드',             group: 'Texture / Material Generation', tier: '⭐' },

    /* ── Rigging / Skinning ── */
    { name: 'zhan-xu/RigNet',                   url: 'https://github.com/zhan-xu/RigNet',                   note: '자동 리깅',                 group: 'Rigging / Skinning', tier: '⭐⭐' },
    { name: 'VAST-AI-Research/UniRig',          url: 'https://github.com/VAST-AI-Research/UniRig',          note: '범용 자동 리깅',            group: 'Rigging / Skinning', tier: '⭐⭐' },

    { name: 'PeizhuoLi/neural-blend-shapes',    url: 'https://github.com/PeizhuoLi/neural-blend-shapes',    note: '뉴럴 블렌드셰입',            group: 'Rigging / Skinning', tier: '⭐' },
    { name: 'pKrime/brignet',                   url: 'https://github.com/pKrime/brignet',                   note: 'Blender RigNet',             group: 'Rigging / Skinning', tier: '⭐' },
    { name: 'Isabella98Liu/RigAnything',        url: 'https://github.com/Isabella98Liu/RigAnything',        note: '범용 리깅 파이프라인',       group: 'Rigging / Skinning', tier: '⭐' },

    /* ── Character Animation / Motion Generation ── */
    { name: 'sebastianstarke/AI4Animation',     url: 'https://github.com/sebastianstarke/AI4Animation',     note: '캐릭터 모션 ML',            group: 'Character Animation / Motion Generation', tier: '⭐⭐' },
    { name: 'GuyTevet/motion-diffusion-model',  url: 'https://github.com/GuyTevet/motion-diffusion-model',  note: 'MDM 공식',                  group: 'Character Animation / Motion Generation', tier: '⭐⭐' },
    { name: 'OpenMotionLab/MotionGPT',          url: 'https://github.com/OpenMotionLab/MotionGPT',          note: '모션 LLM',                  group: 'Character Animation / Motion Generation', tier: '⭐⭐' },
    { name: 'DeepMotionEditing/deep-motion-editing', url: 'https://github.com/DeepMotionEditing/deep-motion-editing', note: '뉴럴 모션 에디팅',     group: 'Character Animation / Motion Generation', tier: '⭐⭐' },
    { name: 'facebookresearch/ai4animationpy',  url: 'https://github.com/facebookresearch/ai4animationpy',  note: 'AI4Animation Python',       group: 'Character Animation / Motion Generation', tier: '⭐⭐' },
    { name: 'EricGuo5513/HumanML3D',            url: 'https://github.com/EricGuo5513/HumanML3D',            note: '모션-텍스트 데이터셋',      group: 'Character Animation / Motion Generation', tier: '⭐⭐' },
    { name: 'EricGuo5513/momask-codes',         url: 'https://github.com/EricGuo5513/momask-codes',         note: 'MoMask 공식',               group: 'Character Animation / Motion Generation', tier: '⭐⭐' },

    { name: 'mingyuan-zhang/MotionDiffuse',     url: 'https://github.com/mingyuan-zhang/MotionDiffuse',     note: '텍스트→모션 디퓨전',         group: 'Character Animation / Motion Generation', tier: '⭐' },
    { name: 'Mael-zys/T2M-GPT',                 url: 'https://github.com/Mael-zys/T2M-GPT',                 note: '텍스트→모션 GPT',            group: 'Character Animation / Motion Generation', tier: '⭐' },
    { name: 'priormdm/priormdm',                url: 'https://github.com/priormdm/priormdm',                note: 'Prior MDM',                  group: 'Character Animation / Motion Generation', tier: '⭐' },

    /* ── Speech-Driven 3D Facial Animation ── */
    { name: 'EvelynFan/FaceFormer',             url: 'https://github.com/EvelynFan/FaceFormer',             note: '음성 기반 페이셜',           group: 'Speech-Driven 3D Facial Animation', tier: '⭐' },
    { name: 'Doubiiu/CodeTalker',               url: 'https://github.com/Doubiiu/CodeTalker',               note: '코드북 기반 페이셜',         group: 'Speech-Driven 3D Facial Animation', tier: '⭐' },

    /* ── Co-Speech Gesture Generation ── */
    { name: 'Advocate99/DiffGesture',           url: 'https://github.com/Advocate99/DiffGesture',           note: '디퓨전 제스처 생성',         group: 'Co-Speech Gesture Generation', tier: '⭐' },
    { name: 'alvinliu0/HA2G',                   url: 'https://github.com/alvinliu0/HA2G',                   note: '계층형 오디오→제스처',       group: 'Co-Speech Gesture Generation', tier: '⭐' },

    /* ── 2D Image-Based Animation ── */
    { name: 'Rudrabha/Wav2Lip',                 url: 'https://github.com/Rudrabha/Wav2Lip',                 note: '립싱크 합성',              group: '2D Image-Based Animation', tier: '⭐⭐⭐' },
    { name: 'guoyww/AnimateDiff',               url: 'https://github.com/guoyww/AnimateDiff',               note: '디퓨전 영상 애니메이션',   group: '2D Image-Based Animation', tier: '⭐⭐⭐' },
    { name: 'magic-research/magic-animate',     url: 'https://github.com/magic-research/magic-animate',     note: 'Magic Animate',            group: '2D Image-Based Animation', tier: '⭐⭐⭐' },

    { name: 'OpenTalker/video-retalking',       url: 'https://github.com/OpenTalker/video-retalking',       note: '영상 리토킹',               group: '2D Image-Based Animation', tier: '⭐⭐' },
    { name: 'TMElyralab/MuseTalk',              url: 'https://github.com/TMElyralab/MuseTalk',              note: '실시간 립싱크',             group: '2D Image-Based Animation', tier: '⭐⭐' },
    { name: 'guoqincode/Open-AnimateAnyone',    url: 'https://github.com/guoqincode/Open-AnimateAnyone',    note: 'Animate Anyone 오픈',       group: '2D Image-Based Animation', tier: '⭐⭐' },

    /* ── 3D Avatar / Human Generation ── */
    { name: 'facebookresearch/pifuhd',          url: 'https://github.com/facebookresearch/pifuhd',          note: '고해상도 휴먼 복원',        group: '3D Avatar / Human Generation', tier: '⭐⭐' },
    { name: 'hongfz16/AvatarCLIP',              url: 'https://github.com/hongfz16/AvatarCLIP',              note: '텍스트→아바타',             group: '3D Avatar / Human Generation', tier: '⭐⭐' },

    { name: 'alvinliu0/HumanGaussian',          url: 'https://github.com/alvinliu0/HumanGaussian',          note: 'Gaussian 기반 휴먼',         group: '3D Avatar / Human Generation', tier: '⭐' },

    /* ── 3D Hair / Strand Generation ── */
    { name: 'eth-ait/GaussianHaircut',          url: 'https://github.com/eth-ait/GaussianHaircut',          note: 'Gaussian 헤어컷',            group: '3D Hair / Strand Generation', tier: '⭐' },
    { name: 'Vanessik/HAAR',                    url: 'https://github.com/Vanessik/HAAR',                    note: '스트랜드 헤어 생성',          group: '3D Hair / Strand Generation', tier: '⭐' },

    /* ── 3D Scene Generation ── */
    { name: 'Mr-Ma-yikun/FastScene',            url: 'https://github.com/Mr-Ma-yikun/FastScene',            note: '빠른 3D 씬 생성',             group: '3D Scene Generation', tier: '⭐' },

    /* ── ComfyUI / Pipeline Integrations ── */
    { name: 'comfyanonymous/ComfyUI',           url: 'https://github.com/comfyanonymous/ComfyUI',           note: '노드 기반 AI 이미지 워크플로', group: 'ComfyUI / Pipeline Integrations', tier: '⭐⭐⭐' },
    { name: 'Stability-AI/generative-models',   url: 'https://github.com/Stability-AI/generative-models',   note: 'Stable Diffusion 계열 공식',  group: 'ComfyUI / Pipeline Integrations', tier: '⭐⭐⭐' },
    { name: 'black-forest-labs/flux',           url: 'https://github.com/black-forest-labs/flux',           note: 'FLUX 이미지 생성 모델',       group: 'ComfyUI / Pipeline Integrations', tier: '⭐⭐⭐' },

    { name: 'MrForExample/ComfyUI-3D-Pack',     url: 'https://github.com/MrForExample/ComfyUI-3D-Pack',     note: 'ComfyUI 3D 노드 팩',           group: 'ComfyUI / Pipeline Integrations', tier: '⭐⭐' },
  ],
};
