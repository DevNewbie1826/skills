# Rendered-page quality lint

Read this when a built page needs a render-based quality check: contrast against the painted background, computed type scale, overflow at width, heading outline, images with a missing or placeholder source, or page script errors.

`scripts/detect/` is a TypeScript library with a thin CLI. It renders a page in a real browser engine and lints what was actually drawn, not what the source says. One source-text rule reads the project's design tokens and runs on stylesheets. It runs after the source-level draft lint (`scripts/perfection/check-draft-guard.ts`) and before `visual-qa`. The draft lint reads files; this one needs pixels, so it catches what source can't show: a table header at 4.2:1 on a dark surface, an h1 followed by an h3, a card that overflows at 390 px, an image whose source attribute is missing or a placeholder. Network-level failures (an image URL that returns an error status) are outside what a snapshot can see; check those with a link checker.

## Run it

From code, import `index.ts`. Importing has no side effects:

```ts
const detect = await import(`${SKILL_DIR}/scripts/detect/index.ts`)
const tokens = detect.loadTokens("src/tokens.css")
const config = tokens.ok ? detect.mergeTokenColors({}, tokens.colors) : {}
const findings = await detect.detectPage({ kind: "url", url: "http://localhost:5173/settings" }, {
  viewports: [{ width: 1440, height: 900 }, { width: 390, height: 844 }],
  reflow: true,
  config: { ...config, allowFonts: ["Inter"] },
})
// Page rules read the snapshot; the token rule reads stylesheet text, so pass the sheets to lintSources.
const styles = await detect.lintSources([{ path: "src/app.css", text: appCss }], { config })
```

- `detectPage(target, options)`: `target` is `{ kind: "url", url }` or `{ kind: "html", html }`. Options are `viewports`, `reflow`, `config`, and `renderer`. Default viewports are 1440x900 and 390x844.
- `reflow: true` adds 320, 375, 768, 1024, and 1440 widths, with a content stress pass at 320.
- `detectFiles(paths, options)` renders each HTML file. `lintSnapshot` and `lintSources` are the pure rule engines for a snapshot or source set you already hold. `detectFiles` renders HTML as a page, so the stylesheet-only token rule reaches CSS through `lintSources`, or through the CLI when you pass stylesheets next to the pages.
- `renderer`: pass your own to reuse a browser you already drive. The default is a Bun web view backed by system WebKit or an installed Chrome/Chromium.
- `loadTokens(path)` reads a project tokens file: CSS custom properties from any stylesheet, or color strings at any depth in a JSON tokens tree. With no path it returns `{ ok: true, colors: [] }`, which keeps the token rule silent. `mergeTokenColors(config, colors)` folds the loaded colors into `config.designTokens.colors` without duplicating equivalent values.

From a shell:

```bash
bun $SKILL_DIR/scripts/detect/cli.ts [--json] [--reflow] [--config detect.json] [--tokens tokens.css] <file-or-dir-or-url>...
bun $SKILL_DIR/scripts/detect/cli.ts --help
```

Exit 0: no error or warning findings. Exit 1: at least one. Exit 2: usage error, a page that failed to render, an unreadable or malformed tokens file, or no browser runtime.

## Config

`--config <file.json>` (or `options.config`) takes:

| Key | Meaning |
|---|---|
| `rules` | `{ "<rule-id>": "error" \| "warning" \| "advisory" \| "off" }` per rule |
| `designTokens` | `{ colors: ["#1a5cff"], fonts: [], radii: [], fontSizes: [] }`. Token rules read `colors`; without `designTokens.colors` they stay silent. `--tokens <file>` loads them from a project file instead |
| `allowFonts`, `allowEasings` | Parsed and validated for forward compatibility, but no rule in this port reads them (their consumers are taste rules this pack covers statically) |

Rule ids: `low-contrast`, `gray-on-color`, `tiny-text`, `undersized-ui-text`, `line-length`, `tight-leading`, `flat-type-hierarchy`, `oversized-h1`, `text-overflow`, `viewport-reflow`, `first-viewport-column-overflow`, `cramped-padding`, `nested-cards`, `heading-rhythm`, `unbalanced-heading`, `body-text-viewport-edge`, `content-hidden-at-rest`, `text-occlusion`, `clipped-overflow-container`, `skipped-heading`, `broken-image`, `script-error`, `repeated-container-text`, `hard-coded-color`. Placeholder text contrast is checked by `low-contrast` itself (its placeholder path), not a separate id.

`hard-coded-color` is the one source-text rule, and it covers stylesheets (`.css`, `.scss`, `.less`, `.pcss`, `.postcss`). It reports a color literal that repeats a color the project's design tokens already name, so a project with tokens gets told where a token belongs. Comments, quoted strings, nested selector preludes, `var()` calls including their fallbacks, and `url()` values are not reported, and a color literal that overlaps a `var()`, `url()` or string is never inferred from the remaining text. In `.scss` and `.less` files `//` line comments are excluded too; `.css` has no line comments, so `//` there is ordinary text. Color comparison is case-insensitive and notation-insensitive: `#1a5cff`, `#1A5CFF` and `RGB(26 92 255)` are the same color. To lint a project's stylesheets, pass them alongside the pages, or call `lintSources` on their text.

## Waivers

Put `data-detect-ignore="<rule-id> <rule-id>"` on the element or an ancestor. A waiver is only valid when `DESIGN.md` records the reason. Source findings carry a file, line and column instead of a selector, so waive those by fixing the literal or switching the rule off in config.

## Reading the result

- `error` and `warning` fail the gate. Fix them before visual review.
- `advisory` is a prompt to decide. Record the decision in `DESIGN.md`; don't delete a deliberate choice just to silence it.
- A finding you think is wrong: rerun at the viewport it names and read the computed values it quotes before waiving.

## No browser runtime

HTML always needs the renderer; there's no source-only fallback for pages. When neither system WebKit nor an installed Chrome/Chromium is available, the CLI exits 2 with a message naming the missing runtime. Install one, or pass a `renderer` you already drive, then rerun. Don't report the page as clear.

## Not ported

The upstream detector also ships further source-text and decoration slop rules. This pack covers those statically through `references/deslop/scripts/scan.mjs` and `scripts/perfection/check-draft-guard.ts`, or not at all, so beyond `hard-coded-color` only the rendered-quality rules above are ported. Additional token rules are a later wave; the loader and the rule group are the extension point.
