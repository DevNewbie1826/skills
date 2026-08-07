# OMP Agent Skill Pack

An **OMP (Oh My Pi) skill pack**. It holds two kinds of skills:

- **Ported skills** (frontend, programming, tdd, debugging, visual-qa, remove-ai-slops,
  git-master, lore) — self-contained, drop-anywhere, framework/model/agent/language-
  neutral. Each `SKILL.md` is a thin router; detail lives in `references/`.
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
| `dag-workflow/` | OMP-native: a task too big for one pass — decompose into a validated dependency DAG and run it across parallel subagents with a quality loop |

## Install

Clone the pack, then copy only the skills you need:

```bash
git clone https://github.com/DevNewbie1826/skills.git
cd skills
```

Skills are individually self-contained: take only what you need. Commands install
`frontend/`; replace it with another skill directory as needed. Note: `programming/`
routes test-driven development to the standalone `tdd/` skill, so copy both if you
want the full testing guidance.

| Runtime | Install path | Copy one skill |
|---|---|---|
| Claude Code (personal) | `~/.claude/skills/` | `mkdir -p ~/.claude/skills && cp -R frontend ~/.claude/skills/` |
| Claude Code (project) | `.claude/skills/` | `mkdir -p .claude/skills && cp -R frontend .claude/skills/` |
| Codex (user) | `~/.agents/skills/` | `mkdir -p ~/.agents/skills && cp -R frontend ~/.agents/skills/` |
| Codex (project) | `.agents/skills/` | `mkdir -p .agents/skills && cp -R frontend .agents/skills/` |
| OpenCode (global) | `~/.config/opencode/skills/` | `mkdir -p ~/.config/opencode/skills && cp -R frontend ~/.config/opencode/skills/` |
| OpenCode (project) | `.opencode/skills/` | `mkdir -p .opencode/skills && cp -R frontend .opencode/skills/` |
| Gemini CLI (user) | `~/.gemini/skills/` | `mkdir -p ~/.gemini/skills && cp -R frontend ~/.gemini/skills/` |
| Gemini CLI (workspace) | `.gemini/skills/` | `mkdir -p .gemini/skills && cp -R frontend .gemini/skills/` |
| Cursor (user) | `~/.cursor/skills/` | `mkdir -p ~/.cursor/skills && cp -R frontend ~/.cursor/skills/` |
| Cursor (project) | `.cursor/skills/` | `mkdir -p .cursor/skills && cp -R frontend .cursor/skills/` |
| pi | `git:github.com/DevNewbie1826/skills` | `pi install git:github.com/DevNewbie1826/skills` |
| Any agent / no loader | No standard path: `$SKILLS_DIR` you expose to the agent | `mkdir -p "$SKILLS_DIR" && cp -R frontend "$SKILLS_DIR"/` |

`~/.agents/skills/` and `.agents/skills/` are interoperable paths: Codex uses them;
OpenCode, Gemini CLI, and Cursor also discover them. OpenCode also recognizes the
Claude-compatible `~/.claude/skills/` and `.claude/skills/` locations. For a runtime
without a loader, set `SKILLS_DIR` to an agent-readable directory and point the agent
at `SKILL.md`; otherwise check your runtime docs.

### Frontmatter compatibility

All nine skills have Agent Skills-style YAML frontmatter: `name` matches the directory,
uses a 1-64-character lowercase/hyphenated identifier, and includes a 322-991-character
`description` (within the 1-1,024-character limit).

- Claude Code makes `name` optional and recommends `description`; its `description`
  plus `when_to_use` listing is capped at 1,536 characters.
- Codex requires `name` and `description`.
- OpenCode requires both and enforces the naming and description limits above. Gemini
  CLI also requires both as the first content in `SKILL.md`; workspace skills require a
  trusted workspace.
- Cursor requires both, with a lowercase letters/numbers/hyphens `name` matching its
  parent directory. These are skills, not rules: `.cursor/rules/` expects `.mdc` files
  with `description`, `globs`, and `alwaysApply` frontmatter.

### Post-install smoke

1. Restart the agent.
2. Ask which skills are available.
3. If you copied `tools/`, run `python3 tools/check-skills.py`.

## Verifying the pack

`PORTING.md` states the contract: this is an OMP pack — **ported** skills are neutralized
(framework/model/agent/language-neutral), **OMP-native** skills are exempt (Rule 8).
`tools/check-skills.py` (python3 stdlib only) enforces the machine-checkable subset for
ported skills:

```bash
python3 tools/check-skills.py            # full pack, exit 0 = compliant
python3 tools/check-skills.py --json     # machine-readable
```

Content-driven allowlist exceptions (e.g. brand design references) live in
`tools/allowlist/` with a reason per entry.

## Layout note

`.omo/` and `.senpi/` at this root are runtime session/state directories created by
the authoring environment — they are NOT part of the skill pack. Copy only the nine
skill directories (plus `PORTING.md`, `README.md`, `tools/` if you want the checker)
when taking the pack elsewhere.
