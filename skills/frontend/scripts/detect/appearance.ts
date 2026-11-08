export function splitTop(value: string, separator: RegExp = /,/): string[] {
	let depth = 0,
		start = 0
	const parts: string[] = []
	for (let i = 0; i < value.length; i++) {
		const c = value[i] ?? ""
		if (c === "(") depth++
		else if (c === ")") depth--
		else if (depth === 0 && separator.test(c)) {
			parts.push(value.slice(start, i).trim())
			start = i + 1
		}
	}
	parts.push(value.slice(start).trim())
	return parts.filter(Boolean)
}
