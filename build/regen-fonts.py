#!/usr/bin/env python3
"""Re-embed the page typeface into index.html.

index.html is the source of truth for this site. Its copy, CSS and scripts are
edited by hand and nothing regenerates them.

This script touches ONLY the region between the two FONT DATA marker comments in
the stylesheet. It cannot overwrite anything you have written. If the markers are
missing it aborts rather than guessing.

You should not need this again unless you change typeface. To do that, drop the
new .b64 files next to this script, point FAMILY and FACES at them, and run

    python3 build/regen-fonts.py

FACES maps a CSS font-weight descriptor to a file. A variable font is one entry
with a range ("300 600"); a static family is one entry per weight ("400", ...).
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PAGE = HERE.parent / "index.html"
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
    if not PAGE.exists():
        sys.exit(f"No index.html at {PAGE}")

    html = PAGE.read_text()
    start = html.find(START)
    end = html.find(END)
    if start < 0 or end < 0 or end < start:
        sys.exit(
            "Could not find the FONT DATA markers in index.html.\n"
            "Refusing to guess where the fonts belong — nothing was written."
        )

    # Keep the opening marker comment intact; replace only what follows it.
    head_end = html.index("*/", start) + 2

    blocks = []
    for weight, filename in FACES:
        src = HERE / filename
        if not src.exists():
            sys.exit(f"Missing {src.name} — listed in FACES but not on disk.")
        blocks.append(face(weight, src.read_text().strip()))

    updated = html[:head_end] + "\n" + "\n".join(blocks) + "\n" + html[end:]

    if updated == html:
        print("index.html already up to date; nothing written.")
        return

    PAGE.write_text(updated)
    print(f"rewrote font data in {PAGE} ({PAGE.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
