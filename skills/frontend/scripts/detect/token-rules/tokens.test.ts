import { describe, expect, test } from "bun:test"
import { join } from "node:path"
import { fileURLToPath } from "node:url"
import { loadTokens, mergeTokenColors } from "./tokens"

const FIXTURE_DIR = fileURLToPath(new URL(["..", "fixtures", "token-rules", "with-tokens", ""].join("/"), import.meta.url))
const fixture = (name: string): string => join(FIXTURE_DIR, name)

describe("loadTokens", () => {
	test("#given no tokens argument #then the loader returns no colors", () => {
		expect(loadTokens()).toEqual({ ok: true, colors: [] })
	})

	test("#given a CSS custom-property file #then only declared colors load, including uppercase function forms", () => {
		expect(loadTokens(fixture("tokens.css"))).toEqual({ ok: true, colors: ["#1a5cff", "#14161a", "RGB(0 128 64)"] })
	})

	test("#given a JSON tokens tree #then colors load at any depth", () => {
		expect(loadTokens(fixture("tokens.json"))).toEqual({ ok: true, colors: ["#1a5cff", "#14161a", "RGB(0 128 64)"] })
	})

	test("#given a CSS file with quoted and unquoted values #then only the unquoted color loads", () => {
		const file = join(FIXTURE_DIR, "quoted-string.css")
		expect(loadTokens(file)).toEqual({ ok: true, colors: ["#1a5cff"] })
	})

	test("#given a missing file #then the loader reports it instead of empty tokens", () => {
		const loaded = loadTokens(fixture("absent.css"))
		expect(loaded.ok).toBe(false)
	})

	test("#given a malformed JSON tokens file #then the loader reports it instead of empty tokens", () => {
		const loaded = loadTokens(fixture("broken.json"))
		expect(loaded.ok).toBe(false)
	})
})

describe("mergeTokenColors", () => {
	test("#given config colors in another notation #then an equivalent token color is not appended twice", () => {
		const config = { designTokens: { colors: ["#1A5CFF"], radii: [8] } }
		expect(mergeTokenColors(config, ["#1a5cff", "#14161a"])).toEqual({
			designTokens: { colors: ["#1A5CFF", "#14161a"], radii: [8] },
		})
	})

	test("#given a functional color equivalent to a hex token #then it is not appended twice", () => {
		expect(mergeTokenColors({ designTokens: { colors: ["#1a5cff"] } }, ["rgb(26 92 255)", "RGB(26, 92, 255)"])).toEqual({
			designTokens: { colors: ["#1a5cff"] },
		})
	})

	test("#given no loaded colors #then the config is returned unchanged", () => {
		const config = { designTokens: { colors: ["#1a5cff"] } }
		expect(mergeTokenColors(config, [])).toBe(config)
	})
})
