---
type: Layout Pattern
name: holy-grail
title: holy-grail
category: Viewport / Shell
description: Place header, footer, sidebars, and main content in a resilient shell.
primary_spatial_problem: Place header, footer, sidebars, and main content in a resilient shell.
secondary_spatial_problems: none
layout_axis: both
content_shape: mixed
responsiveness: breakpointed
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://web.dev/articles/one-line-layouts
---

# holy-grail

## When To Use

Use this pattern when you need to place header, footer, sidebars, and main content in a resilient shell.

## HTML

```html
<section class="holy_grail" aria-label="News page">
    <header class="holy_grail_header">Daily briefing</header>
    <aside class="holy_grail_left">Topic navigation</aside>
    <main class="holy_grail_main">Lead story and article stream</main>
    <aside class="holy_grail_right">Market snapshot</aside>
    <footer class="holy_grail_footer">Edition links</footer>
</section>
```

## CSS

```css
.holy_grail {
    display: grid;
    gap: 1rem;
    grid-template: "header header header" auto "left main right" 1fr "footer footer footer" auto / minmax(12rem, auto) 1fr minmax(12rem, auto);
    min-block-size: 100dvh;
}

.holy_grail_header {
    grid-area: header;
}

.holy_grail_left {
    grid-area: left;
}

.holy_grail_main {
    grid-area: main;
    min-inline-size: 0;
}

.holy_grail_right {
    grid-area: right;
}

.holy_grail_footer {
    grid-area: footer;
}
```

## Core Properties

- `display`, `gap`, `grid-template`, `min-block-size`, `grid-area`, `min-inline-size` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `display`, `gap`, `grid-template`, `min-block-size`, `grid-area`, `min-inline-size` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- breakpointed responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `holy_grail` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Viewport / Shell patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
