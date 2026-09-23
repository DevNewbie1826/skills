# Analysis and Implementation

Read this when extracting design details from generated images and translating them faithfully into frontend code.

[Back to the image-to-code core](../image-to-code-skill.md)

## 8. CLEAN ANALYSIS STANDARD

Analyze cleanly and systematically.

Do not do vague vibe-only analysis.
Do not jump too fast from image to code.

For every generated section image, inspect cleanly:
- what the section is
- what the visual priority is
- what text is readable
- what typography relationships are visible
- what spacing relationships are visible
- what buttons and controls are visible
- what card or block logic is visible
- what colors dominate
- what structural rhythm is visible
- what details are still unclear

If something is unclear, generate another image before coding.

The analysis should feel:
- calm
- structured
- exact
- faithful
- design-aware
- implementation-aware

---

## 9. DEEP IMAGE ANALYSIS REQUIREMENT

Before implementing anything, deeply analyze the generated image(s).

Do not just glance at them.
Treat them like a design specification.

Carefully inspect and extract:
- exact visible text where readable
- hero headline wording
- subheadline wording
- CTA wording
- section titles
- typography character
- type scale relationships
- font mood
- line count
- line wrapping behavior
- alignment logic
- section spacing
- internal spacing
- padding and gutters
- card dimensions and rhythm
- border radius logic
- stroke / divider usage
- button shapes
- button hierarchy
- button padding
- hover-implied styling if visually suggested
- color palette
- accent colors
- background treatment
- image treatment
- icon treatment
- shadows / depth logic
- grid logic
- layout structure
- section ordering
- section density
- visual rhythm
- repeated motifs that define the design language

Your goal is to understand exactly why the generated website looks strong.

Only after this deep analysis should you implement the frontend.

---

## 21. TEXT EXTRACTION RULE

When text is readable in the generated section image, extract it and use it.

Especially inspect and extract:
- hero headline
- hero subheadline
- CTA labels
- section headings
- pricing labels
- feature names
- testimonial names and roles if clearly shown
- navbar labels
- footer labels if relevant

If the text is too small to extract reliably:
- generate a closer extraction image
- or generate a second clearer version of that section

Do not ignore text extraction.
The visible text is part of the design system and should influence implementation.

---

## 22. TYPOGRAPHY EXTRACTION RULE

Do not only notice that typography “looks nice”.
Analyze it properly.

Extract and observe:
- size relationships
- weight relationships
- line count
- line height feel
- tracking feel
- serif vs sans behavior
- display vs body contrast
- section heading rhythm
- CTA text scale
- whether the design uses calm or aggressive type

Use these findings during implementation.
Do not flatten typography into a generic coded hierarchy.

---

## 23. SPACING EXTRACTION RULE

Analyze spacing deliberately.

Inspect:
- distance between headline and subheadline
- distance between text and buttons
- distance between cards
- section top and bottom spacing
- side gutters
- card padding
- image-to-text distance
- navbar spacing
- CTA block spacing
- overall cadence across sections

The goal is not exact pixel OCR.
The goal is faithful spacing logic.

Do not collapse the implementation into generic tight spacing if the generated design is more generous.

---

## 24. BUTTON / COMPONENT EXTRACTION RULE

Buttons and components must be analyzed, not guessed.

Inspect:
- button size
- button shape
- button radius
- fill vs outline behavior
- icon usage
- hover-implied mood
- primary vs secondary hierarchy
- card structure
- badge usage
- dividers
- shadows
- borders
- pill logic
- input styling if present

If button or card detail is too small, generate a closer image.

---

## 25. COLOR EXTRACTION RULE

Actively analyze and extract colors from the generated image(s).

Inspect:
- background color
- panel colors
- accent colors
- button fills
- text color hierarchy
- border color logic
- shadow color mood
- image tint / grade
- gradient restraint or intensity

The implemented website should preserve the original color logic as closely as reasonably possible.

Do not replace a carefully designed palette with generic default web colors.

---

---

## 26. DESIGN-TO-CODE COPY DISCIPLINE

After generating and analyzing the reference image(s), implement the website in a copy-oriented way.

This means:
- follow the references closely
- preserve layout logic
- preserve spacing rhythm
- preserve section ordering
- preserve text/image balance
- preserve typography mood
- preserve component style
- preserve overall visual cleanliness

Do not drift into a different design direction during implementation.
Do not “improve” the design by replacing it with a generic coded layout.

The goal is not:
- inspired by the image

The goal is:
- visually faithful to the image, translated into real frontend

---

## 27. ANTI-DRIFT IMPLEMENTATION RULE

A common failure mode is design drift:
the generated images look strong, but the coded result becomes generic.

Strictly avoid that.

During implementation:
- do not simplify into default templates
- do not replace distinctive sections with generic rows
- do not compress generous spacing into dense layout
- do not replace strong typography with plain hierarchy
- do not remove the page’s visual identity for convenience
- do not merge section logic into repetitive patterns that were not present in the source images
- do not reintroduce nested-box complexity that was intentionally removed during analysis

The final coded result should still feel like the same website as the generated references.

---

## 28. MISSING DETAIL RESOLUTION

When implementing from images, some details may still be unclear.

Resolve ambiguity by following this order:
1. preserve the visible design language
2. preserve layout and spacing logic
3. preserve component family
4. preserve mood and polish level
5. generate an extra detail image if needed
6. regenerate the section as a fresh standalone image if needed
7. only then choose the most implementation-friendly faithful version

Do not fill ambiguity with generic defaults too quickly.
