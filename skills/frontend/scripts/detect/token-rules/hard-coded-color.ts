import { lineAt, parseColor, positionAt, type Rgba } from "../core"
import type { SourceHit, SourceRule } from "../rule"

const COLOR_LITERAL = /#[0-9a-fA-F]{3,8}\b|(?:rgba?|color|oklab|oklch|lab|lch)\([^()]*\)/gi
const MASKED_CALL = /^(?:var|url)\s*\(/i
const STYLESHEET_EXTENSIONS = ["css", "scss", "less", "pcss", "postcss"]

interface Span {
	readonly start: number
	readonly end: number
}

const sameColor = (a: Rgba, b: Rgba): boolean =>
	Math.abs(a.r - b.r) < 0.5 && Math.abs(a.g - b.g) < 0.5 && Math.abs(a.b - b.b) < 0.5 && Math.abs(a.a - b.a) < 0.005

const skipComment = (text: string, from: number): number => {
	const end = text.indexOf("*/", from + 2)
	return end === -1 ? text.length : end + 2
}

const skipString = (text: string, from: number): number => {
	const quote = text[from] ?? ""
	let i = from + 1
	while (i < text.length && text[i] !== quote) i += text[i] === "\\" ? 2 : 1
	return i + 1
}

const isSpace = (c: string): boolean => c === " " || c === "\t" || c === "\n" || c === "\r" || c === "\f"

const skipTrivia = (text: string, from: number): number => {
	let i = from
	while (i < text.length) {
		const c = text[i] ?? ""
		if (isSpace(c)) {
			i++
			continue
		}
		if (c === "/" && text[i + 1] === "*") {
			i = skipComment(text, i)
			continue
		}
		break
	}
	return i
}

/** First index in [from, end) whose character is a terminator at parenthesis depth 0, or `end`. */
const skipTo = (text: string, from: number, end: number, terminators: string): number => {
	let i = from
	let parens = 0
	while (i < end) {
		const c = text[i] ?? ""
		if (c === "/" && text[i + 1] === "*") {
			i = Math.min(end, skipComment(text, i))
			continue
		}
		if (c === "\"" || c === "'") {
			i = Math.min(end, skipString(text, i))
			continue
		}
		if (c === "(") {
			parens++
			i++
			continue
		}
		if (c === ")") {
			if (parens > 0) parens--
			i++
			continue
		}
		if (parens === 0 && terminators.includes(c)) return i
		i++
	}
	return end
}

/** Index just past the close parenthesis matching the `(` at `from`, or `end`. Comments and strings inside are skipped. */
const closeParen = (text: string, from: number, end: number): number => {
	let i = from
	let parens = 0
	while (i < end) {
		const c = text[i] ?? ""
		if (c === "/" && text[i + 1] === "*") {
			i = Math.min(end, skipComment(text, i))
			continue
		}
		if (c === "\"" || c === "'") {
			i = Math.min(end, skipString(text, i))
			continue
		}
		if (c === "(") {
			parens++
			i++
			continue
		}
		if (c === ")") {
			parens--
			i++
			if (parens === 0) return i
			continue
		}
		i++
	}
	return end
}

/** Sub-ranges of a declaration value that may hold a reportable literal: no comments, strings, `var()` or `url()`. */
const reportableSpans = (text: string, start: number, end: number): readonly Span[] => {
	const spans: Span[] = []
	let chunk = start
	let i = start
	while (i < end) {
		const c = text[i] ?? ""
		if (c === "/" && text[i + 1] === "*") {
			if (i > chunk) spans.push({ start: chunk, end: i })
			i = Math.min(end, skipComment(text, i))
			chunk = i
			continue
		}
		if (c === "\"" || c === "'") {
			if (i > chunk) spans.push({ start: chunk, end: i })
			i = Math.min(end, skipString(text, i))
			chunk = i
			continue
		}
		if (MASKED_CALL.test(text.slice(i, Math.min(end, i + 8)))) {
			if (i > chunk) spans.push({ start: chunk, end: i })
			const open = text.indexOf("(", i)
			i = closeParen(text, open === -1 ? i : open, end)
			chunk = i
			continue
		}
		i++
	}
	if (end > chunk) spans.push({ start: chunk, end })
	return spans
}

/**
 * Declaration values of a stylesheet, in source order, excluding custom-property definitions. Walks the
 * text once so comments, strings and nested blocks are consumed where they appear instead of being
 * re-scanned by a later pass.
 */
const declarationValueSpans = (text: string): readonly Span[] => {
	const spans: Span[] = []
	const n = text.length
	let i = 0
	let depth = 0
	while (i < n) {
		if (depth === 0) {
			i = skipTo(text, i, n, "{;")
			if (i < n) {
				if (text[i] === "{") depth++
				i++
			}
			continue
		}
		i = skipTrivia(text, i)
		if (i >= n) break
		const c = text[i] ?? ""
		if (c === "}") {
			depth--
			i++
			continue
		}
		if (c === "@") {
			i = skipTo(text, i, n, "{;")
			if (i < n) {
				if (text[i] === "{") depth++
				i++
			}
			continue
		}
		let j = i
		while (j < n) {
			const d = text[j] ?? ""
			if (isSpace(d) || d === ";" || d === "{" || d === "}" || d === ":" || d === "(" || d === ")" || d === ",") break
			j++
		}
		const name = text.slice(i, j)
		const afterName = skipTrivia(text, j)
		if (name.length > 0 && (text[afterName] ?? "") === ":") {
			const valueStart = skipTrivia(text, afterName + 1)
			const valueEnd = skipTo(text, valueStart, n, "};")
			if (!name.startsWith("--")) spans.push(...reportableSpans(text, valueStart, valueEnd))
			i = valueEnd
			if ((text[i] ?? "") === ";") i++
			continue
		}
		i = skipTo(text, i, n, "{;}")
		if (i < n) {
			if (text[i] === "{") depth++
			i++
		}
	}
	return spans
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
		for (const span of declarationValueSpans(file.text)) {
			for (const match of file.text.slice(span.start, span.end).matchAll(COLOR_LITERAL)) {
				const offset = span.start + (match.index ?? 0)
				const color = parseColor(match[0])
				if (!color || !tokens.some((token) => sameColor(token, color))) continue
				const at = positionAt(file.text, offset)
				hits.push({
					line: at.line,
					column: at.column,
					message: `Hard-coded ${match[0]} is a design-token color; use the token instead.`,
					snippet: lineAt(file.text, offset),
				})
			}
		}
		return hits
	},
}
