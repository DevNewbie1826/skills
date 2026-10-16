Read this when steps 6-13 of the flow start; SKILL.md, The 13 steps, lists it.

# dag-workflow: verification, review, and merge

Covers steps 6-13 of the flow (see SKILL.md, The 13 steps).

## Step 6: Pre-PR verification

A failure that touches no IS or COMPANION row and fails the same way on the base commit (both runs captured) goes to the follow-up file (`SKILL.md`, Follow-up record) and the final report; every other failure, and any check that could not run, is fixed and rerun before the PR.

Run the two branches in one `parallel()` call of two `agent(agent='task', ...)` nodes. Both nodes' prompts follow SKILL.md, Delegation prompts. Both branches must pass before the PR (gate order: SKILL.md, Non-negotiable rules).

- Branch (a), one `task` node: run the repository test suite, then the mutation check. Pick the 3-5 highest-risk changed behaviors (all of them if fewer changed). For each, break the production code with one small edit in a throwaway copy of the worktree, run the tests that should guard it, and record killed or survived. A mutation is killed only when its guard test passes unmutated and fails under the mutation; a run that fails for any other reason is not a kill. A survivor means a regression would pass unnoticed: strengthen that behavior's guard test until the mutation is killed, or record a no-test reason in the plan's risk list. Branch (a) passes when every failure is fixed or sent to the follow-up file under the rule above, and every mutation is killed or resolved this way. Behaviors under a valid no-test row get no mutation.
- Branch (b), one `task` node: run every QA scenario's happy case and failure case on the real surface. Record per scenario the command, the observable, PASS or FAIL, the output capture, and the cleanup receipt for anything the scenario started. A failing scenario follows the rule above.

## Step 7: Code review round

Run one `reviewer` once per round, before the PR. Its prompt follows SKILL.md, Delegation prompts, and requires the reviewer to load and apply `remove-ai-slops` and `programming` and to state in its report whether that check ran. It reports findings by severity CRITICAL, HIGH, MEDIUM, LOW. Fix the CRITICAL and HIGH findings once, through `task` nodes, then continue; the round gets no second pass. MEDIUM and LOW are notes for the report. In a REVISE round the reviewer sees only the delta diff since the last reviewed commit.

## Step 8: Open the PR

One PR to the repository's main branch. The body states the behavior delivered, the tests and QA run with their capture paths, and the real limits. Claims stay within what the captures hold; never retype a number or SHA that a capture already holds. In a REVISE round, update the PR body.

## Step 9: Final review

One fresh `reviewer`, never one that worked on the task, after the PR exists. It reports every code defect of the PR in one verdict, never stopping at the first defect, and ends APPROVED or REVISE. Its prompt follows SKILL.md, Delegation prompts.

## Step 10: Evidence problems

The evidence rule is in SKILL.md, Delegation prompts. Apply it from there without restating it.

## Step 11: APPROVED or REVISE

- APPROVED: the lead merges the PR.
- REVISE, code problems only: go back to step 1 (`references/planning.md`, Step 1: Discovery) for the cited problems: re-run discovery with the variant sweep; update the plan (step 2: a COMPANION row for each in-scope variant, a risk row for each fix; `references/planning.md`, Step 2: The plan file); run the fixes as a correction run under `references/execution.md`, Step 5: Run the plan, in the SAME worktree and SAME PR with more commits; then run steps 6, 7 (delta diff), 8 (update the PR body), and 9 again. Steps 3 and 4 are not repeated: the plan review is one round and the goal already exists.

## Step 12: Post-merge verification

After the merge, one `task` node runs every QA scenario, plus the repository test suite, typecheck, and build where the repository has them, on the merged result. Its prompt follows SKILL.md, Delegation prompts. A failure follows the Step 6 rule; a fix goes through steps 5-11 again from the merged base, never as a direct patch to main.

## Step 13: Cleanup and final report

- Clean up the task: remove the worktree and the branch, stop owned processes, and record a cleanup receipt for each.
- Complete the goal once the merged result passes step 12.
- Final report: results, evidence locations, limits, and every out-of-scope finding with its follow-up record path (`SKILL.md`, Follow-up record), or "none".

Stop conditions and the report shape: see SKILL.md, Finish.
