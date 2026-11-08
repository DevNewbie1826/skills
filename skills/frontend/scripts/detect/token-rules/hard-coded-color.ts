import { extensionOf, parseColor, type Rgba } from "../core"
import type { SourceHit, SourceRule } from "../rule"

const COLOR_LITERAL = /#[0-9a-fA-F]{3,8}\b|(?:rgba?|color|oklab|oklch|lab|lch)\([^()]*\)/gi
const MASKED_CALL = /^(?:var|url)\s*\(/i
const POISON = "\u0001"
const URL_CALL = /^url\s*\(/i
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

/**
 * Index just past a `var()`/`url()` call starting at `i`, or -1. `//` inside `url()` is never a line
 * comment: a protocol-relative or scheme URL would otherwise swallow the rest of the file.
 */
function maskedCallEnd(text: string, i: number, end: number, lineComments: boolean): number {
	if (i > 0 && isIdentifierChar(text[i - 1] ?? "")) return -1
	if (!MASKED_CALL.test(text.slice(i, Math.min(end, i + 8)))) return -1
	const open = text.indexOf("(", i)
	if (open === -1 || open >= end) return -1
	const inUrl = URL_CALL.test(text.slice(i, Math.min(end, i + 8)))
	return closeCall(text, open, end, inUrl ? false : lineComments)
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

/** First index in [from, end) holding a terminator at nesting depth 0, or `end`. */
function skipTo(text: string, from: number, end: number, terminators: string, lineComments: boolean): number {
	let i = from
	let parens = 0
	let brackets = 0
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
		const callEnd = maskedCallEnd(text, i, end, lineComments)
		if (callEnd > i) {
			i = callEnd
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
		if (c === "[") {
			brackets++
			i++
			continue
		}
		if (c === "]") {
			if (brackets > 0) brackets--
			i++
			continue
		}
		if (parens === 0 && brackets === 0 && terminators.includes(c)) return i
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

/**
 * Index at which a custom property that starts a block value ends: past the `;` that closes its
 * declaration, or at the `}` closing the enclosing rule. Per CSS a custom property value runs to the next
 * top-level `;`, so text after its block is still part of the value, not a declaration of its own.
 */
function endOfCustomProperty(text: string, from: number, end: number, lineComments: boolean): number {
	let i = from
	let braces = 0
	let parens = 0
	let brackets = 0
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
		const callEnd = maskedCallEnd(text, i, end, lineComments)
		if (callEnd > i) {
			i = callEnd
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
		if (c === "[") {
			brackets++
			i++
			continue
		}
		if (c === "]") {
			if (brackets > 0) brackets--
			i++
			continue
		}
		if (c === "{") {
			braces++
			i++
			continue
		}
		if (c === "}") {
			if (braces === 0 && parens === 0 && brackets === 0) return i
			if (braces > 0) braces--
			i++
			continue
		}
		if (c === ";" && braces === 0 && parens === 0 && brackets === 0) return i + 1
		i++
	}
	return end
}

/**
 * The value with every non-reportable region overwritten: comments and escapes become spaces, because they
 * are whitespace to a CSS parser and a functional color stays whole around them; `var()`, `url()` and
 * strings become `POISON`, a character that cannot parse as a number, so a color overlapping substituted
 * content is unparseable instead of invented. Blanking those to spaces would turn `rgb(var(--r) 92 255)`
 * into `rgb(92 255)` and report a color the declaration never had. Replacement is same-length, so offsets
 * stay aligned with the source.
 */
function maskedValue(text: string, start: number, end: number, lineComments: boolean): string {
	const chars = text.slice(start, end).split("")
	const blank = (from: number, to: number, fill: string): void => {
		for (let k = Math.max(0, from); k < Math.min(chars.length, to); k++) chars[k] = fill
	}
	let i = 0
	while (i < chars.length) {
		const abs = start + i
		if (text[abs] === "\\") {
			blank(i, i + 2, " ")
			i += 2
			continue
		}
		if (atBlockComment(text, abs)) {
			const stop = Math.min(end, skipBlockComment(text, abs))
			blank(i, stop - start, " ")
			i = stop - start
			continue
		}
		const callEnd = maskedCallEnd(text, abs, end, lineComments)
		if (callEnd > abs) {
			blank(i, callEnd - start, POISON)
			i = callEnd - start
			continue
		}
		if (atLineComment(text, abs, lineComments)) {
			const stop = Math.min(end, skipLineComment(text, abs))
			blank(i, stop - start, " ")
			i = stop - start
			continue
		}
		if (text[abs] === "\"" || text[abs] === "'") {
			const stop = Math.min(end, skipString(text, abs))
			blank(i, stop - start, POISON)
			i = stop - start
			continue
		}
		i++
	}
	return chars.join("")
}

/**
 * Value ranges of declarations, in source order, excluding custom-property definitions. A statement is a
 * declaration only when it reaches `;` or `}` before any `{`; reaching `{` first makes it a nested rule or
 * block, so a selector prelude such as `&:hover` or `#abc` is never read as a property name or a value.
 */
function declarationValueRanges(text: string, lineComments: boolean): readonly Span[] {
	const ranges: Span[] = []
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
			const name = colon === -1 ? "" : text.slice(i, colon).trim()
			if (name.startsWith("--")) {
				i = endOfCustomProperty(text, stop, n, lineComments)
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
				ranges.push({ start: skipTrivia(text, colon + 1, lineComments), end: stop })
			}
		}
		i = stop
		if (terminator === ";") i++
	}
	return ranges
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
