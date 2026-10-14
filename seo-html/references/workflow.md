# Workflow: brief, write, check, fix, report

Read this when you start a new page or need the fix loop and its stop conditions.

The whole job is five steps. Steps 3 to 5 repeat as a loop of at most 3 rounds.

## 1. Brief

Collect these before writing. If the user didn't give one, pick a sensible value and say so in the report.

| Field | Example |
|---|---|
| Topic and the one question the page answers | "How long does a passport renewal take?" |
| Language | `ko` or `en` (sets `<html lang>`, `og:locale`, and `--lang`) |
| Canonical URL (absolute) | `https://example.com/guides/passport-renewal` |
| Primary keyword (optional) | passed to the checker as `--keyword` |
| Page type | Article, BlogPosting, NewsArticle, WebPage, Product |
| Author, organization, dates | name, about URL, `datePublished`, `dateModified` in ISO 8601 |
| Share image | absolute URL, width, height, alt text |
| Sources | primary sources to cite for numbers and claims |

## 2. Write

Copy `templates/page.html` to a working page and replace every placeholder. The working page is the user's file, not part of the skill, so it can live anywhere. Pass it to the checker by path, for example `python3 scripts/check_page.py path/to/page.html --json --lang ko` run from the skill directory. Placeholders left in JSON-LD fail LD-05, so search for `[`, `TODO`, and `REPLACE_` before checking.

- Head: [head-meta.md](head-meta.md)
- Body layout: [semantic-html.md](semantic-html.md)
- JSON-LD: [structured-data.md](structured-data.md)
- Text: [writing.md](writing.md), then [korean-naver.md](korean-naver.md) or [english.md](english.md)

## 3. Script check

Run from the skill directory:

```sh
python3 scripts/check_page.py page.html --json --lang ko
python3 scripts/check_page.py page.html --json --lang en --keyword "passport renewal"
```

Other flags: `--strict` (warnings also fail), `--lang auto` (reads `<html lang>`), `--allow-noindex` (only for pages that are meant to stay out of the index). Save each round's JSON, for example `round-1.json`. Finding IDs are explained in [rules.md](rules.md).

## 4. Model check

Go through [model-checklist.md](model-checklist.md). Record each M rule as pass or fail with one line of evidence.

## 5. Fix and re-check (at most 3 rounds)

One round = fix, then run steps 3 and 4 again.

1. Fix every `error` first. Then fix `warn` findings that don't fight the brief. Treat `info` as advice.
2. Fix failed M rules the same way.
3. Re-run the checker and the checklist; save the new JSON.

Stop as soon as one of these holds:

- The checker reports 0 errors and every M rule passes. That's done; warnings may remain if each has a stated reason.
- Round 3 is finished. Stop editing and report every remaining finding with why it's still there.
- The checker exits 2. Fix the file or the command (encoding, path, flags) before counting a round.

Never silence a finding by deleting real content or by adding `--allow-noindex` to a page meant to rank.

## 6. Report

Write the report in the shape from [report-format.md](report-format.md): final checker summary, per-round counts, remaining findings, M rule results, and out-of-scope site-level follow-ups.
