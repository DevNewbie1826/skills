---
type: Layout Pattern
name: page-grid
title: page-grid
category: Grid / Repetition
description: Align page content to margins, gutters, and a central track.
primary_spatial_problem: Align page content to margins, gutters, and a central track.
secondary_spatial_problems: none
layout_axis: inline
content_shape: mixed
responsiveness: fluid
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://carbondesignsystem.com/elements/2x-grid/overview/
---

# page-grid

## When To Use

Use this pattern when you need to align page content to margins, gutters, and a central track.

## HTML

```html
<section class="page_grid" aria-label="Article page">
    <main class="page_grid_content">Centered article track with fluid outer gutters</main>
</section>
```

## CSS

```css
.page_grid {
    display: grid;
    gap: 1rem;
    grid-template-columns: minmax(1rem, 1fr) minmax(0, 72rem) minmax(1rem, 1fr);
}

.page_grid_content {
    grid-column: 2;
}
```

## Core Properties

- `display`, `gap`, `grid-template-columns`, `grid-column` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `display`, `gap`, `grid-template-columns`, `grid-column` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- fluid responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `page_grid` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Grid / Repetition patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
