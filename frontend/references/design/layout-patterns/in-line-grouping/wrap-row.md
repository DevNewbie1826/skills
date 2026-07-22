---
type: Layout Pattern
name: wrap-row
title: wrap-row
category: In-line grouping
description: Wrap controls into rows with stable gaps.
primary_spatial_problem: Wrap controls into rows with stable gaps.
secondary_spatial_problems: none
layout_axis: inline
content_shape: mixed
responsiveness: wrap
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://developer.mozilla.org/en-US/docs/Web/CSS/How_to/Layout_cookbook
---

# wrap-row

## When To Use

Use this pattern when you need to wrap controls into rows with stable gaps.

## HTML

```html
<form class="wrap_row" aria-label="Filter tickets">
    <label>Status <select></select></label>
    <label>Owner <select></select></label>
    <button>Apply filters</button>
</form>
```

## CSS

```css
.wrap_row {
    align-items: center;
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
}
```

## Core Properties

- `align-items`, `display`, `flex-wrap`, `gap` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `align-items`, `display`, `flex-wrap`, `gap` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- wrap responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `wrap_row` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [In-line grouping patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
