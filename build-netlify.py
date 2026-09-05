#!/usr/bin/env python3
"""Baut aus index.html eine eigenstaendige Seite fuer statisches Hosting.

index.html ist die Quelle des veroeffentlichten Artifacts: nur Seiteninhalt,
ohne doctype/head, mit allen Medien als base64 eingebettet. Beides ist dort
erzwungen -- der Artifact-Dienst ergaenzt den Rahmen selbst, und seine CSP
laesst keine externen Medien zu.

Auf einem normalen Host gilt das nicht. Dieses Skript erzeugt deshalb:

  * ein vollstaendiges Dokument mit echtem <head> und lang-Attribut,
  * ausgelagerte Cover und Audiodateien unter assets/,

womit die Erstauslieferung von 6,73 MiB auf gut 1 MiB faellt. Die sechs
Hoerproben laden dann erst beim Abspielen, wie preload="none" es vorsieht.
"""

import base64, bisect, hashlib, pathlib, re, shutil, sys

SRC = pathlib.Path("index.html")
OUT = pathlib.Path("dist")
LANG = "en"

DATA_URI = re.compile(r"data:(image/jpeg|audio/mpeg);base64,([A-Za-z0-9+/=]+)")
ID_BEFORE = re.compile(r"id:'([^']+)'")

EXT = {"image/jpeg": "jpg", "audio/mpeg": "mp3"}
SUB = {"image/jpeg": "covers", "audio/mpeg": "audio"}


def main() -> int:
    if not SRC.exists():
        print(f"{SRC} nicht gefunden", file=sys.stderr)
        return 1

    html = SRC.read_text(encoding="utf-8")

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets" / "covers").mkdir(parents=True)
    (OUT / "assets" / "audio").mkdir(parents=True)

    # id-Positionen einmal einsammeln, damit jedes Medium die zu ihm
    # gehoerende id findet, ohne den 7-MB-String erneut zu durchsuchen.
    id_positions: list[int] = []
    id_names: list[str] = []
    for m in ID_BEFORE.finditer(html):
        id_positions.append(m.start())
        id_names.append(m.group(1))

    used: dict[str, str] = {}
    saved = [0]

    def extract(match: re.Match) -> str:
        mime, b64 = match.group(1), match.group(2)
        raw = base64.b64decode(b64)
        digest = hashlib.sha256(raw).hexdigest()
        if digest in used:
            return used[digest]

        # Jedes Objektliteral nennt seine id vor dem Medium. Ein fester
        # Rueckblick reicht dafuer nicht: vor dem Cover einer Hoerprobe steht
        # deren base64-Audio und schiebt die id ausser Reichweite. Deshalb die
        # letzte id vor dieser Stelle aus der vorab gebauten Liste.
        pos = bisect.bisect_left(id_positions, match.start()) - 1
        stem = id_names[pos] if pos >= 0 else digest[:12]
        stem = re.sub(r"[^A-Za-z0-9_-]", "-", stem)

        name = f"{stem}.{EXT[mime]}"
        path = OUT / "assets" / SUB[mime] / name
        n = 2
        while path.exists():
            name = f"{stem}-{n}.{EXT[mime]}"
            path = OUT / "assets" / SUB[mime] / name
            n += 1
        path.write_bytes(raw)

        rel = f"assets/{SUB[mime]}/{name}"
        used[digest] = rel
        saved[0] += len(b64) - len(rel)
        return rel

    body = DATA_URI.sub(extract, html)

    # Kopfbereich aus dem Inhalt herausloesen: title, description, die
    # Schrift-Links und das Stylesheet gehoeren in ein echtes <head>.
    head_parts: list[str] = []

    def lift(pattern: str) -> None:
        nonlocal body
        for m in re.findall(pattern, body, flags=re.S):
            head_parts.append(m.strip())
            body = body.replace(m, "", 1)

    lift(r"<title>.*?</title>")
    lift(r'<meta name="description"[^>]*>')
    lift(r"<link rel=\"preconnect\"[^>]*>")
    lift(r"<link rel=\"stylesheet\" media=\"print\".*?>")
    lift(r"<noscript><link rel=\"stylesheet\"[^>]*></noscript>")
    lift(r"<style>.*?</style>")

    doc = (
        f"<!doctype html>\n<html lang=\"{LANG}\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
        + "\n".join(head_parts)
        + "\n</head>\n<body>\n"
        + body.strip()
        + "\n</body>\n</html>\n"
    )
    (OUT / "index.html").write_text(doc, encoding="utf-8")

    (OUT / "netlify.toml").write_text(
        "# Die Seite ist eine einzelne HTML-Datei mit ausgelagerten Medien.\n"
        "[[headers]]\n"
        '  for = "/*"\n'
        "  [headers.values]\n"
        '    X-Content-Type-Options = "nosniff"\n'
        '    Referrer-Policy = "strict-origin-when-cross-origin"\n\n'
        "# Cover und Hoerproben sind ueber ihren Inhalt benannt und aendern\n"
        "# sich nur mit dem Inhalt, das HTML dagegen bei jedem Deploy.\n"
        "[[headers]]\n"
        '  for = "/assets/*"\n'
        "  [headers.values]\n"
        '    Cache-Control = "public, max-age=31536000, immutable"\n\n'
        "[[headers]]\n"
        '  for = "/index.html"\n'
        "  [headers.values]\n"
        '    Cache-Control = "public, max-age=0, must-revalidate"\n',
        encoding="utf-8",
    )

    total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"  dist/index.html      {(OUT / 'index.html').stat().st_size:>9,} Bytes")
    print(f"  assets/covers        {len(list((OUT / 'assets' / 'covers').iterdir())):>9} Dateien")
    print(f"  assets/audio         {len(list((OUT / 'assets' / 'audio').iterdir())):>9} Dateien")
    print(f"  dist gesamt          {total:>9,} Bytes")
    print(f"  Quelle index.html    {SRC.stat().st_size:>9,} Bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
