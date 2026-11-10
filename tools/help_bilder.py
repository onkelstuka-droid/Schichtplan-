#!/usr/bin/env python3
"""Erzeugt die Bilder der Anleitung (help/*.jpg) neu – für jede Sprache.

Aufruf (im Projektordner, vorher: python3 -m http.server 8765):
    python3 tools/help_bilder.py en tr ro        # -> help/en/*.jpg, help/tr/*.jpg, help/ro/*.jpg
    python3 tools/help_bilder.py de              # -> help/*.jpg (deutsche Bilder überschreiben!)
Optional: Umgebungsvariable JSPDF=/pfad/jspdf.umd.min.js, falls cdnjs nicht erreichbar ist.
Alle Bilder zeigen Beispieldaten; das Datum ist fest auf Di 3.11.2026 gestellt.
"""
import os, sys, datetime
from playwright.sync_api import sync_playwright
from PIL import Image

U = "http://localhost:8765/index.html"
W, H, DPR = 375, 760, 1.5
OUTW, OUTH = 560, 1134
LOCALE = {"de": "de-DE", "en": "en-GB", "tr": "tr-TR", "ro": "ro-RO", "ru": "ru-RU", "pl": "pl-PL"}
# Beispieltexte je Sprache (Nutzerdaten werden in der App nicht übersetzt)
TXT = {
 "de": dict(n1="Urlaub genehmigt von Herrn Maier", n2="Zahnarzt 10 Uhr", n3="Elternabend 19 Uhr", ot="Inventur", rt="Hausordnung", ra="HO",
            c1="Monika Schlichting", c2="Thomas Huber", c2i="Schichtgruppe B", opa="Opa Karl", me="Hans-Jürgen", model="Mein Schichtmodell 1", wife="Frau"),
 "en": dict(n1="Leave approved by Mr Maier", n2="Dentist 10 am", n3="Parents' evening 7 pm", ot="Stocktaking", rt="Cleaning duty", ra="CD",
            c1="Monika Schlichting", c2="Thomas Huber", c2i="Shift group B", opa="Grandpa Karl", me="Hans-Jürgen", model="My shift model 1", wife="Wife"),
 "tr": dict(n1="İzni Bay Maier onayladı", n2="Diş hekimi saat 10", n3="Veli toplantısı saat 19", ot="Envanter", rt="Bina temizliği", ra="BT",
            c1="Monika Schlichting", c2="Thomas Huber", c2i="Vardiya grubu B", opa="Dede Karl", me="Hans-Jürgen", model="Vardiya modelim 1", wife="Eşim"),
 "ro": dict(n1="Concediu aprobat de dl Maier", n2="Dentist la ora 10", n3="Ședința cu părinții la 19", ot="Inventar", rt="Curățenie scară", ra="CS",
            c1="Monika Schlichting", c2="Thomas Huber", c2i="Grupa de tură B", opa="Bunicul Karl", me="Hans-Jürgen", model="Modelul meu 1", wife="Soția"),
 "ru": dict(n1="Отпуск одобрил г-н Майер", n2="Стоматолог в 10:00", n3="Родительское собрание в 19:00", ot="Инвентаризация", rt="Уборка подъезда", ra="УП",
            c1="Monika Schlichting", c2="Thomas Huber", c2i="Смена B", opa="Дедушка Карл", me="Hans-Jürgen", model="Моя модель смен 1", wife="Жена"),
 "pl": dict(n1="Urlop zatwierdził pan Maier", n2="Dentysta o 10:00", n3="Zebranie rodziców o 19:00", ot="Inwentaryzacja", rt="Sprzątanie klatki", ra="SK",
            c1="Monika Schlichting", c2="Thomas Huber", c2i="Grupa zmianowa B", opa="Dziadek Karl", me="Hans-Jürgen", model="Mój model zmian 1", wife="Żona"),
}

def dn(y, m, d):  # Tagnummer wie in der App (Monat 1–12)
    return (datetime.date(y, m, d) - datetime.date(1970, 1, 1)).days

def seed_js(lang):
    t = TXT[lang]; import json
    vac = {}
    for d in range(9, 14): vac[dn(2026, 11, d)] = "U"
    vac[dn(2026, 11, 23)] = "AG"; vac[dn(2026, 11, 24)] = "AG"; vac[dn(2026, 11, 4)] = "K"
    notes = {dn(2026, 11, 9): {"t": t["n1"], "to": dn(2026, 11, 13)}, dn(2026, 11, 19): {"t": t["n2"]}}
    ot = [{"id": "o1", "d": dn(2026, 11, 17), "from": "21:00", "to": "23:30", "pause": 0, "min": 150, "note": t["ot"]}]
    contacts = [{"name": t["c1"], "tel": "0160 9876543", "info": "", "who": "Familie"},
                {"name": t["c2"], "tel": "0171 2345678", "info": t["c2i"], "who": "Teamleiter"}]
    bdays = [{"id": "a", "name": "Monika", "d": "11-08", "y": 1972}, {"id": "b", "name": "Thomas", "d": "11-27", "y": 1985},
             {"id": "c", "name": t["opa"], "d": "12-24", "y": 1940}, {"id": "d", "name": "Anna", "d": "01-09", "y": 2010},
             {"id": "e", "name": "Lisa", "d": "03-15", "y": None}, {"id": "f", "name": "Sabine", "d": "03-02", "y": 1968}]
    routines = [{"id": "r", "name": t["rt"], "ab": t["ra"], "start": "2026-11-07", "n": 2, "unit": "w", "end": ""}]
    wk = lambda a, b: {str(d): [a, b] for d in range(1, 6)}
    cals = [{"id": "frau", "name": t["wife"], "icon": "👩", "type": "shift"},
            {"id": "k1", "name": "Lena", "icon": "🎒", "type": "week", "kind": "schule", "col": "#7c5cff", "ferien": True,
             "week": dict(wk("08:00", "13:00"), **{"5": ["08:00", "12:15"]}), "exc": {str(dn(2026, 11, 13)): {"off": 1, "why": ""}}, "notes": {str(dn(2026, 11, 12)): t["n2"]}},
            {"id": "k2", "name": "Max", "icon": "🧸", "type": "week", "kind": "kita", "col": "#00a3a3", "ferien": False,
             "week": dict(wk("07:30", "14:00"), **{"5": ["07:30", "13:00"]}), "exc": {}, "notes": {}}]
    wvac = {str(dn(2026, 11, d)): "U" for d in (11, 12)}
    data = {"sp_cals": cals, "sp_c_frau_sp_anchor2": "2026-11-09", "sp_c_frau_sp_vac2": wvac,
            "sp_vac2": vac, "sp_notes": notes, "sp_ot": ot, "sp_contacts": contacts, "sp_bdays": bdays, "sp_routines": routines,
            "sp_anim": False, "sp_sound": False, "sp_lastbak": 1793700000000, "sp_lang": lang, "sp_myname": t["me"], "sp_otcfg": {"agHours": 8, "carry": 0}}
    return "()=>{localStorage.clear();" + "".join(f"localStorage.setItem({json.dumps(k)},{json.dumps(json.dumps(v))});" for k, v in data.items()) + "}"

def run(lang):
    out = "help" if lang == "de" else os.path.join("help", lang)
    os.makedirs(out, exist_ok=True)
    t = TXT[lang]
    with sync_playwright() as p:
        loc = LOCALE[lang].replace("-", "_") + ".UTF-8"  # 24-Stunden-Uhrzeit in Zeitfeldern
        b = p.chromium.launch(args=["--lang=" + LOCALE[lang]], env=dict(os.environ, LANG=loc, LC_ALL=loc))
        def ctx():
            c = b.new_context(viewport={"width": W, "height": H}, device_scale_factor=DPR, service_workers="block",
                              locale=LOCALE[lang], timezone_id="Europe/Berlin")
            c.grant_permissions(["clipboard-read", "clipboard-write"], origin="http://localhost:8765")
            return c
        c = ctx(); pg = c.new_page(); pg.set_default_timeout(4000)
        pg.clock.set_fixed_time(datetime.datetime(2026, 11, 3, 10, 0))
        if os.environ.get("JSPDF"):
            pg.route("**/jspdf.umd.min.js", lambda r: r.fulfill(path=os.environ["JSPDF"], content_type="application/javascript"))
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(U); SEED = seed_js(lang)

        def fresh():
            pg.evaluate(SEED); pg.reload(); pg.wait_for_timeout(900)
        def shot(name, crop=None):
            pg.wait_for_timeout(450); f = os.path.join(out, name + ".png"); pg.screenshot(path=f)
            im = Image.open(f).convert("RGB")
            if crop: im = im.crop(tuple(int(v * DPR) for v in crop))
            im.resize((OUTW, OUTH), Image.LANCZOS).save(os.path.join(out, name + ".jpg"), quality=84); os.remove(f)
        def day(y, m, d, off=-200):
            n = dn(y, m, d)
            pg.evaluate(f"document.querySelector('[data-d=\"{n}\"]').scrollIntoView({{block:'center'}})"); pg.wait_for_timeout(200)
            pg.click(f'[data-d="{n}"]'); pg.wait_for_timeout(350); return n
        def scroll_to_day(y, m, d, off):
            n = dn(y, m, d)
            pg.evaluate(f"(()=>{{const e=document.querySelector('[data-d=\"{n}\"]');window.scrollTo(0,e.getBoundingClientRect().top+scrollY+({off}))}})()")
            pg.wait_for_timeout(400)
        def scroll_to_month(y, m, extra=0):
            n = dn(y, m, 1)
            pg.evaluate(f"(()=>{{const s=document.querySelector('[data-d=\"{n}\"]').closest('section'),hd=s.querySelector('h2')||s,top=document.querySelector('.dow').getBoundingClientRect().bottom;window.scrollTo(0,hd.getBoundingClientRect().top+scrollY-top-6+({extra}))}})()")
            pg.wait_for_timeout(400)
        def menu(m):
            pg.click("#menuBtn"); pg.wait_for_timeout(300); pg.click(f"[data-m={m}]"); pg.wait_for_timeout(500)
        def sheet_scroll(sel, block="center"):
            pg.evaluate(f"document.querySelector('{sel}').scrollIntoView({{block:'{block}'}})"); pg.wait_for_timeout(300)

        scenes = []
        def scene(f): scenes.append(f); return f

        @scene
        def kalender(): fresh(); scroll_to_month(2026, 11); shot("kalender")
        @scene
        def kopf():
            fresh(); scroll_to_month(2026, 11)
            box = pg.evaluate("(()=>{const e=document.querySelector('.dow');const r=e.getBoundingClientRect();return r.bottom})()")
            shot("kopf", crop=(0, 0, W, min(H, box + 4)))
        @scene
        def tag(): fresh(); day(2026, 11, 25); shot("tag")
        @scene
        def zeitraum():
            fresh(); day(2026, 11, 25); pg.click('[data-a="type"][data-t="U"]'); pg.wait_for_timeout(300)
            pg.click('[data-a="multi"]'); pg.wait_for_timeout(300); pg.click(f'[data-pd="{dn(2026,11,27)}"]'); shot("zeitraum")
        @scene
        def notiz():
            fresh(); day(2026, 11, 30); pg.click('[data-a="note"]'); pg.wait_for_timeout(300); pg.fill("#noteTxt", t["n3"]); shot("notiz")
            pg.click('[data-a="nsave"]'); shot("kalendereintrag")
        @scene
        def ueberstunden():
            fresh(); day(2026, 11, 17); pg.click('[data-a="otnew"]'); pg.wait_for_timeout(300)
            pg.fill("#otFrom", "22:00"); pg.fill("#otTo", "00:30"); pg.fill("#otPause", "15"); pg.dispatch_event("#otPause", "input"); shot("ueberstunden")
        @scene
        def feiertage(): fresh(); scroll_to_month(2026, 12); shot("feiertage")
        @scene
        def menue(): fresh(); pg.click("#menuBtn"); shot("menue")
        @scene
        def statistik(): fresh(); menu("stats"); shot("statistik")
        @scene
        def statistik2():
            fresh(); menu("stats")
            pg.evaluate("(()=>{const v=document.getElementById('statsView'),e=v.querySelector('[data-s=calpdf]');v.scrollTop=e.getBoundingClientRect().top+v.scrollTop-170})()")
            shot("statistik2")
        @scene
        def eintraege(): fresh(); menu("entries"); shot("eintraege")
        @scene
        def notizen(): fresh(); menu("notes"); shot("notizen")
        @scene
        def jahr(): fresh(); menu("year"); shot("jahr")
        @scene
        def modelle():
            fresh(); menu("models"); pg.click('[data-a="mnew"]'); pg.wait_for_timeout(300); pg.fill("#mName", t["model"]); shot("modelle")
        @scene
        def geburtstage(): fresh(); menu("bdays"); shot("geburtstage")
        @scene
        def geburtstage2(): fresh(); scroll_to_month(2026, 11, 120); shot("geburtstage2")
        @scene
        def routinen():
            fresh(); menu("routines"); pg.click('[data-a="rnew"]'); pg.wait_for_timeout(300)
            pg.fill("#rName", t["rt"]); pg.fill("#rAb", t["ra"]); pg.dispatch_event("#rAb", "input"); shot("routinen")
        @scene
        def routinen2(): fresh(); scroll_to_day(2026, 11, 30, -330); shot("routinen2")
        @scene
        def reiter(): fresh(); pg.click('[data-tab="c:frau"]'); pg.wait_for_timeout(500); scroll_to_month(2026, 11); shot("reiter")
        @scene
        def kinder(): fresh(); pg.click('[data-tab="c:k1"]'); pg.wait_for_timeout(500); scroll_to_month(2026, 11); shot("kinder")
        @scene
        def kinder2(): fresh(); pg.click('[data-tab="c:k1"]'); pg.wait_for_timeout(400); pg.click("[data-tabed]"); shot("kinder2")
        @scene
        def uebersicht(): fresh(); pg.click('[data-tab="ov"]'); pg.wait_for_timeout(400); pg.click('[data-fv="7"]'); shot("uebersicht")
        @scene
        def versionen(): fresh(); menu("news"); shot("versionen")
        @scene
        def teamleiter(): fresh(); menu("contacts"); shot("teamleiter")
        @scene
        def leer(): fresh(); menu("models"); sheet_scroll("#sheet .basebox"); shot("leer")
        @scene
        def einstellungen(): fresh(); menu("settings"); sheet_scroll("#animChk", "start"); pg.evaluate("document.getElementById('sheet').scrollTop-=90"); shot("einstellungen")
        @scene
        def farben(): fresh(); menu("settings"); pg.click('[data-a="colors"]'); pg.wait_for_timeout(300); shot("farben")
        @scene
        def sicherung(): fresh(); menu("backup"); shot("sicherung")
        @scene
        def partner():
            fresh(); menu("partner"); shot("partner")
            pg.click('[data-a="copy"]'); pg.wait_for_timeout(400)
            link = pg.evaluate("navigator.clipboard.readText()")
            c2 = ctx(); q = c2.new_page(); q.set_default_timeout(4000); q.clock.set_fixed_time(datetime.datetime(2026, 11, 3, 10, 0))
            q.goto(U); q.evaluate(f"()=>{{localStorage.clear();localStorage.setItem('sp_anim','false');localStorage.setItem('sp_lang',JSON.stringify('{lang}'))}}")
            q.goto("about:blank"); q.goto(link.replace("https://onkelstuka-droid.github.io/Schichtplan-/", U)); q.wait_for_timeout(1400)
            for name, act in (("partner2", None), ("partner3", '[data-a="ok"]')):
                if act: q.click(act); q.wait_for_timeout(3800)
                q.wait_for_timeout(400); f = os.path.join(out, name + ".png"); q.screenshot(path=f)
                Image.open(f).convert("RGB").resize((OUTW, OUTH), Image.LANCZOS).save(os.path.join(out, name + ".jpg"), quality=84); os.remove(f)
            c2.close()

        only = [x for x in os.environ.get("SZENEN", "").split(",") if x]  # z. B. SZENEN=routinen,tag
        for f in scenes:
            if only and f.__name__ not in only: continue
            try: f()
            except Exception as e: errs.append(f.__name__ + ": " + str(e)[:200])
        b.close()
    print(lang, "fertig,", len(os.listdir(out)), "Dateien in", out, "| Probleme:", errs or "keine")

if __name__ == "__main__":
    for l in sys.argv[1:] or ["en", "tr", "ro"]: run(l)
