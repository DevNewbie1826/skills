---
type: Layout Pattern
name: card-grid
title: card-grid
category: Grid / Repetition
description: Align repeating cards in rows and columns.
primary_spatial_problem: Align repeating cards in rows and columns.
secondary_spatial_problems: none
layout_axis: both
content_shape: mixed
responsiveness: fluid
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://developer.mozilla.org/en-US/docs/Web/CSS/How_to/Layout_cookbook
---

# card-grid

## When To Use

Use this pattern when you need to align repeating cards in rows and columns.

## HTML

```html
<section class="card_grid" aria-label="Project cards">
    <article>Design audit</article>
    <article>Analytics migration</article>
    <article>Onboarding rewrite</article>
</section>
```

## CSS

```css
.card_grid {
    display: grid;
    gap: 1rem;
    grid-template-columns: repeat(auto-fit, minmax(min(18rem, 100%), 1fr));
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

Use `card_grid` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Grid / Repetition patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
