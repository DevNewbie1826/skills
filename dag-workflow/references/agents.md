<agents>

## Built-in agents

Pick via `agent="..."` in the `agent()` call.

| agent | when to use |
|---|---|
| `task` | general-purpose work — default for most slices |
| `scout` | read-only exploration, codebase research, file scanning |
| `reviewer` | code review, adversarial verification, quality checks |
| `designer` | UI/UX design, visual refinement |
| `security-reviewer` | security analysis, vulnerability discovery |
| `librarian` | external library/API research |
| `sonic` | strictly mechanical updates, data collection — low reasoning |

## Skill matching

Per slice, assign `skills` — pack skills the subagent must read+follow. The skill list is dynamic; discover and match at plan time:

1. List available skills by scanning the pack for `SKILL.md` files.
2. Read each skill's `description` (frontmatter) — it defines what the skill covers and when to use it.
3. Match the slice's primary work type to the skill whose description best fits.
4. Record the skill name (not path) — the subagent resolves it via OMP's skill discovery.

Rules:
- Match by the slice's PRIMARY work type — don't stack skills speculatively.
- Multiple skills OK when genuinely needed.
- When unsure, omit — an unspecified skill is better than a wrong one.
</agents>
