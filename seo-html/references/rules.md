# Rule catalog

Read this when a finding ID needs explaining, or you need a rule's severity, type, threshold, source, or verification status.

Severity: E = error (exit 1), W = warn (exit 1 only with `--strict`), I = info. M rules have no severity; they pass or fail in [model-checklist.md](model-checklist.md). Score = max(0, 100 - 10 x errors - 3 x warnings). Type S = checked by `scripts/check_page.py`, M = checked by the model.

Title and description lengths (HEAD-04, HEAD-06) are a weighted display width: collapse whitespace, then count 2.0 units for each wide or fullwidth code point (Unicode East Asian Width W or F, which covers Hangul, CJK, and kana) and 1.0 for every other code point. One range applies to every language. Other lengths are plain Unicode code points, never bytes. Thresholds live as constants in the script.

Source abbreviations: FYSA = fire-your-seo-agency reference prose, SUS = seo-unified-skill reference prose, CS = the checker behavior reference listed in [ATTRIBUTION.md](../ATTRIBUTION.md), OGP = ogp.me, Naver = searchadvisor.naver.com guide, Google = Google Search Central. Status `verified:` cites the official page that backs the rule; `unverified:` says why it's kept anyway. An unverified rule is still enforced at its severity; it's an owner or reference value, not a search-engine requirement.

| ID | Sev | Type | Rule | Source | Status |
|---|---|---|---|---|---|
| HEAD-01 | E | S | `<meta charset>` utf-8 present and within first 1024 bytes | SUS head-tags | verified: https://html.spec.whatwg.org/multipage/semantics.html#charset |
| HEAD-02 | E | S | viewport meta contains `width=device-width` | SUS head-tags; Naver | verified: https://searchadvisor.naver.com/guide/markup-mobile |
| HEAD-03 | E | S | exactly one non-empty `<title>` | SUS head-tags; CS | unverified: Google title doc covers display, not the one-title rule |
| HEAD-04 | W | S | title weighted width outside 50-60 units | FYSA seo.md; CS; owner value | unverified: owner value; Google and Naver set no length limit and truncate to display width; wide CJK glyphs take about two Latin widths, so they weigh 2.0 |
| HEAD-05 | E | S | exactly one non-empty meta description | SUS head-tags; CS | unverified: best practice; Google uses the description as one snippet source but does not require it |
| HEAD-06 | W | S | description weighted width outside 150-160 units | FYSA seo.md; CS; owner value | unverified: owner value; Google and Naver set no length limit and truncate to display width; wide CJK glyphs take about two Latin widths, so they weigh 2.0 |
| HEAD-07 | E | S | robots meta (`robots`/`googlebot`/`yeti`) contains noindex or none; `--allow-noindex` downgrades to I | SUS head-tags; Naver | verified: https://searchadvisor.naver.com/guide/markup-structure |
| HEAD-08 | I | S | icon link and theme-color present | SUS head-tags | unverified: reference repo only |
| HEAD-09 | E | S | `<html lang>` present; with --lang ko/en it must start with that code | SUS head-tags; CS | unverified: HTML best practice; no search-engine doc requires it |
| HEAD-10 | W | S | meta description equals the title after whitespace/case normalization | Naver | verified: https://searchadvisor.naver.com/guide/markup-content |
| HEAD-11 | I | S | robots meta contains `nosourceinfo` (Naver AI source description off) | Naver | verified: https://searchadvisor.naver.com/guide/markup-structure |
| OG-01 | E | S | og:title, og:type, og:image, og:url present | SUS head-tags; OGP | verified: https://ogp.me/ |
| OG-02 | W | S | og:description present | SUS head-tags; Naver | verified: https://searchadvisor.naver.com/guide/markup-content |
| OG-03 | W | S | og:image present without og:image:alt | OGP | verified: https://ogp.me/ |
| OG-04 | W | S | declared og:image:width/height under 150x150 or aspect ratio over 3:1 | Naver | verified: https://searchadvisor.naver.com/guide/markup-content |
| OG-05 | I | S | og:site_name, og:locale missing, or og:locale not matching lang (ko_KR / en_*) | SUS head-tags | unverified: reference repo only |
| OG-06 | W | S | og:url differs from canonical, or og:url is not an absolute http(s) URL with a valid host and port | SUS head-tags; CS | unverified: reference repo only |
| OG-07 | I | S | og:image:width/height missing or below 1200x630 | SUS head-tags | unverified: 1200x630 is not on ogp.me or Naver docs |
| TW-01 | W | S | twitter:card missing or not one of summary, summary_large_image, app, player | SUS head-tags | unverified: developer.x.com cards markup page renders by script; fetch returned no rule text |
| TW-02 | I | S | twitter:title/description/image missing (OG fallback noted) | SUS head-tags | unverified: developer.x.com cards markup page renders by script; fetch returned no rule text |
| SEM-01 | E | S | exactly one `<main>` | CS | unverified: HTML Standard allows one visible main; search impact is reference repo only |
| SEM-02 | W | S | `<header>`, `<footer>`, `<article>` each present | FYSA seo.md; CS | unverified: reference repo only |
| SEM-03 | I | S | `<nav>` present | CS | unverified: reference repo only |
| SEM-04 | W | S | `div`/`span` with onclick (use button/a) | CS | unverified: accessibility best practice; reference repo only |
| SEM-05 | I | S | `<figure>` without `<figcaption>` | CS | unverified: reference repo only |
| SEM-06 | W | S | `<time>` without a valid ISO 8601 `datetime` | CS | unverified: reference repo only |
| H-01 | E | S | exactly one `<h1>` | FYSA seo.md; CS | unverified: reference repo only; Google does not require a single h1 |
| H-02 | W | S | heading level skip (h2 -> h4) | CS | unverified: accessibility best practice; reference repo only |
| H-03 | W | S | empty, digits-only, or <= 2 code point heading | CS | unverified: reference repo only |
| LD-01 | E | S | every `application/ld+json` block parses; at least one block exists | SUS schema-templates; CS | unverified: Google requires valid markup to use it; one block per page is this skill's choice |
| LD-02 | E | S | `@context` missing on a top-level node; http://schema.org -> W | SUS schema-templates; CS | unverified: reference repo only |
| LD-03 | E | S | node without `@type` (except @graph container) | SUS schema-templates; CS | unverified: reference repo only |
| LD-04 | E | S | `@graph` not a list | CS | unverified: JSON-LD 1.1 syntax; not checked against the spec in this pass |
| LD-05 | E | S | placeholder text (`[...]` tokens, `REPLACE_*`, `TODO`, `lorem ipsum`) in any LD string | CS | unverified: reference repo only |
| LD-06 | E | S | phased-out types: HowTo, ClaimReview, CourseInfo, EstimatedSalary, LearningVideo, SpecialAnnouncement, VehicleListing, Book actions | CS | verified: https://developers.google.com/search/blog/2025/06/simplifying-search-results and https://developers.google.com/search/updates#how-to-deprecation |
| LD-07 | I | S | FAQPage present (valid schema; no rich result since 2026-05-07) | CS | verified: https://developers.google.com/search/updates |
| LD-08 | W | S | Article/BlogPosting/NewsArticle missing headline, author, datePublished, dateModified, or image | SUS schema-templates; FYSA content.md | verified: https://developers.google.com/search/docs/appearance/structured-data/article |
| LD-09 | E | S | BreadcrumbList: ListItems need position + name, item on all but last | SUS schema-templates | verified: https://developers.google.com/search/docs/appearance/structured-data/breadcrumb |
| LD-10 | E | S | Product: name and at least one of offers, review, aggregateRating | CS | verified: https://developers.google.com/search/docs/appearance/structured-data/product-snippet |
| LD-11 | W | S | Organization/WebSite missing name or url | SUS schema-templates | unverified: reference repo only |
| LD-12 | W | S | date fields (datePublished, dateModified, startDate, uploadDate) not ISO 8601 | SUS schema-templates; CS | unverified: ISO 8601 recommendation not re-fetched in this pass |
| LD-13 | W | S | url/@id/item/image/logo values not absolute http(s) URLs | CS | unverified: reference repo only |
| LD-14 | W | S | Article headline / WebPage name not found in visible title or h1 | CS | unverified: Google asks markup to match visible content; exact matching rule is this skill's choice |
| IMG-01 | E | S | `<img>` without alt attribute (alt="" is fine) | SUS head-tags; CS | unverified: accessibility best practice; reference repo only |
| IMG-02 | W | S | alt longer than 125 code points or looks like a filename | CS | unverified: reference repo only |
| IMG-03 | W | S | `<img>` without width and height | CS | unverified: layout-shift best practice; reference repo only |
| IMG-04 | I | S | first `<img>` in main has loading="lazy" | CS | unverified: reference repo only |
| LINK-01 | E | S | exactly one canonical, absolute http(s) | SUS head-tags; Google; Naver | verified: https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls and https://searchadvisor.naver.com/guide/markup-structure |
| LINK-02 | W | S | hreflang set present but missing self (canonical) or invalid code; hreflang hrefs must be absolute http(s) URLs with a valid host and port; I if no x-default | SUS head-tags | verified: https://developers.google.com/search/docs/specialty/international/localized-versions |
| LINK-03 | W | S | non-descriptive anchor text (click here, here, read more, more, 여기, 클릭, 여기를 클릭, 더보기, 자세히) | CS | unverified: Google link best practice; the word list is this skill's choice |
| LINK-04 | I | S | `<a>` with empty or `#` href | CS | unverified: reference repo only |
| A11Y-01 | W | S | form control without label[for], wrapping label, aria-label, or aria-labelledby | CS | unverified: accessibility best practice; reference repo only |
| PERF-01 | I | S | `<script src>` in head without async/defer/type=module | SUS head-tags; CS | unverified: reference repo only |
| CONT-01 | E | S | visible text inside `<main>` under 300 code points (thin); the count covers all visible text in `<main>`, including headings, byline and figure captions | CS | unverified: owner value; no official minimum length |
| CONT-02 | W | S | with `--keyword K`: density outside 1-3% | CS | unverified: owner value; no official density target |
| CONT-03 | I | S | paragraph with a number+%/unit and no `<a>`, `<cite>`, or `<sup>` | FYSA geo.md | unverified: reference repo only |
| W-01 | - | M | answer-first: first paragraph answers the page question in 1-2 sentences | FYSA aeo.md | unverified: reference repo only |
| W-02 | - | M | self-contained paragraphs: subject, number, date, and method in the same paragraph | FYSA geo.md | unverified: reference repo only |
| W-03 | - | M | numbers and claims cite primary sources inline | FYSA geo.md; neo-naver.md | unverified: reference repo only |
| W-04 | - | M | E-E-A-T: visible author, publish/update date, about/contact path | SUS core-eeat; Google | unverified: Google helpful-content guidance not fetched in this pass |
| W-05 | - | M | plain language, no filler, no keyword stuffing | FYSA content.md; Naver | unverified: Naver covers title/description spam only (see NAV-01, NAV-02) |
| KR-01 | - | M | Korean spelling and spacing (맞춤법, 띄어쓰기) clean; one register (합니다 or 해요) throughout | project-local | unverified: style rule |
| KR-02 | - | M | Hangul title fits the visible display (50-60 weighted width units, see HEAD-04); key term first | FYSA content.md | unverified: display width is observed, not documented |
| KR-03 | - | M | facts in label-value grids (table or dl) where the topic has attributes | FYSA neo-naver.md | unverified: AI 브리핑 citation hypothesis; not in Naver docs |
| EN-01 | - | M | English: active voice, short sentences, US or UK spelling consistent, sentence-case headings | project-local | unverified: style rule |
| NAV-01 | - | M | title unique, no keyword repeated 2+ times, no spam or promo words | Naver | verified: https://searchadvisor.naver.com/guide/markup-content |
| NAV-02 | - | M | description 1-2 sentences, unique per page, not a keyword list, not the whole body | Naver | verified: https://searchadvisor.naver.com/guide/markup-content |
| NAV-03 | - | M | og:image unique per page, file at least 5,000 bytes | Naver | verified: https://searchadvisor.naver.com/guide/markup-content |
| NAV-04 | - | M | core answer visible on the first mobile screen | FYSA neo-naver.md | unverified: AI 브리핑 hypothesis; not in Naver docs |

## Notes on the verified facts

- Google sets no limit on title or meta description length; it truncates to the device width. HEAD-04 and HEAD-06 are owner values kept as warnings: one weighted-width range for every language (title 50-60 units, description 150-160 units), where a wide CJK code point counts 2.0 and any other counts 1.0.
- Article structured data has no required properties on Google; LD-08 lists the recommended ones, so it's a warning.
- FAQ rich results stopped appearing in Google Search from 2026-05-07. FAQPage is still valid schema, so LD-07 is info only.
- HowTo rich results were removed from Google Search and the docs were withdrawn; the other LD-06 types were phased out in June 2025.
- Product snippets need `name` plus one of `offers`, `review`, or `aggregateRating`.
- The charset declaration has to be serialized within the first 1024 bytes of the document.
