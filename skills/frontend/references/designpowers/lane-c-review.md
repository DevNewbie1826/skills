# Lane C: Review & Repair

Read this when UI implementation needs evidence-based visual, accessibility, heuristic, and persona review before final sign-off.

Lane C runs after implementation and before final sign-off. It requires objective `visual-qa` evidence first, then applies designpowers judgment to the same artifact, then hands reconciled context to the project's review workflow. Measurements and screenshots anchor the review; designpowers adds human-centered judgment that metrics alone do not encode.

## Leaves in this lane

| Leaf | Read when |
|---|---|
| [design-review.md](review/design-review.md) | an existing or built surface must be evaluated — one reconciled craft, accessibility, and usability critique |
| [heuristic-evaluation.md](review/heuristic-evaluation.md) | a usability check is needed — Nielsen H1–H10 with evidence plus per-task cognitive walkthroughs |
| [synthetic-user-testing.md](review/synthetic-user-testing.md) | a built design needs validation by walking key tasks as each inclusive persona |
| [usability-testing.md](review/usability-testing.md) | planning or running usability tests with real participants |

## Phase owner

| Capability | Owner | Mapping |
|---|---|---|
| Review an existing surface without rerunning discovery | [design-review.md](review/design-review.md) | Use for critique context while still capturing objective artifacts. |
| Critique against brief, plan, personas, principles, taste, and craft | [design-review.md](review/design-review.md) — intent and craft lenses | Run after screenshots and objective checks so findings cite the built surface. |
| WCAG, COGA, keyboard, screen reader, motion, content, and adaptive needs | [design-review.md](review/design-review.md) — accessibility lens | Name affected users and exact fixes. |
| Nielsen heuristics and cognitive walkthroughs | [heuristic-evaluation.md](review/heuristic-evaluation.md) | Walk key tasks and classify H1-H10 findings with severity. |
| Persona and task walkthroughs | [synthetic-user-testing.md](review/synthetic-user-testing.md) | Validate that inclusive personas can complete real tasks in assistive or situational contexts. |
| Human testing plan when needed | [usability-testing.md](review/usability-testing.md) | Produce a participant-test plan or follow-up recommendation when synthetic testing is insufficient. |
| Completion evidence discipline | Review workflow (salvage below) | Summarize completion, accessibility, persona, content, and debt status. |

## Salvaged from removed references

Short items whose full source documents were removed as duplicated elsewhere:

- **From former ui-composition:** test colour-dependent information with simulated colour-vision deficiency (protanopia, deuteranopia, tritanopia) — not only contrast ratios.

## Prompt injection

Use this sequence for UI review and repair:

```text
Run `visual-qa` first against the built surface. Capture objective screenshots, diffs, browser or terminal artifacts, and any required visual QA report.

Then apply Lane C Review & Repair to the same artifact:
- critique against brief, plan, principles, personas, taste, craft, and design-system alignment
- accessibility review for WCAG, COGA, keyboard, screen reader, touch, motion, adaptive preferences, and content
- heuristic evaluation for Nielsen H1-H10 and cognitive walkthroughs
- persona walkthroughs for relevant inclusive personas
- a real-participant testing plan when synthetic evidence is insufficient
- one evidence-backed report reconciling the findings

Resolve conflicts in this order: accessibility, usability, brief, personas, aesthetics. Escalate unresolved trade-offs to the user.

Pass the reconciled report, objective `visual-qa` artifacts, open findings, and accepted debt to the review workflow.
```

## Evidence requirements

Lane C requires:

- `visual-qa` artifacts from the actual surface;
- critique findings citing the plan, brief, personas, or taste direction;
- accessibility findings with severity, affected users, exact fix, and type;
- heuristic-evaluation results for relevant tasks;
- persona walkthrough results with task, steps, outcome, and barriers;
- a repair decision for every Critical or Major issue; and
- deferred Minor or Note findings routed to design debt with final review context.

## URL Discovery Protocol

When evaluating a live website, discover real URLs before attempting to fetch any sub-pages. Follow this protocol in order. **Never infer or guess a URL from a nav label, button text, or any other interface element** — a label "Vendre" does not mean the URL is `/vendre`. Guessed URLs produce false 404 findings and damage the credibility of the evaluation.

1. **Extract hrefs from the page source.** Resolve each actual href against the effective document base URL: the page URL unless the document declares a `<base href>`, in which case use that base URL. Use only those resolved URLs for follow-up fetches; discard any URL you constructed from interface labels or other guesses. *(from former heuristic-evaluator)*
2. **Try the sitemaps.** Fetch `[origin]/sitemap.xml`; if that returns 404, also try `[origin]/sitemap_index.xml`. If a sitemap is found, use it as the authoritative URL list for the site.
3. **Check robots.txt.** Look for any `Sitemap:` directives — these point to the canonical sitemap location even when the default `/sitemap.xml` path doesn't exist.
4. **Accept the limit.** If all three steps fail to yield sub-page URLs, stop trying to fetch sub-pages and state explicitly in the evaluation: "Sub-page structure could not be verified — evaluation is based on homepage content only."

| href at `https://example.test/catalog/items/` | Resolved against the document URL |
|---|---|
| `../contact` | `https://example.test/catalog/contact` |
| `contact` | `https://example.test/catalog/items/contact` |
| `/contact` | `https://example.test/contact` |

Href types: relative hrefs (for example, `/acheter`, `../contact`) resolve against the effective document base URL before fetching; fragment hrefs (`#section`) are classified after resolution — skip one as same-document only when its resolved URL without the fragment equals the current document URL (on `https://example.test/catalog/items/`, `#section` resolves to `…/catalog/items/#section`, same document; with `<base href="../docs/">` it resolves to `…/catalog/docs/#section`, a different document that follows the normal fetch policy); JavaScript hrefs (`javascript:void(0)`, `onclick` handlers, missing `href`) indicate JS-rendered navigation — flag as a potential SEO and accessibility issue and do not fetch; external hrefs are fetched only when directly relevant to the evaluation. *(from the former heuristic-evaluator role reference)*

## Guardrails

- Do not run design judgment before objective `visual-qa` evidence exists.
- A high numeric visual score cannot override an accessibility, usability, or persona-blocking finding.
- Critical findings require repair, escalation, or explicit blocking status.
- Minor findings may be deferred only when recorded as debt with affected users and a suggested fix.
- Lane C supplies review input; the independent review workflow owns final sign-off.
- Static screenshots can support visual critique, but unexercised interaction, keyboard, and screen-reader findings are labeled inferred.

## Pass / fail behavior

PASS when objective `visual-qa` evidence exists, review lanes pass or have explicit accepted debt, and reconciled context reaches independent final review.

FAIL when review lacks real artifacts, skips relevant heuristic or persona testing, treats accessibility as optional, leaves Critical or Major issues unrepaired, or omits design findings from final review.
