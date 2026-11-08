# Rendered-page quality lint

Read this when a built page needs a render-based quality check: contrast against the painted background, computed type scale, overflow at width, heading outline, images with a missing or placeholder source, or page script errors.

`scripts/detect/` is a TypeScript library with a thin CLI. It renders a page in a real browser engine and lints what was actually drawn, not what the source says. It runs after the source-level draft lint (`scripts/perfection/check-draft-guard.ts`) and before `visual-qa`. The draft lint reads files; this one needs pixels, so it catches what source can't show: a table header at 4.2:1 on a dark surface, an h1 followed by an h3, a card that overflows at 390 px, an image whose source attribute is missing or a placeholder. Network-level failures (an image URL that returns an error status) are outside what a snapshot can see; check those with a link checker.

## Run it

From code, import `index.ts`. Importing has no side effects:

```ts
const detect = await import(`${SKILL_DIR}/scripts/detect/index.ts`)
const findings = await detect.detectPage({ kind: "url", url: "http://localhost:5173/settings" }, {
  viewports: [{ width: 1440, height: 900 }, { width: 390, height: 844 }],
  reflow: true,
  config: { allowFonts: ["Inter"], designTokens: { radii: [8, 12] } },
})
```

- `detectPage(target, options)`: `target` is `{ kind: "url", url }` or `{ kind: "html", html }`. Options are `viewports`, `reflow`, `config`, and `renderer`. Default viewports are 1440x900 and 390x844.
- `reflow: true` adds 320, 375, 768, 1024, and 1440 widths, with a content stress pass at 320.
- `detectFiles(paths, options)` renders each HTML file. `lintSnapshot` and `lintSources` are the pure rule engines for a snapshot or source set you already hold.
- `renderer`: pass your own to reuse a browser you already drive. The default is a Bun web view backed by system WebKit or an installed Chrome/Chromium.

From a shell:

```bash
bun $SKILL_DIR/scripts/detect/cli.ts [--json] [--reflow] [--config detect.json] <file-or-dir-or-url>...
bun $SKILL_DIR/scripts/detect/cli.ts --help
```

Exit 0: no error or warning findings. Exit 1: at least one. Exit 2: usage error, a page that failed to render, or no browser runtime.

## Config

`--config <file.json>` (or `options.config`) takes:

| Key | Meaning |
|---|---|
| `rules` | `{ "<rule-id>": "error" \| "warning" \| "advisory" \| "off" }` per rule |
| `allowFonts`, `allowEasings`, `designTokens` | Parsed and validated for forward compatibility, but no rule in this port reads them (their consumers are taste rules this pack covers statically) |

Rule ids: `low-contrast`, `gray-on-color`, `tiny-text`, `undersized-ui-text`, `line-length`, `tight-leading`, `flat-type-hierarchy`, `oversized-h1`, `text-overflow`, `viewport-reflow`, `first-viewport-column-overflow`, `cramped-padding`, `nested-cards`, `heading-rhythm`, `unbalanced-heading`, `body-text-viewport-edge`, `content-hidden-at-rest`, `text-occlusion`, `clipped-overflow-container`, `skipped-heading`, `broken-image`, `script-error`, `repeated-container-text`. Placeholder text contrast is checked by `low-contrast` itself (its placeholder path), not a separate id.

## Waivers

Put `data-detect-ignore="<rule-id> <rule-id>"` on the element or an ancestor. A waiver is only valid when `DESIGN.md` records the reason.

## Reading the result

- `error` and `warning` fail the gate. Fix them before visual review.
- `advisory` is a prompt to decide. Record the decision in `DESIGN.md`; don't delete a deliberate choice just to silence it.
- A finding you think is wrong: rerun at the viewport it names and read the computed values it quotes before waiving.

## No browser runtime

HTML always needs the renderer; there's no source-only fallback for pages. When neither system WebKit nor an installed Chrome/Chromium is available, the CLI exits 2 with a message naming the missing runtime. Install one, or pass a `renderer` you already drive, then rerun. Don't report the page as clear.

## Not ported

The upstream detector also ships source-text and decoration slop rules. This pack covers those statically through `references/deslop/scripts/scan.mjs` and `scripts/perfection/check-draft-guard.ts`, so only the rendered-quality rules above are ported.
