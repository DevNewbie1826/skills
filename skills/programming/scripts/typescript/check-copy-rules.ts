#!/usr/bin/env bun
/**
 * Check TypeScript sources for copy-text and suppression-honesty violations.
 *
 * Rules:
 *   no-em-dash-copy            an em dash (U+2014) outside comments, i.e. inside
 *                              string literals, template text, or JSX text that
 *                              users and agents read
 *   require-suppression-reason a lint or type-checker suppression directive in a
 *                              comment that does not say why it applies
 *
 * Usage:
 *   bun scripts/typescript/check-copy-rules.ts [--json] <file-or-dir>...
 *
 * Exit codes: 0 no findings, 1 findings, 2 input error.
 *
 * The scanner is comment-aware: a directive-looking string literal is not a
 * comment, and an em dash inside a comment is not copy. Outside comments the
 * em dash has no legal syntax position, so flagging every non-comment
 * occurrence covers strings, templates, and JSX text in one pass.
 */
import { readdirSync, readFileSync, statSync } from "node:fs"
import { extname, join } from "node:path"
import process from "node:process"
import { fileURLToPath } from "node:url"

export type RuleId = "no-em-dash-copy" | "require-suppression-reason"

export const RULE_IDS: readonly RuleId[] = ["no-em-dash-copy", "require-suppression-reason"]

export type Finding = {
  readonly file: string
  readonly line: number
  readonly rule: RuleId
  readonly message: string
}

const EM_DASH = "\u2014"
const EM_DASH_MESSAGE = "em dash in copy: use a period, comma, colon, or parentheses instead"
const SUPPRESSION_MESSAGE = "suppression directive without a reason: say why it does not apply"

const INCLUDED_EXTENSIONS = new Set([".ts", ".tsx", ".mts", ".cts"])
const EXCLUDED_DIRS = new Set([".git", ".next", ".nuxt", ".turbo", ".yarn", "coverage", "dist", "build", "node_modules"])

const TS_DIRECTIVE = /@ts-(?:expect-error|ignore|nocheck)(?![\w-])/
const GENERIC_DIRECTIVE = /(?:^|[^a-zA-Z0-9])[a-z][a-z0-9]*(?:-[a-z0-9]+)*-(?:disable|enable|ignore|suppress)(?:-(?:next-)?line)?(?=$|[\s(:])/
const SUPPRESS_DIRECTIVE = /@suppress(?![\w-])/
const RULE_TOKEN = /^[A-Za-z0-9_.*\/@-]+/
const REASON_LETTER = /[a-z\u00c0-\u024f\u0370-\uffff]/

type CommentLine = { readonly text: string; readonly line: number }

type ScanResult = { readonly dashLines: readonly number[]; readonly comments: readonly CommentLine[] }

function scanSource(text: string): ScanResult {
  const dashLines: number[] = []
  const comments: CommentLine[] = []
  const parts: string[] = []
  let state: "code" | "line" | "block" | "single" | "double" | "template" = "code"
  let line = 1
  let commentStartLine = 1
  let braceDepth = 0
  const templateStack: number[] = []
  const pushComment = (raw: string, startLine: number): void => {
    const lines = raw.split("\n")
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].trim().length > 0) comments.push({ text: lines[i], line: startLine + i })
    }
  }
  for (let i = 0; i < text.length; i++) {
    const ch = text[i]
    const next = i + 1 < text.length ? text[i + 1] : ""
    if (ch === "\n") line += 1
    if (state === "code") {
      const prevCh = i > 0 ? text[i - 1] : ""
      if (ch === "/" && next === "/" && prevCh !== ":") {
        state = "line"
        commentStartLine = line
        parts.length = 0
        i += 1
      } else if (ch === "/" && next === "*") {
        state = "block"
        commentStartLine = line
        parts.length = 0
        i += 1
      } else if (ch === EM_DASH) {
        dashLines.push(line)
      } else if ((ch === "'" || ch === '"') && !/[A-Za-z0-9_$]/.test(prevCh)) {
        state = ch === "'" ? "single" : "double"
      } else if (ch === "`") {
        state = "template"
      } else if (ch === "{") {
        braceDepth += 1
      } else if (ch === "}") {
        if (templateStack.length > 0 && braceDepth === templateStack[templateStack.length - 1]) {
          templateStack.pop()
          state = "template"
        } else if (braceDepth > 0) {
          braceDepth -= 1
        }
      }
      continue
    }
    if (state === "line") {
      if (ch === "\n") {
        pushComment(parts.join(""), commentStartLine)
        state = "code"
      } else {
        parts.push(ch)
      }
      continue
    }
    if (state === "block") {
      if (ch === "*" && next === "/") {
        parts.push("*")
        pushComment(parts.join(""), commentStartLine)
        state = "code"
        i += 1
      } else {
        parts.push(ch)
      }
      continue
    }
    if (state === "single" || state === "double") {
      if (ch === "\\") {
        if (next === EM_DASH) dashLines.push(line)
        if (next === "\n") line += 1
        i += 1
      } else if (ch === EM_DASH) {
        dashLines.push(line)
      } else if ((state === "single" && ch === "'") || (state === "double" && ch === '"')) {
        state = "code"
      }
      continue
    }
    if (state === "template") {
      if (ch === "\\") {
        if (next === EM_DASH) dashLines.push(line)
        if (next === "\n") line += 1
        i += 1
      } else if (ch === EM_DASH) {
        dashLines.push(line)
      } else if (ch === "`") {
        state = "code"
      } else if (ch === "$" && next === "{") {
        templateStack.push(braceDepth)
        state = "code"
        i += 1
      }
      continue
    }
  }
  if (state === "line") pushComment(parts.join(""), commentStartLine)
  if (state === "block") pushComment(parts.join(""), commentStartLine)
  return { dashLines, comments }
}

function directiveRemainders(commentText: string): string[] {
  const remainders: string[] = []
  for (const pattern of [TS_DIRECTIVE, GENERIC_DIRECTIVE, SUPPRESS_DIRECTIVE]) {
    const match = pattern.exec(commentText)
    if (match !== null) remainders.push(commentText.slice(match.index + match[0].length))
  }
  return remainders
}

function carriesReason(remainder: string): boolean {
  let rest = remainder.replace(/^[ \t]*\([^()]*\)/, "")
  rest = rest.replace(/^[ \t]*\{[^{}]*\}/, "")
  rest = rest.replace(/^[ \t]*:[ \t]*/, "")
  rest = rest.replace(/^[ \t]+/, "")
  const dashAt = rest.indexOf("--")
  if (dashAt >= 0) return REASON_LETTER.test(rest.slice(dashAt + 2))
  const colonAt = rest.indexOf(":")
  if (colonAt >= 0) return REASON_LETTER.test(rest.slice(colonAt + 1))
  for (;;) {
    const commaToken = /^([A-Za-z0-9_.*\/@-]+)[ \t]*,[ \t]*/.exec(rest)
    if (commaToken === null) break
    rest = rest.slice(commaToken[0].length)
  }
  const leadToken = RULE_TOKEN.exec(rest)
  if (leadToken !== null) rest = rest.slice(leadToken[0].length)
  return REASON_LETTER.test(rest.trim())
}

export function lintSource(path: string, text: string): Finding[] {
  const findings: Finding[] = []
  const { dashLines, comments } = scanSource(text)
  for (const line of dashLines) {
    findings.push({ file: path, line, rule: "no-em-dash-copy", message: EM_DASH_MESSAGE })
  }
  for (const comment of comments) {
    const remainders = directiveRemainders(comment.text)
    if (remainders.some((remainder) => !carriesReason(remainder))) {
      findings.push({ file: path, line: comment.line, rule: "require-suppression-reason", message: SUPPRESSION_MESSAGE })
    }
  }
  return findings.sort((a, b) => a.line - b.line || (a.rule < b.rule ? -1 : 1))
}

const USAGE = "usage: check-copy-rules.ts [--json] <file-or-dir>..."

function isScanned(file: string): boolean {
  return INCLUDED_EXTENSIONS.has(extname(file)) && !file.endsWith(".d.ts")
}

function* walk(root: string): Generator<string> {
  if (statSync(root).isFile()) {
    yield root
    return
  }
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (!EXCLUDED_DIRS.has(entry.name)) yield* walk(join(root, entry.name))
    } else if (entry.isFile()) {
      yield join(root, entry.name)
    }
  }
}

function scan(paths: readonly string[]): Finding[] {
  const findings: Finding[] = []
  for (const target of paths) {
    for (const file of walk(target)) {
      if (isScanned(file)) findings.push(...lintSource(file, readFileSync(file, "utf8")))
    }
  }
  return findings.sort((a, b) => (a.file < b.file ? -1 : a.file > b.file ? 1 : a.line - b.line))
}

function main(argv: readonly string[]): number {
  if (argv.includes("--help") || argv.includes("-h")) {
    console.log(USAGE)
    return 0
  }
  const json = argv.includes("--json")
  const paths = argv.filter((arg) => arg !== "--json")
  if (paths.length === 0) {
    console.error(USAGE)
    return 2
  }
  for (const target of paths) {
    try {
      statSync(target)
    } catch {
      console.error(`error: ${target} does not exist`)
      return 2
    }
  }
  const findings = scan(paths)
  if (json) {
    console.log(JSON.stringify({ findings, rules: RULE_IDS }, null, 2))
  } else {
    for (const finding of findings) console.log(`${finding.file}:${finding.line} ${finding.rule} ${finding.message}`)
    console.log(findings.length === 0 ? "check-copy-rules: no findings" : `check-copy-rules: ${findings.length} finding(s)`)
  }
  return findings.length === 0 ? 0 : 1
}

if (process.argv[1] !== undefined && fileURLToPath(import.meta.url) === process.argv[1]) process.exit(main(process.argv.slice(2)))
