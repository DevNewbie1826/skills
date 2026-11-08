import { lineAt, parseColor, positionAt, type Rgba } from "../core"
import type { SourceHit, SourceRule } from "../rule"

const COLOR_LITERAL = /#[0-9a-fA-F]{3,8}\b|(?:rgba?|color|oklab|oklch|lab|lch)\([^()]*\)/gi

const STYLESHEET_EXTENSIONS = ["css", "scss", "less", "pcss", "postcss"]

const sameColor = (a: Rgba, b: Rgba): boolean =>
	Math.abs(a.r - b.r) < 0.5 && Math.abs(a.g - b.g) < 0.5 && Math.abs(a.b - b.b) < 0.5 && Math.abs(a.a - b.a) < 0.005

/**
 * Offsets that can never be a hard-coded use of a token color: comments, quoted strings, `var()` calls
 * (including a fallback, at any paren depth), selector preludes, and custom-property declarations, which
 * are where the token itself is defined.
 */
function ignoredOffsets(text: string): readonly boolean[] {
	const ignored = new Array<boolean>(text.length).fill(false)
	const mark = (from: number, to: number): void => {
		for (let i = Math.max(0, from); i < Math.min(text.length, to); i++) ignored[i] = true
	}
	for (let i = 0; i < text.length; i++) {
		const pair = text.slice(i, i + 2)
		if (pair === "/*") {
			const end = text.indexOf("*/", i + 2)
			const stop = end === -1 ? text.length : end + 2
			mark(i, stop)
			i = stop - 1
			continue
		}
		const quote = text[i]
		if (quote === "\"" || quote === "'") {
			let j = i + 1
			while (j < text.length && text[j] !== quote) j += text[j] === "\\" ? 2 : 1
			mark(i, j + 1)
			i = j
		}
	}
	for (const call of text.matchAll(/var\s*\(/gi)) {
		if (call.index === undefined) continue
		let depth = 1
		let j = call.index + call[0].length
		while (j < text.length && depth > 0) {
			if (text[j] === "(") depth++
			else if (text[j] === ")") depth--
			j++
		}
		mark(call.index, j)
	}
	for (let i = 0; i < text.length; i++) {
		if (text[i] !== "{") continue
		let start = i
		while (start > 0 && ![";", "}", "{"].includes(text[start - 1] ?? "")) start--
		mark(start, i + 1)
	}
	for (const declaration of text.matchAll(/--[A-Za-z0-9_-]+\s*:/g)) {
		if (declaration.index === undefined) continue
		let j = declaration.index + declaration[0].length
		let depth = 0
		while (j < text.length) {
			const ch = text[j]
			if (ch === "(") depth++
			else if (ch === ")") depth--
			else if (depth === 0 && (ch === ";" || ch === "}" || ch === "\n")) break
			j++
		}
		mark(declaration.index, j)
	}
	return ignored
}

export const hardCodedColor: SourceRule = {
	meta: {
		id: "hard-coded-color", name: "Hard-coded design-token color", category: "slop", severity: "warning", engine: "source",
		description: "A stylesheet color literal repeats a color the project's design tokens already name.",
		fixHint: "Use the matching design token instead of the literal value (a custom-property reference in CSS).",
	},
	extensions: STYLESHEET_EXTENSIONS,
	check: ({ file, config }) => {
		const tokens = (config.designTokens?.colors ?? []).flatMap((text) => {
			const color = parseColor(text)
			return color ? [color] : []
		})
		if (tokens.length === 0) return []
		const ignored = ignoredOffsets(file.text)
		const hits: SourceHit[] = []
		for (const match of file.text.matchAll(COLOR_LITERAL)) {
			if (match.index === undefined || ignored[match.index]) continue
			const color = parseColor(match[0])
			if (!color || !tokens.some((token) => sameColor(token, color))) continue
			const at = positionAt(file.text, match.index)
			hits.push({
				line: at.line,
				column: at.column,
				message: `Hard-coded ${match[0]} is a design-token color; use the token instead.`,
				snippet: lineAt(file.text, match.index),
			})
		}
		return hits
	},
}
