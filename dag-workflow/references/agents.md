<agents>

## Built-in agents

Pick via `agent="..."` in the `agent()` call.

This table lists EVAL agent types for `agent()` calls. Implementation nodes are dispatched via the separate session `task` TOOL (see SKILL.md Step 2), not through this table — the `agent` field in Step 1 for an implementation node specifies its VERIFICATION agent (the eval reviewer that will refute its output), not the implementer.

| agent | when to use |
|---|---|
| `task` | general-purpose ANALYSIS and multi-step VERIFICATION within eval; never implementation (implementation uses the session task TOOL, a separate mechanism — see SKILL.md Step 2) |
| `scout` | read-only exploration, codebase research, file scanning |
| `reviewer` | code review, adversarial verification, quality checks |
| `designer` | UI/UX design, visual refinement |
| `security-reviewer` | security analysis, vulnerability discovery |
| `librarian` | external library/API research |
| `sonic` | strictly mechanical updates, data collection — low reasoning |

## Finder / verifier role assignment

When a workflow decomposes into finder and verifier slices, assign `agent` by role — do NOT unify them onto a single agent type:

| role | agent | scope |
|---|---|---|
| finder (findings-producing) | `reviewer` | code review, adversarial checks that surface findings |
| verifier | `reviewer` | verifying prior findings, re-checking claimed fixes |
| scope discovery | `scout` | Step 1 only: file lists, call-site mapping — never generates findings |
| security lens | `security-reviewer` | security analysis exclusively, when a security angle is in scope |

Rules:
- `scout` is scope-only: it maps the surface (files, call sites) and produces no findings. Never use it as a findings-producing finder.
- Both finders and verifiers use `reviewer`; do not reserve `reviewer` for one role only, and do not substitute `scout` for either.
- `security-reviewer` is the security lens only — use it for the security pass, not as a general finder or verifier.

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
