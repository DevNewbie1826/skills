# Bundled Script Dependencies

This file declares the non-standard-library packages imported by bundled scripts. The library and CLI need no packages at all.

## `scripts/detect/*` (library, CLI, rules)

**Third-party packages:** none for the library and the CLI. They use Node built-ins only.

**Run:** `bun $SKILL_DIR/scripts/detect/cli.ts [--json] [--reflow] [--config <file.json>] <file-or-dir-or-url>...` or import `index.ts` from code. Rendering a page needs a browser runtime: system WebKit or an installed Chrome/Chromium; without one the CLI exits 2 with a message naming what is missing.

## `scripts/detect/*.test.ts`

**Third-party packages:** none beyond the test framework built into the runtime. The test files import the runtime's own test module `bun:test`, which ships with Bun and is not an npm dependency.

**Install:** nothing. **Run:** `bun test $SKILL_DIR/scripts/detect`.
