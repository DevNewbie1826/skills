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

## Per-call model override

`agent()` accepts `model="@<role>"` to override the agent's default model for that call only:

```python
agent(prompt, agent="task", model="@slow")   # this one call uses slow model
agent(prompt, agent="task")                   # next call uses default model
```

| role | when |
|---|---|
| `@slow` | hard reasoning, architecture, deep debugging |
| `@advisor` | strategic advice, tradeoff analysis |
| `@plan` | decomposition, DAG design, gap analysis |
| `@designer` | design decisions, visual planning |
| `@commit` | commit messages, changelog |
| `@vision` | image analysis, screenshot review |
| `@task` | default task agent model |
| `@default` | normal work (implicit when not specified) |
| `@smol` | simple scoring, classification |
| `@tiny` | minimal tasks |


## Skill matching

Per slice, assign `skills` — pack skills the subagent must read+follow. The skill list is dynamic; discover and match at plan time:

1. List available skills by scanning the pack for `SKILL.md` files.
2. Read each skill's `description` (frontmatter) — it defines what the skill covers and when to use it.
3. Match the slice's primary work type to the skill whose description best fits.
4. Assign as a flow array: `["programming"]`, `["programming", "frontend"]`, etc.

Rules:
- Match by the slice's PRIMARY work type — don't stack skills speculatively.
- Multiple skills OK when genuinely needed.
- When unsure, omit — an unspecified skill is better than a wrong one.
</agents>
