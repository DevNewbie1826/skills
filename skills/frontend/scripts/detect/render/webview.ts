import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs"
import { tmpdir } from "node:os"
import { dirname, join } from "node:path"
import { fileURLToPath, pathToFileURL } from "node:url"
import { collectPageSnapshot, SCRIPT_ERROR_PROBE, STYLE_PROPS } from "../snapshot"
import type { PageSnapshot } from "../types"
import { insertAfterProlog } from "./probe-placement"
import { CONTENT_STRESS_SCRIPT, RenderError, type RenderRequest, type RenderTarget, type Renderer } from "./renderer"

const MAX_ELEMENTS = 20_000
const SETTLE_FRAMES = "new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(() => requestAnimationFrame(() => resolve(true)))))"

const MISSING_RUNTIME_MESSAGE = "no browser runtime available (install Chrome or Chromium, or run on a host with system WebKit)"
const MISSING_RUNTIME = /(Failed to spawn Chrome|ERR_DLOPEN_FAILED|install Chrome\/Chromium|only available on macOS|BUN_CHROME_PATH)/i

/** True for the constructor and navigation failures Bun reports when no system WebKit or installed Chrome/Chromium can be found. */
function isMissingRuntime(error: unknown): boolean {
	const code = typeof error === "object" && error !== null ? Reflect.get(error, "code") : undefined
	const text = `${error instanceof Error ? error.message : String(error)} ${typeof code === "string" ? code : ""}`
	return MISSING_RUNTIME.test(text)
}

function withProbe(html: string, baseHref?: string): string {
	return insertAfterProlog(html, `${baseHref ? `<base href="${baseHref}">` : ""}<script>${SCRIPT_ERROR_PROBE}</script>`)
}

function isSnapshot(value: unknown): value is PageSnapshot {
	return typeof value === "object" && value !== null && Array.isArray(Reflect.get(value, "elements"))
}

/** A renderer backed by Bun.WebView (system WebKit on macOS, installed Chrome/Chromium elsewhere). One view per request. */
export function createWebViewRenderer(options: { readonly backend?: "webkit" | "chrome" } = {}): Renderer {
	const scratch = mkdtempSync(join(tmpdir(), "frontend-detect-"))
	let counter = 0
	const chrome = options.backend === "chrome" || (options.backend === undefined && process.platform !== "darwin")
	const writePage = (html: string, baseHref?: string): string => {
		const file = join(scratch, `page-${counter++}.html`)
		writeFileSync(file, withProbe(html, baseHref))
		return pathToFileURL(file).href
	}
	const open = async (view: Bun.WebView, target: RenderTarget): Promise<void> => {
		if (target.kind === "html") return view.navigate(writePage(target.html))
		if (chrome) {
			await view.navigate("about:blank")
			await view.cdp("Page.addScriptToEvaluateOnNewDocument", { source: SCRIPT_ERROR_PROBE })
			return view.navigate(target.url)
		}
		if (target.url.startsWith("file:")) {
			const path = fileURLToPath(target.url)
			return view.navigate(writePage(readFileSync(path, "utf8"), pathToFileURL(`${dirname(path)}/`).href))
		}
		return view.navigate(target.url)
	}
	return {
		async render(request: RenderRequest): Promise<PageSnapshot> {
			const label = request.target.kind === "url" ? request.target.url : "inline html"
			if (typeof Bun.WebView !== "function") throw new RenderError(label, MISSING_RUNTIME_MESSAGE)
			let view: Bun.WebView | null = null
			try {
				view = new Bun.WebView({
					width: request.viewport.width,
					height: request.viewport.height,
					...(options.backend ? { backend: options.backend } : {}),
				})
				await open(view, request.target)
				await view.evaluate("document.fonts ? document.fonts.ready.then(() => true) : true")
				await view.evaluate(SETTLE_FRAMES)
				if (request.contentStress) await view.evaluate(CONTENT_STRESS_SCRIPT)
				const snapshot: unknown = await view.evaluate(`(${collectPageSnapshot.toString()})(${JSON.stringify(STYLE_PROPS)}, ${MAX_ELEMENTS})`)
				if (!isSnapshot(snapshot)) throw new Error("the page did not return a snapshot")
				return snapshot
			} catch (error) {
				throw new RenderError(label, isMissingRuntime(error) ? new Error(MISSING_RUNTIME_MESSAGE, { cause: error }) : error)
			} finally {
				if (view !== null) {
					try {
						await view.close()
					} catch {
						// A close failure must not mask the render outcome that was already decided.
					}
				}
			}
		},
		async close(): Promise<void> {
			rmSync(scratch, { recursive: true, force: true })
		},
	}
}
