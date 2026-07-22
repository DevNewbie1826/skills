---
type: Layout Pattern
name: supporting-pane
title: supporting-pane
category: Split / Sidebar
description: Keep supplemental information beside a primary task.
primary_spatial_problem: Keep supplemental information beside a primary task.
secondary_spatial_problems: none
layout_axis: inline
content_shape: mixed
responsiveness: reflow
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://m3.material.io/foundations/adaptive-design/canonical-layouts
---

# supporting-pane

## When To Use

Use this pattern when you need to keep supplemental information beside a primary task.

## HTML

```html
<section class="supporting_pane" aria-label="Invoice editor">
    <main class="supporting_pane_main">Invoice line-item editor</main>
    <aside class="supporting_pane_summary">Payment summary</aside>
</section>
```

## CSS

```css
.supporting_pane {
    display: grid;
    gap: 1rem;
    grid-template-columns: repeat(auto-fit, minmax(min(20rem, 100%), 1fr));
}

.supporting_pane_main {
    min-inline-size: 0;
}

.supporting_pane_summary {
    min-inline-size: 0;
}
```

## Core Properties

- `display`, `gap`, `grid-template-columns`, `min-inline-size` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `display`, `gap`, `grid-template-columns`, `min-inline-size` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- reflow responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `supporting_pane` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Split / Sidebar patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
