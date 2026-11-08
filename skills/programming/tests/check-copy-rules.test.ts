import { spawnSync } from "node:child_process"
import { readdirSync, readFileSync } from "node:fs"
import { join } from "node:path"
import { describe, expect, test } from "bun:test"
import { lintSource, RULE_IDS, type Finding, type RuleId } from "../scripts/typescript/check-copy-rules"

const FIXTURES = join(import.meta.dir, "..", "scripts", "typescript", "fixtures", "check-copy-rules")
const SCRIPT = join(import.meta.dir, "..", "scripts", "typescript", "check-copy-rules.ts")

const EXPECTED: Record<string, Array<[number, RuleId]>> = {
  "em-dash-string.ts": [[1, "no-em-dash-copy"], [2, "no-em-dash-copy"]],
  "em-dash-template.tsx": [[1, "no-em-dash-copy"], [4, "no-em-dash-copy"]],
  "bare-ts-directives.ts": [
    [1, "require-suppression-reason"],
    [4, "require-suppression-reason"],
    [7, "require-suppression-reason"],
  ],
  "bare-tool-directives.ts": [
    [1, "require-suppression-reason"],
    [4, "require-suppression-reason"],
    [7, "require-suppression-reason"],
  ],
}

const lintFixture = (kind: "positive" | "negative", name: string): Finding[] =>
  lintSource(join(kind, name), readFileSync(join(FIXTURES, kind, name), "utf8"))

describe("#given the rule table", () => {
  test("#when the module loads #then it exports both rules in order", () => {
    expect(RULE_IDS).toEqual(["no-em-dash-copy", "require-suppression-reason"])
  })
})

describe("#given a positive fixture with dashes or bare suppressions", () => {
  test("#when fixtures are listed #then every positive fixture has an expectation", () => {
    expect(readdirSync(join(FIXTURES, "positive")).sort()).toEqual(Object.keys(EXPECTED).sort())
  })

  for (const [name, expected] of Object.entries(EXPECTED)) {
    test(`#when ${name} is linted #then it reports exactly ${expected.length} finding(s) at the expected lines`, () => {
      expect(lintFixture("positive", name).map((f): [number, RuleId] => [f.line, f.rule])).toEqual([...expected])
    })
  }
})

describe("#given a negative fixture (comment dashes, reasoned suppressions, directives in strings)", () => {
  for (const name of readdirSync(join(FIXTURES, "negative"))) {
    test(`#when ${name} is linted #then it reports nothing`, () => {
      expect(lintFixture("negative", name)).toEqual([])
    })
  }
})

describe("#given the reason grammar", () => {
  test("#when a ts directive stands alone #then it is bare", () => {
    expect(lintSource("unit.ts", "// @ts-ignore\nconst a = 1\n")).toEqual([
      expect.objectContaining({ line: 1, rule: "require-suppression-reason" }),
    ])
    expect(lintSource("unit.ts", "const a = 1\n// @ts-expect-error\n")).toEqual([
      expect.objectContaining({ line: 2, rule: "require-suppression-reason" }),
    ])
    expect(lintSource("unit.ts", "/* @ts-nocheck */\n")).toEqual([
      expect.objectContaining({ line: 1, rule: "require-suppression-reason" }),
    ])
  })

  test("#when a generic disable carries only rule identifiers #then it is bare", () => {
    expect(lintSource("unit.ts", "// linttool-disable\n")).toEqual([
      expect.objectContaining({ rule: "require-suppression-reason" }),
    ])
    expect(lintSource("unit.ts", "// linttool-disable-next-line rule-x\n")).toEqual([
      expect.objectContaining({ rule: "require-suppression-reason" }),
    ])
    expect(lintSource("unit.ts", "// linttool-disable-next-line E402\n")).toEqual([
      expect.objectContaining({ rule: "require-suppression-reason" }),
    ])
    expect(lintSource("unit.ts", "// linttool-ignore(rule-a,rule-b)\n")).toEqual([
      expect.objectContaining({ rule: "require-suppression-reason" }),
    ])
  })

  test("#when a directive is followed by a human reason #then it stays clean", () => {
    expect(lintSource("unit.ts", "// @ts-expect-error: upstream misdeclares the overload\n")).toEqual([])
    expect(lintSource("unit.ts", "// linttool-disable-next-line rule-x -- legacy schema cannot change\n")).toEqual([])
    expect(lintSource("unit.ts", "// linttool-ignore(rule-a): generated file, see the generator\n")).toEqual([])
    expect(lintSource("unit.ts", "// @suppress unused-var: kept for the public API surface\n")).toEqual([])
  })

  test("#when a directive sits inside a string literal #then it is not a comment", () => {
    expect(lintSource("unit.ts", 'const doc = "// @ts-ignore"\n')).toEqual([])
    expect(lintSource("unit.ts", "const doc = `docs mention linttool-disable in prose`\n")).toEqual([])
  })
})

describe("#given the dash scanner", () => {
  test("#when a dash sits in a comment #then it is not copy and stays clean", () => {
    expect(lintSource("unit.ts", "// a note — with a dash\nconst a = 1\n")).toEqual([])
    expect(lintSource("unit.ts", "/* block note — dash */\n")).toEqual([])
  })

  test("#when a dash sits in a string inside a template interpolation #then it is flagged", () => {
    const findings = lintSource("unit.ts", 'const t = `a ${"b — c"} d`\n')
    expect(findings).toEqual([expect.objectContaining({ line: 1, rule: "no-em-dash-copy" })])
  })

  test("#when a dash is escaped inside a string #then it is still flagged", () => {
    expect(lintSource("unit.ts", 'const s = "before \\— after"\n')).toEqual([
      expect.objectContaining({ line: 1, rule: "no-em-dash-copy" }),
    ])
  })
})

describe("#given the CLI", () => {
  const run = (...args: string[]) => spawnSync(process.execPath, [SCRIPT, ...args], { encoding: "utf8", timeout: 30_000 })

  test("#when it scans the positive fixtures #then it exits 1 and prints file:line findings", () => {
    const result = run(join(FIXTURES, "positive"))
    expect(result.status).toBe(1)
    expect(result.stdout).toMatch(/em-dash-string\.ts:1 no-em-dash-copy/)
    expect(result.stdout).toMatch(/bare-tool-directives\.ts:4 require-suppression-reason/)
    expect(result.stdout).toMatch(/check-copy-rules: 10 finding\(s\)/)
  })

  test("#when it scans the negative fixtures #then it exits 0 with no findings", () => {
    const result = run(join(FIXTURES, "negative"))
    expect(result.status).toBe(0)
    expect(result.stdout).toContain("check-copy-rules: no findings")
  })

  test("#when --json is passed #then stdout is a parseable findings object", () => {
    const result = run("--json", join(FIXTURES, "positive", "em-dash-string.ts"))
    expect(result.status).toBe(1)
    const parsed = JSON.parse(result.stdout)
    expect(parsed.rules).toEqual(["no-em-dash-copy", "require-suppression-reason"])
    expect(parsed.findings).toEqual([
      expect.objectContaining({ line: 1, rule: "no-em-dash-copy" }),
      expect.objectContaining({ line: 2, rule: "no-em-dash-copy" }),
    ])
  })

  test("#when no path is given #then it exits 2 with usage", () => {
    const result = run()
    expect(result.status).toBe(2)
    expect(result.stderr).toContain("usage: check-copy-rules.ts")
  })

  test("#when a path is missing #then it exits 2 naming the path", () => {
    const result = run("/nope/missing.ts")
    expect(result.status).toBe(2)
    expect(result.stderr).toContain("does not exist")
  })

  test("#when --help is passed #then it exits 0 and prints usage", () => {
    const result = run("--help")
    expect(result.status).toBe(0)
    expect(result.stdout).toContain("usage: check-copy-rules.ts")
  })

  test("#when it scans its own source #then it finds nothing", () => {
    const result = run(SCRIPT)
    expect(result.status).toBe(0)
    expect(result.stdout).toContain("check-copy-rules: no findings")
  })
})
