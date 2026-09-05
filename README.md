# maetinio west

Einseitige Startseite. Eine Datei, alle Medien eingebettet.

## Aufbau

| Datei | Zweck |
|---|---|
| `index.html` | Quelle. Nur Seiteninhalt, ohne `doctype`/`head`, Medien als base64. |
| `build-netlify.py` | Erzeugt aus `index.html` ein `dist/` für normales Hosting. |

`index.html` ist bewusst kein vollständiges Dokument: Es ist die Quelle des
veröffentlichten Artifacts, und der Artifact-Dienst ergänzt Rahmen und
Kopfbereich beim Veröffentlichen selbst. Die eingebetteten base64-Medien sind
dort ebenfalls erzwungen, weil die Content-Security-Policy des Dienstes keine
externen Bilder oder Audiodateien zulässt.

## Für Netlify oder anderes statisches Hosting

```sh
python3 build-netlify.py     # schreibt dist/
```

Das Skript löst die Medien heraus, benennt sie nach ihrer Track-ID und baut ein
vollständiges Dokument mit echtem `<head>` und `lang`-Attribut. Der Ordner
`dist/` ist danach direkt deploybar — bei Netlify per Drag & Drop, ohne
Build-Befehl.

Gemessener Unterschied über HTTP:

| | Erstauslieferung | First Contentful Paint |
|---|---|---|
| `index.html` (alles eingebettet) | 5,02 MiB gzip | – |
| `dist/` | 100 KB | 208 ms |

Die sechs Hörproben laden im `dist/`-Build erst beim Abspielen. In der
eingebetteten Fassung lädt jeder Besucher alle 5,5 MiB Audio mit, auch wenn er
nie auf Play drückt: `preload="none"` wirkt bei `data:`-URIs nicht, weil die
Bytes bereits im HTML stehen.

## Inhalt pflegen

Alle Daten stehen als Listen am Anfang des Skriptblocks in `index.html`:

- `TRACKS` — veröffentlichte Titel (Spotify-ID, Titel, Datum, Länge, Cover)
- `PREVIEWS` — unveröffentlichte Hörproben samt vorberechneter Wellenform
- `DATES` — Termine; leer, dann zeigt die Seite einen entsprechenden Hinweis
- `SOCIALS`, `MAIL`, `TICKER`, `BIO` — Links, Adresse, Laufband, Terminaltext

## Bekannte, bewusst so belassene Entscheidungen

- Das Track-Raster bleibt auf allen Breiten vierspaltig. Auf 360 px sind die
  Kacheln dadurch 74 px breit und die Titel 9 px groß.
- Die Reihenfolge der Titel folgt keiner Sortierung.
- Abschnittsüberschriften sind beim Einscrollen rund eine Sekunde lang
  unlesbar (Scramble-Animation), ebenso bei jedem Überfahren mit der Maus.
