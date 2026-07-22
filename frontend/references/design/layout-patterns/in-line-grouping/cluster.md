---
type: Layout Pattern
name: cluster
title: cluster
category: In-line grouping
description: Keep related items together while allowing wrapping.
primary_spatial_problem: Keep related items together while allowing wrapping.
secondary_spatial_problems: none
layout_axis: inline
content_shape: mixed
responsiveness: wrap
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://every-layout.dev/layouts/
---

# cluster

## When To Use

Use this pattern when you need to keep related items together while allowing wrapping.

## HTML

```html
<nav class="cluster" aria-label="Project actions">
    <a href="#">Backlog</a>
    <a href="#">Milestones</a>
    <a href="#">Roadmap</a>
</nav>
```

## CSS

```css
.cluster {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    justify-content: flex-start;
}
```

## Core Properties

- `display`, `flex-wrap`, `gap`, `justify-content` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `display`, `flex-wrap`, `gap`, `justify-content` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- wrap responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `cluster` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [In-line grouping patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
