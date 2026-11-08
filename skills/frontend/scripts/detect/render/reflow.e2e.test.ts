import { describe, expect, test } from "bun:test"
import { detectPage } from "../detect"
import { RenderError } from "./renderer"
import { createWebViewRenderer } from "./webview"

// These tests need a real render runtime (system WebKit or an installed Chrome/Chromium).
// They run wherever one exists and skip everywhere else — including CI, whose no-runtime
// path is covered by render/degrade.test.ts.
const canRender = await (async () => {
	if (typeof Bun.WebView !== "function") return false
	try {
		const renderer = createWebViewRenderer()
		await renderer.render({ target: { kind: "url", url: "about:blank" }, viewport: { width: 100, height: 100 } })
		await renderer.close()
		return true
	} catch (error) {
		if (error instanceof RenderError) return false
		return false
	}
})()

const fixtureUrl = (...parts: string[]): string => new URL(parts.join("/"), import.meta.url).href

describe("render-path regressions (runtime-gated)", () => {
	test.skipIf(!canRender)("#given a page rendered with the reflow matrix #then the stress pass evaluates without a render failure", async () => {
		const findings = await detectPage(
			{ kind: "url", url: fixtureUrl("..", "fixtures", "detect", "page.html") },
			{ reflow: true },
		)
		expect(Array.isArray(findings)).toBe(true)
	})

	test.skipIf(!canRender)("#given readable pale text over a background painted on the root element #then low-contrast does not flag it", async () => {
		const findings = await detectPage(
			{ kind: "url", url: fixtureUrl("..", "fixtures", "detect", "dark-root.html") },
			{ viewports: [{ width: 1280, height: 800 }] },
		)
		expect(findings.some((f) => f.ruleId === "low-contrast")).toBe(false)
	})
})
