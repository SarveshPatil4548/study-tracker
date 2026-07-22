const CACHE_NAME = 'study-tracker-v1';
const STATIC_CACHE = 'study-tracker-static-v1';

const PRECACHE_URLS = [
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/offline.html',
  '/',
  '/dashboard',
  '/subjects',
  '/stats',
  '/calendar',
  '/exams',
  '/notes',
  '/sessions/new',
  '/sessions',
];

const NEVER_CACHE = [
  '/login',
  '/logout',
  '/register',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll(PRECACHE_URLS).catch(() => {});
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME && name !== STATIC_CACHE)
          .map((name) => caches.delete(name))
      );
    })
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  const path = url.pathname;

  for (const route of NEVER_CACHE) {
    if (path.startsWith(route)) return;
  }

  if (path.startsWith('/static/')) {
    event.respondWith(cacheFirst(event.request));
  } else {
    event.respondWith(networkFirst(event.request));
  }
});

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const offlinePage = await caches.match('/static/offline.html');
    if (offlinePage) return offlinePage;
    return new Response('Offline', { status: 503 });
  }
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) return cached;
    const offlinePage = await caches.match('/static/offline.html');
    if (offlinePage) return offlinePage;
    return new Response('Offline', { status: 503 });
  }
}
