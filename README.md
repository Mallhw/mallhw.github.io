# matthewli-site

A single-page personal site. One self-contained `index.html` — no build step, no
dependencies, no external network requests. Open it directly in a browser to preview:

```sh
open index.html
```

## Editing

**`index.html` is the site.** Open it, change it, save, refresh the browser. There is no
build step and nothing regenerates it, so anything you write there stays written.

Where things are, top to bottom:

| Line-ish | What |
| --- | --- |
| `<style>` → `:root` | **Colours.** Five variables: `--bg`, `--fg`, `--name`, `--dim`, `--rule`, plus `--sea` / `--sea-k` for the animation |
| `@media print` | print palette — see below |
| `FONT DATA` markers | **Generated. Skip it.** One enormous base64 line |
| `YOUR COPY STARTS HERE` | **The words.** One paragraph, then a `<ul>` of bullets, then the footer links |
| the `<script>` | the background animation |

The copy is plain HTML. In practice you need `<strong>bold</strong>`, `<em>italic</em>`,
`<a href="...">link</a>`, `<li>a bullet</li>`, `<hr>` for a divider, and `&mdash;` for an
em dash. Add and delete `<li>` items freely; nothing depends on how many there are.

### The font

Karla, embedded in the file as base64 woff2 (~31 KB). It's a variable font, so one file
covers every weight the page uses (300-600) — that's smaller than the four static files
it replaced. No Google Fonts request, so it renders instantly, works offline, and leaks
nothing to a third party. It's under the SIL Open Font License, which permits bundling it
this way — `build/Karla-LICENSE.txt` is that license, and it should travel with the
project.

Karla was picked by running every candidate through a head-to-head tournament rather than
by eye. It beat 30 other open-licensed faces over 428 pairwise comparisons.

**Size and measure are part of the choice, not decoration.** Three numbers hang together
and should move together:

| Where | Value | Why |
| --- | --- | --- |
| `body` font-size | `14.8px` | a proportional face reads smaller than a monospace at the same pixel size; this is the equivalent of the old 14px mono |
| `body` line-height | `1.8` | mono needs the extra air that `2` gave it, Karla doesn't |
| `.wrap` width | `min(90vw, 576px)` | 576 minus the 28px gutters leaves a 520px column ≈ 75 characters a line |

That last one matters most. The previous 770px cap was sized for a monospace at ~85
characters a line. Karla is narrower per character, so the *same box* would run 93-103
characters — well past readable. If you ever change the typeface again, re-check the
measure; roughly 60-75 characters a line is the target.

The font data sits between two `FONT DATA` marker comments at the end of the stylesheet.
You will almost certainly never touch it. If you ever change typeface, drop the new
`.b64` file into `build/`, point `FAMILY` and `FACES` at it in `build/regen-fonts.py`,
and run:

```sh
python3 build/regen-fonts.py
```

`FACES` is a list of `(css-font-weight, filename)`. A variable font is one entry with a
range (`"300 600"`); a static family is one entry per weight. That script rewrites
**only** the region between those two markers — it cannot overwrite your copy, and it
aborts rather than guessing if the markers are missing.

## The background animation

A waterline sits just below your name, with a buoy riding it and a hydrophone hanging
below sending pings out into the dark — a callback to MobyGlobal. Drawn on a single
`<canvas>` fixed behind the text, in about 120 lines of plain JS in the second
`<script>`. No library, no external request, so it still works over `file://`.

**The one knob you'll actually want is `--sea-k`** in the `:root` blocks. It multiplies
the opacity of everything in the scene. Raise it to make the ocean more visible, drop it
toward `0` to make it disappear. It sits at `1.7` because dark ink on a light page
carries less contrast per unit alpha than the reverse would.

Other constants, at the top of that script:

| Constant | Does |
| --- | --- |
| `WAVE_A` | opacity of the two surface lines (0.07) |
| `BUOY_A` | opacity of the buoy hull and the hydrophone (0.105) |
| `TETHER_A` | opacity of the line between them, deliberately the faintest of the three (0.07) |
| `RING_A` | opacity of a ping at the moment it's emitted (0.06) |
| `PING_MS` | milliseconds between pings (6500) |
| `LIFE_MS` | how long a ping takes to cross the screen and fade (9000) |
| `TETHER` | how far the hydrophone hangs below the buoy (150px) |
| `BUOY_R` | radius of the buoy hull (11px). Ride height and the tether's anchor are both derived from it, so changing it keeps the buoy sitting in the water correctly |
| `HYD_R` | radius of the hydrophone circle (2.5px) |
| `TET_BOW` | how far the slack cable's mid-span bows as the current leans on it (9px, one cycle per ~22s) |
| `TET_SWAY` | the ripple travelling down the cable, widest at the free end (3px) |
| `TET_SEG` | segments the cable is drawn with (20) |
| `ANT_H` / `ANT_R` | antenna mast height above the hull (14px) and the bead at its head (1.5px) |

The cable hangs loose rather than taut. Both its bow and its ripple fall to zero at the
hull, where it's tied, and are largest at the bottom — so the hydrophone swings with the
free end, and pings are emitted from wherever it has drifted to.
| `PARTS` | the three sine waves that sum into the surface |
| `TIDE_AMP` / `TIDE_W` | the slow rise and fall underneath, one cycle per ~90s |

All four opacity values are multiplied by `--sea-k`, so that variable still scales the
whole scene at once without disturbing the balance between the parts.

The waterline is anchored to the bottom of `.header`, so it stays just under your name at
any window size. Pings are clipped to below the surface — sound out of a hydrophone stays
in the water. The loop stops while the tab is in the background.

If `prefers-reduced-motion: reduce` is set, the scene renders one static frame and never
animates. It also listens for that setting *changing*, so turning Reduce Motion on stops
the animation immediately rather than only on the next page load.

Printing forces a black-on-white palette in a `@media print` block and hides the ocean.
Browsers don't print background colours, so without it the page's tan would drop out and
leave mid-brown text on white paper — and the ocean would print as a grey smudge.

## Deploying

Pick one. All three serve a static file, so all three work as-is.

**GitHub Pages** — free, and you already have an account.

```sh
git init
git add -A
git commit -m "personal site"
gh repo create Mallhw.github.io --public --source=. --push
```

It goes live at `https://mallhw.github.io` within a minute or two. For a custom domain,
buy it, add a `CNAME` file containing just the bare domain (e.g. `matthewli.com`), and
point the domain's DNS at GitHub's Pages IPs.

**Netlify** — drag the folder onto <https://app.netlify.com/drop>. No account needed to
start.

**Vercel** — `npx vercel` from inside this folder.

## Notes

- Content is sourced from `Matthew Resume.pdf` (the one-page version, Aug 2026).
- Your Stanford SUID, phone number, and home address are deliberately not on this page.
  The only contact detail published is the Gmail address already printed on your resume.
- Your age isn't stated either — add it to the first paragraph if you want it.
- Some resume items were left off to keep the page to one screen: the full awards list,
  Lima Grand Prix, R2 referee / AIC coaching, CodeQuest and the MIT AI Olympiad
  qualifier, and the skills section. All easy to add back as another `<li>`.
- Every external link was verified live on 2026-08-03 and returns 200, except the
  Washington Post URL, which blocks automated requests behind its paywall. It's a real
  article — just not machine-checkable.
