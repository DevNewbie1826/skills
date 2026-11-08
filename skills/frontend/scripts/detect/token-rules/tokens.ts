import { readFileSync } from "node:fs"
import { parseColor } from "../core"
import type { DetectConfig } from "../types"

const COLOR_LITERAL = /#[0-9a-fA-F]{3,8}\b|(?:rgba?|color|oklab|oklch|lab|lch)\([^()]*\)/g
const COMMENT = /\/\*[\s\S]*?\*\//g
const CUSTOM_PROPERTY = /--[A-Za-z0-9_-]+\s*:\s*([^;{}]+)/g

export type LoadedTokens =
	| { readonly ok: true; readonly colors: readonly string[] }
	| { readonly ok: false; readonly error: string }

function literalsIn(text: string): readonly string[] {
	const colors: string[] = []
	for (const match of text.matchAll(COLOR_LITERAL)) {
		if (parseColor(match[0])) colors.push(match[0])
	}
	return colors
}

function cssTokenColors(text: string): readonly string[] {
	const colors: string[] = []
	for (const declaration of text.replace(COMMENT, "").matchAll(CUSTOM_PROPERTY)) {
		colors.push(...literalsIn(declaration[1] ?? ""))
	}
	return colors
}

function jsonTokenColors(value: unknown, colors: string[]): void {
	if (typeof value === "string") {
		const text = value.trim()
		if (parseColor(text)) colors.push(text)
		return
	}
	if (Array.isArray(value)) {
		for (const item of value) jsonTokenColors(item, colors)
		return
	}
	if (typeof value === "object" && value !== null) {
		for (const item of Object.values(value)) jsonTokenColors(item, colors)
	}
}

/** Reads a project tokens file: CSS custom properties in any stylesheet, or color strings anywhere in a JSON tokens tree; no path means no colors. */
export function loadTokens(path?: string): LoadedTokens {
	if (path === undefined) return { ok: true, colors: [] }
	let text: string
	try {
		text = readFileSync(path, "utf8")
	} catch (error) {
		// no-excuse-ok: catch (CLI boundary: an unreadable tokens file is reported to the caller as a message)
		const detail = error instanceof Error ? error.message : String(error)
		return { ok: false, error: `cannot read tokens file: ${detail}` }
	}
	if (!path.toLowerCase().endsWith(".json")) return { ok: true, colors: cssTokenColors(text) }
	let raw: unknown
	try {
		raw = JSON.parse(text)
	} catch (error) {
		// no-excuse-ok: catch (CLI boundary: malformed token JSON is reported to the caller as a message)
		const detail = error instanceof Error ? error.message : String(error)
		return { ok: false, error: `invalid JSON tokens file: ${detail}` }
	}
	const colors: string[] = []
	jsonTokenColors(raw, colors)
	return { ok: true, colors }
}

const colorKey = (text: string): string => {
	const color = parseColor(text)
	return color ? `${color.r},${color.g},${color.b},${color.a}` : text
}

/** Returns the config with the loaded token colors appended to designTokens.colors, first copy of each value kept. */
export function mergeTokenColors(config: DetectConfig, colors: readonly string[]): DetectConfig {
	const existing = config.designTokens?.colors ?? []
	const seen = new Set(existing.map(colorKey))
	const added = colors.filter((color) => {
		const key = colorKey(color)
		if (seen.has(key)) return false
		seen.add(key)
		return true
	})
	if (added.length === 0) return config
	return { ...config, designTokens: { ...(config.designTokens ?? {}), colors: [...existing, ...added] } }
}
