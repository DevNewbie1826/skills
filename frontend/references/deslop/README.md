# Deslop — find and remove AI slop

This ruleset covers **visual and copy slop**: the generic, machine-default
tells of vibe-coded products (indigo→violet gradients, gradient-clip headlines,
kickers over every heading, invented stat rows, the default Inter/Space Grotesk
look, and 29 more — the full 34-tell taxonomy lives in `taxonomy.md`). It is
distinct from the `remove-ai-slops` skill in this pack, which removes
*code-level* slop (obvious comments, dead code, over-defensive code); this
ruleset judges what the user *sees and reads*.

Three ways the frontend workflow uses it:

1. **Audit mode** — the user asks to "kill AI slop", "de-slop", "remove the AI
   look", or says a page feels templated / AI-generated. Run the full
   Scope → Scan → Triage → Report → Fix workflow below.
2. **Creation-time checklist** — during any greenfield build or redesign, hold
   the taxonomy as a don't-list: none of the 34 tells may appear in new work.
   Reading `taxonomy.md` once is enough; the scanner verifies at the end.
3. **Final QA gate** — before declaring a build done, run the scanner over the
   new/changed source and triage any hits. A clean scan is required alongside
   the `visual-qa` evidence gate; a passing scan is not a substitute for it
   (the scanner sees code, not pixels — several tells are visual judgments).

AI slop is **ugly** in a specific way: it piles on every possible style and
detail without settling on a focus. A gradient, a glow, a mascot, emoji, a wall
of glowing cards, every default switched on at once, until every product looks
like the same garish template. It reads as "designed" in a thumbnail and falls
apart the moment anyone looks. Your job is to strip it back to something a
person would actually choose.

The principles, held on every fix you make:

1. **Decide before you decorate.** Every visual choice must be explainable.
2. **One accent, one voice.**
3. **Hierarchy from scale and space.** Coloring words or swapping fonts is a shortcut.
4. **Subtract first.** The first move toward not-ugly is removing things.
5. **Specific beats punchy** in copy.
6. **Decoration must mean something** — icons, badges, callouts are signals.

## Workflow (audit mode)

Follow these steps in order. Do not mass-edit before the user has seen the report.

### 1. Scope
Confirm what to scan. Default to the app/site source (skip `node_modules`,
`dist`, `build`, `.git`, `vendor`, lockfiles, minified files). Ask if the
project mixes several apps.

### 2. Scan
Run the bundled scanner, which greps the codebase for the code-level signals of
each tell and prints grouped `file:line` hits:

```
node scripts/scan.mjs <root>          # human-readable report
node scripts/scan.mjs <root> --json   # machine-readable, for triage
```

(Run from this ruleset directory, or pass the script's absolute path.) It is
pure Node (no dependencies) and never edits files. Use its output as a
starting map, not gospel — confirm each hit by reading the code.

To narrow a scan: `--only=01,06` / `--skip=19` filter by tell id, and
`--exclude=legacy` drops paths (substring match on the project-relative path).
`--rules=extra.mjs` loads additional project- or language-specific tells
(`$SKILL_DIR/references/deslop/scripts/rules.ru.mjs` is a shipped Russian-copy example and the template for
your own). Hits the user has confirmed as intentional can be pinned in source
with `deslop-ignore`, `deslop-ignore-next-line 06`, or `deslop-ignore-file`
comments — prefer the id-scoped forms so new tells still surface.

### 3. Triage
For every hit, open the file and decide **slop vs. intentional**. This is the
step that separates this ruleset from a lint rule. A gradient, a serif, or an
emoji can be a real, defended choice. Keep anything the user clearly chose
(brand tokens, a logo, a deliberate illustration). Flag only defaults.

Read `taxonomy.md` for what each tell is and why it reads as machine-made, and
`detection.md` for the exact patterns and their common false positives.

### 4. Report
Before changing anything, give the user a grouped summary: each tell, the
`file:line` hits you confirmed, one sentence on why, and the proposed fix.
Mirror the format:

```
slop  src/Hero.tsx:12   indigo→violet gradient        → one solid accent
slop  src/Hero.tsx:31   gradient-clip headline        → solid ink, scale up
slop  src/Note.tsx:8    border-l-4 callout ×3         → 1 aside, rest is body
slop  copy.md:1         "not just X — it's Y"         → say the specific thing
→ 4 groups, 11 hits.
```

Then ask which groups to apply, or whether to proceed on all.

### 5. Fix
Apply the minimal change that removes the tell while preserving intent and
function. Use `fixes.md` for the before→after pattern per tell.

- Prefer editing shared tokens/components over touching every call site. In a
  project with a `DESIGN.md`, the fix usually lands there first — the deslop
  pass updates tokens (accent, radius, font choices) and the tokens fix the
  call sites.
- Never invent new brand colors; if a palette must change, propose neutrals +
  the project's existing accent and let the user confirm.
- Keep copy meaning; make it specific, don't just delete it.
- Re-run the scanner after fixing to confirm the count dropped, and note any
  hits you intentionally left (with the reason).

## Guardrails

- **Respect authorship.** Treat unfamiliar files and deliberate flourishes as
  someone's choice. When unsure whether something is slop, ask — don't strip it.
- **Small, reviewable diffs.** Never reformat unrelated code. Never run
  `git add -A`; stage explicit files only, and leave others' work-in-progress
  alone.
- **No new dependencies** to do this work.
- **Verify visually when possible.** If a dev server exists, look at the before
  and after; a passing scan is not the same as a better page. For significant
  deslop work, run `visual-qa` after the fixes.

## Files

- `taxonomy.md` — the 34 tells: what each is, why it's slop, the fix.
- `detection.md` — concrete ripgrep/regex patterns + false positives.
- `fixes.md` — before→after remediation patterns.
- `$SKILL_DIR/references/deslop/scripts/scan.mjs` — the dependency-free scanner.
- `$SKILL_DIR/references/deslop/scripts/rules.ru.mjs` — example extension rules (Russian copy tells).
