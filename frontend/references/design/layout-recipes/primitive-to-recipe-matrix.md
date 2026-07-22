---
type: Planning Guide
title: Primitive To Recipe Matrix
description: Matrix that explains which layout primitives each screen recipe uses, why the slot exists, and what risk follows from substitution.
---

# Primitive To Recipe Matrix

Use this matrix before selecting a recipe or generating a visual reference. It shows which primitives are part of each recipe, which slots are structural, and which slots can be replaced when the content model asks for a different spatial behavior.

Legend:

- `E` = essential: removing or replacing this primitive changes the recipe's spatial model.
- `H` = helper: supports rhythm, grouping, or local readability without defining the screen type by itself.
- `S` = substitutable: useful default, but another primitive may fit the same recipe slot when content constraints differ.
- `-` = not part of the recommended recipe stack.

## Recipe Pattern Matrix

| Recipe | `stack` | `box` | `center` | `cluster` | `content-limiter` | `super-center` | `icon-frame` | `frame` | `cover` | `sidebar` | `switcher` | `media-object` | `split-nav` | `holy-grail` | `sticky-footer` | `sticky-header` | `scroll-body-shell` | `fixed-sidenav-shell` | `sticky-aside` | `ram-grid` | `card-grid` | `twelve-span-grid` | `page-grid` | `grid-wrapper` | `columns` | `deconstructed-pancake` | `line-up` | `clamped-card` | `fluid-styles` | `split-screen` | `list-detail` | `supporting-pane` | `feed` | `breadcrumb` | `pagination` | `badge-list` | `step-nav` | `tab-strip` | `reel` | `imposter` | `panel-layout` | `overlay-stack` | `wrap-row` | `dense-grid` | `masonry-approx` | `main-with-rail` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [Homepage](homepage.md) | H | - | - | H | E | - | - | S | E | - | - | - | - | - | - | - | - | - | - | S | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| [SaaS settings](saas-settings.md) | H | - | - | - | E | - | - | - | - | - | - | - | - | - | - | - | - | E | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| [Dashboard](dashboard.md) | - | - | - | H | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | E | - | E | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| [Article page](article-page.md) | H | - | - | - | E | - | - | - | - | - | - | - | - | - | - | - | - | - | S | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| [List detail](list-detail.md) | H | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | H | - | - | - | - | - | - | - | - | - | - | - | - | - | E | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| [Form flow](form-flow.md) | E | - | - | H | E | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| [Command surface](command-surface.md) | - | - | - | - | - | - | - | - | - | - | - | - | H | - | - | - | E | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | E | - | - | - |

## Slot Classification Table

| Recipe | Pattern stack | Essential slots | Helper slots | Substitutable slots | Source lineage and semantic risk |
| --- | --- | --- | --- | --- | --- |
| [Homepage](homepage.md) | `cover`, `content-limiter`, `stack`, `cluster`, `ram-grid`, `frame` | `cover`, `content-limiter` | `stack`, `cluster` | `ram-grid`, `frame` | Local webpage synthesis from homepage section jobs, with Every Layout influence for cover/stack/cluster and MDN grid/media constraints. Risk: replacing `cover` or `content-limiter` weakens the first-viewport hook or readable explanation path; replacing `ram-grid`/`frame` is acceptable when proof or media content has a different shape. |
| [SaaS settings](saas-settings.md) | `fixed-sidenav-shell`, `content-limiter`, `stack` | `fixed-sidenav-shell`, `content-limiter` | `stack` | - | Local settings synthesis, with Material-style settings navigation and MDN sticky/overflow mechanics. Risk: replacing the shell changes scroll ownership and wayfinding; replacing `content-limiter` makes form-like settings harder to scan. |
| [Dashboard](dashboard.md) | `page-grid`, `card-grid`, `cluster` | `page-grid`, `card-grid` | `cluster` | - | Material dashboard layout and MDN grid lineage. Risk: replacing `page-grid` or `card-grid` removes comparable panel alignment; `cluster` can be adjusted only when action groups still wrap safely. |
| [Article page](article-page.md) | `content-limiter`, `sticky-aside`, `stack` | `content-limiter` | `stack` | `sticky-aside` | Every Layout sidebar/stack influence and MDN sticky positioning. Risk: replacing `content-limiter` harms readable measure; replacing `sticky-aside` is acceptable when supplemental content must remain in normal reading order. |
| [List detail](list-detail.md) | `list-detail`, `scroll-body-shell`, `stack` | `list-detail` | `scroll-body-shell`, `stack` | - | Local split-view synthesis, with Material master-detail patterns and MDN overflow mechanics. Risk: replacing `list-detail` changes the browse-and-inspect contract; shell behavior must preserve clear scroll ownership. |
| [Form flow](form-flow.md) | `content-limiter`, `stack`, `cluster` | `content-limiter`, `stack` | `cluster` | - | GOV.UK-style form sequencing with Every Layout stack/cluster influence. Risk: replacing `content-limiter` or `stack` breaks the single-column completion path; action grouping can vary only if labels and errors remain adjacent. |
| [Command surface](command-surface.md) | `scroll-body-shell`, `split-nav`, `wrap-row` | `scroll-body-shell`, `wrap-row` | `split-nav` | - | Local command-surface synthesis, with MDN overflow/flex wrapping mechanics. Risk: replacing `scroll-body-shell` destabilizes command/content regions; replacing `wrap-row` can create overflow or hidden controls. |

## Lineage And Risk Notes

### Homepage

The homepage recipe is local synthesis: it maps raw webpage content into hook, explanation, proof, comparison, conversion, and navigation jobs before visual styling. `cover` and `content-limiter` are essential because they protect first-viewport framing and readable copy. `ram-grid` and `frame` are substitutable when repeated proof or media should use `card-grid`, `columns`, or no media slot.

### SaaS settings

The SaaS settings recipe combines fixed navigation with a constrained settings column. `fixed-sidenav-shell` and `content-limiter` are essential because they define stable wayfinding and readable edit sections. The main semantic risk is accidental independent scrolling inside settings groups, which can separate labels, help text, errors, and controls.

### Dashboard

The dashboard recipe comes from page-level grid alignment and repeated panel comparison. `page-grid` and `card-grid` are essential because users scan across comparable cards and panels. `cluster` is a helper for filters and actions; it can be replaced with `wrap-row` when command density grows.

### Article page

The article recipe prioritizes reading measure before supplemental layout. `content-limiter` is essential; `sticky-aside` is substitutable because some supporting content should remain inline for source-order or narrow-screen reasons. The main risk is letting the aside become a second reading path that competes with the article.

### List detail

The list-detail recipe is a task model, not just a split screen. `list-detail` is essential because it defines peer list and detail regions with a selected item relationship. `scroll-body-shell` is a helper when the viewport owns a stable shell, but the recipe still has to name whether the list, detail, or page owns scrolling.

### Form flow

The form flow recipe is a sequential completion path. `content-limiter` and `stack` are essential because they keep groups readable and preserve vertical task progression. `cluster` is a helper for actions that need to wrap before overflow.

### Command surface

The command surface recipe is local synthesis for tool-heavy shells. `scroll-body-shell` is essential because command regions should remain stable while content changes. `wrap-row` is essential because controls must remain reachable under long labels and narrow widths; `split-nav` is a helper for separating command groups.

## Substitution Rules

- Substitute `ram-grid` with `card-grid`, `columns`, or `masonry-approx` only after naming the repeated content shape and scan behavior.
- Substitute `sticky-aside` with normal inline `stack` content when supporting material must be read in sequence.
- Substitute `cluster` with `wrap-row` when controls have longer labels or stronger overflow risk.
- Do not substitute `content-limiter` out of reading, form, or homepage explanation sections unless another primitive preserves readable measure.
- Do not substitute `scroll-body-shell`, `fixed-sidenav-shell`, or `list-detail` without renaming scroll ownership and focus-return behavior.

## IA Navigation

Parent: [Layout Recipes](index.md).
Next: [Layout Pattern Catalog](../layout-patterns/CATALOG.md) when replacing a primitive.
