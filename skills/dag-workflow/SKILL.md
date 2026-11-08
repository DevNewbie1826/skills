---
name: dag-workflow
description: "Use for any nontrivial task that benefits from implementation delegation or independent verification, from a single focused change to a large migration: run a bounded staged flow (collect, define, one reviewed plan with confirmation devices, a goal-bound build with one PR per unit, per-head verify lanes, a frozen-head VERDICT round, merge, post-merge verification, and cleanup; requires the eval tool). Triggers: parallelize, fan out, decompose this task, split work across agents, orchestrate subagents, big task, too large for one pass, broad sweep, large refactor, large migration, audit sweep, DAG, workflow. Do NOT use for a trivial edit, a quick lookup, a one-step answer, or work that needs no verification machinery"
omp-native: true
---

# dag-workflow

Entry is `/wf <task>` (the pack rewrites it to `/goal task: <task>` plus an instruction to read this router) or the user naming this skill. Running the flow authorizes collection, definition, planning, implementation in worktrees, verification, opening PRs, review to APPROVED, merge, and cleanup, so phases already covered are never asked again. Genuine owner decisions (irreversible, destructive, spending money, or a contract-level limit to accept) are asked once, at decide, as one batch with a recommended default each; after that nothing is asked, and a decision that appears mid-run parks only its own lane.

## When to run the flow

- **Inline.** Trivial work that needs no verification machinery: a quick lookup, a single trivial edit, a one-step answer. No agents, no flow.
- **Review/sweep.** Analysis only, no code changes. Run finder and verifier lanes per [references/orchestration.md](references/orchestration.md): the `<structure>` finder->verifier contract and the `**Review/sweep rounds (bounded)**` pattern in `<patterns>`. Findings are reported. Acting on them starts the implementation flow.
- **Implementation.** Anything else runs the stage map below.

## The stage map

Read each reference at its stage, not before, and report the reads in that stage's first handoff. A rule that composes a prompt before a reference's stage — the node fields at build, the evidence rule at the round — reads that reference's named section at the moment it composes; the schedule forbids prefetching whole files, not a rule's own dependency. The record column names what the stage leaves in the evidence dir (SKILL.md, Follow-up record). The order is mechanical, not advisory: the later gates refuse to run when an earlier record is missing or stale.

| # | stage | what runs it | record |
|---|---|---|---|
| 0 | intake | the session: tier triage; `todo` carries the stage steps | the plan file, created here and never pre-created |
| 1 | collect | one workflow-tool run (or one `parallel()` wave): `scout` for scope and for outside-source reading (it has web_search), `sonic` for mechanical harvest slices, `task` for extract and reduce and for questions that must run the product | `collect.md`; an unread source is named, never omitted |
| 2 | define | the session, seeded by collect | `define.md` + the difference rows in `gaps.tsv` |
| 3 | before | the session: one pre-edit capture per defect row and per row that edits existing UI | capture receipts, taken before the first edit |
| 4 | plan | the session writes it in this pack's plan grammar | the plan (`references/planning.md`) |
| 5 | plan_lint | the session checks the plan against the lint rules — no script, the rule list itself | a clean check, or every complaint fixed |
| 6 | plan_review | one fresh `reviewer` plan review; a plan-gate branch adds a second fresh `reviewer` with the plan-gate lens | review record: OKAY, or blockers each with one fix |
| 7 | decide | the session collects the one decision batch | decision records with a recommended default each |
| 8 | goal | the host's goal tool: `/wf` already armed the run's one goal; its objective is the register's IS-to-QA pairing, and a unit never opens a second goal | the goal id |
| 9 | build | one workflow-tool/eval run per unit; the commit node loads git-master | build records; one PR per unit |
| 10 | verify_lane | one task-tool batch per head: for code, `task` for `tests` (suite plus one mutation per guard row), `reviewer` for `sweep`, `task` for `qa`, `reviewer` for `code-review` (loading `remove-ai-slops` and `programming`), `reviewer` for `adversarial` at tier L or on a HIGH-RISK row pinned to a model family other than the author's; other work types: mechanical checkers and captures (draft-guard, capture, lint) run `sonic`, QA and execution checks (qa, execution-verify) run `task`, and every judging lane (vqa passes, fact-verify, claim-gate, skeptic, delivery-gate, spot, register-schema) runs `reviewer` | the lane receipt per required lane |
| 11 | triage | the session | findings rows |
| 12 | fix | a correction run per round; the reuse rule re-runs only stale lanes | fix + reuse records |
| 13 | freeze | the session records head and tree, and commits nothing after | freeze record: head, tree, pr |
| 14 | pr_open | `gh pr create` with the generated body; the host's monitor watches the PR | the open PR |
| 15 | round | the gate check, then one fresh `reviewer` every round (round 1 full, later rounds delta), pinned to the strongest configured model and, where required, a family other than the author's by setting `task.agentModelOverrides.reviewer` to an exact model from another family; when none is configured, the round record states same-family as a known limit rather than refusing to dispatch; the session reads the VERDICT line and confirms it names the frozen head | final review record + verdict |
| 16 | merge | the session merges | merge record: sha, pr |
| 17 | post_merge | `task`: smoke when the merged tree equals the frozen tree, the full pass otherwise | post-merge record |
| 18 | checkpoint | the goal checkpoint; `reviewer` reads the evidence record with the narrow scope (presence, criteria match, schema only) stated in the caller's prompt; the lead records the checkpoint | checkpoint record |
| 19 | cleanup | the session: memory for the classes it caught; teardown receipts | cleanup record |

Stages 3 and 12 are conditional: when one truly does not apply, its step stays in the `todo` with `skip: <reason>`, never silently dropped. While any unit runs, report a PROGRESS line on every transition that changes a number and at least every 30 minutes; a repeat with no change is suppressed.

## Plans, units, and tiers

- One plan per unit, written in the plan grammar of [references/planning.md](references/planning.md): front matter, `Todos` and `Final verification wave` checkbox rows, the contract rows (IS, COMPANION, INVARIANT, LIMIT, SWITCH), QA scenarios with one binary pass condition, DEVICE rows, and the risk list. Every IS row carries a confirmation device; a behaviour the repository cannot test gets the no-test path.
- **Two plan branches.** Default: the plan gets ONE fresh `reviewer` plan review, and the run continues straight to decide. Plan-gate branch, opened only when the requester's own message asked for a planning-workflow review in their words: the plan gets BOTH the `reviewer` plan review and a second fresh `reviewer` with the plan-gate lens, its read-only scope held by the prompt plus a locked review worktree, and no third round. Fresh means a new spawn: nothing depends on a follow-up message reaching it, and its fixes are checked by the final round, not by a re-review.
- **Units.** A request holding more than one independently verifiable unit becomes one PR per unit: disjoint write scope, own worktree and branch, own Before/After in the PR body. The split is decided at plan, never mid-build. A unit's contract is its own IS rows only; one unit's round never blocks another unit's merge.
- **Tiers.** S: small, one scout node, short define and plan; the plan review may start alongside build, and a blocker amends the run; at most one mutation per guard row. M: serial stages, full verify wave. L: adds the adversarial lane without needing a HIGH-RISK row, the state and lifetime transition table in QA, and the mutation cap. A tier is never lowered; a heavy fact found mid-run raises it at once.

## Work types

The type is fixed at intake and decides the required lanes: code (tests, qa, sweep, code-review, plus adversarial at tier L or a HIGH-RISK row), design (draft-guard, capture, both visual-qa passes, code-review, qa), research (fact-verify, claim-gate, skeptic, execution-verify, delivery-gate), audit (lint, spot, register-schema), mixed (the primary type's lanes united with the secondary's). The lane table and the five visual-qa classes: [references/verification.md](references/verification.md).

## Reviews, in the one order that holds

Triage, fix, freeze, pr_open, and round are one sequence, and the order is mechanical: the round refuses to run unless a valid code-review receipt exists at the frozen head — a refused gate, not a reminder. The head is frozen for the whole round: a fix lands only after the verdict and opens the next round. A verdict is valid only for the head it reviewed, so a head that moved during a round is a re-review, never a carried verdict. Review has no round ceiling: APPROVED is the only end. Two consecutive REVISE rounds on the same component or the same defect class stop the patch loop and force one fresh `reviewer` premise review. A third-or-later REVISE that repeats a class an earlier round cited forces an approach switch among premise, family (a `task` fix node pinned to another model family by `task.perCallModel: on` with an exact `model` on the item), strategy, split (program only), and rediscover, and every repeat after it uses one more kind not yet used. On REVISE the flow returns to define for the cited problem, replans and re-lints it, fixes, and appends the fix commits to the same PR, never a second one. Binding detail: [references/verification.md](references/verification.md).

## The finite contract

The plan's IS and COMPANION rows are the request, INVARIANT rows what must keep holding, LIMIT rows what is knowingly not handled. Only an undelivered IS or COMPANION row, or a listed invariant shown violated by a failing test (or a no-test row's failing QA), blocks; everything else is a note or a follow-up. A listed LIMIT is never a finding. WARN never blocks; a FAIL receipt is a claim the session reproduces first. The boundary and the companion guards: [references/planning.md](references/planning.md).

## Non-negotiable rules

1. One goal for the run, armed by `/wf` at entry; never a second. Its objective carries the register pairing; each unit's plan holds its own IS-to-QA rows, and `todo` holds progress.
2. Gate order: never open the PR before the verify lanes pass and the code-review lane has run; never run the round without the freeze; never merge before the round returns APPROVED.
3. Nothing commits after the freeze: a memo goes to the evidence dir, never the branch.
4. Every run file has one writer. A receipt is valid while its tree matches; a verdict only while its round's head equals the frozen head and the observed head.
5. Record only what you've checked. A commit counts once `git cat-file -t <sha>` prints `commit`.
6. Every command pins the task worktree; commits are serialized.

## Agents per stage

The table in [references/agents.md](references/agents.md) mirrors the stage map; anything neither names is not spawned, and never subagents spawning subagents: `task` declares spawns "*" and `reviewer` may spawn `scout`, so the no-nesting rule is held by the prompt, or set `task.maxRecursionDepth: 1`.

## The purpose boundary

The original request and its companion items are the boundary for every stage: discovery, plan, tests, QA, and review. A companion is the same grain as the change and something the requester would naturally expect done together; it must pass the four guards (one hop from a request IS row, no new owner decision, same task and PR, recorded as a COMPANION row) — the guards in full are [references/planning.md](references/planning.md). Same-pattern sibling bugs found while fixing are companions under the guards. Everything else is out of scope: recorded in the follow-up record and named in the final report, never fixed in this task.

## Follow-up record

Out-of-scope findings live in `<evidence dir>/follow-ups.md`. The evidence dir is a directory outside the task worktree, recorded in the plan. Each record carries the finding, a reproduction, evidence, impact, and the exclusion reason naming the guard it failed. Create the file only when a real finding exists. Every out-of-scope finding also appears in the final report; with none, the report says "none".

## Rules

- **Tests and devices:** every IS row carries a confirmation device — existing tests, a guard mutation, or the no-test path with a QA scenario. A device that mostly tests mocks, encodes implementation details, depends on timing, or needs heavy infrastructure for a small fix is a bad device; prefer no new test over a bad one. Prose gets read-through QA, never wording tests.
- **Evidence capture:** capture the command and its output; never retype a SHA or number a capture holds.
- **Test discipline:** no sleeps; wait on the event or state change itself.

## Delegation prompts

Every node prompt carries purpose, scope (permitted paths and the worktree pin), blockers, separate findings, the no-spawning rule, the companion definition, and the return-once instruction; the fields TASK, DELIVERABLE, SCOPE, VERIFY, STOP WHEN; and, where the reference names it, a TIMEBOX. Every reviewer prompt carries the evidence rule verbatim from [references/verification.md](references/verification.md): evidence problems are never a REVISE reason; only a code problem inside the finite contract blocks.

## Progress reporting

`todo` is the live checklist: register it right after the plan is written, one task per atomic unit, mark start and done the instant each happens. Write a short handoff at each stage transition and in each REVISE round.

## Finish

Stop when the register is closed (every defect row fixed, accepted-limit, or out-of-scope), every unit's PR is merged with post-merge recorded, the checkpoint is complete, worktrees and branches are removed with receipts, and the final report is delivered with evidence, limits, and out-of-scope findings. Respond in the user's language; write agent prompts in English.
