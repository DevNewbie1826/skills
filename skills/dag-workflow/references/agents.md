<agents>
Read this when choosing which agent runs a dag-workflow stage; SKILL.md, The stage map, is the binding stage list this file maps to agents.

## Dispatch surfaces

omp has two dispatch surfaces. Both select a bundled agent by exact name in the call itself.

| surface | call | names this flow uses |
|---|---|---|
| task tool | the task tool, selecting the agent by exact name in its `agent` field: one call, or a batch `{context, tasks:[...]}` with a per-item `agent` | `task`, `sonic`, `scout`, `reviewer`, `security-reviewer` |
| eval agent | `agent(prompt, agent="<name>")` in eval | `task`, `sonic`, `scout`, `reviewer`, `security-reviewer` |

omp 18.18.0 bundles exactly `task`, `sonic`, `scout`, `reviewer`, `security-reviewer`, and `seance`; this flow uses the first five and leaves `seance` unused. Model strength comes from the agent's model role: `scout` and `sonic` run the fast role (@smol), `reviewer` the thinking role (@slow), `task` the session model (@task), `security-reviewer` the session model. A specific model is pinned per agent with the omp setting `task.agentModelOverrides`, or per call with `model` when the setting `task.perCallModel` allows it (default off). A "`task` node" below means a node run by the `task` agent, and "spawn" means a dispatch through the task tool or eval `agent()`.

## Stage routing

This table mirrors `SKILL.md`, The stage map, which is binding; anything these two do not name is not spawned.

| stage | agent |
|---|---|
| 0 intake | the lead; sets the tier and the `todo` list; no agent |
| 1 collect | one dependency-ordered workflow-tool run: a `scout` for scope and for outside-source reading (it has `web_search`), `sonic` for mechanical harvest slices, `task` for extract and reduce and for questions that must run the product; the lead assembles the collect report |
| 2 define | the lead, seeded by the collect report; an optional report-only `reviewer` pass with `remove-ai-slops` may feed it and edits nothing |
| 3 before | the lead; an optional `sonic` capture node that writes only to the evidence dir |
| 4 plan | the lead; reads the skills below before writing; no agent |
| 5 plan_lint | the lead, or a report-only `sonic` node, checks the planning grammar, including valid blocked rows |
| 6 plan_review | one fresh `reviewer` plan review through the task tool; in the plan-gate branch (the requester explicitly asked for the planning workflow in their words) add a second fresh `reviewer` with the plan-gate lens (fresh = a new spawn); read-only; OKAY or one fix per blocker; never re-reviewed |
| 7 decide | the lead; one decision batch; no agent |
| 8 goal | the lead; the host goal tool; no agent |
| 9 build | one `task` per implementation node, `sonic` for strictly mechanical edits, one serialized `task` commit node loading `git-master`; each node owns its change and proof; no separate verification, review, or synthesis node in the run |
| 10 verify_lane | for code, one task-tool batch per head: `task` for `tests` (suite plus one mutation per guard row), `reviewer` for `sweep`, `task` for `qa`, `reviewer` for `code-review` loading `remove-ai-slops` and `programming`, and `reviewer` for `adversarial` at tier L or on a HIGH-RISK row, pinned to a model family other than the author's; other work types use their required lanes: mechanical checkers and captures (`draft-guard`, `capture`, `lint`) run `sonic`; QA and execution checks (`qa`, `execution-verify`) run `task`; every judging lane (`vqa` passes, `fact-verify`, `claim-gate`, `skeptic`, `delivery-gate`, `spot`, `register-schema`) runs `reviewer` |
| 11 triage | the lead; no agent |
| 12 fix | one `task` per fix node, one component per node, plus the serialized `task` commit node loading `git-master`; only stale lanes re-run; a `family` switch pins the fix node's model |
| 13 freeze | the lead; no agent |
| 14 pr_open | the lead; the host `monitor` watches the PR; no agent |
| 15 round | one fresh `reviewer` review through the task tool every round: round 1 full, round 2 and later delta and prior findings; pinned to the strongest configured model and, where required, a model family other than the author's; when the work type requires `code-review`, refuse dispatch without a valid receipt at the frozen head |
| 16 merge | the lead; no agent |
| 17 post_merge | `task`: a smoke pass when the merged tree equals the frozen tree, the full pass otherwise |
| 18 checkpoint | `reviewer` reads the evidence record; its narrow scope (presence, criteria match, and schema only) is stated in the caller's prompt; the lead records the checkpoint |
| 19 cleanup | the lead; no agent |
| switch | after two consecutive REVISE rounds on one component or defect class, one fresh `reviewer` premise review; a third-or-later repeat forces a switch: premise, family (a `task` fix node pinned to another model family), strategy, split (program only), or rediscover; record a `SWITCH:` plan row |

Stages 3 and 12 are conditional: when one truly does not apply, its `todo` entry stays with `skip: <reason>`, never silently dropped. Enforce triage -> fix -> freeze -> pr_open -> round. Review has no round ceiling: APPROVED is the only end, and a cap is a switch, never an exit. A verdict covers only the head it reviewed, so a moved head is a re-review, never a carried verdict. Give each evidence file one writer, reuse receipts only under the tree/scope rules, and commit nothing after freeze. Reviewers use a locked read-only review worktree, and each re-review uses a fresh reviewer. `reviewer` has `bash`, so a read-only review is held by the prompt plus the locked review worktree. Other-family independence is pinned, not enforced: set `task.agentModelOverrides.reviewer` to an exact model from another family, and for a family-switch fix node set `task.perCallModel: on` plus an exact `model` on the item; when the user has not configured one, the round record states same-family as a known limit instead of refusing to dispatch. Every reviewer prompt carries the evidence rule of `references/verification.md`, The evidence rule, verbatim.

## Skills to read before a stage

The lead and assigned children read the applicable pack skills before starting their work; assign child skills by name through omp's skill discovery.

| before | read |
|---|---|
| `plan` | `remove-ai-slops`, `programming`, and the work type's skill: `frontend` for a rendered surface, `seo-html` for a static page |
| `build`, `fix` | `programming` when applicable; `tdd` for implementation, fixes, or test changes; `debugging` for runtime failures |
| a commit node of `build` or `fix` | `git-master`; `lore` when the repository records decision trailers |
| `verify_lane`, `round` | `remove-ai-slops` and `programming` in the code-review lane; `visual-qa` with `frontend` when a rendered surface changed |
| design work | `frontend` to build, `visual-qa` to verify |

For research, use the applicable pack skills and the flow's research verification rules; do not assume an unavailable research skill. Match any additional work-specific skill by its description.

## Never

- The lead is the only fan-out point: a subagent never spawns a subagent and never calls `agent()`, `parallel()`, or the task tool; `task` declares `spawns: "*"` and `reviewer` may spawn `scout`, so this rule is held by the prompt, or set `task.maxRecursionDepth: 1`.
- `scout` is scope-only: it maps files and call sites and produces no findings.
- `security-reviewer` is the security lens only, never a general finder or verifier.
- `sonic` runs mechanical work; it never carries a review or a blocking verdict.
- Never assign `dag-workflow` to a child: it is the flow that spawns, and a child following it would spawn again.

## Finder / verifier role assignment

When a workflow decomposes into finder and verifier slices, assign the agent by role — separate invocations for finder and verifier; the same invocation MUST NEVER both find and verify its own claims:

| role | agent | scope |
|---|---|---|
| finder (findings-producing) | `reviewer` | code review, adversarial checks that surface findings |
| verifier | `reviewer` | verifying prior findings, re-checking claimed fixes |
| scope discovery | `scout` | collect and discovery: file lists, call-site mapping — never generates findings |
| security lens | `security-reviewer` | security analysis exclusively, when a security angle is in scope |

Rules:
- Both finders and verifiers use `reviewer`; do not reserve `reviewer` for one role only, and do not substitute `scout` for either.

Review/sweep route: per lens, one finder `reviewer` (plus a `security-reviewer` for a security lens), one batch verifier per 15 or fewer findings, one synthesis `reviewer` per round; in FULL mode or batch-local escalation, two additional batch verifiers per batch containing HIGH or CRITICAL findings (three votes per HIGH or CRITICAL finding, never per-finding councils).

## Skill matching

The pack ships ten skills: `frontend`, `programming`, `tdd`, `debugging`, `visual-qa`, `remove-ai-slops`, `git-master`, `lore`, `seo-html`, `dag-workflow`. `dag-workflow` is the flow itself and is never assigned to a child. Match at plan time:

1. Read each skill's `description` (frontmatter) — it defines what the skill covers and when to use it.
2. Match the slice's primary work type to the skill whose description best fits.
3. Record the skill name (not path) — the subagent resolves it through omp's skill discovery.

Rules:
- Match by the slice's PRIMARY work type — don't stack skills speculatively.
- Multiple skills are OK when genuinely needed.
- When unsure, omit — an unspecified skill is better than a wrong one.
</agents>
