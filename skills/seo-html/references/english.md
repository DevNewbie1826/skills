# English pages

Read this when the page is in English.

General writing rules are in [writing.md](writing.md); this file adds what's specific to English.

## Style (EN-01)

- Active voice and short sentences. Aim for most sentences under 25 words.
- Pick US or UK spelling and keep it. Match `og:locale` (`en_US`, `en_GB`) and `<html lang>` (`en`, `en-US`, `en-GB`).
- Sentence-case headings ("How long renewal takes"), not Title Case for every word, unless the site's style says otherwise.
- Spell out an acronym the first time: "Search Engine Results Page (SERP)".
- Write dates unambiguously in text ("October 14, 2026" or "14 October 2026"); ISO 8601 goes in `datetime` and JSON-LD.

## Title and description

- A weighted width of 50-60 units for the title and 150-160 for the description are the checker's targets (HEAD-04, HEAD-06, owner values). Latin letters, digits, and spaces count 1.0 unit each, so for plain English text width equals the character count. Google has no hard limit; it truncates to the device width, so the first 50 characters carry the meaning.
- Front-load the primary keyword, then the benefit: "Passport renewal time in 2026: steps, fees, and faster options".
- The description is a short pitch, not the title again (HEAD-10).

## Keywords

- With `--keyword`, density is counted on word tokens and should land between 1% and 3% (CONT-02).
- Use natural variants and plurals; don't force exact-match phrases into every heading.

## Link text

Say where the link goes: "the State Department fee schedule", not "click here", "here", "read more", or "more" (LINK-03).
