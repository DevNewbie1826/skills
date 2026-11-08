Read this when stages 1-8 (collect with the context graph, define, the plan, its checks and review, and the goal with its worktree) of the dag-workflow flow start; SKILL.md, The stage map, lists it.

# dag-workflow: context graph, definition, plan, and goal

Covers stages 1-8 of the flow (see `SKILL.md`, The stage map).

## Stage 1: Collect — the context graph

Stage 1 is the context graph: the overall context and history of the work gathered at maximum parallelism, as nodes with edges, handoff files, per-node checks and one reducer. It produces the evidence stage 2 defines the ideal state from. Why each phase is one graph, and what a graph must satisfy, are owned by `references/graphs.md`, The flow's three graphs; this section owns stage 1's nodes, edges and closing check.

### Open questions first

Write the questions down before any node runs, to `<evidence>/collect/questions.md`: one line per question with a stable id, the question in a form one answer can settle, the node that owns it, and the citation that settles it (`file:line`, `sha`, a memory path, a session id, a url). A question that cannot name what would settle it is not ready; split it until it can. Start from:

- **The request's own ambiguities** — what must be true for the work to be done, and what the requester would call a failure.
- **The code the request touches** — layout, the real surfaces users go through, existing tests, and the call sites that make them real.
- **Git history of the touched paths** — what changed recently, when, and why.
- **Memory** — durable facts, past decisions, and regressions earlier runs caught.
- **Earlier session evidence** for the same area.
- **Outside sources** — a library, an external API, current docs.

A memory hit is a pointer to evidence, not an answer.

### The graph

Every open question, and every slice of the request whose survey stands alone, is one node with a stable id. The default slices are the code, its history, memory and earlier sessions; the request adds the rest. The lead's own reads are nodes too, never work done beside the graph. Route by what the node does: `scout` for scope, file maps and outside-source reading (it has `web_search`); `sonic` for a mechanical harvest; `task` for extract, for a question that must run the product, and, when an outside question needs a heavier read than one page, for that one external question as its own node. Outside facts never come from memory.

A slice node writes `<evidence>/collect/<id>.md`: its answers, the citation for each, and every source it could not open, by exact path. One `task` check node, `<id>-check`, depends on it and re-opens each cited line, sha and url, writing `<evidence>/collect/<id>.check.md` as `PASS` or as the exact citation and what it actually says; a check that cannot read its slice's file fails that node. One `task` reducer, `collect-reduce`, depends on every check node and writes `<evidence>/collect.md`: one section per question, the answer with its evidence, every conflict between slices, and every unread source named by exact path. An unread source is named in `collect.md`, never omitted.

The edges do only one job, ordering: slice → its check, every check → the reducer. Data moves through the files, and a consumer treats a missing or malformed handoff as a failure of its producer, never as an empty answer.

```js
// agent(), wait() and write() are eval prelude helpers; references/graphs.md, Running a graph on omp owns the full runner.
const dir = "/evidence/run-42/collect";

// Questions exist before the first dispatch; one node per open question or slice.
const nodes = [
  { id: "q-code", agent: "scout", cite: "file:line", ask: "Which files, real entry surfaces and tests does the request touch?" },
  { id: "q-history", agent: "scout", cite: "sha", ask: "What changed on each touched path recently, and why?" },
  { id: "q-memory", agent: "task", cite: "memory path", ask: "Which durable facts, decisions and regressions name this area?" },
  { id: "q-sessions", agent: "task", cite: "session id", ask: "What did earlier sessions record about this area?" },
  { id: "q-ext", agent: "scout", cite: "url", ask: "What do the current docs say about each outside API the request depends on?" },
];
// An outside question too heavy for one page gets its own task node instead of joining q-ext.

await write(`${dir}/questions.md`, nodes.map((n) => `${n.id} | ${n.agent} | ${n.cite} | ${n.ask}`).join("\n") + "\n");

// One chain per slice: its check node starts the moment that slice settles, and nothing else waits.
const chains = nodes.map(async (n) => {
  await wait([agent(
    `${n.ask}\nAnswer in ${dir}/${n.id}.md with file:line, sha, url, memory or session evidence, and name every source you could not read by exact path.`,
    { agent: n.agent, label: n.id },
  )]);
  await wait([agent(
    `Re-open every citation in ${dir}/${n.id}.md. Write PASS, or the exact citation and what it really says, to ${dir}/${n.id}.check.md.`,
    { agent: "task", label: `${n.id}-check` },
  )]);
  return n.id;
});
await Promise.all(chains);

// One reducer, ready only when every check node has settled.
const reducer = agent(
  `Read ${dir}/questions.md and every ${dir}/*.md, including the .check.md verdicts. Write ${dir}/../collect.md: one section per question, the answer and its evidence, every conflict between slices, and every unread source named by exact path.`,
  { agent: "task", label: "collect-reduce" },
);
await wait([reducer]);
```

A question a slice opens but does not answer is a revision: the lead adds its node and check, records the change against the graph, and re-runs only the reducer, which is downstream of every check. The stage closes when every question in `questions.md` is answered and two consecutive waves add nothing new — a wave that answers nothing and opens nothing is recorded as empty, and two consecutive empty waves close it. The lead's close check then reads `collect.md` against `questions.md`: every question answered, every unread source named, every `<id>.check.md` `PASS`. A close-check failure reopens only the slice the named citation belongs to, and the lead records the stage on the strength of that check.

### Before launch

Define the whole graph before the first dispatch and hold it to `references/graphs.md`, Before launch: the graph checks. Those checks are: unique ids, every dependency exists, no cycle, no two concurrently runnable nodes writing the same file, and verification coverage for every node. Writes are disjoint by construction; the waves are as wide as the ready set allows, so every ready node starts before the graph waits, and nothing is capped at a fixed batch size. The bound is the session's background-job limit (`async.maxJobs`). The slices are heterogeneous, so each is its own node; a pool suits one shape repeated over many items, and `references/graphs.md`, Wide graphs: shards, reducers, bounded reports owns that shard form. At tier S the graph collapses to the one slice that matters and its check; the shape and the checks do not change.

Let the survey range wide enough to name everyone the result touches, then apply the boundary before planning: see `SKILL.md`, The purpose boundary.

### When a review sends work back

The REVISE correction path (`references/verification.md`, After the verdict: APPROVED or REVISE) opens a new context graph for the cited defect class instead of returning to the old one: extra nodes list the axes along which that class varies, probe representative inputs at the real entry point for each axis, and group the failures by root cause. The same per-node check nodes re-open each probe's cited lines, and one reducer writes the sweep record beside `collect.md`. The sweep is nodes inside that graph, never separate dispatches outside it, and its reducer merges nothing a check node did not verify.

## Stage 2: Define — the ideal state

Stage 2 turns `collect.md` into the definition the rest of the run is measured against. It is written from `collect.md`'s evidence only: every user, use, property, difference and decision point below cites the section, capture or file-and-line in `collect.md` that carries it. A fact the definition needs but `collect.md` does not carry sends the run back to stage 1 for one more context-graph node; it is never filled from memory, from the request's wording alone, or from an assumption. Check the handoff before using it (graphs.md, Handoff files): a missing or malformed `collect.md` is a failure to report, not a gap to paper over.

The output is the evidence-based ideal state: what the result must be for its users once nothing is constrained by today's code, and which major decisions settle it. It is the yardstick for every later choice, and stage 8 copies it into the goal. `define.md` is the run's definition snapshot: one writer, the session, and a revision is recorded with its reason, never edited silently.

### Users and their use

Name every party the evidence shows the result touches, then give each one its current and its intended use:

- **Affected users** — every party `collect.md` shows the result touches: the person who asks for the work, the person who operates or reads the result, the maintainer who inherits it, and any other skill, command, service or downstream consumer that reads the surface. One entry per party, with the collect evidence that shows the touch.
- **Current use** — what each party does today, through which real surface (command, file, page, API, receipt), and where it hurts. The evidence is the collect row, not an adjective.
- **Intended use** — what each party must be able to do when the work is done, stated as an observable action with an observable result.

A party the request implies but `collect.md` never shows is an open question back at stage 1, not a row invented here.

### The ideal properties

For each property, state what must hold, the party it serves, the reason it must hold (what breaks, for whom, if it does not), and the collect evidence that the property matters:

```text
- P<n>: <property that must hold> ; party: <affected party> ; reason: <what breaks without it> ; evidence: <collect.md section or capture path>
```

Properties describe the ideal end state, not today's behavior: "unchanged" and "works as now" are not properties. The set is complete when every intended use is served by at least one property and every property names a party and a reason. A property nobody needs is dropped; a need no property serves is a missing property.

### Differences from today

Each difference from today is one row in `gaps.tsv`, with its cause, impact, affected party and evidence:

```text
- G<n>: <the difference> ; party: <affected party> ; cause: <why it exists today> ; impact: <what the party hits> ; evidence: <collect.md section, capture path, or file:line> ; state: gap | no gap
```

- **A satisfied property is a row too.** It records `no gap` and the evidence that shows it is already satisfied: the command and its output, the capture, or the file and line. "No gap" without evidence is an unverified claim and cannot enter the register.
- **Register ids.** New differences take the next free `G<n>`. When the run already carries a gap register (an audit register, or one handed in with the request), its entries keep their ids and are cited as they are; the definition never renumbers them. Every later IS row names the `G<n>` it closes.
- **Boundary.** Request properties and qualifying companions are in scope; every other finding goes to the follow-up record, never into this register (SKILL.md, The purpose boundary; SKILL.md, Follow-up record). A companion enters only through the four guards.

### Major decision points

Name every major decision point the definition opens: the forks that change what gets built, how the work is split, or what counts as done. Settle each one from evidence here:

```text
- D<n>: <decision point> ; options: <the live options> ; settled by: <collect evidence> -> <the choice> ; affects: <G ids, properties> ; state: settled | owner decision
```

- **Settled here.** When collect's evidence decides it, record the evidence and the choice in the same row. A settled decision is not reopened at stage 7 and is not asked of the owner.
- **Owner decision.** When the evidence cannot settle it because the choice is irreversible, destructive, spends money, or accepts a contract-level limit, mark the row `owner decision` and carry it to stage 7 decide with a recommended default and its reason. It is asked once, in the one decision batch, and never again.
- **No silent forks.** A fork with no row is the defect this section exists to prevent: it resurfaces mid-build as an unowned choice. When a later stage finds one, revise define before that stage continues.

### The ideal end state as the yardstick

Write the end state once, as one paragraph: the users, the use they get, the properties that hold, and the decisions that are settled. That paragraph is the yardstick for every later choice. A plan row, a node split, a device, a lane, a fix, or a review finding is checked against it, and a choice that makes a property unreachable or reverses a settled decision is wrong even when it is locally convenient.

- **Changing the definition is a revision.** Record the reason, re-derive the affected rows, re-check the plan, and re-run the stages the change invalidates. It is never edited silently mid-build.
- **Copied into the goal.** Stage 8 creates the goal and the worktree, and the end-state paragraph is copied into the run's one goal, together with the IS-to-QA pairing, so the goal and this definition cannot drift and no second goal is created.

### The IS pairing

The pairing is declared here, not invented at plan time. Every delivered property becomes one `IS-<n>` row in the plan's contract; each IS row names at least one declared QA scenario; every QA scenario is named by at least one IS. When a gap register exists, each IS row also cites the declared `G<n>` it closes; without one, the IS rows stand alone and no gap target is claimed.

The pairing is complete only when both directions hold. A register gap with no IS row is undelivered work; an IS row the request never asked for is out of the boundary unless it is a qualifying companion. A `no gap` row yields no IS row: it stays in the register and is re-checked at verify.

### What stage 2 leaves behind

- `define.md` in the evidence dir: the users and their current and intended use, the properties with reasons, the decision rows, the end-state paragraph, and the IS-to-`G<n>` pairing table.
- `gaps.tsv` in the evidence dir: the difference rows, `no gap` rows included, one writer.
- The plan is written from this definition; the next section owns its grammar and the checks it must pass.

## Stages 4-5: The plan file and its checks

Write one plan file in the evidence dir outside the task worktree, and record that path in the plan. When a request has independently verifiable units, write and explicitly select one plan per unit. The plan, `todo`, and evidence dir hold progress; hand the named plan to the build graph (`references/execution.md`, Stage 9: Build — the build graph), not to a second planning pass. A node owns a disjoint write scope and its proof. The goal carries the IS-to-QA pairing.

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

All QA fields are nonempty and ordered as shown; `run` is last, so its command may contain semicolons, pipes, quotes or arrows. State happy and failure cases and capture paths. A scenario that runs a command is a re-runnable script kept with its evidence. Every IS has at least one DEVICE row; write gap-targeted devices in the same form. When a register exists, each IS cites its declared gap. Each fix row also names its fix device, which must fail on the code before the fix and pass on the head.

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

The default is one fresh `reviewer` plan review of the checked plan. The reviewer reads the request, boundary, gaps, graph, required device sentences, proof choices, and semantic checks; answers `OKAY` or lists blockers with a fix for each. Record fixes in the plan's review record and continue to the decision batch and goal without an approval question or a re-review of that round. Evidence wording, numerical and formatting problems are correction memos; a blocker is a failure to satisfy the request, an introduced regression, or a proof that shows the code does not do what is claimed.

Only when the requester's own message explicitly asks for the separate planning workflow, run that workflow with its approval gate and add a second fresh `reviewer` with the plan-gate lens alongside the first review. This branch has both reviews, no third round, and no follow-up message to that reviewer. Its fixes are checked by final review.

## Stage 8: The goal and the worktree

`/wf` already armed the run's one goal; keep it and never create a second. Its objective is the register's IS-to-QA pairing written as one paragraph; in a multi-unit request each unit's plan holds its own IS rows and their QA scenarios, and the single run goal covers the register. Without `/wf`, create that one goal with the host's goal tool. The plan files and the `todo` list hold progress.

The objective also carries the ideal end state recorded in `define.md`, written as one sentence, and a concrete `WHEN-TO-STOP:` line naming the observable condition that ends the run. Write both into the objective itself, not into a side note: the goal is the run's durable objective, so an objective missing either one is incomplete and is repaired before the first build node starts. The stop line names the flow's finish, not a stage boundary: the register closed, every unit's PR merged with its post-merge record written, the checkpoint complete, the worktrees and branches removed with receipts, and the final report delivered.

Each unit then gets a fresh worktree off main before build, so no unit starts on a tree that another unit or an earlier run has touched:

```text
git worktree add -b <branch> <path> main
```

Every later command pins that worktree with `cd <path> && ...` or `git -C <path> ...`; a node prompt that names a bare command or relies on a default cwd is refused at dispatch. A one-unit request still gets its own worktree and one PR. A correction run for a unit reuses that unit's worktree and PR, and the run's one goal already covers it. The worktree and branch live through that unit's merge, and cleanup removes them with receipts. Record the goal id and each unit's worktree path in the plan's evidence dir. Build rules continue in references/execution.md, Stage 9: Build — the build graph.
