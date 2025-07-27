// AndyLibrary Service Worker - Educational Mission Offline Support
// Getting education into the hands of people who can least afford it!

const CACHE_NAME = 'andylibrary-v1';
const EDUCATIONAL_MISSION_CACHE = 'educational-content-v1';

// Critical files for offline educational access
const CORE_CACHE_FILES = [
  '/',
  '/bowersworld.html',
  '/auth.html', 
  '/setup.html',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png'
];

// Educational content to cache for offline access
const EDUCATIONAL_CACHE_FILES = [
  '/api/categories',
  '/api/books/featured',
  '/api/books/offline-essentials'
];

// Install event - Cache core files
self.addEventListener('install', event => {
  console.log('📚 AndyLibrary Service Worker: Installing for educational mission');
  
  event.waitUntil(
    Promise.all([
      // Cache core application files
      caches.open(CACHE_NAME).then(cache => {
        console.log('📦 Caching core application files');
        return cache.addAll(CORE_CACHE_FILES);
      }),
      
      // Cache educational content for offline learning
      caches.open(EDUCATIONAL_MISSION_CACHE).then(cache => {
        console.log('📚 Caching educational content for offline access');
        return cache.addAll(EDUCATIONAL_CACHE_FILES);
      })
    ]).then(() => {
      console.log('✅ AndyLibrary ready for offline educational access!');
      // Force activation of new service worker
      return self.skipWaiting();
    })
  );
});

// Activate event - Clean up old caches
self.addEventListener('activate', event => {
  console.log('🚀 AndyLibrary Service Worker: Activating educational mission');
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          // Delete old cache versions
          if (cacheName !== CACHE_NAME && cacheName !== EDUCATIONAL_MISSION_CACHE) {
            console.log('🗑️ Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      // Take control of all pages immediately
      return self.clients.claim();
    })
  );
});

// Fetch event - Serve cached content when offline
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  
  // Handle different types of requests
  if (event.request.method === 'GET') {
    
    // Educational API requests - Cache-first for offline learning
    if (url.pathname.startsWith('/api/books') || url.pathname.startsWith('/api/categories')) {
      event.respondWith(
        caches.match(event.request).then(response => {
          if (response) {
            console.log('📚 Serving educational content from cache:', url.pathname);
            return response;
          }
          
          // Fetch from network and cache for future offline use
          return fetch(event.request).then(response => {
            if (response.ok) {
              const responseClone = response.clone();
              caches.open(EDUCATIONAL_MISSION_CACHE).then(cache => {
                cache.put(event.request, responseClone);
              });
            }
            return response;
          }).catch(() => {
            // Network failed - show offline message for educational content
            return new Response(JSON.stringify({
              error: 'offline',
              message: 'Educational content temporarily unavailable. Check your internet connection.',
              cached_content: 'Available in offline mode'
            }), {
              headers: { 'Content-Type': 'application/json' }
            });
          });
        })
      );
    }
    
    // Static files - Cache-first strategy
    else if (url.pathname.startsWith('/static/') || 
             url.pathname.endsWith('.css') || 
             url.pathname.endsWith('.js') ||
             url.pathname.endsWith('.png') ||
             url.pathname.endsWith('.ico')) {
      
      event.respondWith(
        caches.match(event.request).then(response => {
          return response || fetch(event.request).then(response => {
            if (response.ok) {
              const responseClone = response.clone();
              caches.open(CACHE_NAME).then(cache => {
                cache.put(event.request, responseClone);
              });
            }
            return response;
          });
        })
      );
    }
    
    // HTML pages - Network-first, fallback to cache
    else if (url.pathname.endsWith('.html') || url.pathname === '/') {
      event.respondWith(
        fetch(event.request).then(response => {
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        }).catch(() => {
          // Network failed - serve from cache
          return caches.match(event.request).then(response => {
            if (response) {
              console.log('📱 Serving page from cache (offline):', url.pathname);
              return response;
            }
            
            // No cache - show offline page
            return caches.match('/').then(fallback => {
              return fallback || new Response(`
                <!DOCTYPE html>
                <html>
                <head>
                  <title>AndyLibrary - Offline</title>
                  <meta name="viewport" content="width=device-width, initial-scale=1.0">
                  <style>
                    body { font-family: Arial; text-align: center; padding: 50px; }
                    .offline { color: #667eea; }
                  </style>
                </head>
                <body>
                  <div class="offline">
                    <h1>📚 AndyLibrary</h1>
                    <h2>Educational Mission Continues Offline</h2>
                    <p>You're currently offline, but cached educational content is still available.</p>
                    <p><strong>Mission:</strong> Getting education into the hands of people who can least afford it!</p>
                    <button onclick="location.reload()">🔄 Try Again</button>
                  </div>
                </body>
                </html>
              `, {
                headers: { 'Content-Type': 'text/html' }
              });
            });
          });
        })
      );
    }
  }
});

// Background sync for educational mission data
self.addEventListener('sync', event => {
  if (event.tag === 'educational-content-sync') {
    console.log('🔄 Background sync: Updating educational content');
    event.waitUntil(
      // Sync educational content when connection is restored
      updateEducationalContent()
    );
  }
});

// Update educational content in background
async function updateEducationalContent() {
  try {
    const cache = await caches.open(EDUCATIONAL_MISSION_CACHE);
    const responses = await Promise.allSettled([
      fetch('/api/books/featured'),
      fetch('/api/categories'),
      fetch('/api/books/offline-essentials')
    ]);
    
    responses.forEach((response, index) => {
      if (response.status === 'fulfilled' && response.value.ok) {
        const urls = ['/api/books/featured', '/api/categories', '/api/books/offline-essentials'];
        cache.put(urls[index], response.value.clone());
      }
    });
    
    console.log('✅ Educational content updated in background');
  } catch (error) {
    console.log('⚠️ Background educational content update failed:', error);
  }
}

// Notify clients about updates
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    console.log('🚀 Updating AndyLibrary for enhanced educational experience');
    self.skipWaiting();
  }
});

console.log('📚 AndyLibrary Service Worker loaded - Educational mission enabled!');