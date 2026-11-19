# Baut aus englisch/src/vokabelheft.html die Englisch-App (PWA) im Ordner englisch/:
# index.html, sw.js, manifest.webmanifest, icons/*.png
# Aufruf: python3 englisch/build.py  – danach committen und auf main pushen (GitHub Pages veröffentlicht automatisch)
# Adresse: https://onkelstuka-droid.github.io/Schichtplan-/englisch/
import os, json, hashlib, glob
os.chdir(os.path.dirname(os.path.abspath(__file__)))
src = open('src/vokabelheft.html', encoding='utf-8').read()
ver = hashlib.sha1((src + open(__file__, encoding='utf-8').read()).encode()).hexdigest()[:10]

# App-Symbole (blaues Heft mit „EN“ und gelbem Textmarker), nur wenn sie fehlen
def icons():
    from PIL import Image, ImageDraw, ImageFont
    font = '../fonts/SPSans-Bold.ttf'
    def make(size, maskable, name):
        s = size * 4
        im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        blue, yellow = (36, 64, 194, 255), (255, 228, 92, 255)
        if maskable:
            d.rectangle([0, 0, s, s], fill=blue); k = 0.62
        else:
            d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.22), fill=blue); k = 0.8
        f = ImageFont.truetype(font, int(s * 0.36 * k))
        tw = d.textlength('EN', font=f)
        x, y = (s - tw) / 2, s * 0.5 - s * 0.26 * k
        mh = s * 0.075 * k
        d.rectangle([x - s * 0.02, y + s * 0.36 * k, x + tw + s * 0.02, y + s * 0.36 * k + mh], fill=yellow)
        d.text((x, y), 'EN', font=f, fill=(255, 255, 255, 255))
        d.rectangle([s * 0.5 - s * 0.26 * k, s * 0.5 + s * 0.27 * k, s * 0.5 + s * 0.26 * k, s * 0.5 + s * 0.27 * k + s * 0.012], fill=(255, 255, 255, 140))
        im.resize((size, size), Image.LANCZOS).save('icons/' + name)
    os.makedirs('icons', exist_ok=True)
    for size, mask, name in [(192, False, 'icon-192.png'), (512, False, 'icon-512.png'), (192, True, 'icon-maskable-192.png'),
                             (512, True, 'icon-maskable-512.png'), (180, True, 'apple-touch-icon.png')]:
        if not os.path.exists('icons/' + name):
            make(size, mask, name)
icons()

head = '''<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#2440c2">
<meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Vokabelheft">
<link rel="manifest" href="manifest.webmanifest"><link rel="icon" href="icons/icon-192.png"><link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,-apple-system,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
<script>if("serviceWorker" in navigator)addEventListener("load",function(){navigator.serviceWorker.register("sw.js")});</script>
</head><body>
'''
open('index.html', 'w', encoding='utf-8').write(head + src + '\n</body></html>\n')

man = {"name": "Vokabelheft Englisch", "short_name": "Englisch", "description": "Englisch lernen: Vokabeln, Hören, Schreiben, Satzbau, Grammatik und Sprechen.",
       "lang": "de", "start_url": "./", "scope": "./", "display": "standalone", "orientation": "portrait", "background_color": "#f4f6fb", "theme_color": "#2440c2",
       "icons": [{"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
                 {"src": "icons/icon-maskable-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
                 {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}
open('manifest.webmanifest', 'w', encoding='utf-8').write(json.dumps(man, ensure_ascii=False, indent=1))

pre = ["./", "index.html", "manifest.webmanifest"] + ["icons/" + os.path.basename(f) for f in sorted(glob.glob('icons/*.png'))]
sw = '''// Offline-Speicher der Englisch-App. Version wechselt bei jedem Update.
const CACHE="vokabelheft-%s";const PRE=%s;
self.addEventListener("install",e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(PRE)).then(()=>self.skipWaiting()))});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith("vokabelheft-")&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener("fetch",e=>{const r=e.request;if(r.method!=="GET")return;const u=new URL(r.url);
  if(r.mode==="navigate"||u.pathname.endsWith("/index.html")){ // Seite: erst online (für Updates), sonst aus dem Speicher
    e.respondWith(fetch(r).then(res=>{const c=res.clone();caches.open(CACHE).then(x=>x.put("index.html",c));return res}).catch(()=>caches.match("index.html")));return}
  e.respondWith(caches.match(r).then(hit=>hit||fetch(r).then(res=>{if(res.ok||res.type==="opaque"){const c=res.clone();caches.open(CACHE).then(x=>x.put(r,c))}return res})))});
''' % (ver, json.dumps(pre))
open('sw.js', 'w', encoding='utf-8').write(sw)
print("version", ver, "files", len(pre))
