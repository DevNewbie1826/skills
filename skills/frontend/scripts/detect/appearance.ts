import { ancestors, isRendered, px, styleOf } from "./core"
import type { ElementSnapshot, PageSnapshot } from "./types"

export const sides = ["top", "right", "bottom", "left"] as const
export const corners = ["top-left", "top-right", "bottom-right", "bottom-left"] as const
export const length = (value: string): number => px(value) ?? (value.trim() === "0" ? 0 : Number.NaN)
const radius = (el: ElementSnapshot, corner: string): number => {
	const parts = styleOf(el, "border-" + corner + "-radius").split(/\s+/)
	const values = parts.map((v) => (v.endsWith("%") ? (Number.parseFloat(v) * Math.min(el.rect.width, el.rect.height)) / 100 : length(v)))
	return Math.min(...values)
}
export const radii = (el: ElementSnapshot): readonly number[] => corners.map((c) => radius(el, c))
export const visible = (s: PageSnapshot, e: ElementSnapshot): boolean =>
	isRendered(s, e) &&
	[e, ...ancestors(s, e)].every(
		(a) => styleOf(a, "display") !== "none" && styleOf(a, "visibility") !== "hidden" && a.attributes["hidden"] === undefined,
	)
export const context = (s: PageSnapshot, e: ElementSnapshot, predicate: (e: ElementSnapshot) => boolean): boolean =>
	[e, ...ancestors(s, e)].some(predicate)
export const selected = (e: ElementSnapshot): boolean =>
	e.attributes["aria-selected"] === "true" ||
	(e.attributes["aria-current"] !== undefined && e.attributes["aria-current"] !== "false") ||
	/^(selected|active|checked|current)$/i.test(e.attributes["data-state"] ?? e.attributes["data-status"] ?? "") ||
	/(?:^|[\s_-])(?:selected|current|checked|active)(?:$|[\s_-])/.test(e.attributes["class"] ?? "")
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
