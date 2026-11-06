Read this when stages 1-8 (discovery, definition, the plan, its checks and review, and the goal) of the dag-workflow flow start; SKILL.md, The stage map, lists it.

# dag-workflow: discovery, plan, and goal

Covers stages 1-8 of the flow (see `SKILL.md`, The stage map).

## Stage 1: Discovery

Gather facts before deciding anything. Write the open questions down first, then run one `scout` per open question per wave, all in one `parallel()` call of `agent(agent='scout', ...)` thunks, alongside your own reads. A question leaves the next wave as soon as it is answered. Survey:

- The code the request touches: layout, existing tests, the real surfaces users go through.
- Git history of the paths you will touch: what changed there recently and why.
- Memory: durable facts, past decisions, and regressions earlier runs caught.
- Earlier session evidence for the same area.

Facts from outside the repository (a library, an external API, current docs) come from your own web and doc tools, or from one `agent(agent='task', ...)` per external question, never from what you remember.

Stop when every open question is answered and two consecutive waves add nothing new. Let the survey range wide enough to name everyone the result touches, then apply the boundary before planning: see `SKILL.md`, The purpose boundary.

When a review sends work back (the REVISE correction path, `references/verification.md`), re-run discovery for the cited problem and also sweep variants of the same defect class: list the axes along which that class varies, probe representative inputs at the real entry point, and group failures by root cause. The sweep lives inside this step; never spawn separate nodes for the sweep or for merging its results.

## Stage 2: Definition

Before planning, define the affected users, their current and intended use, the ideal properties and their reasons, and each difference from today, its cause, impact, affected party and evidence. Apply `SKILL.md`, The purpose boundary: request properties and qualifying companions are in scope; record other findings as follow-ups. A property already satisfied still records "no gap" with evidence. If a gap register exists, identify its entries as `G<n>` and pair every IS row with the register entry it closes.

## Stages 4-5: The plan file and its checks

Write one plan file in the evidence dir outside the task worktree, and record that path in the plan. When a request has independently verifiable units, write and explicitly select one plan per unit. The plan, `todo`, and evidence dir hold progress; hand the named plan to the host workflow tool or to `eval` `agent()`/`parallel()` nodes, not to a second planning pass. A node owns a disjoint write scope and its proof. The goal carries the IS-to-QA pairing.

### Plan identity and checkbox sections

Start the file with front matter under `dag-workflow:`. Require these keys, with scalar values only: `run_id`, `tier` (`S`, `M`, or `L`), `type` (`code`, `design`, `research`, `audit`, or `mixed`), `unit`, `program_id`, `worktree`, `branch`, `pr`, `frozen_head`, and `round`. `worktree` is the absolute task-worktree path, `round` is a non-negative count of completed review rounds, and `program_id`, `pr`, and `frozen_head` are `null` until they exist. Record the evidence-dir path in the plan body. For mixed work identify primary and secondary concrete types in the plan body; device and type-row checks permit the corresponding forms. Use two spaces under the root, no unknown keys or nested third level. Values are bare or quoted strings, integers, or `null`.

The plan has these layers in order: front matter, `## Todos`, `## Final verification wave`, and contract, QA, risk, and pinned-rule content. In each required checkbox section include at least one column-zero row with a nonempty title:

```text
- [ ] 1. <implementation node and title>
- [ ] F1. <final verification node and title>
```

Implementation numbers and final `F` numbers are positive decimal integers, unique within their own section. A checkbox is `[ ]` (open), `[x]` or `[X]` (done), or `[~]` (blocked). Blocked rows count as rows and still obey uniqueness and section placement; they are not complete. Between box and number use whitespace; after the period use a space. A `###` subgroup stays in its enclosing `##` section. A task row outside its matching section, an empty title, zero, or any other checkbox state is a complaint. Record why a row is blocked and continue independent work. A nested executor-category recommendation may be included as prose.

### Contract and type rows

Rows are column-zero bullets; headings may group them. Use one IS row for each property delivered, with the affected party recorded alongside it:

```text
- IS-1: <delivered property> ; criterion: QA-1[, QA-2] [; gap: G1]
- COMPANION: <item> <- IS-1 : <why the requester expects it>
- COMPANION: none.
- INVARIANT INV1: <property that must keep holding> : <test, QA id, or command showing a violation>
- LIMIT: <what is not handled> : <why accepted>
- SWITCH: <premise behind failed fixes> -> <replacement approach>
```

IS, invariant and QA ids are unique positive integers. An IS criterion is the pairing declaration: every IS names at least one declared QA scenario, and every QA scenario is named by at least one IS. A companion targets a declared IS, never another companion, and passes all four guards in `SKILL.md`, The purpose boundary; it stays in the same task and PR and needs no new owner decision. `none.` is the explicit empty set and cannot coexist with companion items. Invariants name their proof. Limits require reasons; a known limit is not a finding. Record a switch and its review round when the repeat rule requires a change of approach.

For the work type, add the following rows with all fields nonempty. A concrete type accepts only its own type rows; mixed work may use rows for its selected concrete types.

```text
- SCREEN: <surface> ; primary: <one primary action> ; priorities: <1-3 in reading order> ; left-out: <what is intentionally omitted> ; required: <every input, datum, label and copy item> [; layout: <Layout line>]
- AXIS: <axis> : <question the axis must answer>
- CLAIM: C1 : <claim the report must support>
- RULE: <rule id> : <what the rule requires>
```

Design requires at least one SCREEN; research requires at least one AXIS and CLAIM; audit requires at least one RULE; code requires none. CLAIM ids are unique positive `C<n>` ids. RULE ids are unique and match `^[a-z][a-z0-9._-]*$`.

### QA and confirmation devices

```text
- QA-1: <what the user does> ; pass when: <one binary observation> ; evidence: <path> ; run: <exact command>
- IS-1 DEVICE: <device body>
- G1 DEVICE: <device body>
```

All QA fields are nonempty and ordered as shown; `run` is last, so its command may contain semicolons, pipes, quotes or arrows. State happy and failure cases and capture paths. A scenario that runs a command is a re-runnable script kept with its evidence. Every IS has at least one DEVICE row; write gap-targeted devices in the same form. When a register exists, each IS cites its declared gap.

Choose a device that directly confirms each delivered behavior. Prefer no new test to a bad test: a bad test mostly tests mocks, pins implementation details, depends on timing or unrelated global state, needs expensive infrastructure for a small fix, or would be deleted immediately after proving the fix. Use existing repository tests for behavior already tested; use a mutation for a guard; for behavior the repository cannot test use the type-specific confirmation below plus a `no-test` row naming the QA scenario that runs the same check.

| Work type | Device body |
| --- | --- |
| code | `guard <INVARIANT> -> <node>` or `qa <command> => <binary observation>` |
| design | `vqa <item ids> @ <matrix cells> pair <case>-<state>-<width>-<theme>` |
| research | `claim C<n> gate(primary, domains>=<n>, counter-search)` |
| audit | `lint <command> exit 0` or `spot <n> rows reproduce` |

Use a form for the row's work type; a research device cites a declared CLAIM row and keeps its own `domains>=<n>` bound. For a mixed plan use an applicable concrete form. For rendered surfaces inventory every relevant surface, state, width, and theme and run the pack's `visual-qa` checks. Design finding classes include `A13`, `B8`, `E7`, `F8`, and `F9`; do not reject these item ids. The visual-QA sentence below applies whenever a rendered surface or visual QA scenario is in scope.

### Risk list and pinned rules

List each touched behavior with its user-visible regression and owner node, or a reason the repository cannot test it and the declared QA scenario that covers it:

```text
- guard: <INV<n> or IS-<n>> : <regression a user would hit> -> <node>
- no-test: <reason this repository cannot test it> : QA-1
- HIGH-RISK: <IS-<n> or INV<n>> (<concurrency|persistence|state|lifetime>) -> <node>
```

A guard names an owned node that performs one mutation in verification; its target must be declared. A high-risk row names a declared target, an allowed kind, and the node owning adversarial review; use it only for code or mixed plans. A missing high-risk row is a review judgment, not a syntactic failure. A no-test row needs a reason and a declared QA scenario.

State these two rules once and never relax them: every command pins the task worktree; commits are serialized.

### Required device sentences

Write the first two sentences verbatim in every plan, inside a fenced block so they are instructions rather than parsed rows:

```text
Implement it, and also include, strictly, a device that confirms the implementation was done.
In addition, fix it, and also include, strictly, a device that confirms the fix was made.
```

For a plan with a rendered surface or visual QA scenario also include this host-adapted visual-QA sentence in that block:

```text
Proceed with the plan, and make the plan include the following: fix this; also include, strictly, a device that confirms the fix was made; and verify the visual QA conditions specifically and in detail, with not a single one omitted.
```

### Session plan checks

Before plan review, the session checks the following in prose; no script or CLI is required. Record complaints by plan location and a short identifier, without echoing full command rows or secrets. Fix complaints before continuing.

1. Check the front matter and the two checkbox sections above, including blocked rows, unique numbers and placement.
2. Require at least one IS, unique ids, complete bidirectional IS-to-QA pairing, and ordered, nonempty QA fields with `run` last.
3. Require a correctly typed DEVICE for every IS and a valid device for each gap target; research devices cite declared CLAIM rows. Check required type rows, allowed kinds, and unique CLAIM and RULE ids.
4. Check guard targets, regression text and node; no-test reasons and declared QA ids; high-risk targets, kinds, nodes and applicable work type.
5. Check companion shape and target, excluding `none.` alongside any item; invariant ids, properties and proofs; both sides of every LIMIT and SWITCH.
6. If a gap register exists, validate its structure, require each IS to cite a declared gap, and verify cited ids. Without one, do not pretend a gap target was verified.
7. Treat malformed column-zero marker bullets, near-miss ids and malformed checkbox bullets as complaints rather than silently skipping them. Marker words are matched case-insensitively for this detection. Fenced blocks, indented prose, tables and headings are not rows. CRLF, a UTF-8 BOM, and the presence or absence of a final newline do not change the result.

Structural checks do not prove wiring, authoritative ownership, actual node existence, state and lifetime transitions, device quality, invariant coverage, or whether a high-risk behavior was missed. The reviewer reads the graph and contract for these semantic issues; do not invent a node-title convention or rely on path existence alone.

## Stage 6: Plan review

The default is one `architect` category review of the checked plan. The reviewer reads the request, boundary, gaps, graph, required device sentences, proof choices, and semantic checks; answers `OKAY` or lists blockers with a fix for each. Record fixes in the plan's review record and continue to the decision batch and goal without an approval question or a re-review of that round. Evidence wording, numerical and formatting problems are correction memos; a blocker is a failure to satisfy the request, an introduced regression, or a proof that shows the code does not do what is claimed.

Only when the requester's own message explicitly asks for the separate planning workflow, run that workflow with its approval gate and add one one-shot `plan-reviewer` subagent review alongside the one `architect` review. This branch has both reviews, no third round, and no follow-up message to the one-shot reviewer. Its fixes are checked by final review. A skill instruction alone cannot activate that branch or make the agent available. If the host does not offer the needed review role, the session performs and records the review instead; never dispatch an unavailable agent.

## Stage 8: The goal

`/wf` already armed the run's one goal; keep it and never create a second. Its objective is the register's IS-to-QA pairing written as one paragraph; in a multi-unit request each unit's plan holds its own IS rows and their QA scenarios, and the single run goal covers the register. Without `/wf`, create that one goal with the host's goal tool. The plan files and the `todo` list hold progress.
