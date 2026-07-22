---
type: Layout Pattern
name: media-object
title: media-object
category: Split / Sidebar
description: Align media and descriptive content as a stable pair.
primary_spatial_problem: Align media and descriptive content as a stable pair.
secondary_spatial_problems: none
layout_axis: inline
content_shape: mixed
responsiveness: reflow
constraints: Uses only local class hooks and explicit layout constraints.
scroll_ownership: No internal scroll container.
source_lineage: https://developer.mozilla.org/en-US/docs/Web/CSS/How_to/Layout_cookbook
---

# media-object

## When To Use

Use this pattern when you need to align media and descriptive content as a stable pair.

## HTML

```html
<article class="media_object">
    <figure class="media_object_media"><img alt="Speaker portrait"></figure>
    <div class="media_object_content">
        <h2>Design systems briefing</h2>
        <p>Speaker details align beside the portrait without squeezing the text.</p>
    </div>
</article>
```

## CSS

```css
.media_object {
    align-items: start;
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
}

.media_object_media {
    flex-basis: 6rem;
    flex-grow: 0;
}

.media_object_content {
    flex-basis: min(20rem, 100%);
    flex-grow: 1;
    min-inline-size: 0;
}
```

## Core Properties

- `align-items`, `display`, `flex-wrap`, `gap`, `flex-basis`, `flex-grow`, `min-inline-size` define the spatial behavior for this pattern.

## Properties That Break The Layout If Removed

- Removing `align-items`, `display`, `flex-wrap`, `gap`, `flex-basis`, `flex-grow`, `min-inline-size` changes the pattern from its documented layout responsibility back toward ordinary flow or an unsafe fixed arrangement.

## Constraints And Change Points

- reflow responsiveness is part of the contract; change sizing values only when the new minimum, maximum, or wrap point is documented with the pattern.
- Keep the HTML class hooks and CSS selectors in one-to-one agreement.

## Scroll Ownership

No internal scroll container.

Shared policy: see [CATALOG.md#shared-pattern-policy](../CATALOG.md#shared-pattern-policy).

## Composition Notes

Use `media_object` as the stable pattern root and compose additional layout behavior outside that root unless the child class is part of the documented relationship.

## IA Navigation

Parent: [Split / Sidebar patterns](index.md) in [Pattern Categories](../index.md).
Next: [Layout Recipes](../../layout-recipes/index.md) for screen-level composition, or return to the [Layout Pattern Catalog](../CATALOG.md) when choosing another primitive.
