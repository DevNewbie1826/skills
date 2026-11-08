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
const css = (text: string): SourceFile => ({ path: "inline.css", text })
const lines = (file: SourceFile, tokens: readonly string[] = ["#1a5cff", "#14161a"]): readonly number[] =>
	hardCodedColor.check({ file, config: mergeTokenColors({}, tokens) }).map((hit) => hit.line)

describe("hard-coded-color", () => {
	test("#given no design tokens #then literals are silent", () => {
		const file = source("without-tokens/component.css")
		expect(hardCodedColor.check({ file, config: {} })).toEqual([])
		expect(lintSources([file])).toEqual([])
	})

	test("#given CSS tokens #then literals repeating a token fire and are located at the literal", () => {
		const file = source("with-tokens/component.css")
		const hits = hardCodedColor.check({ file, config: configFrom("tokens.css") })
		expect(hits.map((hit) => hit.line)).toEqual([2, 3, 7, 24])
		const body = file.text.split("\n")
		expect(hits.every((hit) => /^[\s]*[a-z-]+:/.test((body[hit.line - 1] ?? "").slice(0, hit.column - 1)))).toBe(true)
		expect(hits.map((hit) => hit.message)).toEqual([
			"Hard-coded #1a5cff is a design-token color; use the token instead.",
			"Hard-coded #14161a is a design-token color; use the token instead.",
			"Hard-coded #1a5cff is a design-token color; use the token instead.",
			"Hard-coded RGB(26 92 255) is a design-token color; use the token instead.",
		])
	})

	test("#given JSON tokens #then literals repeating a token fire", () => {
		expect(hardCodedColor.check({ file: source("with-tokens/component.css"), config: configFrom("tokens.json") }).map((hit) => hit.line)).toEqual([2, 3, 7, 24])
	})

	test("#given a literal with no matching token #then it is not reported", () => {
		const messages = hardCodedColor.check({ file: source("with-tokens/component.css"), config: configFrom("tokens.css") }).map((hit) => hit.message)
		expect(messages.some((message) => message.includes("#ff00aa"))).toBe(false)
	})

	test("#given token declarations, var() fallbacks, quoted strings and comments #then none of them are reported", () => {
		expect(hardCodedColor.check({ file: source("with-tokens/tokens.css"), config: configFrom("tokens.css") })).toEqual([])
		const reported = hardCodedColor.check({ file: source("with-tokens/component.css"), config: configFrom("tokens.css") }).map((hit) => hit.line)
		expect(reported).toEqual([2, 3, 7, 24])
	})

	test("#given a functional fallback inside var() #then the fallback is not reported", () => {
		expect(lines(css(".a { color: var(--brand, rgb(26 92 255)); }"))).toEqual([])
		expect(lines(css(".a { color: var(--brand, rgb(var(--r, 26) 92 255)); }"))).toEqual([])
		expect(lines(css(".a { color: rgb(26 92 255); }"))).toEqual([1])
	})

	test("#given a custom property next to a real declaration #then only the real declaration reports", () => {
		expect(lines(css(":root { --brand: #1a5cff; }\n.a { color: #1a5cff; }"))).toEqual([2])
	})

	test("#given selector text, quoted content and comments #then only declarations report", () => {
		const tokens = ["#1a5cff", "#14161a", "#fade", "#abc"]
		expect(lines(css("#abc, #fade .x{ color: #1a5cff; }"), tokens)).toEqual([1])
		expect(lines(css(".a { color: #1a5cff; }\n#fade { border-color: #14161a; }"), tokens)).toEqual([1, 2])
		expect(lines(css(".a { content: \"#1a5cff\"; }"), tokens)).toEqual([])
		expect(lines(css("/* #1a5cff */\n.a { color: #14161a; }"), tokens)).toEqual([2])
		expect(lines(source("with-tokens/id-selector.css"), [...tokens, "rgb(0 128 64)"])).toEqual([2, 7, 11])
	})

	test("#given a question mark before a hex run #then the question mark is not part of the match", () => {
		const hits = hardCodedColor.check({ file: css("a{background:url(a?#1a5cff)}"), config: mergeTokenColors({}, ["#1a5cff"]) })
		expect(hits.map((hit) => hit.message)).toEqual(["Hard-coded #1a5cff is a design-token color; use the token instead."])
	})

	test("#given the built-in registry #then the rule runs on stylesheet sources with project tokens", () => {
		expect(ALL_RULES.some((rule) => rule.meta.id === "hard-coded-color")).toBe(true)
		const findings = lintSources([source("with-tokens/component.css")], { config: configFrom("tokens.css") })
		expect(findings.map((finding) => [finding.ruleId, finding.severity, finding.location.kind])).toEqual([
			["hard-coded-color", "warning", "source"],
			["hard-coded-color", "warning", "source"],
			["hard-coded-color", "warning", "source"],
			["hard-coded-color", "warning", "source"],
		])
	})

	test("#given the rule switched off #then token literals are silent", () => {
		const config = { ...configFrom("tokens.css"), rules: { "hard-coded-color": "off" as const } }
		expect(lintSources([source("with-tokens/component.css")], { config })).toEqual([])
	})
})
