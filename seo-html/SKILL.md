---
name: seo-html
description: "Write and check one complete SEO-optimized static HTML page (head, meta tags, Open Graph, Twitter card, JSON-LD structured data, semantic HTML) in Korean or English with Naver rules, then audit it with a stdlib Python checker and fix up to 3 rounds. Triggers: SEO, HTML writing, SEO 최적화 HTML 작성, 메타태그, meta tags, Open Graph, Twitter card, JSON-LD, 구조화 데이터, structured data, 시맨틱 HTML, semantic HTML, 네이버, Naver, 서치어드바이저, Search Advisor, SEO 점검, SEO audit, SEO check."
---

# seo-html

This skill writes one complete, static, SEO-ready HTML page and then proves it. The page starts from `templates/page.html` and gets a full head (charset, viewport, title, description, canonical, robots, icons), Open Graph and Twitter tags, a semantic body, and JSON-LD. A stdlib Python checker (`scripts/check_page.py`) audits the script rules, a model checklist covers what a script can't judge, and you fix and re-check for up to 3 rounds. Korean and English are first-class, and Naver rules sit next to Google's. Every rule says whether an official source backs it.

## Workflow

| Step | Do | Read |
|---|---|---|
| 1. Brief | Pin topic, audience, language (ko/en), canonical URL, primary keyword, page type, author, dates, image | [workflow](references/workflow.md) |
| 2. Write | Fill `templates/page.html`; write the body answer-first | [head-meta](references/head-meta.md), [semantic-html](references/semantic-html.md), [structured-data](references/structured-data.md), [writing](references/writing.md), plus [korean-naver](references/korean-naver.md) or [english](references/english.md) |
| 3. Script check | From the skill directory: `python3 scripts/check_page.py page.html --json --lang ko` (or `--lang en`) | [rules](references/rules.md) |
| 4. Model check | Walk the M rules and record pass/fail with a reason each | [model-checklist](references/model-checklist.md) |
| 5. Fix and report | Fix every error, re-run steps 3 and 4, at most 3 rounds; then report what's left | [workflow](references/workflow.md), [report-format](references/report-format.md) |

Exit codes: 0 = no errors (and no warnings under `--strict`), 1 = errors (or warnings under `--strict`), 2 = unreadable file or bad usage.

## Read this when

| Reference | Read it when |
|---|---|
| [workflow.md](references/workflow.md) | You start a page, or need the fix loop and its stop conditions |
| [rules.md](references/rules.md) | A finding ID needs explaining, or you need a severity, threshold, or source |
| [head-meta.md](references/head-meta.md) | You write or fix anything inside `<head>`: meta, canonical, hreflang, OG, Twitter |
| [structured-data.md](references/structured-data.md) | You write or fix JSON-LD, or an LD-* finding fires |
| [semantic-html.md](references/semantic-html.md) | You lay out the body, or SEM, H, IMG, LINK, A11Y findings fire |
| [writing.md](references/writing.md) | You write the body text in any language |
| [korean-naver.md](references/korean-naver.md) | The page is Korean or must do well on Naver |
| [english.md](references/english.md) | The page is English |
| [model-checklist.md](references/model-checklist.md) | Step 4, the checks a script can't make |
| [report-format.md](references/report-format.md) | You write the final report, or parse the checker JSON |

## Scope

One page at a time. Site-level work (robots.txt, sitemap, duplicate titles across pages, live crawling, Core Web Vitals) is out of scope; mention it in the report as follow-up if it matters.
