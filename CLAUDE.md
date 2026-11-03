# Schichtplan 17,5 – Projektübergabe für Claude

App-Link: https://onkelstuka-droid.github.io/Schichtplan-/
Repository: github.com/onkelstuka-droid/Schichtplan- (Branch `main`, GitHub Pages aus `/ (root)`)
Idee und Konzept: **Hans-Jürgen Schlichting** (Nutzer, spricht Deutsch, Android-Handy Pixel, kein Programmierer).
Umsetzung: Claude. Immer auf Deutsch antworten, einfach erklären, Schritte für das Handy beschreiben.

## Aufbau
- `src/schichtplan.html` – **die gesamte App in einer Datei** (HTML, CSS, JS). Nur hier ändern.
- `build.py` – baut daraus `index.html` (mit Head, Manifest-Link, Download-Ersatz für `window.claude`, Service-Worker-Registrierung), `sw.js` (Offline-Cache, Version = Hash der Quelle), `manifest.webmanifest`, `404.html`.
- `help/*.jpg` – Bildschirmfotos für die Anleitung in der App (19 Stück, Beispieldaten).
- `icons/` – App-Symbole (192/512, maskable, apple-touch).
- Veröffentlichen: `python3 build.py`, committen, `git push origin main`. GitHub Pages aktualisiert in 1–2 Min. Nutzer bekommen das Update beim nächsten Öffnen.
- Das Einschalten von Pages über die API ist im Sandbox-Proxy gesperrt; Pages ist bereits eingeschaltet.
- Eine ältere Version läuft noch als Claude-Artifact (claude.ai/artifact/XitXTSjShxG3JBC1FLzfe6). Weiterentwicklung nur noch hier.

## Daten (nur localStorage auf dem Gerät)
`sp_anchor2` (Montag, an dem ein Spät-Block beginnt; Standard 2026-12-21 → Nachtschicht ab So 03.01.2027), `sp_vac2` ({Tagnummer: U|TZ|AG|K|SU}), `sp_quota` ({U:30,TZ:8}), `sp_notes` ({Starttag:{t,to}}), `sp_ot` (Überstunden [{id,d,from,to,pause,min,note}]), `sp_otcfg` ({agHours:8,carry}), `sp_contacts` (Teamleiter), `sp_models` (eigene Schichtmodelle), `sp_colors`, `sp_anim`, `sp_sound`, `sp_vol`. Tagnummer = Tage seit 1.1.1970 (UTC).
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
Endlos-Kalender (ganze Seite scrollt, Kopf sticky), Wochentage in Kacheln, Wochenend-Band (Standardfarbe Orange #ff8000, einstellbar), Feiertagssymbole (Emoji), Tag antippen → Urlaub/TZ/Ausgleich/Krank (dunkelrot, 🌡️)/Sonderurlaub (hellrosa), ein Tag oder Zeitraum mit Mini-Kalender, „Nur Notiz hinzufügen“ + danach Angebot Google-Kalender-Link, Überstunden mit Von/Bis/Pause, Statistik-Seite, Meine Einträge (ändern/löschen/springen), Notizen-Seite, Teamleiter-Nummern, Jahresübersicht (nur Schichten + Feiertage) mit „Als PDF speichern und drucken“ (jsPDF von cdnjs), Excel/CSV-Export, Sicherung, Farben einstellbar, Schichtmodell-Editor, Anleitung mit Bildern, Impressum, Hinweis 14 Tage vor Zeitumstellung.

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
