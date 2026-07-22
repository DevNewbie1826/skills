---
type: Layout Pattern
name: twelve-span-grid
title: twelve-span-grid
category: Grid / Repetition
description: Provide a twelve-column placement scaffold.
primary_spatial_problem: Provide a twelve-column placement scaffold.
secondary_spatial_problems: none
layout_axis: both
content_shape: mixed
responsiveness: fluid
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://web.dev/articles/one-line-layouts
---

# twelve-span-grid

## When To Use

Use this pattern when you need to provide a twelve-column placement scaffold.

## HTML

```html
<section class="twelve_span_grid" aria-label="Dashboard modules">
    <article class="twelve_span_grid_item">Revenue module</article>
    <article class="twelve_span_grid_item">Retention module</article>
    <article class="twelve_span_grid_item">Pipeline module</article>
</section>
```

## CSS

```css
.twelve_span_grid {
    display: grid;
    gap: 1rem;
    grid-template-columns: repeat(12, minmax(0, 1fr));
}

.twelve_span_grid_item {
    grid-column: span 4;
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

Use `twelve_span_grid` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Grid / Repetition patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
