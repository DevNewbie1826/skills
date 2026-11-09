// Lexical scanner for stylesheet-like text: comments, strings, escapes, var()/url() calls and trivia.
// Every function works on raw source offsets so callers can keep positions aligned with the file they read.

const MASKED_CALL = /^(?:var|url)\s*\(/i
const POISON = "\u0001"
const URL_CALL = /^url\s*\(/i

const isIdentifierChar = (c: string): boolean => /[A-Za-z0-9_-]/.test(c)

/** The character a CSS escape denotes, or a replacement when the escape is malformed or a hex escape runs past its terminator. */
function decodeEscape(text: string, at: number): { readonly char: string; readonly next: number } {
	const hex = /^[0-9a-f]{1,6}/i.exec(text.slice(at + 1, at + 7))
	if (hex) {
		const stop = at + 1 + hex[0].length
		const after = text[stop] === " " || text[stop] === "\t" || text[stop] === "\n" ? stop + 1 : stop
		const code = Number.parseInt(hex[0], 16)
		return { char: code > 0 && code <= 0x10ffff ? String.fromCodePoint(code) : "\u0001", next: after }
	}
	if (at + 1 >= text.length) return { char: "\u0001", next: text.length }
	return { char: text[at + 1] ?? "\u0001", next: at + 2 }
}

/** The identifier text with CSS escapes decoded, so `v\61 r` is recognised as `var` and `\2d -brand` as `--brand`. */
export function decoded(text: string, limit = 64): string {
	let out = ""
	let i = 0
	while (i < text.length && out.length < limit) {
		if (text[i] === "\\") {
			const step = decodeEscape(text, i)
			out += step.char
			i = step.next
			continue
		}
		out += text[i] ?? ""
		i++
	}
	return out
}

const isSpace = (c: string): boolean => c === " " || c === "\t" || c === "\n" || c === "\r" || c === "\f"
export const atBlockComment = (text: string, i: number): boolean => text[i] === "/" && text[i + 1] === "*"
export const atLineComment = (text: string, i: number, lineComments: boolean): boolean => lineComments && text[i] === "/" && text[i + 1] === "/"

export function skipBlockComment(text: string, from: number): number {
	const end = text.indexOf("*/", from + 2)
	return end === -1 ? text.length : end + 2
}

export function skipLineComment(text: string, from: number): number {
	const end = text.indexOf("\n", from + 2)
	return end === -1 ? text.length : end
}

export function skipString(text: string, from: number): number {
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
export function maskedCallEnd(text: string, i: number, end: number, lineComments: boolean): number {
	if (i > 0 && isIdentifierChar(text[i - 1] ?? "")) return -1
	const ahead = decoded(text.slice(i, Math.min(end, i + 16)))
	if (!MASKED_CALL.test(ahead)) return -1
	const paren = text.indexOf("(", i)
	if (paren === -1 || paren >= end) return -1
	const inUrl = URL_CALL.test(ahead)
	return closeCall(text, paren, end, inUrl ? false : lineComments)
}

export function skipTrivia(text: string, from: number, lineComments: boolean): number {
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

/**
 * The value with every non-reportable region overwritten: comments and escapes become spaces, because they
 * are whitespace to a CSS parser and a functional color stays whole around them; `var()`, `url()` and
 * strings become `POISON`, a character that cannot parse as a number, so a color overlapping substituted
 * content is unparseable instead of invented. Blanking those to spaces would turn `rgb(var(--r) 92 255)`
 * into `rgb(92 255)` and report a color the declaration never had. Replacement is same-length, so offsets
 * stay aligned with the source.
 */
export function maskedValue(text: string, start: number, end: number, lineComments: boolean): string {
	const chars = text.slice(start, end).split("")
	const blank = (from: number, to: number, fill: string): void => {
		for (let k = Math.max(0, from); k < Math.min(chars.length, to); k++) chars[k] = fill
	}
	let i = 0
	while (i < chars.length) {
		const abs = start + i
		if (text[abs] === "\\") {
			blank(i, i + 2, POISON)
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
