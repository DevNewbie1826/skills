---
type: Layout Pattern
name: ram-grid
title: ram-grid
category: Grid / Repetition
description: Repeat items into as many useful columns as space allows.
primary_spatial_problem: Repeat items into as many useful columns as space allows.
secondary_spatial_problems: none
layout_axis: both
content_shape: mixed
responsiveness: fluid
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://web.dev/articles/one-line-layouts
---

# ram-grid

## When To Use

Use this pattern when you need to repeat items into as many useful columns as space allows.

## HTML

```html
<section class="ram_grid" aria-label="Photo albums">
    <article>Spring launch album</article>
    <article>Customer meetup album</article>
    <article>Workshop album</article>
</section>
```

## CSS

```css
.ram_grid {
    display: grid;
    gap: 1rem;
    grid-template-columns: repeat(auto-fit, minmax(min(16rem, 100%), 1fr));
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

Use `ram_grid` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Grid / Repetition patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
