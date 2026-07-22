---
type: Layout Pattern
name: center
title: center
category: Centering
description: Center a block while respecting a maximum measure.
primary_spatial_problem: Center a block while respecting a maximum measure.
secondary_spatial_problems: none
layout_axis: inline
content_shape: mixed
responsiveness: fluid
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://every-layout.dev/layouts/
---

# center

## When To Use

Use this pattern when you need to center a block while respecting a maximum measure.

## HTML

```html
<article class="center" aria-labelledby="center-heading">
    <h2 id="center-heading">Editorial policy</h2>
    <p>Long-form guidance stays readable while the page around it remains fluid.</p>
</article>
```

## CSS

```css
.center {
    margin-inline: auto;
    max-inline-size: 64rem;
    padding-inline: 1rem;
}
```

## Core Properties

- `margin-inline`, `max-inline-size`, `padding-inline` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `margin-inline`, `max-inline-size`, `padding-inline` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- fluid responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `center` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Centering patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
