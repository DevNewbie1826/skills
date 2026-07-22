---
type: Layout Pattern
name: fluid-styles
title: fluid-styles
category: Containment
description: Let a region fill available width without exceeding a readable max.
primary_spatial_problem: Let a region fill available width without exceeding a readable max.
secondary_spatial_problems: none
layout_axis: inline
content_shape: mixed
responsiveness: fluid
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://carbondesignsystem.com/elements/2x-grid/overview/
---

# fluid-styles

## When To Use

Use this pattern when you need to let a region fill available width without exceeding a readable max.

## HTML

```html
<section class="fluid_styles" aria-labelledby="fluid-title">
    <h2 id="fluid-title">Operations overview</h2>
    <p>The region fills the parent without exceeding the shared page measure.</p>
</section>
```

## CSS

```css
.fluid_styles {
    inline-size: min(100%, 72rem);
    margin-inline: auto;
}
```

## Core Properties

- `inline-size`, `margin-inline` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `inline-size`, `margin-inline` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- fluid responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `fluid_styles` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Containment patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
