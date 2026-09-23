# Generation and Workflow

Read this when deciding whether to generate design references, how many images to create, how to regenerate unclear details, and which baseline direction to use.

[Back to the image-to-code core](../image-to-code-skill.md)

## 1. ACTIVE BASELINE CONFIGURATION

- DESIGN_VARIANCE: 8  
  `(1 = rigid / conventional, 10 = highly art-directed / asymmetric)`
- VISUAL_DENSITY: 3  
  `(1 = airy / calm, 10 = dense / packed)`
- ART_DIRECTION: 8  
  `(1 = safe commercial, 10 = bold creative statement)`
- IMPLEMENTATION_CLARITY: 9  
  `(1 = loose moodboard, 10 = highly buildable UI reference)`
- IMAGE_USAGE_PRIORITY: 9  
  `(1 = mostly typographic, 10 = strongly image-led when appropriate)`
- SPACING_GENEROSITY: 9  
  `(1 = compact / tight, 10 = spacious / breathable)`
- ANALYSIS_PRECISION: 10  
  `(1 = broad vibe only, 10 = deep extraction of design details)`
- IMAGE_GENERATION_EAGERNESS: 10  
  `(1 = minimal image count, 10 = generate as many images as needed for excellent extraction)`
- UI_SIMPLICITY_DISCIPLINE: 9  
  `(1 = willing to add many micro-elements, 10 = aggressively reduce clutter and unnecessary UI chrome)`

AI Instruction:
Use these as defaults unless the user clearly wants something else.
Adapt them to the prompt.

Interpretation:
- If the user says “clean”, reduce density and increase clarity.
- If the user says “crazy creative”, increase variance and art direction.
- If the user says “premium SaaS”, keep clarity high and art direction controlled.
- If the user says “editorial”, allow stronger type and more asymmetry.
- Keep sections breathable.
- Prefer readability over squeezing too much into one image.
- Prefer larger, more analyzable section images whenever the available image-generation tool supports them.
- If more images would improve extraction quality, generate more images.
- Do not be lazy with image count.
- Default away from nested containers, excessive pills, tiny labels, and dashboard clutter.

---

## 2. MANDATORY IMAGE-FIRST RULE

For website design requests where visual quality matters, image generation is mandatory first.

This means:
1. generate the design image or image set yourself first
2. deeply inspect and analyze the generated image(s)
3. extract the design system from them
4. implement the frontend only after that

Do not:
- start with freeform coding
- skip straight to implementation
- describe a website without first generating the visual reference when generation is available
- rely on memory of “good frontend taste” instead of producing the actual reference

The image is the design source.
The code is the translation layer.

---

## 3. GENERATE ENOUGH IMAGES RULE

Generate enough images to make the design truly readable and extractable.

Do not be lazy with image count.

If more images would improve:
- text readability
- typography extraction
- spacing analysis
- button analysis
- card analysis
- color extraction
- component inspection
- implementation fidelity
- responsive understanding
- section clarity

then generate more images.

Strong rule:
- it is better to generate too many clear images than too few compressed images
- it is better to generate one clear image per section than one unreadable board for the whole site
- it is better to create an extra detail image than to guess details later

Never reduce image count just for convenience if that harms quality.

---

## 4. SECTION IMAGE RULE

Do not compress too many website sections into one image when that makes text, spacing, buttons, or layout details too small to analyze properly.

Prefer separate large images per section.

Default rule:
- 1 section requested → generate 1 image
- 2 sections requested → generate 2 images
- 3 sections requested → generate 3 images
- 4 sections requested → generate 4 images
- 5 sections requested → generate 5 images
- 6 sections requested → generate 6 images
- 7 sections requested → generate 7 images
- 8 sections requested → generate 8 images
- 9 sections requested → generate 9 images
- 10 sections requested → generate 10 images
- and so on when reasonable

This is preferred because:
- text stays readable
- typography becomes analyzable
- spacing stays visible
- button details stay visible
- layout proportions stay visible
- extraction quality becomes much better
- implementation becomes more faithful

Do not default to:
- one giant multi-column collage
- one long compressed board with tiny unreadable text
- one image containing many sections if that reduces extraction quality

If necessary, generate more images rather than shrinking everything.

A compact multi-section composition is appropriate only when every section remains readable and analyzable. Prioritize section clarity and extraction accuracy.

---

## 5. DO NOT CROP OLD IMAGES RULE

When a section needs a dedicated image or a closer detail view, do not simply crop, cut out, zoom into, or slice it from a previously generated larger image.

Do not:
- crop a hero out of a full-page board
- crop a pricing area out of a larger composition
- crop tiny cards out of a multi-section image
- rely on rough cutouts from existing images
- use extracted image fragments as the main source for implementation if they distort spacing, proportions, or typography

Instead:
- generate a fresh new image for that section
- generate a fresh new detail image for that section
- keep the same design language, palette, typography mood, and component family
- make the new image specifically optimized for readability and extraction

Reason:
cropped images often destroy:
- spacing accuracy
- type scale relationships
- clean margins
- layout proportions
- button clarity
- section balance
- overall implementation fidelity

Fresh section-specific generation is strongly preferred over cropping.

---

## 6. FRESH RE-GENERATION RULE

If a section or detail is not clear enough, generate it again as a new standalone image.

This standalone regeneration should:
- preserve the same visual language as the original overall design
- keep the same palette
- keep the same typography mood
- keep the same button style
- keep the same radius logic
- keep the same image treatment
- keep the same overall brand world

But it should also:
- make text larger and more readable
- make spacing more visible
- make buttons easier to inspect
- make component structure easier to analyze
- make layout proportions clearer
- make the section cleaner if the previous render was too busy

This is not a different design.
It is a cleaner, more analyzable section-specific render of the same design system.

---

## 7. OPTIONAL DETAIL / EXTRACTION IMAGE RULE

If a section image still does not expose the necessary detail clearly enough, generate an additional detail image for that same section.

Examples of useful secondary images:
- a closer hero render to read headline, subheadline, CTA, and typography
- a detail image for pricing cards
- a closer render for testimonials
- a closer render for navbar / header treatment
- a closer render for feature cards or UI panels
- a closer render for footer or CTA section
- a refined variation of the first generated image that makes the section more extractable
- a cleaner re-generation of the same section with larger text for extraction
- an image focused mainly on typography and spacing instead of the full composition

These additional images exist to improve analysis and extraction quality.

Use them when needed for:
- readable text
- clearer button states
- tighter spacing analysis
- card and component inspection
- clearer color extraction
- better typography observation
- more precise implementation

Do not hesitate to create a second or third extraction-oriented image for a section if the first image is too broad.

---

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
