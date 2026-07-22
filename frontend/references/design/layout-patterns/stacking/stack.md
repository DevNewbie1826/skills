---
type: Layout Pattern
name: stack
title: stack
category: Stacking
description: Create consistent vertical rhythm between direct children.
primary_spatial_problem: Create consistent vertical rhythm between direct children.
secondary_spatial_problems: none
layout_axis: block
content_shape: mixed
responsiveness: fluid
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://every-layout.dev/layouts/stack/
---

# stack

## When To Use

Use this pattern when you need to create consistent vertical rhythm between direct children.

## HTML

```html
<section class="stack" aria-labelledby="stack-heading">
    <h2 id="stack-heading">Release checklist</h2>
    <p>Review copy, verify forms, and publish the notes in order.</p>
    <button>Start review</button>
</section>
```

## CSS

```css
.stack {
    display: grid;
    gap: 1rem;
}
```

## Core Properties

- `display`, `gap` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `display`, `gap` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- fluid responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `stack` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Stacking patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
