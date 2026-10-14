# Report format

Read this when you write the final report or need to parse the checker's JSON output.

## Checker JSON (input)

`python3 scripts/check_page.py page.html --json` prints one object:

```json
{
  "file": "page.html",
  "lang": "en",
  "summary": { "error": 0, "warn": 2, "info": 1, "score": 94 },
  "findings": [
    {
      "id": "HEAD-04",
      "severity": "warn",
      "line": 5,
      "message": "title width is 68 units (target 50-60)",
      "evidence": "<title>...</title>",
      "fix": "shorten the title to 50-60 weighted width units"
    }
  ],
  "extracted": {
    "title": "Passport renewal time in 2026",
    "title_len": 29,
    "description_len": 151,
    "h1": "Passport renewal time in 2026",
    "og": { "og:title": "Passport renewal time in 2026" },
    "twitter": { "twitter:card": "summary_large_image" },
    "canonical": "https://example.com/guides/passport-renewal",
    "jsonld_types": ["Organization", "WebSite", "WebPage", "Article", "BreadcrumbList"],
    "images": [
      { "src": "https://example.com/images/passport-form.png", "alt": "Passport renewal form with the photo box highlighted", "width": "1200", "height": "675", "loading": "lazy" }
    ]
  }
}
```

`severity` is `error`, `warn`, or `info`. Score = max(0, 100 - 10 x errors - 3 x warnings). Exit code: 0 = no errors (and no warnings with `--strict`), 1 = errors (or warnings with `--strict`), 2 = unreadable file or usage error. `title_len` and `description_len` are weighted display width units, not character counts: after whitespace collapse each wide or fullwidth code point (East Asian Width W or F, such as Hangul) counts 2.0 and every other code point 1.0. `h1` is the text of the first `<h1>`, or `null` when the page has none. `images` lists each `<img>` as an object with `src`, `alt`, `width`, `height`, and `loading`, where a missing `alt` is `null` and any other missing attribute is an empty string. The example values are illustrative; read the real shape of `extracted` from your run.

## Final report (output)

Give the user a JSON block for machines and a Markdown summary for people.

```json
{
  "page": "page.html",
  "lang": "ko",
  "rounds": [
    { "round": 1, "error": 3, "warn": 4, "info": 2, "score": 58 },
    { "round": 2, "error": 0, "warn": 1, "info": 2, "score": 97 }
  ],
  "final": { "exit": 0, "error": 0, "warn": 1, "info": 2, "score": 97 },
  "remaining": [
    { "id": "HEAD-04", "severity": "warn", "reason": "title kept at 64 width units to include the year" }
  ],
  "model_checklist": [
    { "id": "W-01", "result": "pass", "evidence": "first paragraph states the 4-8 day answer" },
    { "id": "NAV-03", "result": "not checked", "evidence": "image file not available" }
  ],
  "follow_up": ["submit sitemap in Search Advisor", "allow Yeti in robots.txt"]
}
```

The Markdown summary covers, in this order:

1. Outcome in one line: final exit code, errors, warnings, score.
2. Rounds: one line per round with counts.
3. Remaining findings: ID, severity, and why it's left.
4. Model checklist: failed or unchecked M rules with evidence, marking unverified ones.
5. Follow-up: site-level items out of this skill's scope (robots.txt, sitemap, Search Advisor registration).
