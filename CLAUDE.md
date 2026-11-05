# Schichtplan 17,5 – Projektübergabe für Claude

App-Link: https://onkelstuka-droid.github.io/Schichtplan-/
Repository: github.com/onkelstuka-droid/Schichtplan- (Branch `main`, GitHub Pages aus `/ (root)`)
Idee und Konzept: **Hans-Jürgen Schlichting** (Nutzer, spricht Deutsch, Android-Handy Pixel, kein Programmierer).
Umsetzung: Claude. Immer auf Deutsch antworten, einfach erklären, Schritte für das Handy beschreiben.

## Aufbau
- `src/schichtplan.html` – **die gesamte App in einer Datei** (HTML, CSS, JS). Nur hier ändern.
- `build.py` – baut daraus `index.html` (mit Head, Manifest-Link, Download-Ersatz für `window.claude`, Service-Worker-Registrierung), `sw.js` (Offline-Cache, Version = Hash der Quelle), `manifest.webmanifest`, `404.html`.
- `help/*.jpg` – Bildschirmfotos für die Anleitung in der App (25 Stück, Beispieldaten; u. a. partner, partner2, partner3, routinen, routinen2, leer).
- `icons/` – App-Symbole (192/512, maskable, apple-touch).
- Veröffentlichen: `python3 build.py`, committen, `git push origin main`. GitHub Pages aktualisiert in 1–2 Min. Nutzer bekommen das Update beim nächsten Öffnen.
- Das Einschalten von Pages über die API ist im Sandbox-Proxy gesperrt; Pages ist bereits eingeschaltet.
- Eine ältere Version läuft noch als Claude-Artifact (claude.ai/artifact/XitXTSjShxG3JBC1FLzfe6). Weiterentwicklung nur noch hier.

## Daten (nur localStorage auf dem Gerät)
`sp_anchor2` (Montag, an dem ein Spät-Block beginnt; Standard 2026-12-21 → Nachtschicht ab So 03.01.2027), `sp_vac2` ({Tagnummer: U|TZ|AG|K|SU}), `sp_quota` ({U:30,TZ:8}), `sp_notes` ({Starttag:{t,to}}), `sp_ot` (Überstunden [{id,d,from,to,pause,min,note}]), `sp_otcfg` ({agHours:8,carry}), `sp_contacts` (Telefonbuch [{name,tel,info,who}]; ohne `who` = „Teamleiter“), `sp_models` (eigene Schichtmodelle), `sp_colors`, `sp_anim`, `sp_sound`, `sp_vol`, `sp_myname` (eigener Name fürs Teilen), `sp_partners` (empfangene Partner-Pläne [{n,a,m,e,q,b,t}]), `sp_base` ("175" Standard | "none" = 17,5-Modell ausgeschaltet, leerer Kalender), `sp_routines` ([{id,name,ab,start,n,unit:d|w|m,end}]). Tagnummer = Tage seit 1.1.1970 (UTC).
Sicherung (JSON) enthält alles; Laden über Menü → Sicherung.

## Fachliche Regeln
- 17,5-Modell, 28-Tage-Zyklus ab Montag: 6× Spät (Mo–Sa), So frei, 6× Früh (Mo–Sa), 6× Nacht (So–Fr), 9 Tage frei.
- Eigene Schichtmodelle (Blöcke F/S/N/X mit Anzahl, Zeitraum von–bis) überschreiben das Modell im Zeitraum; zuletzt angelegtes gewinnt.
- **Alle Feiertage Bayern + Heiligabend + Silvester sind frei** (rot, „frei“). `rawShift()` = Rhythmus, `shift()` = mit Feiertagen frei.
- Urlaub/TZ werden nur an Schichttagen abgezogen, nie an Feiertagen. AG/K/SU zählen Schichttage, keine Feiertage. Einträge überschreiben sich gegenseitig (eine Art pro Tag).
- Überstunden-Saldo = Übertrag + Überstunden − Ausgleichstage × Stunden pro AG-Tag (Standard 8).
- Zähler FT = Feiertage, die auf einen Schichttag fallen.
- Besondere Tage ohne Feiertag (nur Symbol): Faschingsbeginn 11.11., Weiberfastnacht, Rosenmontag, Faschingsdienstag, Ostersonntag, Muttertag, Nikolaus. Zeitumstellung (letzter So im März/Okt) separat über `dst()`.

## Funktionen (alle vorhanden)
Endlos-Kalender (ganze Seite scrollt, Kopf sticky), Wochentage in Kacheln, Wochenend-Band (Standardfarbe Orange #ff8000, einstellbar), Feiertagssymbole (Emoji), Tag antippen → Urlaub/TZ/Ausgleich/Krank (dunkelrot, 🌡️)/Sonderurlaub (hellrosa), ein Tag oder Zeitraum mit Mini-Kalender, „Nur Notiz hinzufügen“ + danach Angebot Google-Kalender-Link, Überstunden mit Von/Bis/Pause, Statistik-Seite, Meine Einträge (ändern/löschen/springen), Notizen-Seite, Telefonbuch (früher Teamleiter; „Wer ist das?“ mit Schnellwahl Teamleiter/Kollege/Familie/Arzt/Notfall/Sonstige, sortiert), Jahresübersicht (nur Schichten + Feiertage) mit „Als PDF speichern und drucken“ (jsPDF von cdnjs), Excel/CSV-Export, Sicherung, Farben einstellbar, Schichtmodell-Editor, Anleitung mit Bildern, Impressum, Hinweis 14 Tage vor Zeitumstellung. Schwebender Knopf **„‹ Kalender“** (`#backFab`) erscheint auf allen Vollbild-Seiten (Jahresübersicht, Statistik, Notizen, Anleitung, Einträge, Telefonbuch) und schließt sie von überall.

## 17,5-Modell ausschalten
- Menü → **🔁 Schichtplan** (früher „Schichtmodelle“) → unten „17,5-Modell entfernen (leerer Kalender)“ (zweimal tippen). Nicht mehr in den Einstellungen (Wunsch des Nutzers). Setzt nur `sp_base="none"` auf diesem Gerät; ohne den Schlüssel gilt weiter das 17,5-Modell (bestehende Nutzer unverändert). `rawShift()` liefert dann „X“, außer ein eigenes Schichtmodell gilt. Einträge bleiben erhalten. Rückgängig über „17,5-Modell wieder einschalten“.

## Routinen (Menü → Routinen, auch in Einstellungen)
- Wiederkehrende Aufgaben (z. B. Hausordnung alle 2 Wochen am Samstag): Name, eigene Abkürzung (1–3 Zeichen), erster Termin, alle n Tage/Wochen/Monate (Monat = gleicher Tag im Monat), optional Ende. Vorschau der nächsten 6 Termine.
- Anzeige: kleines weißes Kürzel oben rechts in der Tageskachel (`.rt`), bei Feiertagssymbol darunter; mehrere Routinen → erstes Kürzel + „+“. Schichtfarben werden nicht verändert. Tag antippen zeigt den Namen.
- Nicht in Jahresübersicht/PDF, nicht im Partner-Link. In der Sicherung enthalten.

## Partner-Funktion (Menü → Partner)
- Teilen ohne Server: Daten stecken im Link `…/#p=1<base64url(deflate-raw(JSON))>` (Fallback `0` = unkomprimiert). Per WhatsApp (wa.me), Teilen-Menü, Link kopieren oder QR-Code (qrcode-generator 1.4.4, MIT, direkt in der Datei eingebaut, funktioniert offline).
- Geteilt werden nur Rhythmus (Anker, plus `b:0`, wenn das 17,5-Modell aus ist), eigene Schichtmodelle, Urlaubskonto und Einträge U/TZ/AG/SU ab ca. 400 Tagen zurück. **Nicht geteilt:** Krank, Notizen, Überstunden.
- Empfänger: Link öffnen → „Speichern und ansehen“. Partner-Plan ist eine eigene, schreibgeschützte Ansicht (blaue Leiste „Plan von …“ + „Zurück zu meinem Plan“). Während der Ansicht werden die eigenen Variablen getauscht und `store.set` für eigene Daten gesperrt (`PV`, `PVKEYS`).
- Neuer Link mit gleichem Namen ersetzt den alten Stand. Kein automatischer Live-Abgleich (Wunsch des Nutzers: ohne Server).
- iPhone: Safari und Home-Bildschirm-App haben getrennte Speicher → Hinweis, Link in der App unter Partner → „Link übernehmen“ einzufügen.

## Animation & Sound (Wünsche des Nutzers, bitte einhalten)
- Jahreszeiten-Hintergrund mit Teilchen (Schnee/Blüten/Sonne/Laub), Böen, Figuren passend zum Monat (Enten, Osterhase nur um Ostern, Bienen, Eichhörnchen, Laternen im Nov., Weihnachtsmann-Schlitten, Christkind, Nikolaus, Schneemann). Herbst: gelegentlich Blitz + Donner. Feuerwerk, wenn der 31.12. in der Bildschirmmitte steht, und an Silvester/Neujahr.
- Sound (Web Audio, alles synthetisch erzeugt). **Behalten:** Kohlmeise, Buchfink, Rotkehlchen, Kuckuck, Spatzen, Grillen (leise), Bienen, Herbstwind (im November leiser), Winterwind mit Pfeifen, Kaminknistern, Ente mit Küken (quakt, wenn sie im Bild ist), Weihnachtslieder als Spieluhr (kurz, nur 20.–31.12.), Kirchenglocken, Feuerwerk-Knall, Fasching (Tusch + Tröten), Ostern, Allerheiligen, 1. Mai Blasmusik, Tag der Einheit Fanfare, Muttertag Spieluhr, Zeitumstellung als **Turmuhr** (Westminster + Schläge + Zeiger drehen), Donner.
- **Entfernt, nicht wieder einbauen:** Amsel, Ringeltaube („Uh uh“), Frösche, Wasser/Bach, Laubrascheln, Regen, Krähe, Eule, zufällige Schlittenglöckchen, synthetische „Ho ho ho“-Stimme, Sektkorken, Sternsinger. Kein Rauschen im Frühling/Sommer.
- Weihnachtsmann-Schlitten = Spieluhr „Jingle Bells“-Anfang; Nikolaus = Spieluhr „Morgen kommt der Weihnachtsmann“.
- Event-Klänge nur am echten Tag oder beim Antippen des Tages. Ton startet erst nach Berührung (pointerup/touchend/click).

## Arbeitsweise
- Änderungen kurz testen (Playwright/Chromium headless ist vorinstalliert; für localStorage über `python3 -m http.server` laden), dann bauen und pushen.
- Bei Klangänderungen Hörproben als MP3 schicken (OfflineAudioContext rendern, ffmpeg), Nutzer entscheidet nach Gehör.
- Druckvorlagen/PDFs, Screenshots für die Anleitung bei größeren Änderungen aktualisieren.
