# Optional React Development Tooling

Read this when a React project would benefit from optional source inspection, render diagnostics, or static analysis.

For React projects, these are optional dev-only tools. Choose them when they fit the project's dependency policy and workflow; use equivalent tooling for other stacks where available.

## The three tools

| Tool | What it does | When it is useful |
|---|---|---|
| **react-grab** | Cmd/Ctrl+C on any UI element copies its source location, nearby code, and component stack into the clipboard. | Useful when source coordinates are needed instead of guessing from a screenshot. |
| **react-scan** | Visually highlights every component render in dev. Detects unnecessary re-renders, slow renders, and tracks render causes. Has a headless `react-scan/lite` mode for automated perf measurement. | Catches re-render regressions the moment they happen, before they ship. Pairs with the perfection ruleset (`../perfection/README.md`) for Lighthouse 100 work. |
| **react-doctor** | Static scanner for React state/effects, performance, architecture, security, and accessibility. A one-shot `npx react-doctor@latest` audit can emit JSON for CI. | Useful for deterministic React findings before review or browser auditing. |

All three are **dev-only** (`process.env.NODE_ENV === 'development'` or `import.meta.env.DEV`). None ship to production.

## Optional setup for a React project

Run from the project root only when the project chooses these tools. Skip them when the user or project policy disallows extra dev dependencies.

```bash
# 1. react-grab — adds itself to package.json + entry file with dev gate
npx grab@latest init

# 2. react-doctor — first audit and optional local integration
npx react-doctor@latest install

# 3. react-scan — adds itself with dev gate
npx react-scan@latest init
```

The `init`/`install` CLIs may handle common React setups and gating. If a CLI does not fit the project, use the relevant manual snippet below or skip the tool and record why.

After install, confirm by reading the diff. Each tool should appear ONLY behind a `process.env.NODE_ENV === "development"` / `import.meta.env.DEV` gate.

## Manual install (when the CLI does not fit)

### Next.js (App Router) — `app/layout.tsx`

```tsx
import Script from "next/script";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        {process.env.NODE_ENV === "development" && (
          <>
            <Script
              src="//unpkg.com/react-grab/dist/index.global.js"
              crossOrigin="anonymous"
              strategy="beforeInteractive"
            />
            <Script
              src="//unpkg.com/react-scan/dist/auto.global.js"
              crossOrigin="anonymous"
              strategy="beforeInteractive"
            />
          </>
        )}
      </head>
      <body>{children}</body>
    </html>
  );
}
```

### Next.js (Pages Router) — `pages/_document.tsx`

Same pattern, but the `<Script>` tags live inside `<Head>` from `next/document` and gate on `process.env.NODE_ENV === 'development'`.

### Vite — `src/main.tsx` (or wherever the entry is)

```tsx
if (import.meta.env.DEV) {
  void import("react-grab");
  void import("react-scan");
}
```

Optionally add the Vite plugin for richer `displayName` data on react-scan:

```ts
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import reactScan from "vite-plugin-react-scan";

export default defineConfig({
  plugins: [react(), reactScan()],
});
```

### Webpack / CRA — entry file top

```ts
if (process.env.NODE_ENV === "development") {
  void import("react-grab");
  void import("react-scan");
}
```

### Remix — `app/root.tsx`

```tsx
export default function App() {
  return (
    <html lang="en">
      <head>
        <Meta />
        {process.env.NODE_ENV === "development" && (
          <>
            <script crossOrigin="anonymous" src="//unpkg.com/react-grab/dist/index.global.js" />
            <script crossOrigin="anonymous" src="//unpkg.com/react-scan/dist/auto.global.js" />
          </>
        )}
        <Links />
      </head>
      <body>
        <Outlet />
        <Scripts />
      </body>
    </html>
  );
}
```

### Astro — `src/layouts/Layout.astro`

```astro
---
const isDev = import.meta.env.DEV;
---
<head>
  {isDev && (
    <>
      <script crossorigin="anonymous" src="//unpkg.com/react-grab/dist/index.global.js" is:inline></script>
      <script crossorigin="anonymous" src="//unpkg.com/react-scan/dist/auto.global.js" is:inline></script>
    </>
  )}
</head>
```

## react-doctor — wire the scan, not the bundle

react-doctor is a one-shot CLI plus an optional CI action, not a runtime injection. Use one or more of these integration points when useful:

1. **As optional local tooling:**

   ```bash
   npx react-doctor@latest install
   ```

   Inspect the resulting changes and retain only integrations that fit the project.

2. **As a local pre-commit or scripted gate:**

   ```bash
   # Manual audit
   npx react-doctor@latest

   # JSON for scripting / CI
   npx react-doctor@latest --json > .react-doctor-report.json
   ```

3. **As an optional CI gate** for static-scan regressions:

   ```yaml
   # .github/workflows/react-doctor.yml
   name: React Doctor
   on: [pull_request]
   jobs:
     audit:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: millionco/react-doctor@main
   ```

## Feature flag — opt-out without surgery

The `NODE_ENV === "development"` gate already keeps these out of production. For temporarily disabling the runtime tools during a dev session (e.g. when profiling without instrumentation overhead), put one env var in front:

```ts
// entry file
const enableDevTools =
  process.env.NODE_ENV === "development" &&
  process.env.NEXT_PUBLIC_DISABLE_REACT_DEVTOOLS !== "1";

if (enableDevTools) {
  void import("react-grab");
  void import("react-scan");
}
```

Then `NEXT_PUBLIC_DISABLE_REACT_DEVTOOLS=1 npm run dev` skips both without re-editing code.

For Vite use `VITE_DISABLE_REACT_DEVTOOLS`, for CRA use `REACT_APP_DISABLE_REACT_DEVTOOLS`. The variable name MUST start with the framework's required prefix or it won't reach the bundle.

## When to skip these optional tools

- **The project is not React.** None of these apply to Solid, Svelte, Vue, Qwik, or any non-React framework. Skip silently.
- **The user explicitly said "no extra dev dependencies"** or the README forbids them. Respect that.
- **The project ships React 16 or earlier.** react-scan and react-doctor target modern React (17+, often 18+). Check `package.json` first; if the project is on legacy React, skip the runtime tools and only run react-doctor's static scan (it's framework-tolerant).
- **The project is a library, not an app.** Libraries have no entry file to inject into; only consumers (apps) should run the runtime tools. The static scan still applies.

## Verification

After install, sanity-check that the tools are loaded ONLY in dev:

```bash
# 1. Build for production
npm run build && npm run start  # or vite build && vite preview, etc.

# 2. Open the production URL and verify
#    - No react-grab toolbar visible
#    - No react-scan overlay or console output
#    - DOM contains zero <script> tags pointing at unpkg.com/react-grab or unpkg.com/react-scan
curl -s http://localhost:3000 | grep -E 'react-grab|react-scan' && echo "LEAK — fix the gate" || echo "OK"
```

If any of those leak into production, the dev gate is broken. Fix the gate before declaring done.

## Cross-skill references

- For **render performance / Lighthouse 100** work, see `../perfection/react-perf-tooling.md` — Playwright + `react-scan/lite` integration used during automated audits.
- For **debugging an in-flight React bug**, if the debugging skill is installed, its browser and runtime tooling references go deeper than this setup guide.
- The Phase 0 Design System Gate in `README.md` is required before UI implementation. This optional React lane can follow it when the project chooses React-specific tooling.

## Guideline

> **Use React-specific tooling when it offers clear value, keep it dev-only, and respect the project's dependency policy.**
