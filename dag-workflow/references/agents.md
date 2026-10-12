<agents>
Read this when choosing which omp agent runs a dag-workflow node; SKILL.md, Stages and required reads, lists it for stage 1.

## Built-in agents

Pick via `agent="..."` in the `agent()` call.

This table lists EVAL agent types for `agent()` calls. `SKILL.md`, Agents per stage, specifies which type RUNS each node — `task` for implementation nodes, `reviewer` for finder/verifier nodes.

| agent | when to use |
|---|---|
| `task` | general-purpose work including implementation and analysis within eval (implementation uses `agent(agent='task')`) |
| `scout` | read-only exploration, codebase research, file scanning (scope-only, no findings — see below) |
| `reviewer` | code review, adversarial verification, quality checks |
| `security-reviewer` | read-only security analysis, vulnerability discovery |
| `sonic` | low-reasoning, strictly mechanical updates or data collection |

`designer` runs only when the host's task tool lists a `designer` agent (omp 18.3.4 built-ins do not; user agent files may add one); never dispatch to an agent the host does not list.

`librarian` is not offered: external library/API research is done by the lead with its own web/doc tools, or by one `task` node per external question.

## Agents by stage

This table mirrors `SKILL.md`, Agents per stage, which is the binding list — anything it does not name is not spawned:

| stage | agent |
|---|---|
| Discovery | one `scout` per open question per wave, in parallel |
| Plan review | exactly one `reviewer` |
| Execution | one `task` per implementation node, `sonic` for strictly mechanical nodes |
| Batch verification | one `reviewer` verification node per parallel batch, plus a `security-reviewer` for a batch that touches security-sensitive code |
| Final review and each delta re-review | a NEW `reviewer` |

## Finder / verifier role assignment

When a workflow decomposes into finder and verifier slices, assign `agent` by role — use separate agent() invocations for finder and verifier — the same invocation MUST NEVER both find and verify its own claims:

| role | agent | scope |
|---|---|---|
| finder (findings-producing) | `reviewer` | code review, adversarial checks that surface findings |
| verifier | `reviewer` | verifying prior findings, re-checking claimed fixes |
| scope discovery | `scout` | Discovery (stage 1) only: file lists, call-site mapping — never generates findings |
| security lens | `security-reviewer` | security analysis exclusively, when a security angle is in scope |

Rules:
- `scout` is scope-only: it maps the surface (files, call sites) and produces no findings. Never use it as a findings-producing finder.
- Both finders and verifiers use `reviewer`; do not reserve `reviewer` for one role only, and do not substitute `scout` for either.
- `security-reviewer` is the security lens only — use it for the security pass, not as a general finder or verifier.

## Skill matching

Per slice, assign `skills`: list the skills from the pack that the subagent must read and follow. The skill list is dynamic; discover and match at plan time:

1. List available skills by scanning the pack for `SKILL.md` files.
2. Read each skill's `description` (frontmatter) — it defines what the skill covers and when to use it.
3. Match the slice's primary work type to the skill whose description best fits.
4. Record the skill name (not path) — the subagent resolves it via OMP's skill discovery.

Rules:
- Match by the slice's PRIMARY work type — don't stack skills speculatively.
- Multiple skills are OK when genuinely needed.
- When unsure, omit — an unspecified skill is better than a wrong one.
</agents>
