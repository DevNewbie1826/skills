# OMP Agent Skill Pack

An **OMP (Oh My Pi) skill pack**. It holds two kinds of skills:

- **Ported skills** (frontend, programming, tdd, debugging, visual-qa, remove-ai-slops,
  git-master, lore, seo-html) — content neutralized per `PORTING.md` (skill prose makes no
  framework/model/agent/language presuppositions). Each `SKILL.md` is a thin router;
  detail lives in `references/`.
- **OMP-native skills** (`dag-workflow`) — written for OMP, may use OMP
  mechanisms (`eval`/`task`/`hub`/`local://`/goal mode); exempt from the neutrality rules
  that govern ported skills (see `PORTING.md` Rule 8).

Progressive disclosure throughout: detail is loaded only when routed to.

## Skills

| Skill | Use when |
|---|---|
| `frontend/` | Any web UI/UX/visual work: building, redesigning, styling, animation, performance, accessibility, design research |
| `programming/` | Writing or editing Python, Rust, TypeScript, or Go code: strict types, modern toolchains, parse-don't-validate, typed errors |
| `tdd/` | Test-driven development in any language: red/green/refactor, test quality, fakes before mocks, determinism |
| `debugging/` | Real runtime debugging in any language or binary: crashes, silent failures, hangs, leaks, reverse engineering |
| `visual-qa/` | Verifying a built UI/page/TUI visually: screenshots, pixel diffs, responsive and CJK checks |
| `remove-ai-slops/` | Cleaning AI-generated code smells from a diff or file list, with regression tests locked first |
| `git-master/` | Commits and git-history investigation: atomic commits, rebase, bisect, blame, log -S/-G |
| `lore/` | Writing non-trivial commit messages that capture decision context, or querying that context from git history |
| `seo-html/` | Writing and checking one complete SEO HTML page: head, meta tags, Open Graph, JSON-LD, semantic HTML, Korean, English, and Naver rules |
| `dag-workflow/` | OMP-native: discover, review one plan, execute in a worktree with eval subagents owning each change and proof, verify before the PR, one code-review round, open a PR, one final review, merge, verify after merge, and clean up |

## Install

This is an OMP skill pack. Install the whole pack with:

```bash
omp install https://github.com/DevNewbie1826/skills.git
```

### Post-install smoke

1. Restart OMP and ask which skills are available.
2. Run `python3 tools/check-skills.py` to verify the pack.

## Verifying the pack

`PORTING.md` states the contract: this is an OMP pack — **ported** skills are neutralized
(framework/model/agent/language-neutral), **OMP-native** skills are exempt (Rule 8).
`tools/check-skills.py` (python3 stdlib only) enforces the machine-checkable subset for
ported skills, and now also checks the OMP-native `dag-workflow` (its `omp-native: true`
frontmatter skips the Tier-A/HAZARDS checks for it):

```bash
python3 tools/check-skills.py            # full pack, exit 0 = compliant
python3 tools/check-skills.py --json     # machine-readable
```

Content-driven allowlist exceptions (e.g. brand design references) live in
`tools/allowlist/` with a reason per entry.

## Layout note

`.omo/` and `.senpi/` at this root are runtime session/state directories created by
the authoring environment — they are NOT part of the skill pack and are not installed
by `omp install`.
