---
type: Layout Pattern
name: fixed-sidenav-shell
title: fixed-sidenav-shell
category: Viewport / Shell
description: Keep side navigation stable while main content scrolls.
primary_spatial_problem: Keep side navigation stable while main content scrolls.
secondary_spatial_problems: none
layout_axis: both
content_shape: mixed
responsiveness: fluid
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: Pattern owns the named scroll container.
source_lineage: https://carbondesignsystem.com/elements/2x-grid/overview/
---

# fixed-sidenav-shell

## When To Use

Use this pattern when you need to keep side navigation stable while main content scrolls.

## HTML

```html
<section class="fixed_sidenav_shell" aria-label="Settings">
    <nav class="fixed_sidenav_shell_list"><a href="#">Profile</a><a href="#">Billing</a></nav>
    <main class="fixed_sidenav_shell_main">Editable settings form scrolls independently</main>
</section>
```

## CSS

```css
.fixed_sidenav_shell {
    display: grid;
    grid-template-columns: 16rem minmax(0, 1fr);
    grid-template-rows: minmax(0, 1fr);
    max-block-size: 100dvh;
}

.fixed_sidenav_shell_list {
    min-block-size: 0;
}

.fixed_sidenav_shell_main {
    min-block-size: 0;
    overflow: auto;
}
```

## Core Properties

- `display`, `grid-template-columns`, `grid-template-rows`, `max-block-size`, `min-block-size`, `overflow` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `display`, `grid-template-columns`, `grid-template-rows`, `max-block-size`, `min-block-size`, `overflow` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- fluid responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

Pattern owns the named scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `fixed_sidenav_shell` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Viewport / Shell patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
