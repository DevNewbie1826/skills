---
type: Layout Pattern
name: step-nav
title: step-nav
category: Stacking
description: Present sequential steps with consistent vertical rhythm.
primary_spatial_problem: Present sequential steps with consistent vertical rhythm.
secondary_spatial_problems: none
layout_axis: block
content_shape: mixed
responsiveness: fluid
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://design-system.service.gov.uk/styles/layout/
---

# step-nav

## When To Use

Use this pattern when you need to present sequential steps with consistent vertical rhythm.

## HTML

```html
<nav class="step_nav" aria-label="Checkout steps">
    <a href="#">Shipping address</a>
    <a href="#">Payment method</a>
    <a href="#">Order review</a>
</nav>
```

## CSS

```css
.step_nav {
    display: grid;
    gap: 0.75rem;
    margin-block: 1rem;
}
```

## Core Properties

- `display`, `gap`, `margin-block` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `display`, `gap`, `margin-block` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- fluid responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `step_nav` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Stacking patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
