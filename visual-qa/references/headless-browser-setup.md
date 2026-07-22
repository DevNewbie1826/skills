Read this when you need a real browser screenshot and the project does not already provide a capture path.

# Headless browser setup

A browser capture is valid only when it renders the real page at the requested state and viewport. Use the first capability available to the runtime; no particular browser driver is required.

## Capability options and fallbacks

1. **Built-in browser control:** Use it when it can navigate, set the required state, and save a screenshot. If it cannot reach the page or lacks a required action, move to a CDP connection.
2. **Headless CLI screenshot:** For quick static captures, invoke Chromium's headless CLI directly (`--headless=new --screenshot=... --window-size=W,H --hide-scrollbars`). No driver or protocol work is required, but see the viewport floor warning below before trusting small-width output. If the CLI path cannot reach the required state or viewport, move to a CDP connection.
3. **CDP-capable Chromium:** Connect a driver to an existing Chromium-family browser with remote debugging enabled. If no CDP endpoint or usable browser binary is available, use Playwright.
4. **Playwright:** Use an installed project dependency or an approved temporary setup to launch or connect to Chromium. If it is unavailable, use another real-browser driver already supported by the environment.
5. **Equivalent driver:** Use a real browser automation capability that can set viewport, navigate, wait for the required state, and write a PNG. If none exists, document the missing capability and do not claim screenshot-based visual verification.

## Headless CLI screenshots (quick captures)

For unauthenticated static pages, the Chromium headless CLI is the cheapest capture path:

```sh
"$CHROMIUM_BIN" --headless=new --disable-gpu --hide-scrollbars \
  --virtual-time-budget=3000 --window-size=1280,900 --screenshot=actual.png "$URL"
```

**Viewport floor warning:** the CLI enforces a minimum CSS layout width (observed: 500 px) — a `--window-size=375,900` capture is silently laid out at the floor width and cropped, producing clipped text that looks like a page defect. Before trusting any sub-500 px capture, probe the real viewport (inject `document.title = innerWidth` and read it via `--dump-dom`); if it does not match the requested width, do not claim that width as verified. For sub-500 px viewports use CDP device metrics (`Emulation.setDeviceMetricsOverride`) or Playwright's `viewport` option, both of which honor exact widths; `--force-device-scale-factor` does not lower the floor.

Do not require a global installation. Prefer the project's existing dependency or browser configuration, and keep any temporary setup outside the product source tree unless the project explicitly requests it.

## CDP-capable Chromium

Start or locate a Chromium-family browser with remote debugging enabled. The exact executable and launch policy vary by environment; a representative launch shape is:

```sh
"$CHROMIUM_BIN" --headless=new --remote-debugging-port=9222 --window-size=1280,720
```

Connect a CDP-capable client to the endpoint, create or select a page, set the exact viewport and device scale factor, navigate to the target, drive the needed state, and save a PNG. If this browser cannot run headlessly, use its headed mode or the next available capability; do not substitute an HTML snapshot for a browser render.

## Playwright option

When Playwright is available, use either its browser launch API or its CDP connection API. The essential sequence is the same regardless of runner:

```js
import { chromium } from "playwright"

const [targetUrl, screenshotPath = "actual.png"] = process.argv.slice(2)
if (!targetUrl) throw new Error("provide a target URL")

const browser = await chromium.launch({ headless: true })
try {
  const page = await browser.newPage({
    viewport: { width: 1280, height: 720 },
    deviceScaleFactor: 1,
  })
  await page.goto(targetUrl, { waitUntil: "networkidle", timeout: 30_000 })
  // Drive the required page state here using deterministic page events or locators.
  await page.screenshot({ path: screenshotPath, fullPage: false })
} finally {
  await browser.close()
}
```

If a browser is already running with a CDP endpoint, replace launch with `chromium.connectOverCDP(endpoint)` and select the intended context and page. If the installed Playwright version, browser channel, or runner cannot perform this sequence, use the CDP or equivalent-driver fallback instead.

## Capture discipline

For every screenshot, record and match the reference's:

- viewport width and height,
- device scale factor and color mode,
- URL or route,
- scroll position,
- authenticated or unauthenticated state, and
- interaction and animation state.

Wait for the page's relevant load, locator, network, or animation condition rather than sleeping for an arbitrary duration. Capture a viewport image unless the reference is explicitly full-page; use matching mode for both target and actual. Validate the PNG signature, compositing, and dimensions before comparison.

Use the image comparison and complete evidence procedure in [Capture evidence](capture-evidence.md). If an authenticated state exists only in a user's own browser session and no permitted capture path can access it, report that limitation rather than attempting to reproduce credentials or declaring the state visually verified.
