Read this when stage 2 defines its batches (batch verification checks) and when stage 3 (verification and final review) runs; SKILL.md, Stages and required reads, lists it.

# dag-workflow: verification and final review

This file covers the checks each batch verification node runs in stage 2, and all of stage 3: combined verification, the one final review, REVISE rounds, and the final report. The flow ends with the report. It never opens a PR and never merges.

## Batch verification checks

Each batch verification node (`references/execution.md`, Batch verification node) runs these on top of rerunning every node's VERIFY, and its verdict file names every finding:

- **Defect classes.** Answer the question of each class the plan chose whose Checked at column in `references/planning.md`, Defect classes, says Batch verification, against the batch's output.
- **Mutation check.** When the batch changes testable runtime behavior, pick the three to five highest-risk changed behaviors, or all of them when fewer than three changed. For each, break the production code with one small edit in a throwaway copy of the worktree, run the tests that should guard it, and record killed (a test failed) or survived (none did). A survivor is a finding for the node that owns that behavior. Behaviors under a valid `no-test` row, including every change in a prose-only batch, get no mutation; the verdict says so and why. This is a bounded sample, not a full mutation-testing run.

## Combined verification

After every implementation node has a PASS verdict, run the task's QA scenarios through their real surfaces, plus the repository's tests for the changed behavior. Tests alone don't prove user-visible behavior; each scenario needs its own artifact. Record the command, the observable, PASS or FAIL, and cleanup receipts for anything the QA started.

- Assert the identity and marker of each record, not only its count. Totals can hold steady while records change or vanish.
- Every artifact a verdict, conformance row, or report cites must exist at the cited path and show the observable itself, uncropped.
- A comparator or harness is evidence only when it fails closed. Run it once on a corrupted or missing input as a control and capture that failure beside the passing run. The control goes through the same comparison; one that would still pass with the comparison replaced by a constant isn't a control.

Then check the plan's risk list:

- Every `guard` row: its test exists and passes, and its injection evidence shows the diff, the failing output, and the passing output after restore, with the diff producing the regression the guard names.
- Every `no-test` row: the reason is one of the allowed ones, any QA scenario it names passed, and each claim it makes was checked against its cited source, recorded with file and line.

A missing guard test, a missing capture, an injection that doesn't produce the guard's regression or stayed green, a scenario that skipped a step it claims, or a `no-test` reason outside the list is invalid evidence. A touched behavior missing from the risk list is in scope when it shows an IS or COMPANION row not delivered, a regression this change introduced, or when it passes companion guards (a) to (c) (`SKILL.md`, The purpose boundary): add the COMPANION row and fix it in the same worktree. Otherwise it goes to the follow-up record (`SKILL.md`, Follow-up record).

A failing scenario is in scope by definition: fix it in the same worktree through a correction batch (`references/execution.md`, Recovery).

Then build the **conformance table**, one row per IS row:

| IS row | GAP closed, or `no gap` + evidence | todo | QA evidence path + PASS/FAIL | guard row or `none` |
| --- | --- | --- | --- | --- |

A row with missing or failed evidence is a mismatch: fix it, then refill the table. Move on only when every row matches. If an IS row itself proves wrong (wrong party, rows that contradict), fix only that row in the plan and record why; never restart the run for it.

## Evidence reuse per target

Evidence is valid for a target (a scenario, test, or review claim) until something it depends on changes. Before reusing it:

1. Check what changed since capture: the files it exercised, its dependencies, and its environment. At minimum, treat as affected the tests of every touched file and of the files that import it, and the scenarios that exercise them.
2. If none of those changed, reuse it. Keep its provenance (when, where, which commit) and write down why it's still valid.
3. If any changed, or you can't tell, rerun that target.

Never overwrite or delete a captured artifact. Write each rerun to a new file with its attempt number as a suffix. The one exception is a verdict file the gate reads at its fixed path (`references/execution.md`, Batch verification node), which carries no suffix.

Don't throw out all evidence because one file changed, and don't rerun the whole matrix after every patch. The one full pass happens right before the final report (Finish and final report).

## Final review

After combined verification passes, run ONE `agent(agent='reviewer', ...)` call: a fresh reviewer, never one that worked on this task. Its prompt follows `SKILL.md`, Delegation prompts, and passes the full diff against the base SHA, the goal and success criteria, the plan's risk list, the conformance table, the plan's Plan review record (`references/planning.md`, Plan review), and the QA artifacts.

The reviewer checks that every plan-review blocker fix is really in place, and answers each class in `references/planning.md`, Defect classes, whose Checked at column says Final review (D9: docs, the report, and UI text match the actual behavior). It ends with `APPROVED` or `REVISE`. Each REVISE item must show goal failure, a regression this change introduced, or invalid evidence, including risk-list evidence that fails Combined verification. An item about a companion that passes guards (a) to (c) counts as goal failure. Anything else is a follow-up note, not a required change.

This review is mandatory, and nothing replaces it.

## REVISE

1. Build a correction batch in the same worktree from the required changes only. Record each one's cause class in the plan, as for any work failure (`references/execution.md`, Recovery).
2. Fix each required change as the defect class it represents, not just the instance it cites: find that class's other inputs and interleavings and fix them in the same batch. Independent fixes run in parallel in one `parallel()` call.
3. Run one verification node over the correction batch (`references/execution.md`, Batch verification node).
4. Rerun the QA the fixes affect; use Evidence reuse per target for the rest.
5. End with a delta re-review by a NEW `reviewer`, never the one that returned REVISE. Pass the delta diff, the required changes it cited, and fresh evidence for the affected targets, including, for each interleaving or input the previous verdict named, a capture showing its test fails with the fix reverted and passes with it.

Never paste an old approval onto changed code, and never run a fresh whole-project review per round. Repeat until `APPROVED`. There's no round limit; each round stays scoped to its delta.

## Finish and final report

Right before the report, run the full verification set once on the final tree: every QA scenario, plus the repository's test suite, typecheck, and build where it has them. Until now the reuse rule decided what reran; this pass is the one exception. Refill the conformance table from it. A failing target here is in scope: fix it through a correction batch and a delta re-review.

Then deliver the report:

- **Results:** what was delivered, the branch, the worktree path, and the commits (`<sha> <subject>`, each confirmed with `git cat-file -t`).
- **Evidence:** the QA scenarios and tests run, with artifact paths.
- **Conformance:** the refilled conformance table and the COMPANION items delivered.
- **Limits:** what wasn't proven, or what the host couldn't do.
- **Removed tests:** each existing test removed, why, and the evidence that replaces it, or "none".
- **Separate findings:** each out-of-scope finding with the companion guard (a) to (d) it fails and the follow-up file path (`SKILL.md`, Follow-up record), or "none".

The flow stops here. Leave the branch and worktree for the user: no push to a shared branch, no PR, no merge unless the user asks for it separately.
