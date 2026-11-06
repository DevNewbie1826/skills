<agents>
Read this when choosing which agent or category runs a dag-workflow stage; SKILL.md, The stage map, is the binding stage list this file maps to agents.

## Dispatch surfaces

omp has three dispatch surfaces. Select the surface specified below; the same word can mean different things on different surfaces.

| surface | call | names this flow uses |
|---|---|---|
| eval agent types | `agent(prompt, agent="...")` in eval | `task`, `scout`, `reviewer`, `security-reviewer`, `sonic` |
| task-tool categories | the task tool, `category` | `architect`, `ultrabrain`, `deep-high`, `deep-low`, `quick` |
| named subagent types | the task tool, `subagent_type` | `explore`, `librarian`, `omo-native-qa-executor`, `omo-native-code-reviewer`, `omo-native-gate-reviewer` |

The eval type `task` and the task tool are different: a "`task` node" below means the eval type, and "spawn" means the task tool. The host also lists `unspecified-low` and `unspecified-high`; this flow routes no stage to them. Never dispatch to a name the host does not list.

## Stage routing

This table mirrors `SKILL.md`, The stage map, which is binding; anything these two do not name is not spawned.

| stage | agent |
|---|---|
| 0 intake | the lead; sets the tier and the `todo` list; no agent |
| 1 collect | one dependency-ordered workflow-tool run: a `scout` for scope, `quick` harvest nodes, `deep-low` extract and reduce nodes, `explore` for repository questions read from the product's viewpoint, one `librarian` for outside sources; the lead assembles the collect report |
| 2 define | the lead, seeded by the collect report; an optional report-only `reviewer` pass with `remove-ai-slops` may feed it and edits nothing |
| 3 before | the lead; a read-only `quick` node may drive the captures |
| 4 plan | the lead; reads the skills below before writing; no agent |
| 5 plan_lint | the lead or a `quick` node checks the planning grammar, including valid blocked rows |
| 6 plan_review | one `architect` category review through the task tool; in the plan-gate branch (the requester explicitly asked for the planning workflow in their words) add one one-shot read-only `plan-reviewer` dispatch; read-only; OKAY or one fix per blocker; never re-reviewed |
| 7 decide | the lead; one decision batch; no agent |
| 8 goal | the lead; the host goal tool; no agent |
| 9 build | one `task` per implementation node, `sonic` for strictly mechanical edits, one serialized `task` commit node loading `git-master`; each node owns its change and proof; no separate verification, review, or synthesis node in the run |
| 10 verify_lane | for code, one task-tool batch per head: `quick` for `tests` and `sweep`, `omo-native-qa-executor` for `qa`, `omo-native-code-reviewer` for `code-review` loading `remove-ai-slops` and `programming`, and `deep-high` for `adversarial` at tier L or on a HIGH-RISK row, in a model family other than the author's; other work types use their required lanes |
| 11 triage | the lead; no agent |
| 12 fix | one `task` per fix node, one component per node, plus the serialized `task` commit node loading `git-master`; only stale lanes re-run |
| 13 freeze | the lead; no agent |
| 14 pr_open | the lead; the host `monitor` watches the PR; no agent |
| 15 round | one `ultrabrain` category review through the task tool: round 1 full, round 2 and later delta and prior findings; a fresh reviewer every round; when the work type requires `code-review`, refuse dispatch without a valid receipt at the frozen head |
| 16 merge | the lead; no agent |
| 17 post_merge | `omo-native-qa-executor`: a smoke pass when the merged tree equals the frozen tree, the full pass otherwise |
| 18 checkpoint | `omo-native-gate-reviewer` reads the evidence record and checks presence, criteria match, and schema only; the lead records the checkpoint |
| 19 cleanup | the lead; no agent |
| switch | after two consecutive REVISE rounds on one component or defect class, one `architect` premise review; a third-or-later repeat forces a switch: premise, family (`deep-high`), strategy, split (program only), or rediscover; record a `SWITCH:` plan row |

Stages 3 and 12 are conditional: when one truly does not apply, its `todo` entry stays with `skip: <reason>`, never silently dropped. Enforce triage -> fix -> freeze -> pr_open -> round. Review has no round ceiling: APPROVED is the only end, and a cap is a switch, never an exit. A verdict covers only the head it reviewed, so a moved head is a re-review, never a carried verdict. Give each evidence file one writer, reuse receipts only under the tree/scope rules, and commit nothing after freeze. Reviewers use a locked read-only review worktree, and each re-review uses a fresh reviewer. Every reviewer prompt carries the evidence rule of `references/verification.md`, The evidence rule, verbatim.

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

- The lead is the only fan-out point: a subagent never spawns a subagent and never calls `agent()`, `parallel()`, or the task tool.
- Never dispatch to a name the host does not list. If the host lists no `architect` category, use its highest-capability category and record the substitution in the plan.
- `scout` is scope-only: it maps files and call sites and produces no findings.
- `security-reviewer` is the security lens only, never a general finder or verifier.
- `quick` and `sonic` run mechanical work; they never carry a review or a blocking verdict.
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
- The stage-10 `code-review` lane is the one exception: it runs `omo-native-code-reviewer`, not `reviewer`.

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
