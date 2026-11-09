import { extensionOf, parseColor, type Rgba } from "../core"
import type { SourceHit, SourceRule } from "../rule"
import { declarationValueRanges } from "./css-declarations"
import { maskedValue } from "./css-tokenizer"

const COLOR_LITERAL = /(?<![A-Za-z0-9_-])#[0-9a-fA-F]{3,8}(?![A-Za-z0-9_-])|(?<![A-Za-z0-9_-])(?:rgba?|color|oklab|oklch|lab|lch)\([^()]*\)/gi
const HEX_LITERAL = /^#(?:[0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})$/i
const NUMBER_TOKEN = /^[+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?%?$/i
/** A hue may carry an angle unit; rejecting it would silently miss a valid oklch()/lch()/hsl() color. */
const ANGLE_TOKEN = /^[+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?(?:deg|grad|rad|turn)$/i
const STYLESHEET_EXTENSIONS = ["css", "scss", "less", "pcss", "postcss"]
const LINE_COMMENT_EXTENSIONS = ["scss", "less"]

/** An 8-bit alpha step is 1/255 (~0.0039), so a looser tolerance would equate two distinct representable opacities. */
const ALPHA_TOLERANCE = 0.002
const sameColor = (a: Rgba, b: Rgba): boolean =>
	Math.abs(a.r - b.r) < 0.5 && Math.abs(a.g - b.g) < 0.5 && Math.abs(a.b - b.b) < 0.5 && Math.abs(a.a - b.a) < ALPHA_TOLERANCE

/** Offset of each line start, so locating many hits is one binary search each instead of a rescan per hit. */
const lineStarts = (text: string): readonly number[] => {
	const starts = [0]
	for (let i = 0; i < text.length; i++) if (text.charCodeAt(i) === 10) starts.push(i + 1)
	return starts
}

const locatedAt = (starts: readonly number[], offset: number): { readonly index: number; readonly line: number; readonly column: number } => {
	let lo = 0
	let hi = starts.length - 1
	while (lo < hi) {
		const mid = (lo + hi + 1) >> 1
		if ((starts[mid] ?? 0) <= offset) lo = mid
		else hi = mid - 1
	}
	return { index: lo, line: lo + 1, column: offset - (starts[lo] ?? 0) + 1 }
}
/**
 * A color literal that is valid CSS source syntax, or null. Computed-value parsing accepts numeric prefixes,
 * so `255garbage` and `rgb(26\x 92 255)` would otherwise compare equal to a real color; source syntax must be
 * checked token by token first. `color()` keeps its space identifier as the first argument.
 */
function sourceColor(text: string): Rgba | null {
	if (HEX_LITERAL.test(text)) return parseColor(text)
	const call = /^(rgba?|color|oklab|oklch|lab|lch)\(([^()]*)\)$/i.exec(text)
	if (!call) return null
	const fn = (call[1] ?? "").toLowerCase()
	const parts = (call[2] ?? "").replaceAll("/", " / ").split(/[\s,]+/).filter(Boolean)
	if (parts.length === 0) return null
	const head = fn === "color" ? 1 : 0
	if (fn === "color" && !/^[a-z][a-z0-9-]*$/i.test(parts[0] ?? "")) return null
	// The hue is one fixed slot per function - first for hsl, third for lch/oklch - and an angle unit is valid
	// nowhere else, so an angle in the chroma slot must not skip numeric validation.
	const hueAt = fn === "hsl" || fn === "hsla" ? 0 : fn === "lch" || fn === "oklch" ? 2 : -1
	const channels = parts.slice(head)
	const alphaAt = channels.indexOf("/")
	// Legacy `rgb(26, 92, 255, 0.5)` puts the alpha in a fourth comma-separated slot, so the arity rule must
	// account for it before requiring three components. Only commas can select that form: `rgb(26 92 255 1)`
	// has four space-separated values and no slash, which is not valid CSS.
	const commaSeparated = /,/.test(call[2] ?? "")
	const commaAlpha = alphaAt === -1 && commaSeparated && fn.startsWith("rgb") && channels.length === 4 ? channels[3] : undefined
	const body = alphaAt !== -1 ? channels.slice(0, alphaAt) : commaAlpha === undefined ? channels : channels.slice(0, 3)
	// Every color function takes exactly three components. Without this arity check the computed-value parser
	// discards surplus channels, so `rgb(26 92 255 1 99)` would be compared as if it were a valid color.
	if (body.length !== 3) return null
	if (alphaAt !== -1 && (alphaAt !== 3 || channels.length !== 5)) return null
	for (const [at, part] of body.entries()) {
		if (at === hueAt ? !NUMBER_TOKEN.test(part) && !ANGLE_TOKEN.test(part) : !NUMBER_TOKEN.test(part)) return null
	}
	const alphaToken = alphaAt !== -1 ? channels[alphaAt + 1] : commaAlpha
	if (alphaToken !== undefined && !NUMBER_TOKEN.test(alphaToken)) return null
	return parseColor(text)
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
		const hits: SourceHit[] = []
		const starts = lineStarts(file.text)
		const lineComments = LINE_COMMENT_EXTENSIONS.includes(extensionOf(file.path))
		for (const range of declarationValueRanges(file.text, lineComments)) {
			const value = maskedValue(file.text, range.start, range.end, lineComments)
			for (const match of value.matchAll(COLOR_LITERAL)) {
				const offset = range.start + (match.index ?? 0)
				const color = sourceColor(match[0])
				if (!color || !tokens.some((token) => sameColor(token, color))) continue
				const at = locatedAt(starts, offset)
				const lineEnd = starts[at.index + 1]
				hits.push({
					line: at.line,
					column: at.column,
					message: `Hard-coded ${match[0]} is a design-token color; use the token instead.`,
					snippet: file.text.slice(starts[at.index] ?? 0, lineEnd === undefined ? file.text.length : lineEnd - 1).trim().slice(0, 160),
				})
			}
		}
		return hits
	},
}
