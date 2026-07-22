---
type: Layout Pattern
name: feed
title: feed
category: Stacking
description: Stack repeated content items with stable rhythm.
primary_spatial_problem: Stack repeated content items with stable rhythm.
secondary_spatial_problems: none
layout_axis: block
content_shape: mixed
responsiveness: fluid
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://m3.material.io/foundations/adaptive-design/canonical-layouts
---

# feed

## When To Use

Use this pattern when you need to stack repeated content items with stable rhythm.

## HTML

```html
<section class="feed" aria-label="Activity feed">
    <article>Build completed</article>
    <article>Review requested</article>
    <article>Deployment approved</article>
</section>
```

## CSS

```css
.feed {
    display: grid;
    gap: 1rem;
    grid-auto-rows: minmax(min-content, auto);
}
```

## Core Properties

- `display`, `gap`, `grid-auto-rows` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `display`, `gap`, `grid-auto-rows` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- fluid responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `feed` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Stacking patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
