import { lineAt, parseColor, positionAt, type Rgba } from "../core"
import type { SourceHit, SourceRule } from "../rule"

const COLOR_LITERAL = /#[0-9a-fA-F]{3,8}\b|(?:rgba?|color|oklab|oklch|lab|lch)\([^()]*\)/g
const COMMENT = /\/\*[\s\S]*?\*\//g
/** Token declarations and var() references (including a fallback) are where literals belong, so both are masked. */
const TOKEN_VALUE = /(?:["']?--[A-Za-z0-9_-]+["']?)\s*:\s*[^;{}]+|var\([^()]*\)/g
/** Selector text is masked so a hex-looking id such as `#fade` is not read as a color literal. */
const SELECTOR = /[^{};]*\{/g

const EXTENSIONS = ["css", "scss", "less", "pcss", "postcss", "html", "htm", "js", "jsx", "mjs", "cjs", "ts", "tsx", "mts", "cts", "vue", "svelte", "astro"]

const sameColor = (a: Rgba, b: Rgba): boolean =>
	Math.abs(a.r - b.r) < 0.5 && Math.abs(a.g - b.g) < 0.5 && Math.abs(a.b - b.b) < 0.5 && Math.abs(a.a - b.a) < 0.005

const mask = (text: string, pattern: RegExp): string => text.replace(pattern, (match) => " ".repeat(match.length))

export const hardCodedColor: SourceRule = {
	meta: {
		id: "hard-coded-color", name: "Hard-coded design-token color", category: "slop", severity: "warning", engine: "source",
		description: "A color literal repeats a color the project's design tokens already name.",
		fixHint: "Use the matching design token instead of the literal value (a custom-property reference in CSS).",
	},
	extensions: EXTENSIONS,
	check: ({ file, config }) => {
		const tokens = (config.designTokens?.colors ?? []).flatMap((text) => {
			const color = parseColor(text)
			return color ? [color] : []
		})
		if (tokens.length === 0) return []
		const scanned = mask(mask(mask(file.text, COMMENT), SELECTOR), TOKEN_VALUE)
		const hits: SourceHit[] = []
		for (const match of scanned.matchAll(COLOR_LITERAL)) {
			if (match.index === undefined) continue
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
