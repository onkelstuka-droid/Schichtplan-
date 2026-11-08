# Schichtplaner – Projektübergabe für Claude

App-Link: https://onkelstuka-droid.github.io/Schichtplan-/
Repository: github.com/onkelstuka-droid/Schichtplan- (Branch `main`, GitHub Pages aus `/ (root)`)
Idee und Konzept: **Hans-Jürgen Schlichting** (Nutzer, spricht Deutsch, Android-Handy Pixel, kein Programmierer).
App-Name: **Schichtplaner** (früher „Schichtplan 17,5“; Wunsch des Nutzers). Sicherungs-Kennung `schichtplan-17-5` bleibt aus Kompatibilitätsgründen.
Umsetzung: Claude. Immer auf Deutsch antworten, einfach erklären, Schritte für das Handy beschreiben.

## Aufbau
- `src/schichtplan.html` – **die gesamte App in einer Datei** (HTML, CSS, JS). Nur hier ändern.
- `build.py` – baut daraus `index.html` (mit Head, Manifest-Link, Download-Ersatz für `window.claude`, Service-Worker-Registrierung), `sw.js` (Offline-Cache, Version = Hash der Quelle), `manifest.webmanifest`, `404.html`.
- `help/*.jpg` – Bildschirmfotos für die Anleitung in der App (32 Stück je Sprache, Beispieldaten; u. a. reiter, kinder, kinder2, uebersicht, versionen, partner…, routinen…, geburtstage…).
- `icons/` – App-Symbole (192/512, maskable, apple-touch).
- Veröffentlichen: `python3 build.py`, committen, `git push origin main`. GitHub Pages aktualisiert in 1–2 Min. Nutzer bekommen das Update beim nächsten Öffnen.
- Das Einschalten von Pages über die API ist im Sandbox-Proxy gesperrt; Pages ist bereits eingeschaltet.
- Eine ältere Version läuft noch als Claude-Artifact (claude.ai/artifact/XitXTSjShxG3JBC1FLzfe6). Weiterentwicklung nur noch hier.

## Daten (nur localStorage auf dem Gerät)
`sp_anchor2` (Montag, an dem ein Spät-Block beginnt; Standard 2026-12-21 → Nachtschicht ab So 03.01.2027), `sp_vac2` ({Tagnummer: U|TZ|AG|K|SU}), `sp_quota` ({U:30,TZ:8}), `sp_notes` ({Starttag:{t,to}}), `sp_ot` (Überstunden [{id,d,from,to,pause,min,note}]), `sp_otcfg` ({agHours:8,carry}), `sp_contacts` (Telefonbuch [{name,tel,info,who}]; ohne `who` = „Teamleiter“), `sp_models` (eigene Schichtmodelle), `sp_colors`, `sp_anim`, `sp_sound`, `sp_vol`, `sp_myname` (eigener Name fürs Teilen), `sp_partners` (empfangene Partner-Pläne [{n,a,m,e,q,b,t}]), `sp_base` ("175" Standard | "none" = 17,5-Modell ausgeschaltet, leerer Kalender), `sp_routines` ([{id,name,ab,start,n,unit:d|w|m,end}]), `sp_bdays` (Geburtstage [{id,name,d:"MM-TT",y|null}]), `sp_bdlead` (Hinweis Tage vorher, Standard 7), `sp_shtimes` (Schichtzeiten {F:[von,bis],S:…,N:…}, Standard 06–14/14–22/22–06), `sp_cals` (Zusatzkalender, s. u.), `sp_c_<id>_<schlüssel>` (Daten eines Zusatzkalenders „Person mit Schichten“). Tagnummer = Tage seit 1.1.1970 (UTC).
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
Endlos-Kalender (ganze Seite scrollt, Kopf sticky), Wochentage in Kacheln, Wochenend-Band (Standardfarbe Orange #ff8000, einstellbar), Feiertagssymbole (Emoji), Tag antippen → Urlaub/TZ/Ausgleich/Krank (dunkelrot, 🌡️)/Sonderurlaub (hellrosa), ein Tag oder Zeitraum mit Mini-Kalender, „Nur Notiz hinzufügen“ + danach Angebot Google-Kalender-Link, Überstunden mit Von/Bis/Pause, Statistik-Seite, Meine Einträge (ändern/löschen/springen), Notizen-Seite, Telefonbuch (früher Teamleiter; „Wer ist das?“ mit Schnellwahl Teamleiter/Kollege/Familie/Arzt/Notfall/Sonstige, sortiert), Jahresübersicht (nur Schichten + Feiertage) mit „Als PDF speichern und drucken“ (jsPDF von cdnjs) und **„🖨️ Schwarz-Weiß-PDF“** (`savePdf(y,true)`, Datei `…-sw.pdf`: F weiß, S hellgrau, N dunkel/weiße Schrift, frei weiß mit grauem „frei“, Feiertag dicker schwarzer Rahmen + „FT“, keine Emojis, Wochenende sehr hellgrau; auch auf der Statistik-Seite). Statistik → unter dem Jahreskalender: **Jahreskalender mit Einträgen** als PDF in Farbe oder Schwarz-Weiß (`savePdf(y,bw,true)`, Datei `Jahreskalender-JJJJ(-sw).pdf`; Einträge U/TZ/AG/K/SU in Farbe bzw. s/w weiß mit gestricheltem Rahmen + Kürzel; zweite Legendenzeile und Zeile mit Urlaub/TZ/AG/K/SU-Zahlen), Excel/CSV-Export, Sicherung, Farben einstellbar, Schichtmodell-Editor, Anleitung mit Bildern, Impressum, Hinweis 14 Tage vor Zeitumstellung. Schwebender Knopf **„‹ Kalender“** (`#backFab`) erscheint auf allen Vollbild-Seiten (Jahresübersicht, Statistik, Notizen, Anleitung, Einträge, Telefonbuch, Geburtstage) und schließt sie von überall.

## Mehrere Kalender, Kinder, Familien-Übersicht (Version 2.0)
- Sicherung davor: Branch `sicherung-vor-familie`.
- **Reiterleiste** `#calTabs` ganz oben im Kopf (`renderTabs`): 👤 Ich (Name aus `sp_myname`), Zusatzkalender, empfangene Partner-Pläne (👀, schreibgeschützt), ⚙️ (gewählten Zusatzkalender bearbeiten), 👨‍👩‍👧 Übersicht, ＋ Kalender. Start immer auf „Ich“.
- `TAB` ("me" | "c:<id>" | "p:<index>"), `CUR` (id eines Zusatzkalenders mit Schichten), `WK` (aktiver Kinder-Wochenplan). `switchTab()` lädt die Daten neu (`loadCal`).
- **Person mit Schichten** (`type:"shift"`): eigene Kopie aller Kalenderdaten. `store.get/set` leiten die Schlüssel in `CALK` (anchor, vac, quota, notes, ot, otcfg, models, base, shtimes) bei aktivem `CUR` auf `sp_c_<id>_<schlüssel>` um. Einstellungen/Schichtplan/Urlaub usw. wirken dann auf diese Person (Hinweis „Gilt für den Kalender …“). Routinen, Geburtstage, Telefonbuch bleiben gemeinsam.
- **Kinder-Wochenplan** (`type:"week"`, kind "schule"|"kita"): `week` {Wochentag 0–6: [von,bis]}, `ferien` (bayerische Schulferien `FER_BY`, 2025–Sommer 2030, Quelle Kultusministerium/kalenderpedia; **ab Herbst 2030 ergänzen**), `exc` {Tag: {off,why} | {from,to}}, `notes`. Feiertage immer frei. Darstellung `paintWeek`/`statWeek`/`todayWeek` (Zeiten in der Kachel, Ferien schraffiert, Ausnahme mit Rahmen), Tag antippen → `weekDaySheet` (frei, andere Zeit, Notiz, zurücksetzen). Anlegen/Bearbeiten `calNew`/`calEditor`, Löschen entfernt auch `sp_c_<id>_*`.
- **Familien-Übersicht** `#famView` (`openFam`/`renderFam`): 7 Tage ab heute, ‹ › wochenweise; Erwachsene (Ich, Zusatz-Personen, Partner) mit Schicht + Uhrzeit, Kinder mit Schule/Kita-Zeit; „Bringen/Abholen: ✓ frei sind …“ = keine Schicht zu dieser Uhrzeit (Nachtschicht vom Vortag bis Schichtende zählt mit, Krank = nicht verfügbar, Grenzen inklusive). Rechnen mit fremden Kalendern über `withCal()`.
- Partner-Link enthält jetzt die Schichtzeiten (`z`) und teilt immer den eigenen Plan, auch wenn ein anderer Reiter aktiv ist.
- Sicherung enthält `cals`, `calData` (alle `sp_c_*`), `shT`.
- **Versionen:** `APP_VERSION` + `CHANGES` (je Version Datum und Punkte in de/en/tr/ro/ru/pl), Seite über Menü „🆕 Was ist neu“ (`openChanges`), Version auch im Impressum. **Bei jeder neuen Version dort einen Eintrag ergänzen und `APP_VERSION` erhöhen.**

## Sprachen (Deutsch, English, Türkçe, Română, Русский, Polski)
- Auswahl: Menü → 🌐 „Sprache · Language“ oder Einstellungen oben. Speichert `sp_lang` ("de" Standard | "en" | "tr" | "ro" | "ru" | "pl") und lädt die Seite neu. Ohne Schlüssel = Deutsch (bestehende Nutzer unverändert).
- Technik (am Anfang des Haupt-Scripts): `LANG`, `LI` (0–4 = en/tr/ro/ru/pl), `L(de,en,tr,ro,ru,pl)`. **Der Code bleibt deutsch**; ein MutationObserver (`startI18n`/`trNode`) übersetzt jeden sichtbaren Text und die Attribute placeholder/aria-label/title/alt über `trS()`:
  1. `I18N_D` = Wörterbuch „deutscher Text → [en, tr, ro, ru, pl]“ (exakter, getrimmter Text),
  2. `I18N_P` = Muster für Texte mit Zahlen/Namen (`$1` = roh, `%1` = übersetzt, `{$1:день|дня|дней}` = russische/polnische Mehrzahl nach Zahl in Gruppe 1, Funktion `plF`),
  3. allgemeine Regeln: Symbol-Präfix, Teile an „ · “, „: “, Klammern, Zahl am Ende, Sätze, Kommas.
- Neue deutsche Texte in der App **immer auch in `I18N_D` (oder als Muster) eintragen**, sonst bleiben sie in den anderen Sprachen deutsch. Prüfen: Crawler-Test in allen Sprachen, Texte suchen, die gleich geblieben sind.
- Direkt lokalisiert (nicht über das Wörterbuch): `MONTHS`, `WD`, `WDL`, `WDH` (Ein-Buchstaben-Wochentage), `fmt`/`fmtS`/`dayMon`/`bdDate`, WhatsApp-Text, Google-Kalender-Text, Zeitraum-Hinweis.
- Anleitung: `I18N_HELP[lang][id] = [Titel, HTML]` ersetzt die Kapitel von `HELP`. Bilder je Sprache in `help/en/`, `help/tr/`, `help/ro/`, `help/ru/`, `help/pl/` (deutsch: `help/*.jpg`); fehlt ein Bild, wird das deutsche gezeigt. Offline vorab gespeichert werden nur die deutschen Bilder, die anderen beim ersten Ansehen. Impressum: `I18N_IMPR`.
- **Bilder neu erzeugen:** `python3 -m http.server 8765` starten, dann `python3 tools/help_bilder.py en tr ro ru pl` (oder `de`, überschreibt die deutschen). Das Skript stellt alle 27 Szenen mit Beispieldaten nach (Datum fest 3.11.2026). Bei neuen Funktionen/Kapiteln dort eine Szene ergänzen.
- PDF: `doc.text`/`getTextWidth` laufen durch `trS` + `pdfTxt` (TR/RO: ersetzt ş ğ ı ș ț ă durch s g i s t a, weil die PDF-Standardschrift sie nicht kennt). **RU/PL:** `pdfFont()` lädt `fonts/SPSans-Regular.ttf`/`-Bold.ttf` (verkleinerte, umbenannte Liberation Sans, SIL OFL, Lizenz in `fonts/OFL.txt`) und leitet `setFont("helvetica")` darauf um; klappt das Laden nicht, Umschrift ohne Sonderzeichen (`deAcc`). Russisch: freie Tage im PDF als „вых.“. Datum RU/PL mit Genitiv-Monat (`MONTHS_G`). Überschriften: Barlow hat kein Kyrillisch, bei RU wird Roboto Condensed von Google Fonts nachgeladen. CSV-Zellen ebenfalls übersetzt.
- Nutzerdaten (Namen, Notizen) werden nicht übersetzt, außer sie gleichen zufällig einem Wörterbuch-Eintrag. Elemente mit Klasse `nt` werden nie übersetzt.
- Schichtbuchstaben F/S/N und Kürzel U/TZ/AG/K/SU/FT/ÜS bleiben in allen Sprachen gleich.
- Sicherung vor Einbau: Branch `sicherung-vor-sprachen` auf GitHub (vor Russisch/Polnisch: `sicherung-vor-ru-pl`).

## 17,5-Modell ausschalten
- Menü → **🔁 Schichtplan** (früher „Schichtmodelle“) → unten „17,5-Modell entfernen (leerer Kalender)“ (zweimal tippen). Nicht mehr in den Einstellungen (Wunsch des Nutzers). Setzt nur `sp_base="none"` auf diesem Gerät; ohne den Schlüssel gilt weiter das 17,5-Modell (bestehende Nutzer unverändert). `rawShift()` liefert dann „X“, außer ein eigenes Schichtmodell gilt. Einträge bleiben erhalten. Rückgängig über „17,5-Modell wieder einschalten“.

## Routinen (Menü → Routinen, auch in Einstellungen)
- Wiederkehrende Aufgaben (z. B. Hausordnung alle 2 Wochen am Samstag): Name, eigene Abkürzung (1–3 Zeichen), erster Termin, alle n Tage/Wochen/Monate (Monat = gleicher Tag im Monat), optional Ende. Vorschau der nächsten 6 Termine.
- Anzeige: kleines weißes Kürzel oben rechts in der Tageskachel (`.rt`), bei Feiertagssymbol darunter; mehrere Routinen → erstes Kürzel + „+“. Schichtfarben werden nicht verändert. Tag antippen zeigt den Namen.
- Nicht in Jahresübersicht/PDF, nicht im Partner-Link. In der Sicherung enthalten.

## Geburtstage (Menü → 🎂 Geburtstage, oder Tag antippen → „Geburtstag an diesem Tag eintragen“)
- Eigene Vollbild-Seite `#bdaysView` (`renderBdays`): oben „+ Geburtstag hinzufügen“, „Als Nächstes“ (3 nächste), dann „Alle Geburtstage“ nach Monaten; jede Karte mit ✎ Bearbeiten und 🗑 Löschen (zweimal tippen); bald anstehende rosa umrandet; „Hinweis vorher“ unten. Bearbeiten öffnet ein Sheet (`bdEditor`), danach zurück zur Seite.
- Neu eintragen: mehrere Personen auf einmal („+ Weitere Person“ fügt Zeilen hinzu, ✕ entfernt, ganz leere Zeilen werden übersprungen, Fehler nennen „Person N“, „Alle speichern“). Bearbeiten bleibt eine Person.
- Eingabe: Tag + Monat (Auswahllisten), dazu **Geburtsjahr oder Alter** (das andere wird live berechnet, Hinweis „Wird 54 am …“); beides leer = Jahr unbekannt, kein Alter. 29.2. erscheint in Nicht-Schaltjahren am 28.2.
- Monatsliste unter dem Kalender (bei den Feiertagen, `statMonth`): „🎂 8.11. Monika wird 54“ (Klasse `bdli`, rosa Datum). Achtung: `statMonth` läuft schon beim Start, dort `escEarly()` statt `esc()` benutzen.
- Kalender: 🎂 im Symbol-Platz oben rechts (`data-ic`, zusammen mit Feiertagssymbol; dann Klasse `ic2` = kleiner). Kein eigener Platz, damit nichts die Zahl überdeckt.
- Hinweisleiste `#bdBar` unter der Heute-Karte (wie Zeitumstellung): „🎂 In 3 Tagen (…): Monika wird 54“, am Tag „🎉 Heute hat Geburtstag: …“. Vorlauf einstellbar 0–30 Tage. Antippen springt zum Tag.
- Pro Geburtstag Knopf „Jedes Jahr in Google Kalender eintragen“ (RRULE:FREQ=YEARLY) für echte Handy-Erinnerung.
- Nicht im Partner-Link, nicht in der Jahresübersicht. In der Sicherung enthalten.

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
