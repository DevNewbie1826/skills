---
type: Layout Pattern
name: line-up
title: line-up
category: Stacking
description: Keep card footer actions aligned at the bottom.
primary_spatial_problem: Keep card footer actions aligned at the bottom.
secondary_spatial_problems: none
layout_axis: block
content_shape: mixed
responsiveness: fluid
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://web.dev/articles/one-line-layouts
---

# line-up

## When To Use

Use this pattern when you need to keep card footer actions aligned at the bottom.

## HTML

```html
<article class="line_up" aria-labelledby="line-up-title">
    <section class="line_up_body"><h2 id="line-up-title">Implementation proposal</h2><p>Variable-length summary copy sits above the aligned action row.</p></section>
    <footer class="line_up_footer"><button>Review proposal</button></footer>
</article>
```

## CSS

```css
.line_up {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.line_up_body {
    min-block-size: 0;
}

.line_up_footer {
    margin-block-start: auto;
}
```

## Core Properties

- `display`, `flex-direction`, `gap`, `min-block-size`, `margin-block-start` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `display`, `flex-direction`, `gap`, `min-block-size`, `margin-block-start` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- fluid responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `line_up` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Stacking patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
