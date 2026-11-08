# Semantic HTML body

Read this when you lay out the page body, or SEM, H, IMG, LINK, A11Y, or CONT findings fire.

## Skeleton

```html
<body>
  <header>
    <a href="https://example.com/">Example Guides</a>
    <nav aria-label="Main">
      <a href="https://example.com/guides/">Guides</a>
    </nav>
  </header>
  <main>
    <article>
      <h1>Passport renewal time in 2026</h1>
      <p>By <a href="https://example.com/about/jane-park" rel="author">Jane Park</a>,
        updated <time datetime="2026-10-14">October 14, 2026</time></p>
      <p>Routine passport renewal takes about six to eight weeks in 2026 ...</p>
      <section>
        <h2>Steps</h2>
        <figure>
          <img src="https://example.com/img/form.jpg" alt="Renewal form with the photo box marked" width="800" height="533">
          <figcaption>The photo box is where most rejections start.</figcaption>
        </figure>
      </section>
    </article>
  </main>
  <footer>
    <a href="https://example.com/about">About</a> · <a href="https://example.com/contact">Contact</a>
  </footer>
</body>
```

## Landmarks

- Exactly one `<main>` (SEM-01). Put `<header>`, `<footer>`, and an `<article>` around the content (SEM-02) and a `<nav>` for site links (SEM-03).
- Clickable things are `<a>` or `<button>`, never a `div` or `span` with `onclick` (SEM-04).
- `<figure>` gets a `<figcaption>` (SEM-05). `<time>` gets a valid ISO 8601 `datetime` (SEM-06).

## Headings

- Exactly one `<h1>` (H-01), matching the page topic and close to the title.
- Don't skip levels: h2 then h3, never h2 then h4 (H-02).
- Headings carry words: no empty, digits-only, or one- or two-character headings (H-03).

## Images

- Every `<img>` has `alt` (IMG-01). Decorative images use `alt=""`, which passes.
- Alt describes the image in at most 125 code points and isn't a filename like `IMG_2041.jpg` (IMG-02).
- Set `width` and `height` to stop layout shift (IMG-03).
- Don't lazy-load the first image in `<main>`; it's usually above the fold (IMG-04).

## Links and forms

- Anchor text says where the link goes. Avoid "click here", "read more", "more", "여기", "클릭", "더보기", "자세히" (LINK-03).
- No empty or `#` hrefs (LINK-04).
- Every visible input, select, and textarea has a `<label for>`, a wrapping `<label>`, `aria-label`, or `aria-labelledby` (A11Y-01).

## Content inside main

- At least 300 code points of visible text in `<main>` (CONT-01). Thin pages are an error.
- With `--keyword`, keep density between 1% and 3% (CONT-02).
- A paragraph with a number and a unit or percent should link or cite its source in the same paragraph (CONT-03). How to write that text: [writing.md](writing.md).
