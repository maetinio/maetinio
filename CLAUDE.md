# Arbeitsanweisungen für dieses Repository

## Nach jeder Änderung an `index.html`: Netlify-Paket mitliefern

Der Betreiber deployt die Seite über Netlify per Drag & Drop. Sobald sich
`index.html` ändert, ohne dass danach gefragt werden muss:

```sh
python3 build-netlify.py
cd dist && zip -r -9 ../maetinio-west-netlify.zip index.html netlify.toml assets
```

und das ZIP ausliefern. Nicht abwarten, bis danach gefragt wird — das ist eine
stehende Anweisung des Betreibers ("bitte immer machen", 6. September 2026).

Vor dem Ausliefern prüfen, dass das Archiv dem Ordner entspricht und die
gebaute Seite lädt. Bewährt hat sich ein lokaler Server plus Chromium
(Playwright liegt global unter `/opt/node22/lib/node_modules`, Browser unter
`/opt/pw-browsers`): keine HTTP-Fehler, keine JavaScript-Fehler, 12 Kacheln,
6 Hörproben, alle 18 Cover geladen, vor dem ersten Play null Audiodateien.

## Zwei Fassungen derselben Seite

`index.html` ist die Quelle des veröffentlichten Artifacts: nur Seiteninhalt,
ohne `doctype`/`head`, alle Medien als base64 eingebettet. Beides ist dort
erzwungen — der Artifact-Dienst ergänzt den Rahmen selbst, und seine
Content-Security-Policy lässt keine externen Medien zu.

`build-netlify.py` erzeugt daraus `dist/` für normales Hosting: vollständiges
Dokument mit echtem `<head>` und `lang`-Attribut, Medien als einzelne Dateien.
Das senkt die Erstauslieferung von rund 5 MiB gzip auf etwa 100 KB, weil die
Hörproben dann erst beim Abspielen laden. Beide Fassungen aktuell halten.

## Das Artifact

Die veröffentlichte Seite liegt unter
`https://claude.ai/code/artifact/f323a4e9-dbb1-4a71-bc3d-46e3fe6f6397`.
Veröffentlicht wird `index.html` unter dieser URL, damit Adresse, Favicon und
die `db`-Capability für die Abstimmung über die unveröffentlichten Titel
erhalten bleiben. Nur veröffentlichen, wenn der Betreiber es verlangt: es
überschreibt seine Live-Seite.

## Keine `README.md` im Wurzelverzeichnis

`maetinio/maetinio` ist das Profil-Repository. Bei übereinstimmendem Repo- und
Benutzernamen rendert GitHub die `README.md` des Default-Branch auf der
öffentlichen Profilseite. Projektdokumentation gehört deshalb nach
`docs/README.md`.

## Bewusste Gestaltungsentscheidungen, nicht ungefragt ändern

- Das Track-Raster bleibt auf allen Breiten vierspaltig, auch wenn die Kacheln
  dadurch auf 360 px nur 74 px breit werden.
- Die Reihenfolge der Titel folgt keiner Sortierung.
- Die Scramble-Animation macht Überschriften beim Einscrollen und beim
  Überfahren mit der Maus kurzzeitig unlesbar.

## Inhaltliche Angaben sind unbestätigt

Spotify-Profil, Titelzahl, Track-IDs, Veröffentlichungsdaten und die
Buchungsadresse wurden nie gegen die Quellen geprüft — die Domains waren aus
der Arbeitsumgebung blockiert. Nicht als bestätigt darstellen.
