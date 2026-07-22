---
type: Layout Pattern
name: box
title: box
category: Containment
description: Wrap content with predictable internal spacing.
primary_spatial_problem: Wrap content with predictable internal spacing.
secondary_spatial_problems: none
layout_axis: block
content_shape: mixed
responsiveness: fixed
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://every-layout.dev/layouts/
---

# box

## When To Use

Use this pattern when you need to wrap content with predictable internal spacing.

## HTML

```html
<aside class="box" aria-labelledby="box-heading">
    <h2 id="box-heading">Support window</h2>
    <p>Responses resume Monday at 09:00.</p>
</aside>
```

## CSS

```css
.box {
    box-sizing: border-box;
    display: block;
    padding: 1rem;
}
```

## Core Properties

- `box-sizing`, `display`, `padding` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `box-sizing`, `display`, `padding` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- fixed responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `box` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Containment patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
