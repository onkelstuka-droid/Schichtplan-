// Die Englisch-App ist nach /Englisch/ umgezogen. Dieser Service Worker räumt den alten Speicher auf und entfernt sich selbst.
self.addEventListener("install",()=>self.skipWaiting());
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith("vokabelheft-")).map(k=>caches.delete(k)))).then(()=>self.registration.unregister()))});
