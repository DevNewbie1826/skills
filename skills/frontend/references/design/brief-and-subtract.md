# Brief, draft guard, subtract

Read this when building or changing any screen, before the first edit (the brief) and again when the draft first renders (draft guard, subtract, scoped fixes).

## Brief: decide what the screen is for before drawing it

Write this for every screen you build or change, into `DESIGN.md` section 5 beside the screen's components (the `Layout:` line goes under section 4), or into the change description when the project has no `DESIGN.md`. The build follows it; `visual-qa` checks the rendered screen against it.

- **Primary action.** Exactly one. It gets the prominent style; its peers differ by style, never by size.
- **Information priorities 1-3.** In reading order. Priority 1 is the first thing the eye lands on.
- **Left out on purpose.** What a generated version of this screen would add and this one will not: the decorative badge, the stat tile nobody acts on, the subtitle under every heading, the callout that repeats the banner.
- **Required content.** Every input, datum, label, and piece of copy the request, the reference, or the existing screen requires, listed by name. Subtraction is checked against this list; nothing on it may disappear or merge.
- **Data shape to component** (data screens): several things to compare -> table; a ranking -> ordered list; one verdict -> conclusion banner first, evidence under it; many items -> filter plus results grid; one object -> detail view with its primary action. Choose from this before reaching for cards.
- **Layout line** (any layout or structure change, an existing `DESIGN.md` included): one `Layout:` line in the format in [../stylegallery/layout/index.md](../stylegallery/layout/index.md) and [layout-skill.md](layout-skill.md), written before the code: `Layout: <screen or region> - <spatial problem> -> <pattern name>; scroll owner: <selector>; anti-patterns: <the pattern's, in your words>`.
- **Before captures** (changing an existing UI): fix the cases now, states x widths, and capture `before` through `visual-qa` before/after mode before the first edit. A baseline reconstructed later is not a baseline.

## Draft guard: tells kept out of the first draft

Some tells regenerate by default, so keep them out of the first draft instead of leaving them for QA.

- **No coloured bar on one side of a box, rounded or square, and no accent outline on a rounded card, decorative or state.** A card, callout, warning, cover block, stat tile, testimonial, alert, or list row never carries a coloured stripe on one side: `border-left: 4px solid <accent>` or `border-l-4 border-indigo-500`, a coloured `::before`/`::after` bar inside it, an inset `box-shadow` stripe, or a hard-stop gradient band or gradient `border-image` along one edge. A rounded card never wears a 2px-or-wider accent outline either (`border: 2px solid var(--primary)`, `ring-2`, an inset ring). Both read as generated whether they decorate the box or mark it selected, focused, or active; an accent underline under a heading, tab, or link counts too (use a neutral 1px rule, or set the text itself in the accent ink). Give the card its identity another way: a tonal surface (one ink at low alpha, or the next step of the surface ramp), a heading in the accent ink, a leading glyph, or more space between groups. Encode state with one ink at many alphas (hover/selected/active washes), a check glyph for selection, and tonal layering for focus. Colored edges that stay allowed: keyboard `focus-visible` rings, validation states on form inputs, neutral 1px hairlines and dividers, table rules, and a blockquote's neutral rule. This covers pre-existing instances on any surface you touch.
- **Lint before visual QA.** Run `bun $SKILL_DIR/scripts/perfection/check-draft-guard.ts <changed files or dirs>` on every stylesheet, component, and HTML file you wrote, including a report or figure you will print, screenshot, or render. It reads CSS/SCSS/Less, HTML, JSX/TSX, Vue, Svelte, Astro, Tailwind classes (including `@apply` and `cva`/`cn` strings), inline styles, and styled-components, and flags the stripes above plus promotional filler copy, emoji used as icons, hype badges, and hard-coded vanity numbers in stat tiles. Exit 1 means a tell is in the draft: remove it, do not argue with the finding. `check-accent-stripes.ts` in the same directory runs only the stripe rules. If `bun` is unavailable, run the deslop scanner ([../deslop/README.md](../deslop/README.md)) and say the draft guard did not run.
- **No decorative badge without a state behind it.** A pill, chip, or tag appears only when it carries a value that can change: a status, a count, a category the user filters by. "New", "Pro", or "AI-powered" on a static heading is decoration.
- **No stat tile without a decision behind it.** A number earns a tile when someone acts on it; four tiles above a table that already holds the numbers are filler.
- **No invented proof.** Testimonials, quotes, customer logos, ratings, user counts, and prices come from the project or stay out. A section that needs proof the project does not have is cut, or ships as an empty slot labelled for the owner to fill; a "sample" testimonial is still a fabricated one.
- **No prop decoration.** A device tilted for effect, a floating reassurance card, decorative coordinates, sparkles, and ornaments that say nothing about the product are the generated version of "premium". A product preview shows a real state of the product, with its text readable at the rendered size.
- **No repeated formula.** A treatment that carries one heading (a serif line with an italic accent phrase, a gradient word, a headline-subtitle pair) becomes a template when every section repeats it; so does one image reused across sections. Use each once, where it means something.
- **No subtitle under every heading.** A heading explains itself; a one-line description under each one is the generated rhythm. Keep a subtitle only where the heading alone would be misread.
- **One fact, one place.** A conclusion banner and a callout that restates it, a summary card and a table row with the same figure, a label repeated as its placeholder: keep one.
- **No dated or borrowed surface.** Glass and blur panels, neumorphism, mesh-gradient heroes, heavy drop shadows, and dated stock-illustration styles date a draft on sight. Surfaces come from `DESIGN.md` section 7; a material ships only when the brief or a concrete reference supplies it.
- **No generated scaffold.** No kicker label above a heading, no icon tile stacked over a heading in a grid of same-size cards, no hero metric, no card inside a card, no neutral gray text on a coloured surface, no monospace as a "technical" costume, and no zero-offset coloured glow standing in for a shadow. [../perfection/craft-floor.md](../perfection/craft-floor.md) gives the replacement for each and says when the brief or its chosen route brings one back.
- **No promotional copy.** Interface copy states what a thing is or does. "Seamlessly", "effortlessly", "smart", "powerful", "at a glance", "supercharge", and their translations are marketing, not interface: rewrite as the plain fact or delete.

## Subtract

After the draft renders and the lint exits 0, walk every element on the screen and ask what the user could not do or know without it. No answer: delete it, whatever the reference or the previous version showed. Then open the brief's required-content list and confirm every item is still on the screen by name, with its own control or field. Subtraction that merges two required inputs into one, drops a datum, or shortens required copy is a regression, not a cleanup. Record what you removed under "Left out on purpose".

Then count the controls: a secondary action most visits do not need moves into a menu or to the object it acts on, and groups separate by whitespace, not by boxes and borders. Fewer controls with room around them is the target.

## Scoped fix passes

After the first build, each fix names one change and the regions it owns (a token fix may own every region) and leaves everything else untouched. A whole-page "make it better" pass breaks what was already right. Hand design-system decisions, evidence, and unresolved debt to your review step for significant work.
