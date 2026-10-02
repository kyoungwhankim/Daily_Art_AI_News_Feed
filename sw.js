/* AI Art Daily — service worker (PWA 오프라인 캐시).
   scripts/build_site.py가 __VERSION__ 과 __PRECACHE__ 를 채워 배포 사이트의 /sw.js 로 낸다.
   - 페이지(HTML), data/index.json·keywords.json, 그 밖의 이 사이트 파일: 네트워크 우선 → 안 되면 저장본
   - ?v= 가 붙은 파일(날짜별 기사 데이터, app.js, CSS), 아이콘, React: 저장본 우선 (내용이 바뀌면 주소가 바뀐다)
   - 기사 이미지 등 다른 사이트 파일은 건드리지 않는다 */
const VERSION = '__VERSION__';
const CACHE = `aiad-${VERSION}`;
const PRECACHE = __PRECACHE__;
const SHELL = '/';

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith('aiad-') && k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

async function networkFirst(request, fallbackUrl) {
  const cache = await caches.open(CACHE);
  try {
    const res = await fetch(request);
    if (res.ok) cache.put(request, res.clone());
    return res;
  } catch (e) {
    const hit = await cache.match(request, { ignoreSearch: request.mode === 'navigate' });
    if (hit) return hit;
    if (fallbackUrl) {
      const shell = await cache.match(fallbackUrl);
      if (shell) return shell;      // 앱은 주소를 읽어 같은 화면을 띄운다
    }
    throw e;
  }
}

async function cacheFirst(request) {
  const cache = await caches.open(CACHE);
  const hit = await cache.match(request);
  if (hit) return hit;
  const res = await fetch(request);
  if (res.ok || res.type === 'opaque') cache.put(request, res.clone());
  return res;
}

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  if (url.origin === self.location.origin) {
    if (req.mode === 'navigate') return event.respondWith(networkFirst(req, SHELL));
    if (url.pathname === '/data/index.json' || url.pathname === '/data/keywords.json') {
      return event.respondWith(networkFirst(req));
    }
    if (url.searchParams.has('v') || url.pathname.startsWith('/icons/')) {
      return event.respondWith(cacheFirst(req));
    }
    return event.respondWith(networkFirst(req));   // config.js, manifest 등
  }
  if (url.hostname === 'unpkg.com') return event.respondWith(cacheFirst(req));
});
