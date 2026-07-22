---
type: Layout Pattern
name: grid-wrapper
title: grid-wrapper
category: Grid / Repetition
description: Center grid tracks while allowing full-width breakout tracks.
primary_spatial_problem: Center grid tracks while allowing full-width breakout tracks.
secondary_spatial_problems: none
layout_axis: inline
content_shape: mixed
responsiveness: fluid
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://developer.mozilla.org/en-US/docs/Web/CSS/How_to/Layout_cookbook
---

# grid-wrapper

## When To Use

Use this pattern when you need to center grid tracks while allowing full-width breakout tracks.

## HTML

```html
<section class="grid_wrapper" aria-label="Marketing page">
    <main class="grid_wrapper_main">Centered campaign copy</main>
</section>
```

## CSS

```css
.grid_wrapper {
    display: grid;
    grid-template-columns: 1fr minmax(0, 64rem) 1fr;
}

.grid_wrapper_main {
    grid-column: 2;
}
```

## Core Properties

- `display`, `grid-template-columns`, `grid-column` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `display`, `grid-template-columns`, `grid-column` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- fluid responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `grid_wrapper` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Grid / Repetition patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
