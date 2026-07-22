---
type: Layout Pattern
name: icon-frame
title: icon-frame
category: Media / Fit
description: Keep an icon aligned inside a fixed square slot.
primary_spatial_problem: Keep an icon aligned inside a fixed square slot.
secondary_spatial_problems: none
layout_axis: both
content_shape: mixed
responsiveness: fixed
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://every-layout.dev/layouts/
---

# icon-frame

## When To Use

Use this pattern when you need to keep an icon aligned inside a fixed square slot.

## HTML

```html
<span class="icon_frame" aria-label="Calendar">
    <svg aria-hidden="true" viewBox="0 0 24 24"></svg>
</span>
```

## CSS

```css
.icon_frame {
    block-size: 2.5rem;
    display: grid;
    inline-size: 2.5rem;
    place-items: center;
}
```

## Core Properties

- `block-size`, `display`, `inline-size`, `place-items` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `block-size`, `display`, `inline-size`, `place-items` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- fixed responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `icon_frame` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Media / Fit patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
