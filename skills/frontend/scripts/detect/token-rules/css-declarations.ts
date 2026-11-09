import { atBlockComment, atLineComment, decoded, maskedCallEnd, skipBlockComment, skipLineComment, skipString, skipTrivia } from "./css-tokenizer"

interface Span {
	readonly start: number
	readonly end: number
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
 * Value ranges of declarations, in source order, excluding custom-property definitions. A statement is a
 * declaration only when it reaches `;` or `}` before any `{`; reaching `{` first makes it a nested rule or
 * block, so a selector prelude such as `&:hover` or `#abc` is never read as a property name or a value.
 */
export function declarationValueRanges(text: string, lineComments: boolean): readonly Span[] {
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
			const name = colon === -1 ? "" : decoded(text.slice(i, colon).trim())
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
			const name = decoded(text.slice(i, colon).trim())
			if (!name.startsWith("--") && !name.startsWith("@")) {
				ranges.push({ start: skipTrivia(text, colon + 1, lineComments), end: stop })
			}
		}
		i = stop
		if (terminator === ";") i++
	}
	return ranges
}
