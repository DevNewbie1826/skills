import { parseColor, WHITE, type Rgba } from "../core"
import { ancestors, styleOf } from "../core"
import type { ElementSnapshot, PageSnapshot } from "../types"

export function splitLayers(value: string): readonly string[] {
	const parts: string[] = []
	let depth = 0
	let start = 0
	for (let i = 0; i < value.length; i++) {
		if (value[i] === "(") depth++
		if (value[i] === ")") depth--
		if (value[i] === "," && depth === 0) {
			parts.push(value.slice(start, i).trim())
			start = i + 1
		}
	}
	parts.push(value.slice(start).trim())
	return parts.filter(Boolean)
}

type Stop = { readonly color: Rgba; readonly position: number | null; readonly raw: string }

export function gradientStops(value: string): readonly Stop[] {
	const out: Stop[] = []
	for (const layer of splitLayers(value)) {
		if (!/gradient\(/i.test(layer)) continue
		for (const raw of splitLayers(layer.slice(layer.indexOf("(") + 1, -1))) {
			const match = /^(rgba?|color|oklab|oklch)\([^()]*\)|^#[0-9a-f]{3,8}\b|^transparent\b|^(white|black)\b/i.exec(raw)
			if (!match) continue
			const literal = match[0].toLowerCase()
			const color = literal === "white" ? WHITE : literal === "black" ? { r: 0, g: 0, b: 0, a: 1 } : parseColor(literal)
			if (!color) continue
			const position = /(-?\d*\.?\d+)%/.exec(raw.slice(match[0].length))
			out.push({ color, raw, position: position ? Number(position[1]) / 100 : null })
		}
	}
	return out
}

export const spread = (c: Rgba): number => Math.max(c.r, c.g, c.b) - Math.min(c.r, c.g, c.b)
export const opacity = (el: ElementSnapshot): number => {
	const n = Number.parseFloat(styleOf(el, "opacity"))
	return Number.isFinite(n) ? Math.max(0, Math.min(1, n)) : 1
}
export const effectiveOpacity = (snapshot: PageSnapshot, el: ElementSnapshot): number =>
	[el, ...ancestors(snapshot, el)].reduce((v, node) => v * opacity(node), 1)

export function oklch(c: Rgba): { readonly l: number; readonly c: number } {
	const linear = (v: number): number => v / 255 <= 0.04045 ? v / 255 / 12.92 : ((v / 255 + 0.055) / 1.055) ** 2.4
	const [r, g, b] = [linear(c.r), linear(c.g), linear(c.b)]
	const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
	const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
	const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
	return { l: 0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s, c: Math.hypot(1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s, 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s) }
}
