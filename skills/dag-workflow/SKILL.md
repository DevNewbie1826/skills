---
name: dag-workflow
description: "Use to work one authorized request to a merged PR on omp: define the ideal state from evidence, run every part as a DAG of eval agent() nodes under one goal, prove each requirement with a strict confirmation device, and review the PR until APPROVED. Triggers: /wf, decompose this task, split work across agents, run it as a DAG, big task, too large for one pass, request to merged PR."
omp-native: true
---

**Read `references/workflow.md` and `references/ultrathink.md` first.**

# dag-workflow

**Then read `references/graph-runs.md`.** It is how a DAG runs on omp: nodes, stages, retries, the goal and resuming.

One request is one authorized piece of work, worked until its PR merges. `/wf <task>` starts it: the pack arms a goal for the task and points here.
Arm the goal first: one omp goal for the whole request, its objective listing every phase with that phase's real success criteria. When `/wf` already armed the goal with the task text, keep it (the `goal` tool cannot rewrite an objective, and dropping it ends goal mode) and write each phase's success criteria as the first `todo` items of that phase. Never run with placeholder criteria. Mirror the phases into `todo` phases, then build every DAG under that goal.

## The request

1. Build a DAG over the whole context and history of the work, analyze it at maximum parallelism, and define from evidence the ideal state for the current problems and the main decision points. Size the analysis by the three questions in Size check: small work is one `scout` node, and only big work gets a full analysis DAG. Independent leaves that don't depend on the definition (translating a reference, for example) may start in this first DAG beside the analysis.
2. From that definition, create a new git worktree. Create one only when the work changes a repository.
3. Set concrete goals and work toward them.
4. Run all the defined work as DAGs for maximum efficiency. Building a DAG follows the DAG reference (see DAGs).
5. Implement it, and strictly include a device that confirms the implementation.
6. Fix whatever needs fixing, and strictly include a device that confirms each fix.
7. While doing so, verify that every requirement is met, rigorously and in full detail, with nothing skipped. A strict confirmation device follows the verification reference (see Confirmation devices).
8. For UI/UX work, verify every `visual-qa` condition in full detail, nothing skipped.

## DAGs

Build every DAG per `references/dag-construction.md`: top-down to atomic tasks, bottom-up convergence through the direct parent, no skipped layer, no flat convergence, maximum parallelism.
`references/dag-construction-ko.md` is the owner's original. Where the two differ, the Korean original governs.
Run each DAG in the `eval` tool with `agent()` nodes under the one goal, as `references/graph-runs.md` describes.
Every part with parallelism is a DAG, and its last node is its review.
Fixes after a review are a DAG too, sized by the same three questions. A 1-2 line fix needs no DAG: make it, confirm it and commit it.
An integration node that only collects and checks its children's results is a check inside the parent, not a separate node (section 4.3 of the DAG reference). Make it a separate node only when integrating needs its own execution, such as merging edits or running the tests over the combined result.

## Node prompts, run files and commits

A scope line in a node prompt names the node: "this node writes only X". Never write it as a statement about the whole repository, such as "the repo is read-only"; a memory tool can keep that as a standing agreement and stop later work.
Put node handoffs and build files in a git-ignored folder inside the worktree; when the repository ignores none, list one in `.git/info/exclude`.
A commit node stages only the paths it names (`git add -- <path>...`, never `git add -A` or `git add .`) and sets the repository's identity for that one command: `git -c user.name=<name> -c user.email=<email> commit`, with no co-author trailer. Take the name and email from the request or brief, never change the global Git identity, and ask before the first commit when no identity is given.

## Confirmation devices

Confirm directly, so another agent can reproduce it from the commands, exit codes, results and unverified items you leave; reuse existing tests and tools; add no ceremonial or duplicate checks; never claim what you didn't verify. The full standard is `references/verification-device.md`.
This holds for every verification node in a DAG, not only the PR review: an evidence typo (a wrong count, an off line range) is a note, never a FAIL and never a loop.
Code size has no line-count targets. Judge bloat by the `remove-ai-slops` skill. If one file gets hard to hold, split it into files inside the tool's own folder.

## Skills and agents per work type

Every name here exists on omp or in this pack; `references/omp-names.md` is the list, and the pack checker fails on any other agent or tool name.

| work type | read and use | for what |
| --- | --- | --- |
| coding (patch, feature, bugfix, refactor) | `programming`, `tdd`, `debugging`, `git-master`, `remove-ai-slops`; `task` agent; `ast_grep`, `ast_edit`, `lsp` tools | `task` nodes own each change and its proof; production code and tests under `programming` and `tdd`; `debugging` for crashes, wrong output or hangs, locked by a failing test; `ast_grep` and `ast_edit` for syntax-shaped search and codemods; `git-master` on every commit node; `remove-ai-slops` to cut slop behind regression tests |
| research | `scout` agent; `web_search`, `read`, `grep` tools | `scout` nodes read and report, one per angle, and a review node checks each claim against its source |
| design / UI | `frontend`, `visual-qa`, `programming`, `remove-ai-slops`, `git-master`; `task` agent; `browser` tool | `frontend` builds; `visual-qa` verifies every one of its conditions in full detail and owns the checklist; the `browser` tool drives the real page for QA; `programming` and `remove-ai-slops` guard the code |
| audit | `remove-ai-slops`, `frontend`, `visual-qa`, `programming`, `seo-html`; `scout` agent | the rule corpus is those skills' own rule sets, cited by id; collection and judging run as one DAG |
| planning | `programming`, `remove-ai-slops`, plus the work type's own skill (`visual-qa` for design); `reviewer` agent | read `programming` and `remove-ai-slops` first so the plan carries real test and slop constraints; a `reviewer` node critiques a contested plan before the build |
| review | `programming`, `remove-ai-slops`, `visual-qa`; `reviewer` and `security-reviewer` agents; `security_scan` and `browser` tools | `programming` and `remove-ai-slops` are the code-review axes; `visual-qa` is the verdict for UI; the `browser` tool captures on-surface evidence; `security-reviewer` and `security_scan` for anything touching security |
| cleanup | `remove-ai-slops`, `git-master` | remove dead code and slop behind regression tests, tear down worktrees and branches under git rules |
| collection / corpus extraction | `programming`, `remove-ai-slops`, `visual-qa`, `frontend`; `scout` agent; `ast_grep` tool | collect in one DAG; extract by syntax shape with `ast_grep`; harvest the distilled rule sets before any raw corpus |
| decision history | `lore`, `git-master` | record and read the constraints and rejected options behind a change |
| multi-unit program | `references/graph-runs.md` | one goal for the program with one phase per unit, one build DAG per wave |
| browser-facing surface work | `visual-qa`; `browser` tool | the `browser` tool drives the page for actions, screenshots and traces; `visual-qa` judges the captured state. Not for a plain search or a static fetch |
| resume after death or compaction | `references/graph-runs.md` | re-read the goal, `todo` and handoff files; re-run only nodes whose handoff is missing, never restart the DAG |

Reviewer dispatch follows Size check and Review and merge below.

## Size check

Answer three questions about the PR:

1. If it's wrong, is the impact small and recoverable with one revert?
2. Is it confirmed at once by CI or by eye?
3. Is it set work with no design judgment? A new file following a pattern counts as set work.

All yes means small work: CI plus a self-review. No other-model review.
Any no, or anything touching security, permissions, data loss, concurrency, schema, several repositories, hard recovery or a design fork, means big work: a `reviewer` agent review, on a different model family from the author when one is configured. Work touching security also gets a `security-reviewer` review.
When unsure, go one level up.

## Review and merge

The end of the work opens a PR. Its body carries the evidence: commands, exit codes, results and unverified items. Keep no receipts and no ledger.
Small work puts its self-review in the PR body.
Big work goes to the `reviewer` agent, which reviews endlessly until APPROVED. There's no round cap, and APPROVED is the only end.
Round 1 reviews the whole PR to the end and lists every problem at once.
Fixes for the cited problems go back to the start of this method, sized as in DAGs: they run as a DAG whose last node is the next round, or, for a 1-2 line fix, are made, confirmed and committed directly before the next round.
From round 2 on, only the fixed parts are reviewed. There's no final full review.
A blocker is one of two things, and only with proof (a reproduce command, or the exact code line and path):
- A. A plan violation: a requirement not met, or a must-hold condition the plan lists broken.
- B. A proven real defect of any kind: security hole, data loss, secret leak, crash, wrong result.
Anything without proof is a note. There is no default-conditions list.
A reviewer who doubts the evidence re-runs the command itself.
Evidence typos are notes, never a loop. Evidence alone never causes a review loop.
After APPROVED (or the small-work self-review), stop and wait for the lead's line `MERGE GO <PR> for head <40-hex> only.` Merge only that PR at that head. Never merge, release or deploy without it.
Remove the worktree after the merge.
