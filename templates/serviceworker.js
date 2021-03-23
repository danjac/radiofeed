{% load static %}
const cacheName = "app-cache";

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(cacheName).then(function(cache) {
      return cache.addAll(
        [
          "{% static debug|yesno:'dev/app.css,dist/app.css' %}",
          "{% static debug|yesno:'dev/app.js,dist/app.js' %}"
        ]
      );
    })
  );
});

self.addEventListener('fetch', function(event) {
  if (!/^https?:$/i.test(new URL(event.request.url).protocol)) return;
  event.respondWith(
    caches.open(cacheName).then(function(cache) {
      const request = new Request(event.request.url, {mode: 'no-cors'});
      return cache.match(request).then(function (response) {
        return response || fetch(request).then(function(response) {
          cache.put(request, response.clone());
          return response;
        });
      });
    })
  );
});
