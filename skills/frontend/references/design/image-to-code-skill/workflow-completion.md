# Workflow, Examples, and Completion

Read this when applying the final image-to-code checklist, interpreting common requests, or deciding whether the result is complete.

[Back to the image-to-code core](../image-to-code-skill.md)

## 10. IMAGE-FIRST WEBSITE WORKFLOW

When an environment supports image generation plus implementation, default to an image-first workflow for website design tasks.

Preferred execution order:
1. infer the section count
2. generate section reference images first
3. generate extra detail/extraction images where needed
4. if needed, regenerate unclear sections as fresh standalone images
5. deeply inspect all generated images
6. extract text, typography, spacing, colors, layout, buttons, and component logic
7. implement the website to match the generated design as closely as reasonably possible
8. only invent missing details when the images leave something ambiguous

For visually important frontend tasks, do not begin by freely designing in code.
Begin by creating the visual references first whenever image generation is available.

The images are the primary art-direction source.
The code is the implementation layer.

---

## 11. WHEN TO TRIGGER IMAGE GENERATION FIRST

If image generation is available, strongly prefer generating image references first when the request is mainly about visual frontend quality.

Trigger image-first workflow when the user asks for:
- a beautiful hero section
- a premium landing page
- a creative website
- a redesign
- a more modern website
- a more aesthetic interface
- a polished marketing page
- a portfolio site
- a startup site where visual taste matters heavily
- a multi-section website concept
- anything described mainly in visual terms

Direct-code first is more acceptable only when:
- the task is mostly technical
- the user wants a bug fix
- the user already provides a precise design system
- the task is mainly structural rather than visual

---

---

## 35. WORKFLOW CHECKLIST

Before finalizing an image-to-code task, verify internally:

1. Infer the site type and number of sections; use the relevant default section pack.
2. For visual website work, when image generation is available and visual quality is central, generate the design image(s) before coding; do not start with freeform code when visual references should lead.
3. Prefer one large, readable image per section instead of a compressed multi-section board.
4. Generate additional detail or extraction images whenever text, components, readability, or analysis quality need them. Do not be lazy with image count.
5. Regenerate unclear sections as fresh standalone images; do not crop previously generated images for section extraction.
6. Choose a strong visual combination, four signature components, and two motion-implied cues.
7. Keep every image in a multi-image site consistent in brand world, type scale, spacing, CTA styling, icon mood, image treatment, tonal language, and component family.
8. Keep the hero clean, spacious, and restrained with a short line count and strong image usage where appropriate; keep the first screen balanced and readable on a small laptop.
9. Make hierarchy obvious and verify typography, spacing relationships, buttons, components, and colors are understood and extracted properly.
10. Keep spacing generous, even, and analyzable; remove unnecessary nested boxing, cards-inside-cards, giant boxed wrappers, useless pills, labels, and fake technical micro-elements.
11. Deeply and cleanly analyze every generated image; keep the analysis structured and specific.
12. Extract text, typography, spacing, buttons, colors, components, and layout logic before implementation.
13. Verify that the design is visually distinctive, free of obvious AI tells, and clear enough to code faithfully.
14. Create final files only after the full analysis pass, then implement as closely as reasonably possible to the generated references used as the primary visual source.
15. Do not ask unnecessary follow-up questions when a strong interpretation is possible.

If any check fails, refine internally before output.

---

## 36. EXAMPLE INTERPRETATIONS

### Example 1
User:
“make me one hero section for an AI startup”

Interpretation:
- generate 1 hero image
- if needed, generate 1 closer extraction image for text/buttons
- do not crop a small region out of a larger board
- if more clarity is needed, regenerate the hero as a fresh cleaner standalone image
- keep the hero calm and readable
- avoid fake utility labels and nested cards
- analyze headline, subheadline, CTA, spacing, colors, hero media
- then implement the hero

### Example 2
User:
“design me an 8-section landing page”

Interpretation:
- generate 8 separate section images
- one per section
- generate extra detail images where necessary
- deeply analyze all 8 sections
- extract text, typography, spacing, buttons, colors, cards, structure
- if one section is still unclear, regenerate that section again cleanly instead of cropping
- keep sections open and not overboxed
- then implement the full site from those references

### Example 3
User:
“make a premium creative agency website with 4 sections”

Interpretation:
- generate 4 separate section images
- keep the hero very clean
- ensure text remains readable
- deeply analyze each section
- do not use rough cutouts from the first renders
- regenerate clearer section images if needed
- avoid over-pilled microcopy and container overload
- then implement the site from those 4 references

---

## 37. COMPLETION RULE

Complete only when the checklist passes and the implementation is a premium, art-directed, clear, structured, readable, analyzable, memorable, anti-generic, implementation-friendly translation of generated, section-specific references that holds up as section images, a design system, under deep analysis, and as an implemented frontend - not an unreadable design board or a generic coded reinterpretation.
