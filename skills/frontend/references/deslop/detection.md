# Detection patterns
Read this when grepping/scanning for tells and false positives.
Adapted from yetone/kill-ai-slop (Apache-2.0); modified for this pack: routing cue added, inline paths prefixed with `$SKILL_DIR`, and the scanner-owned pattern blocks consolidated into `scan.mjs` (manual-only patterns kept and marked).

`$SKILL_DIR/references/deslop/scripts/scan.mjs` owns the machine-checked patterns for every tell and its own scan scope; this file is the human reference for the signals a regex cannot settle and the confirmation each tell needs. Blocks marked *Manual* are patterns the scanner does not encode. Suppression and extension flags are specified in the scanner's header comment.

---

### 01 Indigo→violet gradient
*False positives:* a brand that genuinely is purple (check the logo / design
tokens); a one-off illustration. Slop is the *combination* — purple gradient +
glow + pill button + "AI-powered" eyebrow.

### 02 Gradient-clip headline
*False positives:* a logo wordmark; a single deliberate hero treatment. Slop is
gradient text used as the default heading style.

### 03 Warm "cozy" palette
*False positives:* a food/coffee/craft brand where warm is the identity. Slop is
warm-as-default with no brand reason. A sibling tell: default gray text dropped
onto a tinted surface — the gray was never toned to the background; use a darker
shade of the surface hue instead.

### 04 Default semantic palette
*Confirm:* three or four of the stock `-50 / -600` semantic pairs used together
(info=blue, tip=amber, success=green, error=red), unrelated to the brand. A
single, deliberate status color is fine.

### 05 One-hue status box
*Confirm:* one box where border, text, and a `/10` background are all the same
hue — the whole alert is one color at three opacities. A single muted accent on
a neutral surface is fine.

### 06 Gradients as atmosphere
*Confirm:* a page-wide radial glow behind everything, or card surfaces filled
with a top-to-bottom gradient where a flat color would do; bento cards each
washed in a tint of their own accent (green card → green gradient, purple →
purple); repeating-gradient stripes as surface decoration; colored box-shadow
glows as dark-mode accents. A gradient that points at something specific is a
choice, not slop.

### 07 Serif-italic emphasis
Hard to grep purely; look for a serif font family or `<em>/italic` applied
*inside* an otherwise-sans heading.
```
rg -n '<em>|italic' -g '*.{tsx,jsx,vue,svelte,astro,html}'   # *Manual*: no scanner pattern
```
*Confirm:* the italic/serif span sits within an `<h1>/<h2>` whose base font is
sans.

### 08 Serif where sans belongs
*False positives:* an editorial/publishing product that wants serif. Slop is
display serif as UI/body on a tool or dashboard, or the oversized italic-serif
hero headline. Set it roman or use a non-serif display face; a genuinely
editorial register may keep it.

### 09 Decorative strikes & highlights
*Confirm:* a strike over text that isn't being deleted, an underline that isn't
a link, a highlighter swipe under a heading — decoration, not annotation. Real
edits, links, and annotations are fine. The scanner reads code and style files
only: `.md` is treated as prose, so a `<mark>` in Markdown prose never fires
this tell (`.mdx` is scanned).

### 10 The kicker above every heading
*Confirm:* the same tracked-caps micro-label above the hero *and* every section
heading, saying what the heading already says (FEATURES over features). A
kicker that adds a real dimension — a category, a date, a number in a genuine
sequence — is an editorial device doing its job.

### 11 Full-sentence display headline
```
rg -n -i 'font-size:\s*clamp\([^)]*[4-9]\.?[0-9]*rem'   # *Manual*: clamp() display size the scanner lacks
```
*Confirm:* a full sentence (10+ words) at display size, usually extrabold with
crushed tracking, wrapping to 3+ lines. Two or three words at display size is
what display sizes are for. Crushed tracking on its own is the same tell:
`letter-spacing` past the point where characters keep their shapes.

### 12 Flat type hierarchy
```
rg -n -i 'font-size:\s*1[4-8]px' -g '*.css'   # *Manual*: then count distinct sizes
```
Mostly a visual judgment: open the page and count the sizes actually in use.
*Confirm:* headings barely bigger than body (steps under ~1.25×), hierarchy
carried by gray shades instead of size. A deliberately quiet, single-size
editorial layout with strong spacing is a choice; a dashboard where the page
title and a table cell match is not.

### 13 Highlighted keywords
```
rg -n -i 'font-semibold|font-bold' -g '*.{md,mdx}'   # *Manual*: no scanner pattern
```
*Confirm:* multiple colored/`font-semibold` spans inside one paragraph of body
copy. One accented phrase is fine.

### 14 AI copywriting voice
Also flag paragraphs built from three-word sentences ("Fast. Beautiful. Yours."),
em-dash triplets, and "we killed the X theater" framing — dismissing something
as *theater* is a recurring generated-copy tic; say plainly what the thing does
or doesn't do. *False positives:* a genuine quote; a doc that discusses these
phrases (like this one).

### 15 Emoji everywhere
The scanner matches any `\p{Extended_Pictographic}` code point.
*False positives:* emoji inside a code sample being documented; an emoji picker
feature; user-generated content. Slop is an emoji stuck on *every* heading,
button, and bullet in your chrome.

### 16 Glowing status dot
*Confirm:* a status dot with a pulsing halo or colored glow — usually saturated
green "● Ready / Online." A small flat dot is fine.

### 17 Left-border callout
```
rg -n -i 'border-left:\s*[0-9]+px .*;.*border-radius'   # *Manual*: CSS form the scanner lacks
```
*Confirm:* stacked callouts used as decoration on plain list items, not one
semantic aside. A sibling move: a thick accent ring around a rounded card to
make one tier "pop" — the border fights the rounded corners; remove the ring or
carry the emphasis another way.

### 18 Pastel icon tiles
```
rg -n -i '(lucide|heroicons|@tabler/icons|react-icons)'   # *Manual*: no scanner pattern
rg -n -i '\b[wh]-(20|24|28|32)\b[\s\S]{0,40}(<svg|Icon)'   # *Manual*: icon-sized inline SVG
```
*Confirm:* one icon-in-a-tile per feature, in a grid, icons unrelated to
content — or the same reflex at another size, a giant decorative line icon
parked in a card as filler.

### 19 Max-radius / glassmorphism
*Confirm:* `rounded-full` on cards/inputs (not just avatars/pills); blur used as
the default surface; radius values that don't agree with each other.

### 20 Oversized drop shadow
*Confirm:* the shadow's render range is far bigger than the element casting it —
a small card/icon under a huge, faint, barely-offset blur (a fog, not a drop).
A genuinely large surface (a modal, a full hero) with a proportionate shadow is
fine; so is one small, tight elevation shadow. The "ghost card" variant: a
hairline border *and* a wide diffuse shadow on the same card — two separators
doing one job; commit to an edge or an elevation.

### 21 Corners that don't nest
Hard to grep with certainty; flag the same radius token on nested containers.
*Confirm:* an outer box and an inner box carrying the *same* big radius, so the
corners don't sit concentric. Inner radius should be outer minus the padding; a
single flat radius scale that already nests correctly is fine.

### 22 Border dies at the corner
The break is visual (a stroke on the straight edges, none along the arcs);
grep for the code that produces it — a radius and a border on different boxes.
*Confirm:* a `rounded overflow-hidden` wrapper whose child carries the 1px
border/dividers — the square ring is erased at every corner by the clip; a
`clip-path: inset(… round …)` cutting a border off; or a single-side border
stopping mid-arc on a rounded box. A border set on the rounded element itself
wraps the arc and is fine; so are straight dividers between square-cornered
regions.

### 23 Badge / pill spam
*Confirm:* several decorative pills in chrome. A real version tag is fine.

### 24 AI-drawn SVG icon
The scanner flags `<circle r="…">` primitives and `mascot.svg` / `blob.svg`
asset names, but it never opens a `.svg` file and does not flag every `<svg>`.
*Manual:*
```
rg -n '<svg' -g '*.{tsx,jsx,vue,svelte,astro,html,svg}'   # *Manual*: then open it and judge
```
*Confirm:* a `<svg>` that's a blob-with-dot-eyes or a cartoon creature built
from primitive shapes, shipped as the product's mark. A drawn icon set or a
real designed logo is fine.

### 25 Icon in a tint of itself
```
rg -n -i 'rounded-(md|lg|xl)\s+bg-(indigo|blue|green|amber|red)-[0-9]+/(5|10|15|20)'   # *Manual*: tile with no text-class
```
*Confirm:* an icon tile whose translucent background is the same hue as the icon
inside it — every glyph wrapped in a soft colored square. A deliberate opaque
button surface is fine.

### 26 The springy hover
*Confirm:* scale/lift/bounce on hover across cards, buttons, and images, and
`transition-all` as the default. A drawer that springs as it physically slides
in is motion doing a job; a card that jumps when the cursor grazes it is not.
Also flag animating layout properties (width/height/margin/padding) — jank on
top of the decoration.

### 27 All-caps card grid
```
rg -n -i 'uppercase[\s\S]{0,30}tracking-wider|text-transform:\s*uppercase'   # *Manual*: variants the scanner lacks
```
*Confirm:* an ALL-CAPS micro-label + number/icon repeated across interchangeable
cards — a feature grid or a stat-card grid — points unrelated.

### 28 The invented stat row
*Confirm:* three big round numbers in a row — a `Nk+`, a `99.9%`, a `24/7` —
with tiny uppercase labels, in the hero or above the fold. A real, odd,
sourced figure ("1,847 CI runs yesterday") is the fix, not a hit.

### 29 01/02/03 section markers
*Confirm:* giant faint ordinals stapled to *unordered* marketing sections. A
genuinely ordered sequence — install steps, a changelog, an indexed catalogue —
has earned its numbers.

### 30 Cards inside cards
Grep gives leads; the judgment is in the rendered DOM.
```
rg -n -i 'rounded[^"]*border[^"]*"[\s\S]{0,120}rounded[^"]*border' -g '*.{tsx,jsx,vue,svelte,astro,html}'   # *Manual*: no scanner pattern
```
*Confirm:* three or more nested surfaces each with its own border/radius/shadow
and shrinking padding. A child that is genuinely a separate object (a preview,
an embed) may keep its own surface.

### 31 One gap everywhere
```
rg -n -c 'space-y-4|gap-4'   # *Manual*: per-file counts; high = lead
```
Mostly a visual judgment: the grep only finds the token, the tell is the
*absence of any other value*. Count the distinct spacing values in a component;
one value for both within-group and between-group distances is the tell.
*Confirm:* a heading equidistant from its own body and from the previous
section. A deliberate uniform grid (a photo wall, a calendar) is a choice.

### 32 Inter everywhere (evolved)
```
rg -n 'from ["'\'']next/font/google' -g '*.{ts,tsx,js,jsx}'   # *Manual*: bare import, confirm the face
```
*Confirm:* judgment tell — the faces themselves are good. Slop is the stock
pairing (Space Grotesk display + Inter body) or Inter-by-default with no sign
anyone compared alternatives. A team that tried others and landed on Inter made
a choice; check for any evidence of one (a comment, a brand doc, a deliberate
fallback stack).

### 33 The tasteful terminal (evolved)
```
rg -n '\$ [a-z]' -g '*.{tsx,jsx,vue,svelte,astro,html,md}'   # *Manual*: shell-prompt decoration
```
*Confirm:* monospace on non-code UI chrome; ASCII banners as decoration;
near-black with a single warm accent. This one needs judgment most — it's a
current default, so weigh whether the terminal metaphor actually serves the
product.

### 34 The editorial dashboard (evolved)
```
rg -n -i 'font-serif' -g '*.{tsx,jsx,vue,svelte,astro,html}'   # *Manual*: tell 34 has none; font-serif fires 07
```
*Confirm:* the serif is on app chrome (a dashboard h1, stat-card numerals),
not on genuinely editorial content; the greeting-as-headline sits on an
operational surface; the cream + tracked-caps kicker + deep accent kit came
as a set. A docs site or essay page in a text serif is not this tell.
