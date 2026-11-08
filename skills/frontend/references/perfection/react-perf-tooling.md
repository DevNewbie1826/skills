# Optional React Performance Tooling

Read this when a React app needs component-level render diagnosis alongside a real-browser audit.

This is an optional React lane. The tools below can complement Playwright and Lighthouse by identifying React-specific performance issues that Lighthouse does not diagnose by component:

| Tool | Surface | What it gives you |
|---|---|---|
| **react-scan** (`react-scan/lite`) | Runtime instrumentation, headless | Per-fiber `commit` events with `changeDescription` — "this component re-rendered because <prop / state / context / parent / hook> changed". Correlates with `long-animation-frame` to attribute LoAF to specific components. |
| **react-doctor** | Static scan, CI-friendly | Deterministic findings across state/effects, perf (memoization, list keys, expensive children), architecture, security, a11y. One-shot `npx react-doctor@latest` produces a JSON report. From the Million.dev team. |

The tools are complementary: `react-scan` can show what is slow at runtime, while `react-doctor` can identify structural concerns. Use either or both when they fit the project. Keep them dev-only.

If the project chooses these tools, read `../design/react-dev-tooling-skill.md` for optional setup and production-leak checks.

## Lighthouse run + react-scan/lite

`playwright-lighthouse` already drives a real Chrome. Inject `react-scan/lite` BEFORE React mounts via `page.addInitScript`. Then drain its `onEvent` stream during the run and assert on render budgets at the end.

```ts
// scripts/audit-with-react-scan.ts
import { chromium } from "playwright";
import { playAudit } from "playwright-lighthouse";

const browser = await chromium.launch({ channel: "chrome" });
const context = await browser.newContext();

// Inject react-scan/lite BEFORE the app boots
await context.addInitScript(() => {
  // @ts-ignore — pulled from the project's node_modules or a self-hosted bundle
  import("react-scan/lite").then(({ instrument }) => {
    (window as any).__renderEvents = [];
    instrument({
      onEvent: (event: any) => {
        if (event.kind === "commit") (window as any).__renderEvents.push(event);
      },
      recordChangeDescriptions: true,
      includeFiberSource: true,
      includeFiberIdentity: true,
    });
  });
});

const page = await context.newPage();
await page.goto("http://localhost:3000/<route>");

await playAudit({
  page,
  port: 9222,
  thresholds: { performance: 100, accessibility: 100, "best-practices": 100, seo: 100 },
  reports: { formats: { html: true, json: true }, name: "lighthouse-<route>" },
  config: { extends: "lighthouse:default", settings: { formFactor: "mobile" } },
});

// Pull render events and assert on render quality
const events = await page.evaluate(() => (window as any).__renderEvents);
const unnecessary = events.filter((e: any) =>
  e.tree?.some((node: any) => node.changeDescription?.kind === "unnecessary"),
);

if (unnecessary.length > 0) {
  console.error(`FAIL: ${unnecessary.length} unnecessary renders detected during audit`);
  for (const e of unnecessary.slice(0, 10)) console.error("  -", JSON.stringify(e, null, 2));
  process.exit(1);
}

await browser.close();
```

This is one integration pattern. When using it, run mobile and desktop routes consistently with the base audit and set an explicit render-quality budget alongside the Lighthouse thresholds.

## react-doctor — optional static scan

When selected, run this fast structural scan before the Playwright audit so its findings can inform browser diagnosis.

```bash
npx react-doctor@latest --json > .react-doctor-report.json
```

Parse `.react-doctor-report.json` for performance-category findings and evaluate them alongside the project's audit threshold and render budget.

Wire it into CI as a separate job (cheap, fast, no browser needed):

```yaml
- name: React Doctor static perf scan
  uses: millionco/react-doctor@main
```

Or run inline with a fail filter:

```yaml
- name: React Doctor static perf scan
  run: npx react-doctor@latest --json --fail-on perf
```

## Suggested order when this lane is selected

A useful order is:

1. **`react-doctor`** — cheapest. Catches missing memoization, broken list keys, unstable callback refs, expensive children that re-render unnecessarily. Fix everything it reports BEFORE running Lighthouse — half the perf score wins live here.
2. **`react-scan` interactive in dev** — load the page in real Chrome with `npx react-scan@latest init` already wired (see the dev-tooling reference). Walk the LCP route, the most-clicked CTA, and any animation-heavy view. The toolbar shows render counts; the overlay highlights unnecessary renders in gray. at most three fix cycles per route budget; then report the residual with the render trace.
3. **`react-scan/lite` in the Lighthouse run** — once interactive is clean, run the Playwright audit above. This catches anything that only shows under throttling or only on first paint.
4. **Playwright + Lighthouse** — standard run from `README.md` audit workflow, evaluated with the selected render-quality budget.

## React-specific perf root causes (extends `README.md` ROOT-CAUSE CHECKLIST)

These are the failures `react-scan` and `react-doctor` surface that base Lighthouse won't directly name:

- **Context value identity churn.** A provider value `useMemo` was forgotten; every consumer re-renders on every render of the provider's parent. → `useMemo` the value, or split contexts so high-churn fields don't sit next to stable ones.
- **Inline object/array/callback props on memoized children.** `<Child config={{ a: 1 }} />` breaks `React.memo` every render. → Hoist, `useMemo`, or `useCallback`.
- **List keys = array index.** Reordering shreds the reconciler. → Use a stable id from the data.
- **Expensive components rendered unconditionally above the fold.** → `lazy()` + `Suspense`, or move below the LCP, or pre-render server-side.
- **Effects that fire on every render.** Missing dependency arrays or unstable deps. → Stabilize deps, or split state, or extract to `useEvent`-style ref.
- **Spreading the entire context value into props.** Couples every consumer to every field. → Destructure only the fields used.
- **Hydration mismatches.** SSR markup doesn't equal client first-render. → react-doctor flags structurally; fix the source of the divergence (Date.now, locale, randomness, browser-only APIs).

`react-doctor` finds these statically; `react-scan` can confirm symptoms in a running app. Use their evidence to guide fixes when this optional lane is active.

## Anti-patterns specific to this workflow

- **Forgetting `page.addInitScript` (using `page.evaluate` instead).** `evaluate` runs AFTER React mounts; you'll miss every initial-render event. Use `addInitScript`.
- **`react-scan` non-lite during a Lighthouse run.** The full UI (toolbar, canvas overlay) adds overhead and skews the score. Use `react-scan/lite` ONLY for measurement; the full version is for interactive dev.
- **Reporting Lighthouse 100 with `react-scan` showing 30+ unnecessary renders per route.** The score is not representative if the React layer is thrashing - INP and CLS will degrade under real load even if the synthetic run passed. Diagnose both the synthetic score and render quality.
- **Treating `trackUnnecessaryRenders` as free.** It has measurable overhead; in a Lighthouse run it can drag the perf score by 2-3 points. Use it for interactive diagnosis, not for the audit run.
- **Skipping react-doctor because "it's just a linter".** It's not. It detects React-specific defects (missing keys, broken memo, unstable refs, hydration mismatches) that ESLint plugins miss because they require fiber-level reasoning.

## Mantra

> **When this optional lane is active, report Lighthouse results together with the selected static and render-diagnostic evidence.**
