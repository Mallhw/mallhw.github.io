#!/usr/bin/env python3
"""Re-embed the page typeface into every page that asks for it.

The pages are the source of truth for this site. Their copy, CSS and scripts are
edited by hand and nothing regenerates them.

This script touches ONLY the region between the two FONT DATA marker comments in
each stylesheet. It cannot overwrite anything you have written. A page without
the markers is skipped rather than guessed at.

You should not need this again unless you change typeface. To do that, drop the
new .b64 files next to this script, point FAMILY and FACES at them, and run

    python3 build/regen-fonts.py

FACES maps a CSS font-weight descriptor to a file. A variable font is one entry
with a range ("300 600"); a static family is one entry per weight ("400", ...).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
# Both pages embed the same face. Listing them here rather than copying the
# base64 by hand is what stops the two drifting apart.
PAGES = [HERE.parent / "index.html", HERE.parent / "globe.html",
         HERE.parent / "writing.html"]
# Every writing topic page embeds the face too. Globbed rather than listed so
# adding an essay never means coming back here.
PAGES += sorted((HERE.parent / "writing").glob("*.html"))
FAMILY = "Karla"
# Karla ships as a single variable file covering the whole 300-600 range, which
# is smaller than the four static weights it replaced.
FACES = [("300 600", "karla.b64")]

START = "/* ===== FONT DATA"
END = "  /* ===== END FONT DATA"


def face(weight: str, b64: str) -> str:
    return (
        "  @font-face {\n"
        f"    font-family: '{FAMILY}';\n"
        "    font-style: normal;\n"
        f"    font-weight: {weight};\n"
        "    font-display: swap;\n"
        f"    src: url(data:font/woff2;base64,{b64}) format('woff2');\n"
        "  }"
    )


def main() -> None:
    blocks = []
    for weight, filename in FACES:
        src = HERE / filename
        if not src.exists():
            sys.exit(f"Missing {src.name} — listed in FACES but not on disk.")
        blocks.append(face(weight, src.read_text().strip()))
    payload = "\n" + "\n".join(blocks) + "\n"

    touched = 0
    for page in PAGES:
        if not page.exists():
            print(f"{page.name}: not present, skipped.")
            continue

        html = page.read_text()
        start = html.find(START)
        end = html.find(END)
        if start < 0 or end < 0 or end < start:
            print(f"{page.name}: no FONT DATA markers, skipped.")
            continue

        # Keep the opening marker comment intact; replace only what follows it.
        head_end = html.index("*/", start) + 2
        updated = html[:head_end] + payload + html[end:]

        if updated == html:
            print(f"{page.name}: already up to date.")
            continue

        page.write_text(updated)
        touched += 1
        print(f"{page.name}: rewrote font data ({page.stat().st_size / 1024:.0f} KB)")

    if not touched:
        print("nothing written.")


if __name__ == "__main__":
    main()
