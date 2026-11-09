# OMP Agent Skill Pack

An **OMP (Oh My Pi) skill pack**. It holds two kinds of skills:

- **Ported skills** (frontend, programming, tdd, debugging, visual-qa, remove-ai-slops,
  git-master, lore, seo-html) — content neutralized per `docs/PORTING.md` (skill prose makes no
  framework/model/agent/language presuppositions). Each `SKILL.md` is a thin router;
  detail lives in `references/`.
- **OMP-native skills** (`dag-workflow`) — written for OMP, may use OMP
  mechanisms (`eval`/`task`/`agent()`/`wait()`/`workpool()`/`local://`/goal mode);
  exempt from the neutrality rules that govern ported skills (see `docs/PORTING.md` Rule 8).

Progressive disclosure throughout: detail is loaded only when routed to.

## Skills

| Skill | Use when |
|---|---|
| `skills/frontend/` | Any web UI/UX/visual work: building, redesigning, styling, animation, performance, accessibility, design research |
| `skills/programming/` | Writing or editing Python, Rust, TypeScript, or Go code: strict types, modern toolchains, parse-don't-validate, typed errors |
| `skills/tdd/` | Test-driven development in any language: red/green/refactor, test quality, fakes before mocks, determinism |
| `skills/debugging/` | Real runtime debugging in any language or binary: crashes, silent failures, hangs, leaks, reverse engineering |
| `skills/visual-qa/` | Verifying a built UI/page/TUI visually: screenshots, pixel diffs, responsive and CJK checks |
| `skills/remove-ai-slops/` | Cleaning AI-generated code smells from a diff or file list, with regression tests locked first |
| `skills/git-master/` | Commits and git-history investigation: atomic commits, rebase, bisect, blame, log -S/-G |
| `skills/lore/` | Writing non-trivial commit messages that capture decision context, or querying that context from git history |
| `skills/seo-html/` | Writing and checking one complete SEO HTML page: head, meta tags, Open Graph, JSON-LD, semantic HTML, Korean, English, and Naver rules |
| `skills/dag-workflow/` | OMP-native: one authorized request to a merged PR — define the ideal state from evidence, run every part as a DAG of eval agent() nodes under one goal, prove each requirement with a confirmation device, review the PR until APPROVED, merge on MERGE GO |


### dag-workflow flow

`/wf <task>` arms one goal, reads the dag-workflow router, and works the request in its order:
analyze the context with a DAG and define the ideal state, create a worktree, set the goal's
criteria, run all work as DAGs (each ending in its review) with a confirmation device for every
implementation and fix, open one PR, review it until APPROVED (round 1 the whole PR, later
rounds only the fixes), and merge only on `MERGE GO <PR> for head <40-hex> only.`. The skill
names only omp agents and tools: `references/omp-names.md` lists them, and the checker's
OMP-NAME rule fails on any other name.

Maintenance: the `<system-notice>` at the top of `skills/dag-workflow/SKILL.md` is copied
verbatim from omp 18.18.1 `src/prompts/system/ultrathink-notice.md`.
`skills/dag-workflow/references/workflow.md` is omp 18.18.1
`src/prompts/system/workflow-notice.md` rendered by `renderWorkflowNotice`
(`src/modes/magic-keywords.ts`) with all omp defaults: taskBatch, scoutAvailable, evalTools,
py and js true; freshAgents and perCallModel false. To re-render, call that function with
these values.
## Install

This is an OMP skill pack. Install the whole pack with:

```bash
omp install https://github.com/DevNewbie1826/skills.git
```

### Post-install smoke

1. Restart OMP and ask which skills are available.
2. Run `python3 tools/check-skills.py` to verify the pack.

## Verifying the pack

`docs/PORTING.md` states the contract: this is an OMP pack — **ported** skills are neutralized
(framework/model/agent/language-neutral), **OMP-native** skills are exempt (Rule 8).
`tools/check-skills.py` (python3 stdlib only) enforces the machine-checkable subset for
ported skills, and now also checks the OMP-native `dag-workflow` (its `omp-native: true`
frontmatter skips the Tier-A/HAZARDS checks for it):

```bash
python3 tools/check-skills.py            # full pack, exit 0 = compliant
python3 tools/check-skills.py --json     # machine-readable
```

Content-driven allowlist exceptions, when needed, live in
`tools/allowlist/*.json` with a reason per entry.

## Layout

```text
skills/        one folder per skill: <name>/SKILL.md plus references/, scripts/, tests/
extensions/    omp extensions: skills-pack.ts (skill index), wf-goal.ts (/wf)
commands/      slash-command templates (wf.md)
tools/         pack gate: check-skills.py, verify.sh, install-hooks.sh, tests
docs/          PORTING.md (the porting contract)
package.json   omp pack manifest (pi.skills -> ./skills)
```

Runtime session/state directories that an authoring environment creates at this root are
NOT part of the skill pack and are not installed by `omp install`; keep them out of git
with the clone's `.git/info/exclude`.
