# Model checklist (M rules)

Read this when you reach step 4 of the workflow: the checks a script can't make.

For each rule, read the page and mark pass or fail with one line of evidence (a quote or a location). Status labels match [rules.md](rules.md).

## Writing (all languages)

| ID | Pass when | Fail when |
|---|---|---|
| W-01 | The first paragraph under the h1 answers the page question in 1-2 sentences | It opens with background, a story, or a promise of what's coming |
| W-02 | Every paragraph names its subject; each number sits with its unit, date, and source or method | A paragraph needs the previous one to make sense, or a number floats without context |
| W-03 | Numbers and claims link or cite a primary source in the same paragraph | Claims rest on "studies show" or a secondary article |
| W-04 | Visible byline with author page, visible published and updated dates matching JSON-LD, About and Contact links | Any of those is missing or disagrees with the markup |
| W-05 | Plain words, short sentences, keyword used only where it reads naturally | Filler, padding, or a keyword repeated for count |

## Korean (when --lang ko)

| ID | Pass when | Fail when |
|---|---|---|
| KR-01 | Spelling and spacing are clean; one register (합니다 or 해요) throughout | Spacing errors, or registers mixed |
| KR-02 | The key term sits in the first ~20 syllables of the title | The topic only appears near the end of a long title |
| KR-03 | Topics with attributes (fees, periods, conditions) use a table or dl | Attribute-heavy facts are buried in prose |

## English (when --lang en)

| ID | Pass when | Fail when |
|---|---|---|
| EN-01 | Active voice, short sentences, consistent US or UK spelling matching og:locale, sentence-case headings | Passive-heavy prose, mixed spelling, or locale mismatch |

## Naver

| ID | Pass when | Fail when |
|---|---|---|
| NAV-01 | Title unique, no keyword repeated 2+ times, no spam or promo words | "최저가 최저가 할인", repeated keywords, or a title shared with another page |
| NAV-02 | Description is 1-2 sentences, unique, not a keyword list or pasted body | Keyword list, body dump, or copied from another page |
| NAV-03 | og:image is unique to this page and the file is at least 5,000 bytes (check the file if you have it; otherwise mark "not checked") | Shared site-wide image, or a tiny file |
| NAV-04 | On a 360px-wide screen the h1 and the answer paragraph are visible without scrolling | A hero image or banner pushes the answer below the fold |

KR-02, KR-03, and NAV-04 are unverified (practitioner observations); NAV-01 to NAV-03 are verified by Naver's guide. A failed unverified rule is still worth fixing, but say it's unverified in the report.
