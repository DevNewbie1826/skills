Read this when stage 1 (discovery and plan) of the dag-workflow flow starts; SKILL.md, Stages and required reads, lists it.

# dag-workflow: discovery and plan

This file covers stage 1. It ends with one plan file and one plan review, and then the run moves straight into execution.

## Discovery

Gather evidence before deciding anything: the code, the git history of the paths you'll touch, the existing tests for that behavior, and the docs that describe it.

Write down the open questions first. Then run one `scout` per open question, all of them in one eval `parallel()` call of `agent(agent='scout', ...)` thunks, alongside your own reads. Over-collect inside that bound: a finding that goes unused costs less than a decision made without a fact a lane would have found. A question leaves the next wave as soon as it's answered. Facts from outside the repository (a library, an external API, current docs) come from your own web and doc tools, or from one `agent(agent='task', ...)` per external question; never rely on what you remember about them.

Stop collecting when both hold: every open question is answered, and two consecutive waves have added nothing new. A question still open at that point becomes a stated assumption in the plan, or a question for the owner when the answer changes what gets built. Discovery runs no other agents.

Name everyone and everything the result touches, and how they use it, in four explicit steps before applying the boundary:

1. Name every party the result touches: code and programs, other developers, end users.
2. How each uses it now.
3. How each will use it after the change.
4. Where each snags today, or what bothers them.

These four steps become the plan's affected-parties table. Use that picture to set the boundary, not to grow the request. Apply `SKILL.md`, The purpose boundary: the request and the COMPANION items the requester would naturally expect done together are in scope, and everything else goes to the follow-up record (`SKILL.md`, Follow-up record).

## The plan

Write ONE plan file in the evidence dir, a directory outside the task worktree such as `<worktree>.evidence/`. Record that path in the plan itself. The plan holds:

- **Affected parties and ideal state.** The affected-parties table from Discovery, one row per party. One IS row per property the delivered request must have, stated so that, from the affected party's view, nothing snags, feels odd, regresses, or degrades. Each IS row carries its reason and a success criterion.
- **Success criteria.** Classify each behavior the change touches before writing its criterion. A behavior the request changes (a bug fix, a restore, new code) is checked against intent: the spec or requirement. A behavior the change must leave intact, including persisted state and side effects such as scheduled jobs, queues, and stored records, is checked against a reference recorded before the change: what the code does today, the actual value, even where it looks wrong. Record that reference before editing, as an observation rather than a test written first, and never substitute your own idea of the correct value. A criterion names the observable behavior, not an exact assertion line, because an earlier assertion in the same flow can fire first and make it unsatisfiable. A criterion over records compares them by identity, not count.
- **Gaps.** Every IS row has either a GAP row or `no gap` with the evidence that the property already holds. A GAP row has three columns: current state | user impact (required) | cause (if known).
- **Todos.** Every todo is a checkbox listing the GAP it closes, its method, the reason for that method, the files it writes, and its prerequisites.
- **COMPANION rows.** In-scope items beyond the request itself, one per row as `COMPANION: <item> <- <request IS row> : <why expected>`. Each passes guards (a) to (d) in `SKILL.md`, The purpose boundary; anything failing one is out of scope.
- **QA scenarios from the users' side.** At least one per IS row, each with the reason it proves that row. A scenario names the real surface, the exact invocation, the single PASS/FAIL observable, the happy case and the failure case, and the evidence path. It proves only the steps it actually performed: a rehearsal that skips, stubs, or assumes a step it claims (a reconnect, a restore) is invalid evidence for that step, and its artifact must show the state after that step. Every criterion and scenario must be satisfiable in principle. On a live system that keeps writing, such as a running daemon's state directory, "the file list is identical before and after" fails whether or not QA touched it. Prove non-interference instead: the QA actions ran in their own sandbox (temporary directory, config, socket, port) and wrote there, and read-only before-and-after observations show the same live process IDs, start times, and deployed-binary hash. Only those read-only observations may name a live path. Each scenario that runs a command, harness, or comparator is a re-runnable script kept with its evidence, never a hand-assembled transcript, and it carries a control that can fail (`references/verification.md`, Combined verification). Prose changes get a read-through scenario.
- **Risk list.** One row for each behavior the change touches, in one of two forms:
  - `guard: <regression a user would hit> -> <node> [<existing test path::name>, when one already catches it]`
  - `no-test: <reason>`, where the reason is exactly one of: the change is prose, a prompt, or docs (read-through QA, never wording tests); or the behavior can't be tested in this repository, so QA scenario `<id>` covers it. A row that rests on a claim about behavior, such as restart or recovery, names the source that establishes the claim.

  A guard names a regression a user would hit, never an implementation step. Only `guard` rows get new tests (`references/execution.md`, Regression tests).
- **Defect classes chosen.** The classes from Defect classes below that apply, each with the plan's answer to its check question.
- **Batches and nodes.** Name each node, its write scope, its real dependencies, and the agent that runs it, picked from `SKILL.md`, Agents per stage. Group nodes into batches by dependency. Don't invent nodes to fill a quota.
- **Baseline command.** The repository's test and check commands that establish the green baseline before the first batch.
- **Out of scope.** Anything discovery surfaced that the request doesn't need.
- **Follow-up file.** The path and timing from `SKILL.md`, Follow-up record.
- **Plan review record.** Each blocker the plan review cites, with the fix and where it lives, as `<blocker> -> <fix> -> <where>`.

## Defect classes

Each class is a failure that tends to slip through to late review, written as a check question. At planning, pick the classes that apply to the change and answer their questions in the plan; skip the rest. Each class has one stage that checks it: the plan review (Plan review below), the batch verification node (`references/verification.md`, Batch verification checks), or the final review (`references/verification.md`, Final review). When a run finds a failure class this table lacks, append it with its check question and stage.

| ID | Class | Check question | Checked at |
| --- | --- | --- | --- |
| D1 | Non-discriminating verification | Can this check fail when the defect it names is present, and is there current evidence of it failing, such as an injection or mutation, rather than a single PASS? | Plan review |
| D2 | Proof bypasses the real surface, target, or revision | Does the command or capture run against the claimed target, such as the remote, the live surface, the stated viewport, or the commit under review, rather than a cache, proxy, script, or older revision? | Plan review |
| D3 | Verdict contradicts its own artifact | Does each verdict match the actual text of the artifact it cites? | Batch verification |
| D4 | Fake or fixture diverges from the real contract | Does each test double behave like the real contract it stands for, and does each hard-coded fixture value come from the production constant? | Plan review |
| D5 | Fix-induced regression | Does the fix change adjacent behavior, boundaries included, and does an existing or new guard cover that change? | Batch verification |
| D6 | Boundary, saturation, or empty input | At a capacity limit, a size budget, or an empty or missing input, does the behavior follow the contract instead of silently dropping something? | Plan review |
| D7 | Resource ownership and cleanup | On cancel, failure, or confirmed end, does the owner release each process, connection, socket, lock, or file, without killing a shared resource? | Batch verification |
| D8 | State sampling, branch order, or timing | Does each state comparison use the previous sample rather than a high-water mark, does the branch order keep every due outcome reachable, and does each assertion run after parsing or rendering completes? | Batch verification |
| D9 | Deliverable contradicts the source of truth | Do docs, the final report, and UI text match the actual behavior and source, with no claim stronger than its evidence and nothing invented? | Final review |
| D10 | Superseded requirement not propagated | If the requirement changed during the work, do the implementation, tests, and docs prove the latest one rather than the superseded contract? | Plan review |
| D11 | Nondeterministic or load-sensitive test | Does the test give the same result alone, repeated, and in the full suite under load? | Batch verification |

## Plan review

One review, by one `agent(agent='reviewer', ...)` call. Its prompt follows `SKILL.md`, Delegation prompts, and passes the plan file path, the original request, and `SKILL.md`, The purpose boundary. The reviewer reads the plan against them and the rules in this file and answers `OKAY` or `BLOCKERS:` followed by a list. No panel, no extra advisory lanes.

A plan blocker is something that would make the plan fail the request, introduce a regression, or rest on invalid proof. These count:

- A regression a user would plainly hit has neither a `guard` row nor a valid `no-test` row; a guard names an implementation step instead of a regression; a `no-test` reason is outside the allowed list.
- A COMPANION row fails a guard (a) to (d), or a plainly expected item is missing both as an IS or COMPANION row and as a reasoned follow-up.
- A criterion or scenario can't be met in principle (The plan, QA scenarios from the users' side).
- An applicable class from Defect classes, checked at the plan review, whose question the plan leaves unanswered.

Fix every cited blocker in the plan and record it in the Plan review record. The plan is never re-reviewed: the final review checks these fixes (`references/verification.md`, Final review). Before execution starts, re-read the plan once and confirm each recorded fix is actually in it; that check is not a second review. Other remarks become notes.

## Leaving this stage

When the one plan review has returned and every blocker it cited has a recorded fix, register the `todo` list (`SKILL.md`, Progress reporting) and continue straight into stage 2 under `SKILL.md`, Stages and required reads. Don't stop with a planning-only summary, and don't ask for a second approval: running the flow already authorized execution.
