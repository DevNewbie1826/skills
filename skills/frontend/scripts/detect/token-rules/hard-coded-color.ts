import { extensionOf, parseColor, type Rgba } from "../core"
import type { SourceHit, SourceRule } from "../rule"

const COLOR_LITERAL = /#[0-9a-fA-F]{3,8}\b|(?:rgba?|color|oklab|oklch|lab|lch)\([^()]*\)/gi
const MASKED_CALL = /^(?:var|url)\s*\(/i
const STYLESHEET_EXTENSIONS = ["css", "scss", "less", "pcss", "postcss"]
const LINE_COMMENT_EXTENSIONS = ["scss", "less"]

interface Span {
	readonly start: number
	readonly end: number
}

const sameColor = (a: Rgba, b: Rgba): boolean =>
	Math.abs(a.r - b.r) < 0.5 && Math.abs(a.g - b.g) < 0.5 && Math.abs(a.b - b.b) < 0.5 && Math.abs(a.a - b.a) < 0.005

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

const isIdentifierChar = (c: string): boolean => /[A-Za-z0-9_-]/.test(c)
const isSpace = (c: string): boolean => c === " " || c === "\t" || c === "\n" || c === "\r" || c === "\f"
const atBlockComment = (text: string, i: number): boolean => text[i] === "/" && text[i + 1] === "*"
const atLineComment = (text: string, i: number, lineComments: boolean): boolean => lineComments && text[i] === "/" && text[i + 1] === "/"

function skipBlockComment(text: string, from: number): number {
	const end = text.indexOf("*/", from + 2)
	return end === -1 ? text.length : end + 2
}

function skipLineComment(text: string, from: number): number {
	const end = text.indexOf("\n", from + 2)
	return end === -1 ? text.length : end
}

function skipString(text: string, from: number): number {
	const quote = text[from] ?? ""
	let i = from + 1
	while (i < text.length && text[i] !== quote) i += text[i] === "\\" ? 2 : 1
	return i + 1
}

/** Index just past a call's closing parenthesis, or `end` when it never closes. Escapes, comments and strings are honoured. */
function closeCall(text: string, from: number, end: number, lineComments: boolean): number {
	let i = from
	let parens = 0
	while (i < end) {
		const c = text[i] ?? ""
		if (c === "\\") {
			i += 2
			continue
		}
		if (atBlockComment(text, i)) {
			i = Math.min(end, skipBlockComment(text, i))
			continue
		}
		if (atLineComment(text, i, lineComments)) {
			i = Math.min(end, skipLineComment(text, i))
			continue
		}
		if (c === "\"" || c === "'") {
			i = Math.min(end, skipString(text, i))
			continue
		}
		if (c === "(") parens++
		else if (c === ")") {
			parens--
			if (parens === 0) return i + 1
		}
		i++
	}
	return end
}

/** Index just past the `}` matching the `{` at `from`, or `end`. Used to skip a custom property whose value is a block. */
function closeBrace(text: string, from: number, end: number, lineComments: boolean): number {
	let i = from
	let depth = 0
	while (i < end) {
		const c = text[i] ?? ""
		if (c === "\\") {
			i += 2
			continue
		}
		if (atBlockComment(text, i)) {
			i = Math.min(end, skipBlockComment(text, i))
			continue
		}
		if (atLineComment(text, i, lineComments)) {
			i = Math.min(end, skipLineComment(text, i))
			continue
		}
		if (c === "\"" || c === "'") {
			i = Math.min(end, skipString(text, i))
			continue
		}
		if (c === "{") depth++
		else if (c === "}") {
			depth--
			if (depth === 0) return i + 1
		}
		i++
	}
	return end
}

/** Index of `var(`/`url(` at `i`, or -1. A call is masked whole: its arguments may hold `;`, `{` or `//`. */
function maskedCallEnd(text: string, i: number, end: number, lineComments: boolean): number {
	if (i > 0 && isIdentifierChar(text[i - 1] ?? "")) return -1
	if (!MASKED_CALL.test(text.slice(i, Math.min(end, i + 8)))) return -1
	const open = text.indexOf("(", i)
	if (open === -1 || open >= end) return -1
	return closeCall(text, open, end, lineComments)
}

function skipTrivia(text: string, from: number, lineComments: boolean): number {
	let i = from
	while (i < text.length) {
		const c = text[i] ?? ""
		if (isSpace(c)) {
			i++
			continue
		}
		if (atBlockComment(text, i)) {
			i = skipBlockComment(text, i)
			continue
		}
		if (atLineComment(text, i, lineComments)) {
			i = skipLineComment(text, i)
			continue
		}
		break
	}
	return i
}

/** First index in [from, end) holding a terminator at parenthesis depth 0, or `end`. */
function skipTo(text: string, from: number, end: number, terminators: string, lineComments: boolean): number {
	let i = from
	let parens = 0
	while (i < end) {
		const c = text[i] ?? ""
		if (c === "\\") {
			i += 2
			continue
		}
		if (atBlockComment(text, i)) {
			i = Math.min(end, skipBlockComment(text, i))
			continue
		}
		if (atLineComment(text, i, lineComments)) {
			i = Math.min(end, skipLineComment(text, i))
			continue
		}
		if (c === "\"" || c === "'") {
			i = Math.min(end, skipString(text, i))
			continue
		}
		const callEnd = maskedCallEnd(text, i, end, lineComments)
		if (callEnd > i) {
			i = callEnd
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

/** First `:` in [from, to) at parenthesis depth 0, or -1. */
function topLevelColon(text: string, from: number, to: number, lineComments: boolean): number {
	let i = from
	let parens = 0
	while (i < to) {
		const c = text[i] ?? ""
		if (c === "\\") {
			i += 2
			continue
		}
		if (atBlockComment(text, i)) {
			i = Math.min(to, skipBlockComment(text, i))
			continue
		}
		if (atLineComment(text, i, lineComments)) {
			i = Math.min(to, skipLineComment(text, i))
			continue
		}
		if (c === "\"" || c === "'") {
			i = Math.min(to, skipString(text, i))
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
		if (c === ":" && parens === 0) return i
		i++
	}
	return -1
}

/** Sub-ranges of a declaration value that may hold a reportable literal: no comments, strings, `var()` or `url()`. */
function reportableSpans(text: string, start: number, end: number, lineComments: boolean): readonly Span[] {
	const spans: Span[] = []
	let chunk = start
	let i = start
	while (i < end) {
		const c = text[i] ?? ""
		if (atBlockComment(text, i) || atLineComment(text, i, lineComments)) {
			if (i > chunk) spans.push({ start: chunk, end: i })
			i = Math.min(end, atBlockComment(text, i) ? skipBlockComment(text, i) : skipLineComment(text, i))
			chunk = i
			continue
		}
		if (c === "\\") {
			i += 2
			continue
		}
		if (c === "\"" || c === "'") {
			if (i > chunk) spans.push({ start: chunk, end: i })
			i = Math.min(end, skipString(text, i))
			chunk = i
			continue
		}
		const callEnd = maskedCallEnd(text, i, end, lineComments)
		if (callEnd > i) {
			if (i > chunk) spans.push({ start: chunk, end: i })
			i = callEnd
			chunk = i
			continue
		}
		i++
	}
	if (end > chunk) spans.push({ start: chunk, end })
	return spans
}

/**
 * Declaration values of a stylesheet, in source order, excluding custom-property definitions. A statement
 * is a declaration only when it reaches `;` or `}` before any `{`; anything reaching `{` first is a nested
 * rule or block, so a prelude such as `&:hover` or `#abc` is never read as a property.
 */
function declarationValueSpans(text: string, lineComments: boolean): readonly Span[] {
	const spans: Span[] = []
	const n = text.length
	let i = 0
	let depth = 0
	while (i < n) {
		i = skipTrivia(text, i, lineComments)
		if (i >= n) break
		if (text[i] === "}") {
			if (depth > 0) depth--
			i++
			continue
		}
		const stop = skipTo(text, i, n, "{;}", lineComments)
		const terminator = stop < n ? (text[stop] ?? "") : ""
		if (terminator === "{") {
			const colon = topLevelColon(text, i, stop, lineComments)
			if ((colon === -1 ? "" : text.slice(i, colon).trim()).startsWith("--")) {
				i = closeBrace(text, stop, n, lineComments)
				const after = skipTrivia(text, i, lineComments)
				i = (text[after] ?? "") === ";" ? after + 1 : after
				continue
			}
			depth++
			i = stop + 1
			continue
		}
		const colon = topLevelColon(text, i, stop, lineComments)
		if (colon !== -1) {
			const name = text.slice(i, colon).trim()
			if (!name.startsWith("--") && !name.startsWith("@")) {
				spans.push(...reportableSpans(text, skipTrivia(text, colon + 1, lineComments), stop, lineComments))
			}
		}
		i = stop
		if (terminator === ";") i++
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
		const starts = lineStarts(file.text)
		const lineComments = LINE_COMMENT_EXTENSIONS.includes(extensionOf(file.path))
		for (const span of declarationValueSpans(file.text, lineComments)) {
			for (const match of file.text.slice(span.start, span.end).matchAll(COLOR_LITERAL)) {
				const offset = span.start + (match.index ?? 0)
				const color = parseColor(match[0])
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
