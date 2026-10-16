Read this when steps 1-4 (discovery, plan, and goal) of the dag-workflow flow start; SKILL.md, The 13 steps, lists it.

# dag-workflow: discovery, plan, and goal

Covers steps 1-4 of the flow (see `SKILL.md`, The 13 steps).

## Step 1: Discovery

Gather facts before deciding anything. Write the open questions down first, then run one `scout` per open question per wave, all in one `parallel()` call of `agent(agent='scout', ...)` thunks, alongside your own reads. A question leaves the next wave as soon as it is answered. Survey:

- The code the request touches: layout, existing tests, the real surfaces users go through.
- Git history of the paths you will touch: what changed there recently and why.
- Memory: durable facts, past decisions, and regressions earlier runs caught.
- Earlier session evidence for the same area.

Facts from outside the repository (a library, an external API, current docs) come from your own web and doc tools, or from one `agent(agent='task', ...)` per external question, never from what you remember.

Stop when every open question is answered and two consecutive waves add nothing new. Let the survey range wide enough to name everyone the result touches, then apply the boundary before planning: see `SKILL.md`, The purpose boundary.

When a review sends work back (step 11), re-run discovery for the cited problem and also sweep variants of the same defect class: list the axes along which that class varies, probe representative inputs at the real entry point, and group failures by root cause. The sweep lives inside this step; never spawn separate nodes for the sweep or for merging its results.

## Step 2: The plan file

Write one plan file in the evidence dir (`SKILL.md`, Follow-up record) and record that path in the plan. The plan holds:

- IS rows: one per property the delivered request must have, each with its success criterion and the affected party it serves.
- COMPANION rows: `COMPANION: <item> <- <request IS row> : <why expected>`, each passing the guards of `SKILL.md`, The purpose boundary.
- Gaps: per IS row, the current state, the user impact, and the cause; or "no gap" with the evidence the property already holds.
- User-side QA scenarios: at least one per IS row, run on the real surface, each naming the exact command and one binary pass condition, with the happy case, the failure case, and the evidence path. A scenario that runs a command is a re-runnable script kept with its evidence.
- The IS-row to QA-scenario pairing: which scenario proves which row, so no row is unproven and no scenario is unowned. Step 4 carries this pairing into the goal.
- A risk list: one row per behavior the change touches, either `guard: <regression a user would hit> -> <node>` for behaviors that get a test, or `no-test: <reason>` for prose or behavior this repository cannot test, naming the QA scenario that covers it.
- The two pinned rules, stated once here and never relaxed: every command pins the task worktree, and commits are serialized.

## Step 3: Plan review

One review, by one `agent(agent='reviewer', ...)` call. The prompt follows `SKILL.md`, Delegation prompts, and carries the evidence rule from there. The reviewer reads the plan against the request and answers OKAY or lists blockers: a blocker is anything that would make the plan fail the request, introduce a regression, or rest on a proof that shows the code does not do what is claimed (a code defect); typos, number errors, and wording or format problems in evidence are correction memos. Record one fix per blocker in the plan's review record, then continue; the round is not re-reviewed.

## Step 4: The goal

`/wf` already armed one goal. Keep it and never create a second. Without `/wf`, create one goal with the host's goal tool whose objective is the IS-row to QA-scenario pairing written as one paragraph. The plan file and the `todo` list hold progress.
