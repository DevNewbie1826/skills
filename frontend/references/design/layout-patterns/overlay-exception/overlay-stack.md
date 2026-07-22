---
type: Layout Pattern
name: overlay-stack
title: overlay-stack
category: Overlay / Exception
description: Stack several regions into the same grid cell.
primary_spatial_problem: Stack several regions into the same grid cell.
secondary_spatial_problems: none
layout_axis: both
content_shape: mixed
responsiveness: fluid
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://web.dev/articles/one-line-layouts
---

# overlay-stack

## When To Use

Use this pattern when you need to stack several regions into the same grid cell.

## HTML

```html
<section class="overlay_stack" aria-label="Map with controls">
    <figure class="overlay_stack_item">Transit map</figure>
    <form class="overlay_stack_item">Route search controls</form>
</section>
```

## CSS

```css
.overlay_stack {
    display: grid;
}

.overlay_stack_item {
    grid-area: 1 / 1;
}
```

## Core Properties

- `display`, `grid-area` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `display`, `grid-area` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- fluid responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `overlay_stack` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Overlay / Exception patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
