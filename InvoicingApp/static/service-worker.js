self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open('my-cache').then(function(cache) {
            return cache.addAll([
                '/',
                '/static/css/bootstrap.min.css',
                '/static/js/jquery-3.5.1.slim.min.js',
                '/static/js/popper.min.js',
                '/static/js/bootstrap.min.js',
                '/static/icons/PIM_Icon_Dashboard_N_RGB.jpg',
                '/static/manifest.json'
            ]);
        })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request).then(function(response) {
            return response || fetch(event.request);
        })
    );
});
