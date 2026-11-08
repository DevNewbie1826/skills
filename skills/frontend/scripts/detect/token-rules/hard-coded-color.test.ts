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
const cliFindingMessage = (text: string, tokens: readonly string[]): readonly string[] =>
	hardCodedColor.check({ file: css(text), config: mergeTokenColors({}, tokens) }).map((hit) => hit.message)

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
		const hits = hardCodedColor.check({ file: css("a{background:#1a5cff?x}"), config: mergeTokenColors({}, ["#1a5cff"]) })
		expect(hits.map((hit) => hit.message)).toEqual(["Hard-coded #1a5cff is a design-token color; use the token instead."])
	})

	test("#given a comment holding an unbalanced function or brace #then later declarations still report", () => {
		expect(lines(css("/* var( */ .a { color: #1a5cff; }"))).toEqual([1])
		expect(lines(css("/* { */ .a { color: #1a5cff; }"))).toEqual([1])
		expect(lines(css(".a { /* { */ color: #1a5cff; }"))).toEqual([1])
		expect(lines(css("/* ) */ .a { color: #1a5cff; }"))).toEqual([1])
	})

	test("#given a multi-line custom property #then the declaration is not reported but a real use is", () => {
		expect(lines(css(":root {\n  --brand:\n    #1a5cff;\n}\n.a { color: #1a5cff; }"))).toEqual([5])
	})

	test("#given a comment inside a var() fallback #then the parentheses still balance", () => {
		expect(lines(css(".a { color: var(--brand, /* ) */ #1a5cff); }"))).toEqual([])
		expect(lines(css(".a { color: rgb(26 92 255); }"))).toEqual([1])
	})

	test("#given a url() with a hex-looking fragment #then the fragment is not reported", () => {
		expect(lines(css(".a { background-image: url(sprite.svg#1a5cff); }"))).toEqual([])
		expect(lines(css(".a { background: url(sprite.svg#1a5cff) #1a5cff; }"))).toEqual([1])
	})

	test("#given thousands of hits in one large stylesheet #then location lookup stays linear", () => {
		const block = ".card { border: 1px solid #1a5cff; color: var(--ink, #1a5cff); /* note */ }\n"
		const file = css(block.repeat(20000))
		const started = performance.now()
		const hits = hardCodedColor.check({ file, config: mergeTokenColors({}, ["#1a5cff"]) })
		const elapsed = performance.now() - started
		expect(hits.length).toBe(20000)
		expect(elapsed).toBeLessThan(5000)
		expect(hits.at(-1)?.line).toBe(20000)
		expect(hits.at(-1)?.snippet).toBe(".card { border: 1px solid #1a5cff; color: var(--ink, #1a5cff); /* note */ }")
	})

	test("#given a nested pseudo-selector #then the nested rule reports and the following declaration is still found", () => {
		const tokens = ["#1a5cff", "#14161a", "#abc"]
		expect(lines(css(".a { &:hover { color: #1a5cff; } color: #14161a; }"), tokens)).toEqual([1, 1])
		expect(lines(css(".a { &:hover #abc { color: #1a5cff; } }"), tokens)).toEqual([1])
		expect(cliFindingMessage(".a { &:hover #abc { color: #14161a; } }", tokens).join(" ")).not.toContain("#abc")
	})

	test("#given a custom property whose value is a block #then the block is skipped and the next declaration reports", () => {
		expect(lines(css(":root { --bundle: { color: #1a5cff; background: #14161a; }; color: #1a5cff; }"))).toEqual([1])
	})

	test("#given an escaped parenthesis in url() #then the fragment is not reported", () => {
		expect(lines(css(".a { background-image: url(sprite\\)x.svg#1a5cff); }"))).toEqual([])
	})

	test("#given a scss or less line comment #then the declaration after it is still found", () => {
		const file = (path: string, text: string) => ({ path, text })
		const tokens = mergeTokenColors({}, ["#1a5cff", "#14161a"])
		expect(hardCodedColor.check({ file: file("x.scss", ".a { // color: #1a5cff\n color: #14161a; }"), config: tokens }).map((hit) => hit.line)).toEqual([2])
		expect(hardCodedColor.check({ file: file("x.less", ".a { // color: #1a5cff\n color: #14161a; }"), config: tokens }).map((hit) => hit.line)).toEqual([2])
		expect(hardCodedColor.check({ file: file("x.css", ".a { // color: #1a5cff\n color: #14161a; }"), config: tokens }).length).toBeGreaterThan(0)
	})

	test("#given a url() in a scss or less file #then its slashes are not a line comment", () => {
		const tokens = mergeTokenColors({}, ["#1a5cff", "#14161a"])
		const scss = hardCodedColor.check({ file: { path: "x.scss", text: ".a { background: url(https://assets.test/x.svg) #1a5cff; color: #14161a; }" }, config: tokens })
		expect(scss.map((hit) => hit.line)).toEqual([1, 1])
		const less = hardCodedColor.check({ file: { path: "x.less", text: ".a { background: url(//cdn.test/x.svg) #1a5cff; color: #14161a; }" }, config: tokens })
		expect(less.map((hit) => hit.line)).toEqual([1, 1])
	})

	test("#given a custom property whose block value ends mid-rule #then the following text stays its value", () => {
		expect(lines(css(":root { --bundle: { color: #1a5cff; } color: #14161a; }"))).toEqual([])
		expect(lines(css(":root { --bundle: { color: #1a5cff; }; color: #14161a; }"))).toEqual([1])
	})

	test("#given a functional color interrupted by a comment #then the color still matches", () => {
		expect(lines(css(".a { color: rgb(26 /* note */ 92 255); }"))).toEqual([1])
		expect(lines(css(".a { color: rgb(26/* note */ 92/* note */255); }"))).toEqual([1])
		expect(lines(css(".a { color: rgb(26 /* a\nb */ 92 255); }"))).toEqual([1])
	})

	test("#given a var() inside a functional color #then no color is invented from what remains", () => {
		expect(lines(css(":root { --r: 26; } .a { color: rgb(var(--r) 92 255); }"), ["#5cff00", "#1a5cff", "#14161a"])).toEqual([])
		expect(lines(css(".a { color: rgb(26 var(--g) 255); }"), ["#1a5cff", "#1aff00"])).toEqual([])
	})

	test("#given a string inside a functional color #then no color is invented from what remains", () => {
		expect(lines(css(".a { color: rgb(\"26\" 92 255); }"), ["#5cff00"])).toEqual([])
		expect(lines(css(".a { color: rgb(26 92 255 / \"1\"); }"), ["#1a5cff"])).toEqual([])
	})

	test("#given a custom property value with parentheses #then its semicolons do not end it", () => {
		expect(lines(css(":root { --bundle: { a: b; } foo(a; b: #1a5cff); }"))).toEqual([])
		expect(lines(css(":root { --b: foo(a; b); color: #14161a; }"))).toEqual([1])
	})

	test("#given a custom property value with brackets #then its semicolons do not end it", () => {
		expect(lines(css(":root { --bundle: [a; b: #1a5cff]; color: #14161a; }"))).toEqual([1])
		expect(lines(css(":root { --bundle: { a: b; } [a; b: #1a5cff]; color: #14161a; }"))).toEqual([1])
		expect(lines(css(":root { --b: [[a; b: #1a5cff]]; color: #14161a; }"))).toEqual([1])
	})

	test("#given a source color that is not valid CSS #then nothing is invented from it", () => {
		expect(lines(css(".a { color: rgb(26\\x 92 255); }"))).toEqual([])
		expect(lines(css(".a { color: rgb(26 92 255garbage); }"))).toEqual([])
		expect(lines(css(".a { color: myrgb(26 92 255); }"))).toEqual([])
	})

	test("#given an angle unit outside the hue slot #then the color is not invented", () => {
		expect(lines(css(".a { color: oklch(50% 0.1turn 30); }"), ["oklch(50% 0.1 30)"])).toEqual([])
		expect(lines(css(".a { color: lch(50% 20deg 30); }"), ["lch(50% 20 30)"])).toEqual([])
		expect(lines(css(".a { color: oklch(50% 0.1 30 / 0.5turn); }"), ["oklch(50% 0.1 30 / 0.5turn)"])).toEqual([])
	})

	test("#given a hue carrying an angle unit #then the color is still reported", () => {
		expect(lines(css(".a { color: lch(50% 20 30deg); }"), ["lch(50% 20 30deg)"])).toEqual([1])
		expect(lines(css(".a { color: oklch(50% 0.1 30deg); }"), ["oklch(50% 0.1 30deg)"])).toEqual([1])
		expect(lines(css(".a { color: oklch(0.5 0.1 0.5turn); }"), ["oklch(0.5 0.1 0.5turn)"])).toEqual([1])
	})

	test("#given an escaped function or custom-property name #then it is decoded before matching", () => {
		expect(lines(css(":root { --brand: #14161a; } .a { color: v\\61 r(--brand, #1a5cff); }"))).toEqual([])
		expect(lines(css(":root { \\2d -brand: #1a5cff; }"))).toEqual([])
		expect(lines(css(":root { \\2d -brand: { a: #1a5cff; } }"))).toEqual([])
		expect(lines(css(":root { --brand: #14161a; } .a { color: var(--brand, #1a5cff); }"))).toEqual([])
	})

	test("#given a bracketed selector prelude #then its brackets do not hide the declaration", () => {
		expect(lines(css("[a; b: #1a5cff] { color: #14161a; }"))).toEqual([1])
		expect(lines(css("[data-x=\"a;b\"] { color: #14161a; }"))).toEqual([1])
	})

	test("#given a color written across lines #then it is still reported", () => {
		expect(lines(css(".a { color: rgb(\n 26 92 255\n); }"))).toEqual([1])
		expect(lines(css(".a { color:\n #14161a; }"))).toEqual([2])
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
