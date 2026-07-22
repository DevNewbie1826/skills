---
type: Catalog
title: Layout Pattern Catalog
description: Catalog of layout patterns.
---

# Layout Pattern Catalog

Primary role: pattern lookup.

## Shared Pattern Policy

Apply this policy to every pattern; each pattern document's `Scroll Ownership` section declares whether it owns a named scroll container.

### Accessibility And Source Order

- Semantic role expectation: Preserve the HTML sample's landmark, list, navigation, form, figure, or article roles; layout classes must not replace semantic elements.
- DOM order expectation: Keep semantic elements, DOM order, reading order, and focus order independent from the visual placement created by the layout classes.
- Focus risk: Any interactive descendants follow DOM order; do not use a pattern to create a visual order that keyboard focus cannot follow.
- Scroll expectation: Do not add an internal scroll container when the pattern declares none. When a pattern owns a named scroll container, name it in the consuming layout so context, controls, and return points remain apparent.
- Cognitive risk: Preserve ordinary reading flow when semantic order is correct. Reflow can change spatial adjacency, so labels, controls, and related content must remain adjacent in DOM order; named scroll containers can hide context, controls, or return points if they are not named in the consuming layout.

### Browser And Fallback Notes

The CSS uses modern grid, flex, intrinsic sizing, logical properties, or positioning. If a target browser cannot support a property, fall back to ordinary block flow before adding decorative or script-driven layout behavior.

### Anti-patterns

- Do not add color, border, shadow, typography, or animation rules to reusable pattern CSS.
- Do not use a pattern to repair unclear HTML structure; make the DOM roles legible first.

## Planning Layer

- [Layout Planning Guide](planning-guide.md) - Pre-design entry point for choosing and composing patterns.
- [Decision Tree](guides/decision-tree.md) - Question-driven route from screen constraints to pattern categories.
- [Layout Brief](guides/layout-brief.md) - Questions to answer before selecting a pattern stack.
- [Layout Recipes](../layout-recipes/index.md) - Screen-level compositions built from reusable patterns.

## Patterns

- [stack](stacking/stack.md) - Stacking: Create consistent vertical rhythm between direct children.
- [box](containment/box.md) - Containment: Wrap content with predictable internal spacing.
- [center](centering/center.md) - Centering: Center a block while respecting a maximum measure.
- [cluster](in-line-grouping/cluster.md) - In-line grouping: Keep related items together while allowing wrapping.
- [content-limiter](containment/content-limiter.md) - Containment: Keep prose width readable inside fluid containers.
- [super-center](centering/super-center.md) - Centering: Center one region along both axes.
- [icon-frame](media-fit/icon-frame.md) - Media / Fit: Keep an icon aligned inside a fixed square slot.
- [frame](media-fit/frame.md) - Media / Fit: Preserve media aspect ratio in a responsive slot.
- [cover](viewport-shell/cover.md) - Viewport / Shell: Keep a central region balanced between optional header and footer.
- [sidebar](split-sidebar/sidebar.md) - Split / Sidebar: Let a narrow sidebar and wider content wrap when space is tight.
- [switcher](split-sidebar/switcher.md) - Split / Sidebar: Switch equal regions from row to stack without a viewport breakpoint.
- [media-object](split-sidebar/media-object.md) - Split / Sidebar: Align media and descriptive content as a stable pair.
- [split-nav](in-line-grouping/split-nav.md) - In-line grouping: Separate primary and secondary nav actions in one row.
- [holy-grail](viewport-shell/holy-grail.md) - Viewport / Shell: Place header, footer, sidebars, and main content in a resilient shell.
- [sticky-footer](viewport-shell/sticky-footer.md) - Viewport / Shell: Keep footer at the bottom when content is short.
- [sticky-header](viewport-shell/sticky-header.md) - Viewport / Shell: Keep a header visible above a scrolling content region.
- [scroll-body-shell](viewport-shell/scroll-body-shell.md) - Viewport / Shell: Keep shell regions fixed while only the body scrolls.
- [fixed-sidenav-shell](viewport-shell/fixed-sidenav-shell.md) - Viewport / Shell: Keep side navigation stable while main content scrolls.
- [sticky-aside](split-sidebar/sticky-aside.md) - Split / Sidebar: Keep related aside content visible during long reads.
- [ram-grid](grid-repetition/ram-grid.md) - Grid / Repetition: Repeat items into as many useful columns as space allows.
- [card-grid](grid-repetition/card-grid.md) - Grid / Repetition: Align repeating cards in rows and columns.
- [twelve-span-grid](grid-repetition/twelve-span-grid.md) - Grid / Repetition: Provide a twelve-column placement scaffold.
- [page-grid](grid-repetition/page-grid.md) - Grid / Repetition: Align page content to margins, gutters, and a central track.
- [grid-wrapper](grid-repetition/grid-wrapper.md) - Grid / Repetition: Center grid tracks while allowing full-width breakout tracks.
- [columns](grid-repetition/columns.md) - Grid / Repetition: Flow long content into balanced text columns.
- [deconstructed-pancake](in-line-grouping/deconstructed-pancake.md) - In-line grouping: Let equal cards stretch in a row and stack naturally when narrow.
- [line-up](stacking/line-up.md) - Stacking: Keep card footer actions aligned at the bottom.
- [clamped-card](containment/clamped-card.md) - Containment: Constrain a card to a readable fluid width.
- [fluid-styles](containment/fluid-styles.md) - Containment: Let a region fill available width without exceeding a readable max.
- [split-screen](split-sidebar/split-screen.md) - Split / Sidebar: Split a viewport or region into two balanced panes.
- [list-detail](split-sidebar/list-detail.md) - Split / Sidebar: Place an explorable list beside its detail region.
- [supporting-pane](split-sidebar/supporting-pane.md) - Split / Sidebar: Keep supplemental information beside a primary task.
- [feed](stacking/feed.md) - Stacking: Stack repeated content items with stable rhythm.
- [breadcrumb](in-line-grouping/breadcrumb.md) - In-line grouping: Lay out hierarchy links compactly with wrapping.
- [pagination](in-line-grouping/pagination.md) - In-line grouping: Lay out page controls as a bounded wrapping row.
- [badge-list](in-line-grouping/badge-list.md) - In-line grouping: Align item labels with trailing counts.
- [step-nav](stacking/step-nav.md) - Stacking: Present sequential steps with consistent vertical rhythm.
- [tab-strip](in-line-grouping/tab-strip.md) - In-line grouping: Keep peer tabs in one stable row that can wrap.
- [reel](in-line-grouping/reel.md) - In-line grouping: Let a row scroll horizontally instead of wrapping.
- [imposter](overlay-exception/imposter.md) - Overlay / Exception: Place an overlay region over a parent without changing document order.
- [panel-layout](viewport-shell/panel-layout.md) - Viewport / Shell: Create predictable main and utility panels.
- [overlay-stack](overlay-exception/overlay-stack.md) - Overlay / Exception: Stack several regions into the same grid cell.
- [wrap-row](in-line-grouping/wrap-row.md) - In-line grouping: Wrap controls into rows with stable gaps.
- [dense-grid](grid-repetition/dense-grid.md) - Grid / Repetition: Fill a compact grid with repeated small items.
- [masonry-approx](grid-repetition/masonry-approx.md) - Grid / Repetition: Approximate staggered content with columns when exact row alignment is not needed.
- [main-with-rail](split-sidebar/main-with-rail.md) - Split / Sidebar: Keep primary content dominant with a narrow secondary rail.
