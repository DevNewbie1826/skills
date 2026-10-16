---
name: dag-workflow
description: "Use for any nontrivial task that benefits from implementation delegation or independent verification, from a single focused change to a large migration: run a bounded 13-step flow (discovery, one plan with one plan review, a goal-bound worktree run of eval-based subagent nodes, two-branch pre-PR verification, a code-review round, a PR, one final review, merge, post-merge verification, and cleanup; requires the eval tool). Triggers: parallelize, fan out, decompose this task, split work across agents, orchestrate subagents, big task, too large for one pass, broad sweep, large refactor, large migration, audit sweep, DAG, workflow. Do NOT use for a trivial edit, a quick lookup, or a one-step answer, or work that needs no verification machinery"
omp-native: true
---

# dag-workflow

Entry is `/wf <task>` (the pack rewrites it to `/goal task: <task>` plus an instruction to read this router) or the user naming this skill. Running the flow authorizes discovery, planning, implementation in a worktree, verification, opening a PR, review, merge, and cleanup, so don't ask again for phases already covered. Genuine owner decisions (irreversible, destructive, or spending money) are still asked.

## When to run the flow

- **Inline.** Trivial work that needs no verification machinery: a quick lookup, a single trivial edit, a one-step answer. No agents, no flow.
- **Review/sweep.** Analysis only, no code changes. Run finder and verifier lanes per [references/orchestration.md](references/orchestration.md): the `<structure>` finder->verifier contract and the `**Review/sweep rounds (bounded)**` pattern in `<patterns>`. Findings are reported. Acting on them starts the implementation flow.
- **Implementation.** Anything else runs the 13 steps below.

## The 13 steps

Read each reference at its step, not before, and report the reads in that step's first handoff. Steps 1-4: [references/planning.md](references/planning.md), [references/agents.md](references/agents.md), and [references/orchestration.md](references/orchestration.md) `<helpers>` (Delegation prompts and the step-1 scouts need it). Step 5: [references/execution.md](references/execution.md) and [references/orchestration.md](references/orchestration.md) (`<helpers>`, `<structure>`, `<execution>`). Steps 6-13: [references/verification.md](references/verification.md).

1. Discovery: one `scout` per open question per wave in one `parallel()`; external facts come from the lead's own tools or one `task`. When a REVISE sends work back (step 11), re-run discovery for the cited problem and sweep variants of the same defect class inside this step, with no separate sweep or merge nodes. Details: `references/planning.md`.
2. One plan file: IS rows and COMPANION rows (the request is the boundary), gaps, QA scenarios with binary pass conditions, the IS-row to QA-scenario pairing, a risk list, and the pinned rules (worktree pinned for every command, commits serialized). Details: `references/planning.md`.
3. One plan review: one `reviewer` answers OKAY or blockers; record one fix per blocker and continue; the round is never re-reviewed. Details: `references/planning.md`.
4. One goal: `/wf` already armed one; keep it and never start a second. Without `/wf`, create one goal with the host's goal tool whose objective is the IS-to-QA pairing written as one paragraph. Details: `references/planning.md`.
5. Run the plan: eval `agent()`/`parallel()` nodes with disjoint write scopes; one node owns a change and its proof, with the injection check inside the node; commits serialized after each verified unit; no verification, review, or synthesis node inside the run. Details: `references/execution.md`, `references/orchestration.md`.
6. Pre-PR verification, two parallel branches: (a) one `task` node runs the repository suite and the mutation check; (b) one `task` node runs the QA scenarios on the real surface. Both branches pass before the PR. Details: `references/verification.md`.
7. Code review round: one `reviewer`, before the PR, loads and applies the `remove-ai-slops` and `programming` skills and states in its report whether that check ran; CRITICAL and HIGH findings are fixed once, then continue; in a REVISE round it sees only the delta diff. Details: `references/verification.md`.
8. Open the PR: behavior delivered, tests and QA run with their capture paths, real limits. In a REVISE round, update the PR body. Details: `references/verification.md`.
9. Final review: one fresh `reviewer`, never one that worked on the task, reports every code defect of the PR in one verdict and ends APPROVED or REVISE. Details: `references/verification.md`.
10. Evidence problems: never a REVISE reason; each becomes a correction memo the main session fixes with no re-review (`## Delegation prompts`). Details: `references/verification.md`.
11. APPROVED: the lead merges. REVISE, code problems only: go back to step 1 and run steps 2 and 5-9 again in the same worktree and same PR; steps 3 and 4 are not repeated. Details: `references/verification.md`.
12. Post-merge verification: one full pass on the merged result: every QA scenario plus the repository suite, typecheck, and build where they exist; a fix goes through steps 5-11 again from the merged base. Details: `references/verification.md`.
13. Cleanup and final report: remove the worktree and branch with receipts, complete the goal, deliver the final report with results, evidence locations, limits, and follow-ups. Details: `references/verification.md`.

## Non-negotiable rules

1. Read every required file at its step, in this run. A summary or a copy from an earlier run doesn't count.
2. One goal only, armed by `/wf` or created at step 4; never a second. The plan file and `todo` hold progress.
3. Changes to the task's files run only in delegated nodes (`agent(agent='task')`, or `sonic` for strictly mechanical edits), inside the task worktree. The lead plans, dispatches, reviews, merges, and reports; it never edits the task's files itself. The lead does fix evidence problems and the PR body through correction memos under `## Delegation prompts`, never code.
4. Gate order: never open the PR before step 6 passes and step 7 has run; never merge before the final review returns APPROVED.
5. Record only what you've checked. A commit counts once `git cat-file -t <sha>` prints `commit`. Attribute an action to the user only from the user's own message or artifacts.

## Agents per step

The table in [references/agents.md](references/agents.md) mirrors this list; anything neither names is not spawned.

- **Steps 1-4:** one `scout` per open question per wave in one `parallel()`; the lead writes the plan; one `reviewer` for the plan review; the lead owns the goal.
- **Step 5:** one `task` per implementation node (`sonic` for strictly mechanical nodes); no verification, review, or synthesis node inside the run.
- **Steps 6-9:** two `task` nodes in one `parallel()` (step 6); one `reviewer` loading `remove-ai-slops` and `programming`; `task` nodes for its CRITICAL and HIGH fixes (step 7); the lead opens the PR (step 8); one fresh `reviewer`, never one that worked on the task (step 9).
- **Steps 10-13:** the lead merges (step 11); one `task` node re-verifies the merged result (step 12); the lead cleans up and reports (step 13).
- **Review/sweep route:** one finder `reviewer` per lens (plus a `security-reviewer` for a security lens), batch verifiers, and one synthesis `reviewer` per round, per [references/orchestration.md](references/orchestration.md).
- **Never:** subagents spawning subagents.

## The purpose boundary

The original request and its companion items are the boundary for every step: discovery, plan, tests, QA, and review.

- In scope means the request IS rows plus COMPANION rows: planned from the start, or found later and then added under the guards below. An undelivered COMPANION row is "request not delivered", like an unmet IS row.
- A companion is the same grain as the change and something the requester would naturally expect done together. It must pass: (a) one hop from a request IS row, never chained to another companion; (b) no new owner decision; (c) same task and PR; (d) recorded in the plan as `COMPANION: <item> <- <request IS row> : <why expected>`.
- Same-pattern sibling bugs found while fixing are companions under these guards. A late-found item that passes the guards is added to the plan as a COMPANION row and fixed in the same task.
- Everything else is out of scope: never fix it in this task. Record it in the follow-up record and name it in the final report.

## Follow-up record

Out-of-scope findings live in `<evidence dir>/follow-ups.md`. The evidence dir is a directory outside the task worktree, recorded in the plan (for example `<worktree>.evidence/`). Before that directory exists, hold findings in the plan.

Each record carries the finding, a reproduction, evidence, impact, and the exclusion reason naming the guard, (a) through (d), that it failed. Create the file only when a real finding exists. Every out-of-scope finding also appears in the final report; with none, the report says "none".

## Rules

- **Tests:** code first; no RED-first mandate. A test must break when the behavior changes, not only when the implementation changes, and a fixture for a behavior that consumes more than one value supplies at least two distinct values, so a change that drops any of them breaks it. Add a test only when the repository keeps tests for that behavior and a regression would otherwise pass unnoticed; prose gets read-through QA, never wording tests. Every guard row gets the injection check (step 5).
- **Evidence capture:** capture the command and its output; never retype a SHA or number by hand when a capture holds it; record only what you checked.
- **Test discipline:** no sleeps; wait on the event or state change itself.

## Delegation prompts

Every node prompt carries:

1. **Purpose:** the original requested outcome.
2. **Scope:** this assignment's permitted work, exact paths, and the worktree pin.
3. **Blockers:** an IS or COMPANION row not delivered, a regression this change introduced, or a proof that shows the code does not do what is claimed (a code defect); typos, number errors, and wording or format problems in evidence are correction memos, never blockers.
4. **Separate findings:** anything not companion under `## The purpose boundary` is reported, never fixed.
5. **No spawning:** the child never spawns agents and never calls `agent()`, `parallel()`, or the task tool; only the lead fans out.
6. The companion definition (point to `## The purpose boundary`, or quote it) and the return-once instruction from `references/orchestration.md` `<helpers>`.
7. The fields TASK, DELIVERABLE, SCOPE, VERIFY, and STOP WHEN.

Every reviewer prompt (plan review in step 3, code review in step 7, final review in step 9, and any review/sweep reviewer) carries the following rule verbatim.

Evidence problems are never a REVISE reason. Typos, number errors, and wording or format problems in evidence or reports do not cause REVISE. Write each one as a correction memo in your report; the lead checks the memo and the main session fixes the evidence, with no re-review for it. Only a problem in CODE can cause REVISE.

A reviewer's unrelated quality remarks are follow-up notes, not blockers. The lead owns the boundary and corrects drift by re-scoping the next prompt.

## Progress reporting

`todo` is the live checklist: register it right after the plan is written, one task per atomic unit (where, why, how, verify), and mark start and done the instant each happens. Write a short handoff at each step transition and in each REVISE round.

## Finish

Stop when the PR is merged, the post-merge verification (step 12) passes, the worktree and branch are removed with receipts, the goal is completed, and the final report is delivered. Respond in the user's language; write agent prompts in English.
