import type { PageSnapshot } from "./types"
import { splitTop } from "./appearance"

type Frame = Readonly<Record<string, string>>
type KeyframeStep = { readonly key: string; readonly declarations: Frame }
export function keyframeSteps(s: PageSnapshot, name: string): readonly KeyframeStep[] | null {
	const frames: KeyframeStep[] = []
	let found = false
	for (const css of s.cssText) {
		const text = css.replace(/\/\*[\s\S]*?\*\//g, "")
		for (const m of text.matchAll(/@(?:-webkit-)?keyframes\s+([\w-]+)\s*\{/g)) {
			if (m[1] !== name) continue
			found = true
			let end = (m.index ?? 0) + m[0].length,
				depth = 1
			const start = end
			while (end < text.length && depth > 0) {
				if (text[end] === "{") depth++
				if (text[end] === "}") depth--
				end++
			}
			for (const step of text.slice(start, end - 1).matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
				const entries = (step[2] ?? "").split(";").flatMap((d) => {
					const i = d.indexOf(":")
					return i < 0 ? [] : [[d.slice(0, i).trim().toLowerCase(), d.slice(i + 1).trim()]]
				})
				frames.push({ key: (step[1] ?? "").trim(), declarations: Object.fromEntries(entries) })
			}
		}
	}
	return found ? frames : null
}
export function keyframes(s: PageSnapshot, name: string): readonly Frame[] | null {
	return keyframeSteps(s, name)?.map(step => step.declarations) ?? null
}
