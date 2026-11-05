# Baut aus src/schichtplan.html die App (PWA) im Hauptordner: index.html, sw.js, manifest.webmanifest, 404.html
# Aufruf: python3 build.py   – danach committen und auf main pushen (GitHub Pages veröffentlicht automatisch)
import os, re, json, shutil, hashlib, glob
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
src=open('src/schichtplan.html',encoding='utf-8').read()
ver=hashlib.sha1((src+open(__file__,encoding='utf-8').read()).encode()).hexdigest()[:10]
head='''<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#1d1f24">
<meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Schichtplaner"><meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="manifest" href="manifest.webmanifest"><link rel="icon" href="icons/icon-192.png"><link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,-apple-system,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
<script>
// Ohne Claude: Speichern (PDF, Tabelle, Sicherung) als normaler Download
window.claude={use:function(n){return Promise.resolve(n==="downloads"?{save:function(r){return new Promise(function(ok){
  var ext=(r.filename.split(".").pop()||"").toLowerCase();var T={pdf:"application/pdf",csv:"text/csv;charset=utf-8",json:"application/json",xlsx:"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",txt:"text/plain;charset=utf-8"};
  var b=r.data instanceof Blob&&r.data.type?r.data:new Blob([r.data],{type:T[ext]||"application/octet-stream"});var u=URL.createObjectURL(b);var a=document.createElement("a");a.href=u;a.download=r.filename;
  document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(u);a.remove()},60000);ok({status:"saved"})})}}:null)}};
if("serviceWorker" in navigator)addEventListener("load",function(){navigator.serviceWorker.register("sw.js")});
</script>
</head><body>
'''
open('index.html','w',encoding='utf-8').write(head+src+'\n</body></html>\n')
man={"name":"Schichtplaner","short_name":"Schichtplaner","description":"Persönlicher Schichtkalender für Schichtarbeit. Idee: Hans-Jürgen Schlichting.",
 "lang":"de","start_url":"./","scope":"./","display":"standalone","orientation":"portrait","background_color":"#f3f2ef","theme_color":"#1d1f24",
 "icons":[{"src":"icons/icon-192.png","sizes":"192x192","type":"image/png"},{"src":"icons/icon-512.png","sizes":"512x512","type":"image/png"},
          {"src":"icons/icon-maskable-192.png","sizes":"192x192","type":"image/png","purpose":"maskable"},{"src":"icons/icon-maskable-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]}
open('manifest.webmanifest','w',encoding='utf-8').write(json.dumps(man,ensure_ascii=False,indent=1))
pre=["./","index.html","manifest.webmanifest"]+["icons/"+os.path.basename(f) for f in glob.glob('icons/*.png')]+["help/"+os.path.basename(f) for f in glob.glob('help/*.jpg')]
sw='''// Offline-Speicher: App-Dateien werden auf dem Handy zwischengespeichert. Version wechselt bei jedem Update.
const CACHE="schichtplan-%s";const PRE=%s;
self.addEventListener("install",e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(PRE)).then(()=>self.skipWaiting()))});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener("fetch",e=>{const r=e.request;if(r.method!=="GET")return;const u=new URL(r.url);
  if(r.mode==="navigate"||u.pathname.endsWith("/index.html")){ // Seite: erst online (für Updates), sonst aus dem Speicher
    e.respondWith(fetch(r).then(res=>{const c=res.clone();caches.open(CACHE).then(x=>x.put("index.html",c));return res}).catch(()=>caches.match("index.html")));return}
  e.respondWith(caches.match(r).then(hit=>hit||fetch(r).then(res=>{if(res.ok||res.type==="opaque"){const c=res.clone();caches.open(CACHE).then(x=>x.put(r,c))}return res})))});
'''%(ver,json.dumps(pre))
open('sw.js','w',encoding='utf-8').write(sw)
open('404.html','w').write('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=./"><a href="./">Schichtplan öffnen</a>')
print("version",ver,"files",len(pre))
