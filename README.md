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
| `<link rel="icon">` | **The favicon**, an inline SVG — see below |
| `PHOTO SWAP` marker | the hover-a-word-to-change-the-photo script — see below |
| the first `<script>` | the background animation |

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
| `.wrap` width | `min(92vw, 1012px)` | 1012 = 520 text + 56 gap + 380 photo + the two 28px gutters. The **text** column is still 520px ≈ 75 characters a line |

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

## The favicon

Matthew's own pencil sketch of a smiley face, inlined as a PNG data URI in the
`<link rel="icon">` tag rather than kept as an `.ico` file. That keeps the page's
zero-network-request property and still works over `file://`.

Every stroke in it is from the drawing. Three things were changed, none of which touch
the shape of a line:

- **The marks were re-placed.** In the original they sit in the corners of a mostly-empty
  page — the drawn content filled 61% of the width and 36% of the height, and 0.37% of the
  pixels carried any ink at all. At 16px that is a blank tile. The three marks (two eyes,
  one mouth) were segmented out by connected components and laid out on a tighter grid.
- **The line was thickened.** A 1px pencil stroke is 0.07px at favicon scale — a
  fourteenth of one device pixel. Dilating at high resolution and downsampling once keeps
  the line soft and organic instead of turning it into a hard vector stroke.
- **The colour is a warm mid-tone, not the page's near-black.** With no tile behind it, one
  colour has to survive a white tab strip *and* a dark one. Ink scores 18:1 on white but
  1.4:1 on dark — invisible. The mid-tone gives 3.99:1 and 3.03:1, both past the 3:1 that
  non-text graphics need.

The uneven eyes and the wobble in the smile are the drawing's, not an effect — that is
what makes it read as drawn rather than constructed.

To change it, redraw and regenerate: crop to the marks, thicken, recolour, inline the
base64. Keep the transparent background, and re-check contrast against both tab colours if
you change the colour.

## The photos

The right-hand column holds **one** `<img>`. Hovering a marked-up word in the copy swaps
that image's `src` and the caption under it. The photo then **stays** — it does not snap
back when the pointer leaves, because reverting makes the panel flicker while you read
down the list. Hovering the greeting is the way back to the default photo.

### Adding one

1. Put the file in `img/`.
2. Add two attributes to any word in the copy — a `<span class="ph">` if it has nowhere to
   link, or straight onto an existing `<a>` if it does:

```html
<span class="ph"
  data-hover-img="img/whatever.jpg"
  data-hover-caption="the funny bit"
  data-hover-alt="what the photo shows, for screen readers"
  >the word</span>
```

That's the whole wiring. The script finds every `[data-hover-img]` on the page, so there
is no list to keep in sync, and it preloads each one at startup so the first hover doesn't
flash an empty frame.

The default photo and its caption are whatever is written into the `<img id="photo">` and
`<p id="photo-caption">` in the markup.

`.ph` is styled with a **dotted** underline on purpose — it signals "this does something"
without impersonating a real link's solid underline. Real links that are also photo
triggers keep their normal underline and still navigate when clicked.

### Sizing

Photos do not have to share a shape. The frame is a fixed height with the image
*contained* inside it rather than cropped to a common aspect ratio, so a landscape photo
keeps its sides instead of being sliced to match the portraits — and because the frame
height is fixed, the caption never jumps when the photo changes. The cost is some empty
space around a photo whose shape differs a lot from the frame's.

Keep files to roughly 150KB. `sips` is enough:

```bash
sips -Z 1040 -s format jpeg -s formatOptions 65 original.jpg --out img/name.jpg
```

`-Z` bounds the longest side. 1040 is about right for a portrait (2× the tallest the frame
ever gets); use `-Z 780` for a landscape, which is 2× the column width.

### On phones

Below 1100px the layout is one column and the photo moves directly under the greeting.
There is no hover on a touch screen, so tapping a `<span>` trigger swaps the photo
instead. Taps on real links still follow the link — otherwise the Academies-IT link would
be dead on a phone.

## The writing section

`writing.html` is an index of topics, one page per topic — the shape of
patrickcollison.com, and dressed like it too: **the writing section is white, Helvetica,
blue links**, deliberately unlike the tan-and-Karla rest of the site. The writing room
(`write.html`) wears the same clothes, so typing there is seeing the final page. These
pages embed no webfont at all, which is why `regen-fonts.py` doesn't list them. Linked
from **writing** in the homepage list.

### Adding a topic

1. Write it in `write.html` (autosave, proofread-on-export) and **export** — or copy
   `build/writing-topic-template.html` to `writing/<slug>.html` and write by hand.
2. Drop the file in `writing/`.
3. Add the topic's row to the list in `writing.html`:

   ```html
   <li><a href="writing/<slug>.html">topic</a>
       <span class="gloss">&mdash; optional one-line gloss</span></li>
   ```

No font step: writing pages use system Helvetica.

The old `blog/` and `blogs/` folders are unrelated to this and stay unpublished (they're
excluded in `_config.yml`); this section starts from scratch.

## The Strava caption

The caption under the homepage's default photo shows the latest Strava activity —
`run · 44 min · 3 days ago` — linked to the profile. Until the setup below is done (or
whenever data is missing) it falls back to the caption written in the HTML.

The page cannot call Strava itself: the API needs OAuth tokens that expire six-hourly,
refreshing them needs the client secret, and a public page can hold neither. So a
scheduled GitHub Action (`.github/workflows/strava.yml`) fetches the latest activity four
times a day and rewrites `strava.js`, a generated same-origin file — the page still makes
zero external requests, and "X days ago" is computed in the browser from the activity's
start time so it stays current between refreshes. Only the activity **type**, duration and
start are published — never the user-entered activity name, which routinely leaks routes.

### One-time setup

1. Create an API application at <https://www.strava.com/settings/api> — any category,
   website `https://matthewli.org`, authorization callback domain `localhost`.
2. Authorize it once (replace `CLIENT_ID`):

   ```
   https://www.strava.com/oauth/authorize?client_id=CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read
   ```

   Approve, then copy `code=...` out of the localhost URL it redirects to.
3. Exchange the code for tokens and note the `refresh_token` in the response:

   ```sh
   curl -X POST https://www.strava.com/oauth/token \
     -d client_id=CLIENT_ID -d client_secret=CLIENT_SECRET \
     -d code=CODE -d grant_type=authorization_code
   ```

4. Set the three repo secrets (each prompts for the value; nothing lands in shell history):

   ```sh
   gh secret set STRAVA_CLIENT_ID
   gh secret set STRAVA_CLIENT_SECRET
   gh secret set STRAVA_REFRESH_TOKEN
   ```

5. Put your profile URL into the `PROFILE` constant in `index.html`'s STRAVA CAPTION
   script, then run the workflow once from the Actions tab (or wait for the cron).

Caveats: the scope `activity:read` excludes activities marked private, on purpose. Strava
can in principle rotate the refresh token; in practice it is stable — if the workflow ever
starts failing with auth errors, redo steps 2–4. GitHub pauses cron workflows after ~60
days without repo activity; any commit revives them.

## The globe

`globe.html` is a second page, linked from **travelling** in the list on the homepage. It
draws a spinning globe of the countries you've been to; clicking one stops the spin,
dissolves the globe into that country's outline, and opens a stack of photos beside it that
turn like pages when clicked.

### Adding a country

One table at the top of `globe.html`, and nothing else:

```js
var VISITED = {
  Bulgaria: {
    photos: [
      { img: "img/teamusa.jpg",
        caption: "2 AM in sofia with top tier schwarma",
        alt: "the USA squad out at night in front of a christmas tree" }
    ]
  }
};
```

The key must match the map data's name. If it doesn't, the console tells you so at load —
a country that silently fails to colour in is the sort of thing you don't notice for a
year. A country with no `photos` still colours in and still opens; it just says there are
no photos yet.

**Somewhere too small to have a shape** — Singapore, Monaco, Vatican City, Andorra,
Liechtenstein — gets a pin instead:

```js
Singapore: { pin: [103.82, 1.35], photos: [] },
```

That draws a clickable marker at those coordinates. Pins are checked before shapes when
you click, so a marker always beats the country underneath it.

### Zooming

Three ways, one per input: **ctrl-scroll** with a mouse (a bare scroll is left to the
page on purpose — a globe that eats plain scrolling traps you above the list below it),
**two-finger pinch** on touch (a trackpad pinch arrives as ctrl-scroll and just works),
and the **+ / − buttons** on the orb, which are also the keyboard route. Zoom anchors to
the pointer, drag slows proportionally so it feels like holding the surface, and
selecting a country flies the zoom back home to 1× — the outline view has its own
framing. Limits are 1× to 8×; at 8× one degree is ~35px and the data quantises at
0.01°, so nothing gets blurry before the cap.

### Why the data is the size it is

The obvious way to build this is to fetch the country outlines from a CDN at page load,
which is what most globes do. That would cost 862KB over the wire, put a third-party host
on the critical path, and break the page over `file://` — a `fetch()` of a local file is
blocked by CORS. So the geometry is inlined as a JS literal instead, quantised to 2 decimal
places (~1.1km, well under a pixel at this size).

It is built from **two** Natural Earth sets, because the 1:110m one that's the right weight
for a globe drops every country under a few hundred square kilometres — Aruba, Malta, Cabo
Verde. A travel globe that can't show the trip you took is broken. So 110m is taken whole
and 50m is spliced in for what's missing, filtered **geographically, not by name**: a 50m
unit earns its place only if its own centre falls outside every shape 110m already draws.
That admits Aruba, which 110m thinks is open water, and rejects Wallonia, which sits inside
a Belgium that's already there — adding that would stack two countries on the same ground
and make clicking a coin toss. 183 countries become 253 for about 28KB.

Regenerate with:

```sh
python3 build/regen-countries.py                      # fetches both sources
python3 build/regen-countries.py 110m.json 50m.json   # uses local copies
```

It rewrites only the region between the two `COUNTRY DATA` markers, aborts if they're
missing, and refuses to write at all if fewer than 150 countries survive processing —
otherwise a bad download would quietly replace the whole map with an empty array.

Natural Earth is public domain: "No permission is needed to use Natural Earth."

## The background animation

A waterline sits just below your name, with a buoy riding it and a hydrophone hanging
below sending pings out into the dark — a callback to MobyGlobal. Drawn on a single
`<canvas>` fixed behind the text, in about 120 lines of plain JS in the first
`<script>`. No library, no external request, so it still works over `file://`.

Two things are measured off the DOM in `measure()`, which re-runs on resize: the waterline
sits 13px under `.header`, so it follows the greeting whatever size that is; and the buoy
sits 56px to the left of `.wrap`, so it stays in the margin instead of drifting into the
copy. Both used to be fractions of the window, which broke once the page had a fixed
1012px content column — the window keeps growing and the column doesn't.

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

Printing forces a black-on-white palette in a `@media print` block and hides the ocean and
the photo panel. Browsers don't print background colours, so without it the page's tan
would drop out and leave mid-brown text on white paper — and the ocean would print as a
grey smudge. The photo panel is a hover toy; on paper it is a wasted half-page, so the
columns collapse and the text runs full width. It comes out as one page.

## Deploying

Pick one. All three serve a static file, so all three work as-is.

**GitHub Pages** — free, and you already have an account.

```sh
git init
git add -A
git commit -m "personal site"
gh repo create Mallhw.github.io --public --source=. --push
```

It goes live at `https://mallhw.github.io` within a minute or two.

### The custom domain

The site serves from **matthewli.org**. `mattyli.com` is also registered and redirects to
it — GitHub Pages answers for exactly one custom domain, so the second one is handled by a
redirect rule at Cloudflare rather than by anything in this repo.

Two halves have to agree:

1. The `CNAME` file at the repo root, containing the bare domain and nothing else. This
   is what tells GitHub which host to answer for — it is the same setting as the "Custom
   domain" box in the repo's Pages settings, just stored in the repo. **Don't delete it**;
   a build without it silently reverts the site to `mallhw.github.io`.
2. DNS at the registrar, pointing at GitHub's four Pages IPs:

```
A     @    185.199.108.153
A     @    185.199.109.153
A     @    185.199.110.153
A     @    185.199.111.153
CNAME www  mallhw.github.io
```

**Order matters.** Add the DNS records *first*. If the `CNAME` file lands before DNS
resolves, GitHub starts redirecting `mallhw.github.io` to a domain that doesn't answer
yet, and the site is unreachable until it propagates.

**On Cloudflare, set those records to "DNS only" (grey cloud), not proxied (orange).**
Proxying puts Cloudflare's certificate in front of GitHub's, and GitHub can't complete its
own certificate check through the proxy — "Enforce HTTPS" stays greyed out and the domain
can serve a redirect loop. You can turn the proxy on later, once GitHub has issued the
certificate, if you actually want it.

Once DNS resolves, tick **Enforce HTTPS** in the repo's Pages settings. GitHub issues a
Let's Encrypt certificate automatically, usually within about 15 minutes. `mallhw.github.io`
keeps working and redirects to the custom domain.

### Pointing mattyli.com at it

The second domain is not in this repo at all — GitHub only answers for the one in `CNAME`.
It redirects at Cloudflare instead, which needs two pieces:

1. In **mattyli.com → DNS**, an `A` record for `@` pointing at `192.0.2.1`, and the same
   for `www`. That address is the reserved documentation-only IP; nothing is ever hosted
   there, and nothing needs to be. It exists only to give Cloudflare a record to attach
   the rule to.
2. In **mattyli.com → Rules → Redirect Rules**, a rule matching `hostname` contains
   `mattyli.com`, with a *dynamic* target of
   `concat("https://matthewli.org", http.request.uri.path)`, status **301**, preserve
   query string on.

**These two records must be Proxied (orange cloud) — the opposite of matthewli.org's.**
Redirect rules only run on traffic that passes through Cloudflare, so a grey-cloud record
here means the rule never fires and the domain just fails to load. Getting these two
domains backwards is the easiest mistake to make: the one serving the site is grey, the
one redirecting is orange.

Using the path in the target rather than a plain URL means `mattyli.com/anything` lands on
`matthewli.org/anything` instead of dumping every visitor on the homepage.

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
