#!/usr/bin/env bun
// Thin CLI over the detect SDK (index.ts). Usage:
//   bun cli.ts [--json] [--reflow] [--config <file.json>] [--tokens <file>] <file-or-dir-or-url>...
// Exit 0 no error or warning findings, 1 findings that fail the gate, 2 usage or render failure.
import { readFileSync } from "node:fs"
import { collectFiles } from "../perfection"
import { type DetectConfig, detectFiles, detectPage, type Finding, formatFindingsText, hasFailures, loadTokens, mergeTokenColors, parseConfig, RenderError, sortFindings } from "./index"

const USAGE = "usage: cli.ts [--json] [--reflow] [--config <file.json>] [--tokens <file>] [--help] <file-or-dir-or-url>..."
const HELP = [
	USAGE,
	"  --json                 print findings as JSON",
	"  --reflow               also render the reflow viewport matrix",
	"  --config <file.json>   read rule severities and tokens from a config file",
	"  --tokens <file>        read design tokens from a CSS custom-property or JSON tokens file",
	"  --help                 print this help and exit",
].join("\n")

type Args = { readonly json: boolean; readonly reflow: boolean; readonly config: DetectConfig; readonly targets: readonly string[] }

function readConfig(path: string): DetectConfig | string {
	let raw: unknown
	try {
		raw = JSON.parse(readFileSync(path, "utf8"))
	} catch (error) {
		// no-excuse-ok: catch (CLI boundary: an unreadable or malformed config file is a usage error reported as exit 2)
		if (error instanceof Error) return error.message
		throw error
	}
	return parseConfig(raw)
}

function parseArgs(argv: readonly string[]): Args | "help" | string {
	let json = false
	let reflow = false
	let config: DetectConfig = {}
	const tokenColors: string[] = []
	const targets: string[] = []
	for (let i = 0; i < argv.length; i++) {
		const a = argv[i] ?? ""
		if (a === "--help" || a === "-h") return "help"
		else if (a === "--json") json = true
		else if (a === "--reflow") reflow = true
		else if (a === "--config") {
			const path = argv[++i]
			if (!path) return "--config needs a file"
			const parsed = readConfig(path)
			if (typeof parsed === "string") return `${path}: ${parsed}`
			config = parsed
		} else if (a === "--tokens") {
			const path = argv[++i]
			if (!path) return "--tokens needs a file"
			const loaded = loadTokens(path)
			if (!loaded.ok) return `${path}: ${loaded.error}`
			tokenColors.push(...loaded.colors)
		} else targets.push(a)
	}
	// Merged after the loop so the flag order between --config and --tokens cannot drop either one.
	config = mergeTokenColors(config, tokenColors)
	return targets.length === 0 ? "no targets" : { json, reflow, config, targets }
}

async function main(argv: readonly string[]): Promise<number> {
	const args = parseArgs(argv)
	if (args === "help") {
		process.stdout.write(`${HELP}\n`)
		return 0
	}
	if (typeof args === "string") {
		process.stderr.write(`frontend-detect: ${args}\n${USAGE}\n`)
		return 2
	}
	const urls = args.targets.filter((t) => /^https?:\/\//.test(t))
	const { paths, missing } = collectFiles(args.targets.filter((t) => !urls.includes(t)))
	if (missing.length > 0) {
		process.stderr.write(`frontend-detect: cannot read ${missing.join(", ")}\n`)
		return 2
	}
	const options = { config: args.config, reflow: args.reflow }
	const findings: Finding[] = [...(await detectFiles(paths, options))]
	for (const url of urls) findings.push(...(await detectPage({ kind: "url", url }, { ...options, file: url })))
	const sorted = sortFindings(findings)
	process.stdout.write(args.json ? `${JSON.stringify(sorted, null, 2)}\n` : formatFindingsText(sorted))
	return hasFailures(sorted) ? 1 : 0
}

try {
	process.exitCode = await main(process.argv.slice(2))
} catch (error) {
	// no-excuse-ok: catch (CLI boundary: a render failure is reported as exit 2, anything else propagates)
	if (!(error instanceof RenderError)) throw error
	process.stderr.write(`frontend-detect: ${error.message}\n`)
	process.exitCode = 2
}
