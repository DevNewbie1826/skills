export const extensionOf = (path: string): string => (/\.([a-z0-9]+)$/i.exec(path)?.[1] ?? "").toLowerCase()

/** CSS declaration blocks of a stylesheet-like text: selector plus raw body, with the body's start offset. */
export function cssBlocks(text: string): readonly { readonly selector: string; readonly body: string; readonly offset: number }[] {
	const stripped = text.replace(/\/\*[\s\S]*?\*\//g, (c) => " ".repeat(c.length))
	const out: { selector: string; body: string; offset: number }[] = []
	for (const m of stripped.matchAll(/([^{};]+)\{([^{}]*)\}/g)) {
		if (m.index === undefined) continue
		out.push({ selector: (m[1] ?? "").trim(), body: m[2] ?? "", offset: m.index + (m[1] ?? "").length + 1 })
	}
	return out
}
