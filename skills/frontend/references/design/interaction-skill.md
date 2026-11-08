---
name: interaction-skill
description: "Layer A interaction-mechanics reference. Stacks on any style skill whenever work adds or changes motion or interaction - micro-interactions, animated components, transitions, gestures, hover/press/state feedback, loading/success/error morphs, 'make it feel alive'. Mandates reading the mapped pattern source from an open interaction-pattern catalog before designing an interaction; owns interaction mechanics and reduced-motion discipline; owns zero visual taste. Load it alongside a style skill; it does not replace one."
---

# Interaction Mechanics

Read this when the deliverable adds or changes interaction feel: micro-interactions, animated components, transitions, hover, press, focus or state feedback, gestures, loading, success or error morphs, animated tabs, menus, modals, drawers or toasts - or the request says "make it feel alive", "polish the interactions", "add micro-interactions".

Style skills decide how a surface looks. This file decides how it *moves and responds*: spring physics, layout morphs, enter/exit orchestration, gesture feel, and reduced-motion discipline. It stacks on any Layer A style skill and any Layer B brand, exactly like [layout-skill.md](layout-skill.md), and adds ZERO visual direction: color, type, and material still come from the style skill and `DESIGN.md`.

## 1. The reference contract - never design an interaction from memory

The benchmark is an open interaction-pattern catalog: a free, open-source collection of animated components that publishes its full typed source, ships reduced-motion support on most items, and serves each item over public endpoints. Improvised interaction design produces slop motion the same way freestyled styling produces generic SaaS slop, and the fix is the same: consult the reference before designing.

The contract, in order:

1. **Find the nearest pattern** in the catalog map (section 3). The live index is the catalog's `llms.txt`; refresh from it when a pattern seems missing from the tables below.
2. **Read its real source** through the recipe (section 2). Never guess spring values, exit orchestration, or gesture thresholds from a preview description.
3. **Extract the mechanism**, not the pixels: the spring config, the layout strategy (shared-layout identity vs height morph vs clip path), what animates in what order on enter and exit, where blur cross-fades sit, and what the reduced-motion path swaps to.
4. **Adapt to the project.** Concrete durations, easings, and spring parameters come from the project `DESIGN.md` Motion & Interaction section. Where the catalog and `DESIGN.md` disagree, `DESIGN.md` wins. A value that is not in `DESIGN.md` gets added there first, then used.
5. **No matching pattern?** Run [component-catalogs.md](component-catalogs.md) section 3. If nothing fits there either, compose from the nearest two, or state explicitly that the interaction is novel and record its mechanism in `DESIGN.md` before building it.

## 2. Consultation recipe (public endpoints, no auth, no browser)

```bash
curl -s https://<catalog-origin>/llms.txt                         # catalog: every pattern + one-line feel
curl -s https://<catalog-origin>/r                                # registry index (JSON): slugs, categories, endpoints
curl -s https://<catalog-origin>/r/{slug}                         # item detail (JSON): files, dependencies, dates
curl -s https://<catalog-origin>/r/{slug}/raw                     # item source - the thing to read
curl -s https://<catalog-origin>/components/{category}/{slug}.md  # item doc page as markdown
```

Categories are `motion` (primitives) and `blocks` (composed patterns). When the project needs the component itself rather than the mechanism, a copy-in component registry serves item JSON at `/r/{slug}.json`. Read source to learn; do not vendor catalog files into reference docs, and do not paste whole components into a project when only the mechanism is needed.

## 3. Catalog - pattern routing map

### Buttons, state feedback, and progress

| Pattern | Mechanism | Reach for it when |
|---|---|---|
| button | Spring press; a stateful variant runs idle -> loading -> success/error with blur-swap slots and morphing width; a magnetic variant pulls toward the cursor | Any submit or call to action with async states - never leave a button state-less |
| action-swap | Text or icon swap with blur motion | Copy -> check, send -> stop, any label that changes meaning in place |
| expanding-arrow-button | Expand, hold-to-confirm, and slide interactions | Expressive marketing CTAs, destructive hold-to-confirm |
| animated-badge | Animated state icons, pulse feedback | Connection or status dots, live activity indicators |
| loader | Many variants; reduced motion swaps every transform for an opacity pulse | Any loading state; copy its reduced-motion contract even when hand-rolling |
| otp-input | Gliding focus ring, per-slot digit roll, error shake, success check draw | Code entry, verification flows |
| file-upload | Progress rows, retry/remove, reduced-motion-safe state changes | Upload queues, long-running item lists |
| feedback-widget | Trigger morphs into a popup with sending/success/retry states | Corner feedback affordances, inline report flows |

### Selection and form controls

| Pattern | Mechanism | Reach for it when |
|---|---|---|
| switch | Spring-driven thumb with press feedback | Boolean toggles |
| checkbox | Draw-on checkmark, indeterminate support | Multi-select, tree selection |
| radio | Gliding shared-layout indicator dot | Single-select groups |
| input | Label, icons, error shake, success check draw | Validated text entry |
| select | Panel unfolds bouncily from the trigger; a morph variant grows the trigger into the panel | Dropdown selection with spatial continuity |
| range-slider | Bouncy vertical-bar thumb gliding between snapped steps | Stepped value entry |
| wheel-picker | Native-momentum 3D drum with notch snap | Date, time, or option drums; mobile-feel pickers |
| availability-scheduler | Per-day spring toggles, blur-slide range add/remove | Schedule and slot editors |

### Navigation and wayfinding

| Pattern | Mechanism | Reach for it when |
|---|---|---|
| tabs | Pill, segment, or underline with a spring shared-layout indicator | Tab bars, view-mode selectors |
| expandable-tabs | Active icon expands to a labelled pill; panel morphs height, slides direction-aware | Compact tab bars with rich panels |
| shared-layout-bg | Pill glides between items via shared layout, blur enter/exit | Sidebar and menu hover or active states |
| dock | Grouped actions with a gliding active pill | Toolbars, grouped action rails |
| bounce-sidebar | Active dot jumps between destinations on a curved spring path | Vertical navigation with a playful indicator |
| preview-rail | Compact ticks form a hover pyramid and reveal a floating preview | Dense navigation rails, session switchers |
| expandable-action-bar | Icon actions expand into labelled controls on hover or focus | Compact action clusters |
| overflow-actions | Connected pill rail springs open to reveal extra controls | Primary-plus-overflow action groups |
| command-palette | Fuzzy filter with a spring-animated active row | Keyboard-first command surfaces |
| bloom-menu | Button morphs into a menu blooming from its center with radial stagger | Radial and launcher menus |

### Overlays and surfaces

| Pattern | Mechanism | Reach for it when |
|---|---|---|
| tooltip | Blur enter/exit, spring entrance | Hover and focus hints |
| popover | Gooey filter ooze from the trigger; a morph variant clip-morphs from the trigger corner | Anchored panels that should feel attached to their trigger |
| context-menu | Pointer-origin clip morph, gliding active row, keyboard nav, type-ahead, long-press | Right-click and long-press menus |
| morphing-modal | One panel morphs height between inner views, blur cross-fade on content | Multi-step dialogs, settings panes |
| center-morph-modal | Surface unfolds from its exact center toward every edge and folds back | Focused confirm and detail modals |
| drawer | Spring side panel, backdrop blur, body scroll lock, escape to close | Side panels, inspector panes |
| bottom-sheet | Draggable sheet with snap points, inertia, translucent surface | Mobile-feel sheets on any platform |
| dynamic-island | Pill morphs between live-activity views with bouncy shell resize and blur cross-fades | Live status surfaces, compact expanding widgets |
| notification-stack | Cards spring from a stacked summary into a readable list on hover, focus, or tap | Notification centers, grouped alerts |
| toast-stack | Status morphs, swipe dismissal, layout-aware stacking | Toast systems - layout-aware stacking is the bar |
| theme-toggle | Full-page clip-path reveal through the View Transition API | Theme switching that should feel like one gesture |

### Content, data, and gestures

| Pattern | Mechanism | Reach for it when |
|---|---|---|
| bouncy-accordion | Single-open accordion with weighted spring layout, reduced-motion-safe reveals | Disclosure groups, expandable rows |
| table | Virtualized large row counts, sortable, resizable, minimal reduced-motion-safe motion | Data grids - proof that restraint is also a motion decision |
| infinite-masonry | Virtualized variable-height masonry with progressive load | Media and card walls |
| swipeable-list | Rows swipe to reveal contextual actions | Mobile-style lists with hidden actions |
| pull-to-refresh | Drag resistance, threshold feedback, async refresh | Refreshable feeds |
| marquee | Infinite horizontal or vertical scroll, pause on hover | Logo walls, tickers |
| text-animation | Spring reveals, chromatic sweeps, shimmer loading, letter-cascade swaps | Hero copy, streaming or loading text |
| number | Count-up values, rolling digit tickers | Metrics, token and cost counters |
| cylinder-carousel | Items line a 3D cylinder with springy glide and snap | Showcase carousels |
| knockout-bracket | Animated tournament fixtures paging through rounds | Bracket and progression views |
| trade-ticket | Morphing swap views and account surfaces | Finance-shaped composite widgets |
| not-found | Several animated 404 styles | Error pages that keep the product's feel |

This table is the edge of the interaction catalog. Hero atmospheres, animated or shader backgrounds, typographic reveals, scroll chapters, and card surface effects route to [ambience-skill.md](ambience-skill.md), whose routing map and retrofit checklist own that quadrant.

## 4. Mechanics rules

These sharpen the shared axioms for interaction work; none of them replace the style skill.

- **Motion serves meaning, and each meaning has its motion.** Every animation maps to a real interaction, state change, or affordance; a hover that changes nothing is slop. Pick the motion from the meaning, not from the catalog's most striking demo:

  | Meaning | Motion | Not |
  |---|---|---|
  | Press acknowledged | Scale or wash on the element, same frame | A ripple that arrives after the action fires |
  | Something is in progress | A moving indicator | A static one, which reads as frozen |
  | Something is live or new | A brief highlight or subtle pulse, once | A permanent loop |
  | Something arrived from elsewhere | Enter from the direction of its origin | A fade-in from nowhere |
  | Something moved | It travels there | Disappear here, appear there |
  | An unfamiliar control exists | A one-time introduction on first appearance | Continuous decoration |

- **Transitions keep identity.** A surface that resizes, repositions, or swaps content animates from its old geometry to the new one - a shared-layout identity or a measured-height morph - so the user never suspects a replacement. When items move and others appear, move first, then add. Keep one element still as the anchor while the rest animates. Nothing reflows under the pointer while the user is typing or dragging. A panel leaves the way it came: a sheet that rose from the bottom dismisses downward, and the reverse gesture undoes the forward one.
- **Reduced motion is part of the component, not an afterthought.** Match the catalog's bar, and reduce rather than remove: under `prefers-reduced-motion: reduce`, positional, scale, and depth motion becomes a cross-fade (the loader pattern's opacity-pulse swap is the model); fades, gesture-tracked motion, and progress indicators stay; blur never animates its start or end. Any state that motion conveys is also announced (`aria-live`, a label change). On native mobile targets, respect the system reduce-motion setting.
- **GPU-composited properties only**: `transform`, `opacity`, `filter`. Never animate layout properties; morph layout through shared-layout identity or measured-height primitives instead.
- **Springs move things; easings tint things; continuous input tracks.** Spatial movement (position, scale, layout morphs) wants spring physics so it stays interruptible and retargetable. Color, opacity, and blur want short duration plus easing. Discrete input (a tap, a keypress) animates; continuous input (a drag, a wheel, a slider) follows the pointer 1:1 with no interpolation, then settles with a spring on release. Do not put a fixed-duration tween on a gesture-driven surface.
- **Interruptibility is non-negotiable.** A press, hover-out, or route change mid-animation must retarget smoothly, never queue or block input, and never snap to the end state. That property, not the bounce, is why the reference catalog uses springs.
- **One event, one feedback.** Feedback lives on the object that changed. Do not stack a spinner over a control that already shows progress, re-animate a native control, or confirm routine success with a toast: success is assumed and shown by the changed state; failure is always reported, next to the object, with the cause. Prefer undo to a confirmation dialog; a dialog is for uncommon and irreversible loss only, its buttons name the outcome ("Delete", "Keep editing"), and neither Cancel nor the destructive action takes the default (Enter) role. Send the request when the input lands, not when the acknowledging animation ends.
- **Motion never regresses input latency or stream rendering.** Measure against [craft-floor.md](../perfection/craft-floor.md) when in doubt; a virtualized list's measurement contract beats a pretty reveal.
- **Library choice is a project decision, not a default.** The reference catalog assumes one motion engine plus utility CSS. If the project already has a motion stack, adapt the mechanism to it. If it has none: CSS transitions and the Web Animations API cover micro-interactions; adding a library is justified by shared-layout or spring-physics needs and gets recorded (with bundle cost) in `DESIGN.md`. Check `package.json` before importing anything.

## 5. DESIGN.md integration

[design-system-architecture.md](design-system-architecture.md) defines a Motion & Interaction section in every `DESIGN.md`. This file feeds it:

- Extracted spring configs, durations, and easings land there as named tokens before components use them.
- Each shipped interaction traces to a catalog pattern (or a recorded novel mechanism) plus its reduced-motion behavior.
- New reusable interaction patterns (used twice or more) get documented back into `DESIGN.md` Section 5 with their states, like any other primitive.

## 6. Verification

Interaction work is verified through the `visual-qa` skill with motion actually driven and inspected: hover, press, open/close, swipe, and theme transitions exercised on the rendered surface, an interruption pass (retarget mid-animation, dismiss mid-open) proving nothing snaps or blocks, and a reduced-motion pass (emulate `prefers-reduced-motion: reduce`) proving the fallback exists. Timing-sensitive changes record a short screen capture, not just stills. State the keyboard and focus result against [wcag-gate.md](../perfection/wcag-gate.md).
