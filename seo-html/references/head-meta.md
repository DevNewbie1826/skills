# Head and meta tags

Read this when you write or fix anything inside `<head>`: charset, viewport, title, description, robots, canonical, hreflang, icons, Open Graph, or Twitter tags.

## Order and the minimum set

Put `<meta charset>` first so it lands in the first 1024 bytes (HEAD-01). Then viewport, title, description, canonical, robots, social tags, icons, and JSON-LD.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Passport renewal time in 2026: steps, fees, and how to speed it up</title>
  <meta name="description" content="Routine passport renewal takes about six to eight weeks in 2026. Here are the steps, current fees, and the two legal ways to get it faster.">
  <link rel="canonical" href="https://example.com/guides/passport-renewal">
  <meta name="robots" content="index, follow">
  <link rel="icon" href="https://example.com/favicon.ico">
  <meta name="theme-color" content="#0b5fff">
</head>
```

## Title and description

- One non-empty `<title>` (HEAD-03), one non-empty description (HEAD-05).
- Target a weighted display width of 50-60 units for the title and 150-160 for the description, in every language (HEAD-04, HEAD-06, warnings). Wide CJK code points such as Hangul count 2.0 units, everything else 1.0, after whitespace collapse. Google and Naver set no hard limit; they cut long text to fit the screen, so lead with the words that matter.
- Don't reuse the title as the description (HEAD-10). Naver penalizes it.
- Korean pages show fewer characters per line; see [korean-naver.md](korean-naver.md).

## Robots

- Leave out robots meta or use `index, follow`. `noindex` or `none` in `robots`, `googlebot`, or `yeti` is an error (HEAD-07) unless the brief wants the page hidden and you pass `--allow-noindex`.
- `nosourceinfo` turns off Naver's AI source descriptions (HEAD-11, info). Add it only when the owner asks.

## Canonical and hreflang

- Exactly one canonical, absolute `https://` URL (LINK-01). `og:url` should be the same URL (OG-06).
- For language versions, each page lists itself and every other version, plus `x-default` (LINK-02):

```html
<link rel="alternate" hreflang="ko" href="https://example.com/ko/guides/passport-renewal">
<link rel="alternate" hreflang="en" href="https://example.com/guides/passport-renewal">
<link rel="alternate" hreflang="x-default" href="https://example.com/guides/passport-renewal">
```

## Open Graph

og:title, og:type, og:image, and og:url are required (OG-01). Add og:description (OG-02) and og:image:alt (OG-03). Declare image size: under 150x150 or wider than 3:1 fails Naver (OG-04); 1200x630 is the usual share size (OG-07, info). Add og:site_name and og:locale (`ko_KR` or `en_US`) (OG-05).

```html
<meta property="og:type" content="article">
<meta property="og:title" content="Passport renewal time in 2026">
<meta property="og:description" content="About six to eight weeks for routine service, with two legal ways to go faster.">
<meta property="og:url" content="https://example.com/guides/passport-renewal">
<meta property="og:image" content="https://example.com/img/passport-renewal-1200x630.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="A passport next to a renewal form">
<meta property="og:site_name" content="Example Guides">
<meta property="og:locale" content="en_US">
```

## Twitter (X) card

Use `summary_large_image` for articles (TW-01). X falls back to OG for title, description, and image, but setting them explicitly avoids surprises (TW-02).

```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Passport renewal time in 2026">
<meta name="twitter:description" content="About six to eight weeks for routine service.">
<meta name="twitter:image" content="https://example.com/img/passport-renewal-1200x630.jpg">
```

## Scripts in head

Give every external `<script src>` in head `defer`, `async`, or `type="module"` (PERF-01). JSON-LD blocks aren't affected.
