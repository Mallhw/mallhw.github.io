#!/usr/bin/env python3
"""Re-embed the world's country outlines into globe.html.

globe.html is the source of truth for the globe page. Its copy, CSS and scripts
are edited by hand and nothing regenerates them.

This script touches ONLY the region between the two COUNTRY DATA marker comments.
It cannot overwrite anything you have written. If the markers are missing it
aborts rather than guessing.

You should not need this again unless you want finer coastlines. Run it with:

    python3 build/regen-countries.py                    # fetches both sources
    python3 build/regen-countries.py 110m.json 50m.json # uses local copies

Why this exists at all: the obvious approach is to fetch the GeoJSON at page
load, the way most globes do. That would cost 862 KB over the wire, put a
third-party host on the critical path, and — because a fetch() of a local file
is blocked by CORS — break `open globe.html` from the filesystem. Inlining the
geometry as a JS literal avoids all three. The slimming below is what makes
inlining affordable: ~860 KB becomes ~170 KB.

Why TWO sources: the 1:110m set is the right weight for a globe, but it drops
every country smaller than a few hundred square kilometres — Aruba, Malta,
Singapore, Cabo Verde. Those are places people actually go, and a travel globe
that can't show one is broken for the trip that matters. The 1:50m set has them
but costs 1.4 MB, which is not worth paying for the other 180 countries that
looked fine already.

So: take 110m whole, then splice in only what it is missing. That is NOT the
same as "every name 50m has". 50m is a map-UNITS file, so it also splits Belgium
into Flanders and Wallonia, Bosnia into its two entities, and so on — names 110m
lacks, but territory it already covers. Adding those would draw two countries on
top of each other and make the click target a coin toss. The filter below is
therefore geographic, not by name: a 50m feature earns its place only if its
own centre falls outside every polygon 110m already has. That admits Aruba,
which sits in open water as far as 110m is concerned, and rejects Wallonia,
which sits inside Belgium. Costs about 25 KB for 60-odd countries.
"""
import json
import pathlib
import sys
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
PAGE = HERE.parent / "globe.html"

# Map UNITS, not countries: this dataset splits the UK into England, Scotland,
# Wales and Northern Ireland, which is what you want on a travel map. The
# countries file would collapse all four into one shape.
BASE = "ne_110m_admin_0_map_units.geojson"
FINE = "ne_50m_admin_0_map_units.geojson"
STEM = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
)

# 2 decimal places is ~1.1 km at the equator. The globe is a few hundred pixels
# across, where one pixel is tens of kilometres, so nothing survives to be seen.
PRECISION = 2

START = "/* ===== COUNTRY DATA"
END = "  /* ===== END COUNTRY DATA"


def ring_area(flat):
    """Signed shoelace area of a flat [lon, lat, lon, lat, ...] ring."""
    total = 0.0
    n = len(flat)
    for i in range(0, n, 2):
        x1, y1 = flat[i], flat[i + 1]
        j = (i + 2) % n
        x2, y2 = flat[j], flat[j + 1]
        total += x1 * y2 - x2 * y1
    return total / 2.0


def ring_centroid(flat):
    """Area-weighted centroid of a flat ring, falling back to the mean point.

    The fallback matters for rings so small that the shoelace area underflows to
    zero after rounding — a few island map units do exactly that.
    """
    a = ring_area(flat)
    if abs(a) < 1e-12:
        n = len(flat) // 2
        return (
            sum(flat[0::2]) / n,
            sum(flat[1::2]) / n,
        )
    cx = cy = 0.0
    n = len(flat)
    for i in range(0, n, 2):
        x1, y1 = flat[i], flat[i + 1]
        j = (i + 2) % n
        x2, y2 = flat[j], flat[j + 1]
        cross = x1 * y2 - x2 * y1
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    return cx / (6 * a), cy / (6 * a)


def flatten(ring):
    """[[lon, lat], ...] -> [lon, lat, lon, lat, ...], rounded.

    Flat beats nested here: it drops two brackets and a comma per coordinate
    pair, which is about 15% of the finished file. Consecutive duplicate points
    left behind by the rounding are dropped as they appear.
    """
    out = []
    for lon, lat in ring:
        x = round(lon, PRECISION)
        y = round(lat, PRECISION)
        if out and out[-2] == x and out[-1] == y:
            continue
        out.append(x)
        out.append(y)
    # A ring that closed on itself now has a duplicated last point.
    if len(out) >= 4 and out[0] == out[-2] and out[1] == out[-1]:
        out = out[:-2]
    return out


def load(name, override):
    """Read one source, from a given path or over the network.

    Python on macOS routinely ships without a usable CA bundle, so the network
    path fails with an SSL error on a perfectly healthy machine. Rather than
    pretend that's exotic, the error tells you the two curl commands that fix it.
    """
    if override:
        path = pathlib.Path(override)
        if not path.exists():
            sys.exit(f"No such file: {path}")
        return json.loads(path.read_text())
    print(f"fetching {name} ...")
    req = urllib.request.Request(STEM + name, headers={"User-Agent": "matthewli-site"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode())
    except Exception as exc:  # noqa: BLE001 - the message is the whole point
        sys.exit(
            f"Could not fetch {name}: {exc}\n\n"
            "Download them yourself and pass both paths:\n"
            f"  curl -LO {STEM}{BASE}\n"
            f"  curl -LO {STEM}{FINE}\n"
            f"  python3 build/regen-countries.py {BASE} {FINE}"
        )


def name_of(feature):
    props = feature["properties"]
    return props.get("GEOUNIT") or props.get("ADMIN")


def rings_of(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"]]
    if geom["type"] == "MultiPolygon":
        return geom["coordinates"]
    return []


def point_in_ring(ring, lon, lat):
    """Ray cast against a [[lon, lat], ...] ring."""
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > lat) != (yj > lat):
            if lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
                inside = not inside
        j = i
    return inside


def main() -> None:
    if not PAGE.exists():
        sys.exit(f"No globe.html at {PAGE}")

    html = PAGE.read_text()
    start = html.find(START)
    end = html.find(END)
    if start < 0 or end < 0 or end < start:
        sys.exit(
            "Could not find the COUNTRY DATA markers in globe.html.\n"
            "Refusing to guess where the geometry belongs — nothing was written."
        )

    data = load(sys.argv)

    rows = []
    for feature in data["features"]:
        props = feature["properties"]
        name = props.get("GEOUNIT") or props.get("ADMIN")
        iso = props.get("ISO_A2") or ""
        geom = feature["geometry"]
        if geom["type"] == "Polygon":
            raw = [geom["coordinates"]]
        elif geom["type"] == "MultiPolygon":
            raw = geom["coordinates"]
        else:
            continue

        polys = []
        for poly in raw:
            rings = [flatten(r) for r in poly]
            # Rounding can collapse a tiny ring to a degenerate sliver. A ring
            # needs three distinct points to enclose anything.
            rings = [r for r in rings if len(r) >= 6]
            if rings:
                polys.append(rings)
        if not polys:
            continue

        # Centre on the largest landmass rather than the average of everything,
        # so France centres on France and not halfway to French Guiana.
        biggest = max((r[0] for r in polys), key=lambda r: abs(ring_area(r)))
        clon, clat = ring_centroid(biggest)

        rows.append(
            [name, iso, round(clon, PRECISION), round(clat, PRECISION), polys]
        )

    rows.sort(key=lambda r: r[0])
    body = ",\n".join(json.dumps(r, separators=(",", ":")) for r in rows)
    block = f"  var COUNTRIES = [\n{body}\n  ];"

    head_end = html.index("*/", start) + 2
    updated = html[:head_end] + "\n" + block + "\n" + html[end:]

    if updated == html:
        print("globe.html already up to date; nothing written.")
        return

    PAGE.write_text(updated)
    size = PAGE.stat().st_size / 1024
    print(f"rewrote {len(rows)} countries in {PAGE} ({size:.0f} KB)")


if __name__ == "__main__":
    main()
