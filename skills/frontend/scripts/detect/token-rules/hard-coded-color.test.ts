import { describe, expect, test } from "bun:test"
import { readFileSync } from "node:fs"
import { join } from "node:path"
import { fileURLToPath } from "node:url"
import { lintSources } from "../lint"
import { ALL_RULES } from "../rules"
import type { SourceFile } from "../types"
import { hardCodedColor } from "./hard-coded-color"
import { loadTokens, mergeTokenColors } from "./tokens"

const FIXTURE_DIR = fileURLToPath(new URL(["..", "fixtures", "token-rules", ""].join("/"), import.meta.url))
const source = (name: string): SourceFile => ({ path: join(FIXTURE_DIR, name), text: readFileSync(join(FIXTURE_DIR, name), "utf8") })
const configFrom = (name: string) => {
	const loaded = loadTokens(join(FIXTURE_DIR, "with-tokens", name))
	if (!loaded.ok) throw new Error(loaded.error)
	return mergeTokenColors({}, loaded.colors)
}

describe("hard-coded-color", () => {
	test("#given no design tokens #then literals are silent", () => {
		const file = source("without-tokens/component.css")
		expect(hardCodedColor.check({ file, config: {} })).toEqual([])
		expect(lintSources([file])).toEqual([])
	})

	test("#given CSS tokens #then literals repeating a token fire and are located at the literal", () => {
		const file = source("with-tokens/component.css")
		const hits = hardCodedColor.check({ file, config: configFrom("tokens.css") })
		expect(hits.map((hit) => hit.line)).toEqual([2, 3, 7])
		const lines = file.text.split("\n")
		expect(hits.every((hit) => (lines[hit.line - 1] ?? "").slice(hit.column - 1).startsWith("#"))).toBe(true)
		expect(hits.map((hit) => hit.message)).toEqual([
			"Hard-coded #1a5cff is a design-token color; use the token instead.",
			"Hard-coded #14161a is a design-token color; use the token instead.",
			"Hard-coded #1a5cff is a design-token color; use the token instead.",
		])
	})

	test("#given JSON tokens #then literals repeating a token fire", () => {
		expect(hardCodedColor.check({ file: source("with-tokens/component.css"), config: configFrom("tokens.json") }).map((hit) => hit.line)).toEqual([2, 3, 7])
	})

	test("#given a literal with no matching token #then it is not reported", () => {
		const messages = hardCodedColor.check({ file: source("with-tokens/component.css"), config: configFrom("tokens.css") }).map((hit) => hit.message)
		expect(messages.some((message) => message.includes("#ff00aa"))).toBe(false)
	})

	test("#given token declarations, var() fallbacks and comments #then none of them are reported", () => {
		expect(hardCodedColor.check({ file: source("with-tokens/tokens.css"), config: configFrom("tokens.css") })).toEqual([])
		const hits = hardCodedColor.check({ file: source("with-tokens/component.css"), config: configFrom("tokens.css") })
		expect(hits.some((hit) => [11, 19].includes(hit.line))).toBe(false)
	})

	test("#given the built-in registry #then the rule runs on CSS sources with project tokens", () => {
		expect(ALL_RULES.some((rule) => rule.meta.id === "hard-coded-color")).toBe(true)
		const findings = lintSources([source("with-tokens/component.css")], { config: configFrom("tokens.css") })
		expect(findings.map((finding) => [finding.ruleId, finding.severity, finding.location.kind])).toEqual([
			["hard-coded-color", "warning", "source"],
			["hard-coded-color", "warning", "source"],
			["hard-coded-color", "warning", "source"],
		])
	})

	test("#given a hex-looking id that is also a token color #then the selector itself is never reported", () => {
		const config = mergeTokenColors(configFrom("tokens.css"), ["#fade"])
		const hits = hardCodedColor.check({ file: source("with-tokens/id-selector.css"), config })
		expect(hits.map((hit) => hit.line)).toEqual([2, 7])
		expect(hits.every((hit) => !hit.snippet.startsWith("#"))).toBe(true)
	})

	test("#given the rule switched off #then token literals are silent", () => {
		const config = { ...configFrom("tokens.css"), rules: { "hard-coded-color": "off" as const } }
		expect(lintSources([source("with-tokens/component.css")], { config })).toEqual([])
	})
})
