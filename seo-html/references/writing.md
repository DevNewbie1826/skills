# Writing the body

Read this when you write the page's body text in any language.

Search engines and AI answer boxes quote paragraphs, not pages. Write so that any single paragraph can be lifted out and still be true and clear.

## Answer first

The first paragraph under the `<h1>` answers the page's question in one or two sentences. Details, caveats, and background come after.

- Weak: "Many people wonder about passports. In this guide we'll look at ..."
- Strong: "Routine passport renewal takes about six to eight weeks in 2026, and expedited service cuts that to two to three weeks for an extra fee."

## Self-contained paragraphs

Each paragraph names its subject instead of leaning on "it" or "this" from the previous one. When it has a number, the same paragraph carries the number, its unit, the date or period it applies to, and how it was measured or who reported it.

- Weak: "It went up 12% last year."
- Strong: "The routine renewal fee rose 12% in 2025, from $130 to $145, according to the State Department fee schedule."

Use label-value structure (a `<table>` or `<dl>`) for facts with several attributes: fee, duration, eligibility, deadline. Machines read grids more reliably than prose.

## Sources

- Cite primary sources: the agency, the filing, the dataset, the official doc. Link them inline in the same paragraph, with `<a>`, `<cite>`, or a footnote `<sup>`.
- Prefer the source's own page over a news article that quotes it.
- If you can't find a source for a number, drop the number or say it's an estimate.

## E-E-A-T

Show who wrote it and why they're credible, when it was published and updated, and how to reach the publisher.

- A visible byline linked to an author page, matching the JSON-LD `author`.
- Visible `<time>` for published and updated dates, matching `datePublished` and `dateModified`.
- Footer links to About and Contact.
- First-hand experience where it exists: "We renewed three passports in September 2026; the fastest took 19 days."

## Plain language

Short sentences, common words, one idea per paragraph. Use the keyword where it reads naturally; repeating it to hit a count backfires on both Google and Naver.

Language specifics: [korean-naver.md](korean-naver.md) for Korean, [english.md](english.md) for English.
