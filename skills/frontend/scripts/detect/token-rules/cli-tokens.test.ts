import { describe, expect, test } from "bun:test"
import { join } from "node:path"
import { fileURLToPath } from "node:url"

const CLI = fileURLToPath(new URL(["..", "cli.ts"].join("/"), import.meta.url))
const FIXTURE_DIR = fileURLToPath(new URL(["..", "fixtures", "token-rules", "with-tokens", ""].join("/"), import.meta.url))
const component = join(FIXTURE_DIR, "component.css")
const tokens = join(FIXTURE_DIR, "tokens.css")

type Run = { readonly code: number; readonly stdout: string; readonly stderr: string }

async function run(args: readonly string[], configPath?: string): Promise<Run> {
	const argv = configPath ? [CLI, ...args, "--config", configPath] : [CLI, ...args]
	const child = Bun.spawn(["bun", ...argv], { stdout: "pipe", stderr: "pipe" })
	const [stdout, stderr, code] = await Promise.all([new Response(child.stdout).text(), new Response(child.stderr).text(), child.exited])
	return { code, stdout, stderr }
}

describe("cli token flags", () => {
	test("#given no --tokens flag #then token literals stay silent", async () => {
		const result = await run(["--json", component])
		expect(result.code).toBe(0)
		expect(JSON.parse(result.stdout)).toEqual([])
	})

	test("#given --tokens with a CSS tokens file #then the rule reports the token literals", async () => {
		const result = await run(["--json", "--tokens", tokens, component])
		expect(result.code).toBe(1)
		expect(JSON.parse(result.stdout).map((finding: { ruleId: string }) => finding.ruleId)).toEqual([
			"hard-coded-color", "hard-coded-color", "hard-coded-color", "hard-coded-color",
		])
	})

	test("#given --tokens before --config #then the config does not drop the loaded tokens", async () => {
		const configPath = join(FIXTURE_DIR, "config.json")
		const result = await run(["--json", "--tokens", tokens, component], configPath)
		expect(result.code).toBe(1)
		expect(JSON.parse(result.stdout).length).toBe(4)
	})

	test("#given a missing tokens file #then the CLI exits 2 with a message naming it", async () => {
		const result = await run(["--json", "--tokens", join(FIXTURE_DIR, "absent.css"), component])
		expect(result.code).toBe(2)
		expect(result.stderr).toContain("absent.css")
	})
})
