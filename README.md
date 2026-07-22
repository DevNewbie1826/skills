# Agent Skill Pack

Six self-contained, drop-anywhere agent skills. Framework-neutral, model-neutral,
agent-neutral, language-neutral. Progressive disclosure throughout: each `SKILL.md`
is a thin router; detail lives in `references/` and is loaded only when routed to.

## Skills

| Skill | Use when |
|---|---|
| `frontend/` | Any web UI/UX/visual work: building, redesigning, styling, animation, performance, accessibility, design research |
| `programming/` | Writing or editing code in any language: strict types, modern toolchains, parse-don't-validate, typed errors, TDD |
| `debugging/` | Real runtime debugging in any language or binary: crashes, silent failures, hangs, leaks, reverse engineering |
| `visual-qa/` | Verifying a built UI/page/TUI visually: screenshots, pixel diffs, responsive and CJK checks |
| `remove-ai-slops/` | Cleaning AI-generated code smells from a diff or file list, with regression tests locked first |
| `git-master/` | Commits and git-history investigation: atomic commits, rebase, bisect, blame, log -S/-G |

## Usage

Drop any skill directory into your agent runtime's skills location as-is. No skill
assumes a specific agent, model, framework, or language; where a capability is needed
(delegation, browser driving, image generation), the skill describes the capability and
offers fallbacks instead of presupposing a product.

Bundled scripts live under each skill's `scripts/` and run with stock runtimes
(python3 stdlib / node), invoked via paths relative to the skill directory.

## Verifying the pack

`PORTING.md` states the neutrality/portability contract. `tools/check-skills.py`
(python3 stdlib only) enforces the machine-checkable subset:

```bash
python3 tools/check-skills.py            # full pack, exit 0 = compliant
python3 tools/check-skills.py --json     # machine-readable
```

Content-driven allowlist exceptions (e.g. brand design references) live in
`tools/allowlist/` with a reason per entry.

## Layout note

`.omo/` and `.senpi/` at this root are runtime session/state directories created by
the authoring environment — they are NOT part of the skill pack. Copy only the six
skill directories (plus `PORTING.md`, `README.md`, `tools/` if you want the checker)
when taking the pack elsewhere.
