{% load static %}
var staticCacheName = "bitcaster-pwa-v1";
var filesToCache = [
    "{% static 'bitcaster/images/logos/bitcaster.svg' %}",
    "{% static 'bitcaster/images/logos/logo48.png' %}",
    "{% static 'bitcaster/images/logos/logo128.png' %}",
    "{% static 'bitcaster/images/logos/logo400.png' %}",
    "{% static 'bitcaster/images/logos/name_white.svg' %}",
    "{% url 'pwa:offline' %}",
];

// Cache on install
self.addEventListener("install", event => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(staticCacheName)
            .then(cache => {
                return cache.addAll(filesToCache);
            })
    )
});

// Serve from Cache
self.addEventListener("fetch", event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                return response || fetch(event.request);
            })
            .catch(() => {
                return caches.match('{% url "pwa:offline" %}');
            })
    )
});

// Clear cache on activate
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames
                    .filter(cacheName => (cacheName.startsWith("bitcaster-pwa-")))
                    .filter(cacheName => (cacheName !== staticCacheName))
                    .map(cacheName => caches.delete(cacheName))
            );
        })
    );
});
