---
type: Planning Guide
title: Controlled Vocabulary
description: Canonical terminology, aliases, deprecated terms, and scannability rules for layout guidance.
---

# Controlled Vocabulary

Use this page when a term affects routing, metadata, search, claim records, workflow handoff, or review decisions. Prefer the canonical term in headings, frontmatter, validator output, and route labels. Use aliases only when explaining reader-facing alternatives.

Primary role: vocabulary and scannability contract.

## Canonical Terms

- Canonical: `domain`
  - Concept: top-level knowledge ownership
  - Definition: A documented decision surface with a named scope, exclusions, lifecycle, source of truth, validator, and review owner.
  - Use for: layout documentation with an explicit scope and ownership boundary.
- Canonical: `category`
  - Concept: local browse placement
  - Definition: A canonical grouping inside one domain; it cannot change the owning domain or its evidence boundary.
  - Use for: layout pattern families and other local indexes after a clear need is established.
- Canonical: `pattern`
  - Concept: reusable spatial primitive
  - Definition: A minimal HTML/CSS layout contract that solves one primary spatial problem.
  - Use for: individual pattern pages, catalog entries, pattern stacks, and primitive references.
- Canonical: `recipe`
  - Concept: screen composition
  - Definition: A screen-level composition that maps a common use case to a pattern stack.
  - Use for: recipe pages, planning flow, and primitive-to-recipe dependency records.
- Canonical: `gate`
  - Concept: review decision contract
  - Definition: A named review checkpoint that decides whether a claim is admissible and which evidence can support it.
  - Use for: evaluation and review decisions.
- Canonical: `claim`
  - Concept: review assertion
  - Definition: A statement about layout, design, accessibility, evidence, rationale, or harmony that needs a warrant and boundary.
  - Use for: review records, design rationale, and implementation handoff.
- Canonical: `evidence family`
  - Concept: evidence class
  - Definition: A class of support for a claim, such as mechanical, rendered, accessibility, interpretive, empirical, source, or debt evidence.
  - Use for: review records and evidence references.
- Canonical: `scroll ownership`
  - Concept: scroll responsibility
  - Definition: The named element or region that owns scrolling, fixed behavior, sticky behavior, and height determination.
  - Use for: Pattern frontmatter, layout briefs, recipes, and handoffs.
- Canonical: `harmony`
  - Concept: content layout fit
  - Definition: The fit between content hierarchy, spatial rhythm, visual weight, constraints, accessibility precedence, and pattern boundaries.
  - Use for: webpage generation workflow and harmony evaluation.
- Canonical: `debt`
  - Concept: accepted unresolved risk
  - Definition: A known limitation that is accepted with a boundary, owner, and verification or follow-up path.
  - Use for: evidence records, implementation handoff, and review decisions.
- Canonical: `warrant`
  - Concept: claim reasoning
  - Definition: The reason an evidence family can support a claim in a specific context.
  - Use for: review checkpoints and design rationale.
- Canonical: `boundary`
  - Concept: claim limitation
  - Definition: The explicit limit of what a page, pattern, gate, source, image, test, or screenshot proves.
  - Use for: review records, evidence pages, and implementation handoff.

## Aliases

- Alias: `area` -> `domain`
  - Use only in reader-facing explanation; policy and metadata use `domain`.
- Alias: `section` -> `category`
  - Use only for document structure or explanatory prose, not canonical placement metadata.
- Alias: `primitive` -> `pattern`
  - Use `primitive` only when contrasting individual patterns with recipes.
- Alias: `layout primitive` -> `pattern`
  - Use in explanatory prose only; canonical records should use `pattern`.
- Alias: `screen recipe` -> `recipe`
  - Use when a reader might confuse recipes with CSS snippets.
- Alias: `quality gate` -> `gate`
  - Use in navigation labels; canonical records may use `gate`.
- Alias: `visual reference` -> `generated-image reference`
  - Use `generated-image reference` when the generated-image workflow is specifically involved.

## Deprecated Terms

- Deprecated: `component` -> `pattern`
  - Reason: In Layout, component implies visual or framework ownership; Layout owns spatial pattern contracts.
- Deprecated: `template` -> `recipe`
  - Reason: Template implies copy-paste completeness; recipes are starting compositions.
- Deprecated: `proof` -> `evidence`
  - Reason: Proof overstates what screenshots, tests, generated images, or sources can establish unless the gate names the boundary.
- Deprecated: `style guide` -> `controlled vocabulary`
  - Reason: The vocabulary stabilizes decision language; it does not define brand voice.
- Deprecated: `library` -> `domain`
  - Reason: Library does not name ownership, exclusions, lifecycle, or review responsibility.

## Local-Only Terms

- Local-only: `pattern stack`
  - Meaning: The ordered set of patterns selected for a screen or section.
  - Boundary: Do not use it as a synonym for final product styling.
- Local-only: `section job`
  - Meaning: A content block's role in a webpage decision path, such as hook, explain, prove, compare, convert, navigate, or retain.
  - Boundary: Use in webpage generation, not in every pattern file.

## Scannability Checklist

- Use headings for decision boundaries, not decorative grouping.
- Keep lists short enough to scan; split a long list by task or concept when it carries more than one decision.
- Put the canonical term first, then aliases or boundaries.
- Prefer descriptive link text that names the destination decision, not generic text such as "here" or "more."
- Keep each paragraph to one idea when it explains policy or routing.
- Use tables only when comparison across columns is the reader's task; use lists for simple sequences.
- Put boundaries near the claim they limit so a reader does not have to infer them from another page.

## Vale Proposal

Prose linting should wait until the vocabulary is stable.

When the terms above stop changing, add Vale as a proposal first:

- Add accepted terms to a Vale vocabulary `accept.txt`.
- Add deprecated terms to `reject.txt` only after each replacement is documented here.
- Start with report-only checks for `Vale.Terms` and `Vale.Avoid`.
- Promote lint failures only after the planning guide, recipe pages, and pattern frontmatter are aligned.

## Source Notes

- [Google paragraph structure guidance](https://developers.google.com/style/paragraph-structure) supports short, single-idea paragraphs for scannability.
- [Google cross-reference guidance](https://developers.google.com/style/cross-references) supports descriptive link text.
- [Microsoft scannable content guidance](https://learn.microsoft.com/en-us/style-guide/scannable-content/) supports headings, lists, sidebars, and tables as scan aids.
- [Microsoft headings guidance](https://learn.microsoft.com/en-us/style-guide/scannable-content/headings) treats headings as structure and scan entry points.
- [Vale vocabulary guidance](https://vale.sh/docs/keys/vocab) distinguishes accepted and rejected vocabulary terms.
