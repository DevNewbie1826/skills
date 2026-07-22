---
type: Layout Pattern
name: sticky-footer
title: sticky-footer
category: Viewport / Shell
description: Keep footer at the bottom when content is short.
primary_spatial_problem: Keep footer at the bottom when content is short.
secondary_spatial_problems: none
layout_axis: block
content_shape: mixed
responsiveness: fluid
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://developer.mozilla.org/en-US/docs/Web/CSS/How_to/Layout_cookbook
---

# sticky-footer

## When To Use

Use this pattern when you need to keep footer at the bottom when content is short.

## HTML

```html
<section class="sticky_footer" aria-label="Account setup">
    <header>Account setup</header>
    <main class="sticky_footer_main">Profile fields and preferences</main>
    <footer><button>Save profile</button></footer>
</section>
```

## CSS

```css
.sticky_footer {
    display: grid;
    grid-template-rows: auto 1fr auto;
    min-block-size: 100dvh;
}

.sticky_footer_main {
    min-block-size: 0;
}
```

## Core Properties

- `display`, `grid-template-rows`, `min-block-size` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `display`, `grid-template-rows`, `min-block-size` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- fluid responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `sticky_footer` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Viewport / Shell patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
