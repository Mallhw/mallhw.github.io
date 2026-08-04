#!/usr/bin/env python3
"""Re-embed IBM Plex Mono into index.html.

index.html is the source of truth for this site. Its copy, CSS and scripts are
edited by hand and nothing regenerates them.

This script touches ONLY the region between the two FONT DATA marker comments in
the stylesheet. It cannot overwrite anything you have written. If the markers are
missing it aborts rather than guessing.

You should not need this again unless you change typeface: drop new
w<weight>.b64 files next to this script, then run

    python3 build/regen-fonts.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PAGE = HERE.parent / "index.html"
WEIGHTS = (300, 400, 500, 600)

START = "/* ===== FONT DATA"
END = "  /* ===== END FONT DATA"


def face(weight: int, b64: str) -> str:
    return (
        "  @font-face {\n"
        "    font-family: 'IBM Plex Mono';\n"
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
    for w in WEIGHTS:
        src = HERE / f"w{w}.b64"
        if not src.exists():
            sys.exit(f"Missing {src.name} — expected one .b64 file per weight.")
        blocks.append(face(w, src.read_text().strip()))

    updated = html[:head_end] + "\n" + "\n".join(blocks) + "\n" + html[end:]

    if updated == html:
        print("index.html already up to date; nothing written.")
        return

    PAGE.write_text(updated)
    print(f"rewrote font data in {PAGE} ({PAGE.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
