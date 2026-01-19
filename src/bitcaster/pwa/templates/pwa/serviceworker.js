/*! Copyright 2023 (c)
    @license Private
    Bob    {{project.version}}
    Asset  {{ asset.version }}
*/
var _ = "{% load static %}";
var version = "{{project.version}}";
var staticCacheName = "bob-pwa";
var filesToCache = [
    "{% static 'pwa/pwa.css' %}",
    "{% static 'pwa/pwa.min.js' %}",
    "{% static 'pwa/button/default.png' %}",
    "{% static 'pwa/button/alarmed.png' %}",
    "{% static 'pwa/button/pressed.gif' %}",
    "{% static 'pwa/icons/badge.png' %}",
    "{% static 'pwa/icons/icon-128x128.png' %}",
    "{% static 'sentry/sentry.js' %}",
    "{% static 'vendor/axios.min.js' %}",
    "{% static 'pwa/ko-3.5.1.js' %}",
    // "{% static 'pwa/images/bg_ciao.svg' %}",
    // "{% static 'pwa/images/sos_button.svg' %}",
    "{% static 'bob/images/favicons/android-chrome-256x256.png' %}",
    "{% url 'pwa-offline' %}",
    "/jsi18n/",
    "/jsreverse.js",
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
                return caches.match('/pwa/offline/');
            })
    )
});

// Clear cache on activate
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames
                    .filter(cacheName => (cacheName.startsWith("django-pwa-")))
                    .filter(cacheName => (cacheName !== staticCacheName))
                    .map(cacheName => caches.delete(cacheName))
            );
        })
    );
});
