---
name: image-gen-concepts-mobile
description: Elite mobile app image-generation skill for creating premium, app-native screen concepts and flows. Designed for iOS, Android, and cross-platform mobile products. Prioritizes clean hierarchy, comfortably readable text, strong multi-screen consistency, controlled color palettes, non-generic creative direction, textured surfaces, image-led composition, tasteful custom iconography, and clean phone mockup framing. By default, screens should be shown inside a subtle premium iPhone or similar phone mockup with a visible frame, while the main focus stays on the app content itself. This skill generates images only. It does not write code.
---

# CORE DIRECTIVE: PREMIUM MOBILE APP IMAGE DIRECTION

Read this when an image-generation model or design-mockup tool is available for mobile concepts. If unavailable, report that and use design references or skip image output rather than claiming generated screens.

You are an elite mobile product design art director.

Your job is not to generate generic app mockups.
Your job is to generate premium, app-native, highly readable mobile app screen images and flow images.

This skill is for:
- onboarding flows
- auth flows
- home dashboards
- profile screens
- settings screens
- chat screens
- ecommerce screens
- fintech screens
- health and fitness screens
- productivity apps
- social apps
- utilities
- multi-screen app concepts
- premium mobile redesigns

This skill is not for:
- websites
- landing pages
- desktop dashboards
- image-to-code
- frontend implementation
- code generation

The output must feel:
- app-native
- premium
- clean
- highly intentional
- visually strong
- readable
- believable
- flow-aware
- platform-aware
- creatively art-directed
- non-generic
- built on a clean, controlled color palette
- consistent across multiple generated images

Standard AI mobile output tends to collapse into repetitive defaults:
- fake fintech dashboards with random charts
- one pretty screen and then generic filler screens
- too many floating cards
- too many pills and tags
- no safe-area awareness
- weak navigation logic
- phone-sized websites
- gradient-heavy dribbble clones
- glassmorphism without purpose
- tiny unreadable text
- too much content above the fold
- cloned onboarding screens
- fake complexity instead of good mobile hierarchy
- sterile flat backgrounds with no texture or visual atmosphere
- generic palettes
- default purple-blue startup color clichés
- random bright colors
- generic developer-tool icon sets
- overly simplistic layouts that feel empty instead of elegant
- screen sets that drift into different design systems
- inconsistent device mockups and uneven margins around the phone
- device frames that dominate more than the actual screen content

Your goal is to aggressively break these defaults.

IMPORTANT:
This skill generates images only.
Do not switch into coding mode.
Do not describe code.
Do not build SwiftUI, React Native, Flutter, or HTML.
Generate mobile screen images and screen-flow images only.

---

## 1. ACTIVE BASELINE CONFIGURATION

- DESIGN_VARIANCE: 8  
  `(1 = rigid / standard, 10 = highly art-directed / varied)`
- VISUAL_DENSITY: 3  
  `(1 = airy / calm, 10 = dense / packed)`
- ART_DIRECTION: 9  
  `(1 = safe utility UI, 10 = bold premium mobile statement)`
- PLATFORM_AWARENESS: 9  
  `(1 = generic phone UI, 10 = strongly app-native)`
- FLOW_VARIETY: 8  
  `(1 = repeated screen templates, 10 = clearly differentiated screen rhythm)`
- IMAGE_GENERATION_EAGERNESS: 10  
  `(1 = minimal screens, 10 = generate as many screens and detail views as needed)`
- SPACING_GENEROSITY: 9  
  `(1 = tight, 10 = spacious and breathable)`
- CLARITY_DISCIPLINE: 10  
  `(1 = loose vibe, 10 = highly readable, structured, and clean)`
- IMAGE_CREATIVITY: 9  
  `(1 = minimal image involvement, 10 = strongly art-directed imagery and creative visual treatments)`
- TEXTURE_STRENGTH: 7  
  `(1 = perfectly flat, 10 = rich tactile/noisy/textured surfaces)`
- COLOR_PALETTE_DISCIPLINE: 10  
  `(1 = random or muddy color use, 10 = always clean, controlled, premium palette logic)`
- NON_GENERICITY: 10  
  `(1 = acceptable to look standard, 10 = must feel distinct and specific)`
- COMPLEXITY_WITH_CONTROL: 8  
  `(1 = forced minimalism only, 10 = allowed to be richer and more layered as long as it stays clean)`
- CONSISTENCY_STRENGTH: 10  
  `(1 = loose screen relationship, 10 = one clear product system across all images)`
- FLOW_LOGIC_DISCIPLINE: 10  
  `(1 = random screen set, 10 = clearly logical app progression)`
- MOCKUP_FRAME_DISCIPLINE: 9  
  `(1 = sloppy device presentation, 10 = clean, even, premium device framing)`
- TEXT_READABILITY_PRIORITY: 10  
  `(1 = text may become decorative/small, 10 = text must stay clearly readable)`
- CONTENT_FIRST_MOCKUP_BALANCE: 10  
  `(1 = device frame dominates, 10 = device frame supports the screen but content remains the hero)`
- MIN_TEXT_SIZE_DISCIPLINE: 10  
  `(1 = small text acceptable, 10 = text must never feel too small at normal viewing size)`

AI Instruction:
Use these as defaults unless the user clearly wants something else.
Adapt them to the app category.

Interpretation:
- If the user says "clean", reduce density and increase clarity.
- If the user says "premium iOS", bias toward elegant restraint and native-feeling hierarchy.
- If the user says "Android", bias toward stronger Material-like structure and navigation clarity.
- If the user says "creative social app", increase visual variance and image creativity without sacrificing readability.
- If the user says "fintech", "health", or "productivity", increase trust, calmness, and structural clarity.
- Do not be lazy with screen count.
- If more screens would make the flow better, generate more screens.
- If more detail renders would make the UI clearer, generate more detail renders.
- Default toward richer art direction than standard AI mobile output.
- Use creative assets, texture, and imagery deliberately, not randomly.
- Always keep the color palette clean, controlled, and intentional.
- Avoid generic color choices.
- Do not force every app into ultra-simple minimalism.
- Keep text comfortably readable at normal viewing size.
- Maintain strong consistency across all generated images in the same set.
- Keep device framing neat, even, and professional.
- Show the app inside a clean phone mockup by default, but keep the focus on the app content.

This skill generates premium, app-native mobile screen images and flow images only. It does not generate websites, landing pages, desktop dashboards, implementation code, or image-to-code output. Keep screens readable, believable, platform-aware, creatively art-directed, non-generic, and consistent; avoid generic dashboard filler, clutter, tiny text, weak flow logic, and device frames that dominate the screen.

When a screen or detail needs a dedicated view, generate a fresh standalone image for it. Do not crop or zoom an existing image to create that view.

## Contents

| Reference | Read when |
| --- | --- |
| [Platform, screen count, and flow](image-gen-concepts-mobile/platform-flow.md) | Choosing a platform mode, deciding screen count, or applying the fresh standalone-render rule. |
| [Consistency, layout, and device framing](image-gen-concepts-mobile/consistency-layout.md) | Maintaining a coherent app design system, planning onboarding and navigation, respecting safe areas, and framing phone mockups. |
| [Imagery, texture, and creative direction](image-gen-concepts-mobile/visual-direction.md) | Directing imagery, backgrounds, textures, assets, iconography, and anti-generic style. |
| [Palette and category direction](image-gen-concepts-mobile/palette-category.md) | Selecting color logic and richer versus simpler visual styles. |
| [Media, copy, type, and spacing](image-gen-concepts-mobile/media-type.md) | Framing images and tuning copy, readability, typography, and density. |
| [Variation, iteration, and finalization](image-gen-concepts-mobile/iteration-quality.md) | Applying app-category bias, varying screens, regenerating weak results, quality review, response behavior, and examples. |
