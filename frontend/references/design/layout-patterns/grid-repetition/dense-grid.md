---
type: Layout Pattern
name: dense-grid
title: dense-grid
category: Grid / Repetition
description: Fill a compact grid with repeated small items.
primary_spatial_problem: Fill a compact grid with repeated small items.
secondary_spatial_problems: none
layout_axis: both
content_shape: mixed
responsiveness: fluid
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Grids
---

# dense-grid

## When To Use

Use this pattern when you need to fill a compact grid with repeated small items.

## HTML

```html
<section class="dense_grid" aria-label="Keyboard shortcuts">
    <kbd>Cmd K</kbd>
    <kbd>Cmd Shift P</kbd>
    <kbd>Esc</kbd>
</section>
```

## CSS

```css
.dense_grid {
    display: grid;
    gap: 0.5rem;
    grid-template-columns: repeat(auto-fill, minmax(8rem, 1fr));
}
```

## Core Properties

- `display`, `gap`, `grid-template-columns` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `display`, `gap`, `grid-template-columns` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- fluid responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `dense_grid` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Grid / Repetition patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
