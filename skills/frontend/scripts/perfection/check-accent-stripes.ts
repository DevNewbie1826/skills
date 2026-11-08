#!/usr/bin/env bun
// Flags coloured one-side bars on any box and accent outlines on rounded cards in CSS, Tailwind and JSX.
// Usage: bun check-accent-stripes.ts [--json] <file-or-dir>...   Exit 0 clean, 1 findings, 2 usage or unreadable target; --help prints usage and exits 0.
import { readFileSync } from "node:fs"
import { FIX_HINT, lintFiles, RULE_MESSAGES, type SourceFile } from "./accent-stripes"
import { collectFiles } from "./collect-files"

const USAGE = "usage: check-accent-stripes.ts [--json] <file-or-dir>...   (--help prints this)"

function main(argv: readonly string[]): number {
	if (argv.includes("--help")) {
		process.stdout.write(`${USAGE}\n`)
		return 0
	}
	const json = argv.includes("--json")
	const targets = argv.filter((a) => a !== "--json")
	if (targets.length === 0) {
		process.stderr.write(`${USAGE}\n`)
		return 2
	}
	const { paths, missing } = collectFiles(targets)
	if (missing.length > 0) {
		process.stderr.write(`check-accent-stripes: cannot read ${missing.join(", ")}\n`)
		return 2
	}
	const files: SourceFile[] = paths.map((path) => ({ path, text: readFileSync(path, "utf8") }))
	const findings = lintFiles(files)
	if (json) process.stdout.write(`${JSON.stringify(findings, null, 2)}\n`)
	else {
		for (const f of findings) {
			process.stdout.write(`${f.file}:${f.line}:${f.column}  ${f.rule}  ${RULE_MESSAGES[f.rule]}\n    > ${f.excerpt}\n`)
		}
		const summary = findings.length === 0 ? "no accent stripes" : `${findings.length} accent stripe(s); ${FIX_HINT}`
		process.stdout.write(`check-accent-stripes: ${paths.length} file(s), ${summary}\n`)
	}
	return findings.length === 0 ? 0 : 1
}

process.exitCode = main(process.argv.slice(2))
