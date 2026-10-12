---
name: dag-workflow
description: "Use for any nontrivial task that benefits from implementation delegation or independent verification, from a single focused change to a large migration: run a bounded, staged flow (discovery and one plan review, worktree execution in verified batches of eval-based subagents, combined verification, one final review) that hands back a branch and a report and never opens a PR or merges (requires the eval tool). Triggers: parallelize, fan out, decompose this task, split work across agents, orchestrate subagents, big task, too large for one pass, broad sweep, large refactor, large migration, audit sweep, DAG, workflow. Do NOT use for a trivial edit, a quick lookup, or a one-step answer, work needing no verification machinery"
omp-native: true
---

# dag-workflow

Entry is `/wf <task>` (the pack rewrites it to `/goal task: <task>` plus an instruction to read this router) or the user naming this skill. Running the flow authorizes discovery, planning, implementation in a worktree, verification, and one final review, so don't ask again for phases already covered. Genuine owner decisions (irreversible, destructive, or spending money) are still asked. The flow never opens a PR and never merges: it ends by handing the user the branch, worktree path, commits, evidence, and report.

## When to run the flow

Pick one route before anything else:

- **Inline.** Trivial work that needs no verification machinery: a quick lookup, a single trivial edit, a one-step answer. No agents, no flow.
- **Review/sweep.** Analysis only, no code changes. Run finder and verifier lanes per [references/orchestration.md](references/orchestration.md): the `<structure>` finder->verifier contract and the `**Review/sweep rounds (bounded)**` pattern in `<patterns>`. Findings are reported. Acting on them starts the implementation flow.
- **Implementation.** Anything else runs the three stages below.

## Stages and required reads

Read each file when its stage starts, not before. Every file a stage needs is listed here directly, so no reference has to send you to another one.

1. **Discovery and plan.** Required reads at entry: [references/planning.md](references/planning.md), [references/agents.md](references/agents.md). Bounded discovery, one plan file, one plan review. Exit: the one plan review has returned and every blocker it raised has a recorded fix.
2. **Execution.** Required reads at entry, in this order: [references/execution.md](references/execution.md); [references/orchestration.md](references/orchestration.md) (`<helpers>`, `<structure>`, and `<execution>` at least, in full on first use); [references/verification.md](references/verification.md), read before you define any batch, because the batch verification checks and the closing steps come from it. Create the worktree, establish the green baseline, then run batches of `task` nodes through eval `agent()`/`parallel()`. One verification `reviewer` per parallel batch gates the next batch. Exit: every implementation node has a PASS verdict.
3. **Verification and final review.** Combined verification, then one final `reviewer`. A REVISE verdict loops back to stage 2 with a correction batch in the same worktree, followed by a delta re-review from a NEW `reviewer`. The stage ends at APPROVED.

## Non-negotiable rules

These hold for every model and every request size.

1. Read every required file at its stage entry, in this run. A summary or a copy from an earlier run doesn't count.
2. Report the reads: the first handoff of each stage names the files you read for it.
3. One goal only. `/wf` already armed `/goal` with the task, so never start a second goal. Without `/wf`, run without a goal and keep progress in the plan file and `todo`.
4. Changes to the task's files run only in delegated nodes (`agent(agent='task')`, or `sonic` for strictly mechanical edits), inside the task worktree. The lead plans, dispatches, reviews, and reports. It never edits the task's files itself, however small the change. The Inline route is the only exception, and it runs no flow.
5. Never define a batch before reading `references/execution.md` and `references/orchestration.md`.
6. Gate order: never dispatch batch k+1 before batch k's verdict file says `VERDICT: PASS`; never deliver the final report before the final review returns APPROVED; never open a PR or merge.
7. Record only what you've checked. A commit counts once `git cat-file -t <sha>` prints `commit`. Attribute an action to the user only from the user's own message or artifacts.

## Agents per stage

The stage structure decides who runs. Anything not listed here isn't spawned.

- **Discovery:** one `scout` per open question per wave, in parallel. A question leaves the wave once it's answered. Stop when every open question is answered and two consecutive waves have added nothing new; a question still open at that point becomes a plan assumption or an owner question. External docs come from the lead's own tools, or from one `task` per external question.
- **Plan review:** exactly one `reviewer`. It's never re-reviewed.
- **Execution:** one `task` per implementation node (`sonic` for strictly mechanical nodes) and one `reviewer` verification node per parallel batch. Add a `security-reviewer` only for a batch that touches security-sensitive code; it reviews that batch alongside the verification node. Use `designer` only when the host's task tool lists a `designer` agent; never dispatch to an agent the host doesn't list.
- **Failure:** re-dispatch only the failed nodes, with the cause fixed, plus one new verification node for that re-run batch.
- **Final review:** one `reviewer`. Each REVISE round adds correction nodes for the required changes only, one verification node, and one NEW `reviewer` for the delta re-review. Rounds continue until APPROVED, each scoped to the delta.
- **Review/sweep route:** per lens, one finder `reviewer` (plus a `security-reviewer` for a security lens), one batch verifier per 15 or fewer findings in that lens, and one synthesis `reviewer` per round. Later rounds run only finders seeded by the previous round's uncovered gaps. Stop at the first round with zero new findings and zero gaps, or after exactly N rounds when the user set N.
- **Never:** per-finding verifier councils, task-wide sticky escalation, repeat-until-dry loops over the whole output, or subagents spawning subagents.

## The purpose boundary

The request's IS rows and its COMPANION rows are in scope. A companion is work of the same grain that the requester would ask about if it were left undone. Every companion must pass four guards:

- (a) it's one hop from a request row, never further;
- (b) it needs no new owner decision;
- (c) it belongs to the same task and branch;
- (d) it's visible in the plan as `COMPANION: <item> <- <request IS row> : <why expected>`.

Same-pattern sibling bugs found while fixing are companions under these guards.

An in-scope finding is an IS or COMPANION row not delivered, a regression this change introduced (including a failing test or a stale doc of code it touched), or invalid proof. Fix those in the same task. Everything else goes to the follow-up record and is never fixed here. When the impact is uncertain, run the smallest check that decides it. Uncertainty that blocks proving delivery is invalid evidence, not a follow-up.

## Follow-up record

Out-of-scope findings live in `<evidence dir>/follow-ups.md`. The evidence dir is a directory outside the task worktree, recorded in the plan (for example `<worktree>.evidence/`). Before that directory exists, hold findings in the plan.

Each record carries the finding, a reproduction, evidence, impact, and the exclusion reason naming the guard, (a) through (d), that it failed. Create the file only when a real finding exists. Every out-of-scope finding also appears in the final report; with none, the report says "none".

## Delegation prompts

Every implementation, QA, and review prompt contains these five items:

1. **Purpose:** the original requested outcome.
2. **Scope:** this assignment's permitted work, exact paths, and the worktree pin.
3. **Blockers:** an IS or COMPANION row not delivered, an introduced regression, or invalid proof.
4. **Separate findings:** unrelated (non-companion) findings are reported, not fixed.
5. **No spawning:** the child never spawns agents or calls `agent()`, `parallel()`, or the task tool. Only the lead fans out.

Add the companion definition (point to `SKILL.md`, The purpose boundary, or quote it), the return-once instruction from `references/orchestration.md` `<helpers>`, and the node fields from `references/execution.md`, Worktree and node design. The lead owns the boundary and corrects drift by re-scoping the next prompt. A reviewer's unrelated quality remarks are follow-up notes, not blockers.

## Progress reporting

`todo` is the live checklist. Register it right after the plan is written, one task per atomic unit (where, why, how, verify), and mark start and done the instant each happens. Write a short handoff at each stage transition, after each batch verdict, and in each REVISE round.

## Finish

Stop when the final review is APPROVED, combined verification passes on the final tree, and the report (`references/verification.md`, Finish and final report) is delivered with the branch, worktree path, and commit list. Leave the branch and worktree for the user. Never push to a shared branch, open a PR, or merge unless the user asks for it separately. Respond in the user's language; write agent prompts in English.
