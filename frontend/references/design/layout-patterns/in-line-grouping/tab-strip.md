---
type: Layout Pattern
name: tab-strip
title: tab-strip
category: In-line grouping
description: Keep peer tabs in one stable row that can wrap.
primary_spatial_problem: Keep peer tabs in one stable row that can wrap.
secondary_spatial_problems: none
layout_axis: inline
content_shape: mixed
responsiveness: wrap
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://design-system.service.gov.uk/styles/layout/
---

# tab-strip

## When To Use

Use this pattern when you need to keep peer tabs in one stable row that can wrap.

## HTML

```html
<nav class="tab_strip" aria-label="Report views">
    <a href="#">Summary</a>
    <a href="#">Cohorts</a>
    <a href="#">Exports</a>
</nav>
```

## CSS

```css
.tab_strip {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
}
```

## Core Properties

- `display`, `flex-wrap`, `gap` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `display`, `flex-wrap`, `gap` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- wrap responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `tab_strip` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [In-line grouping patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
