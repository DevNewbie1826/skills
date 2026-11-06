Read this when stages 10-19 of the flow start; SKILL.md, The stage map, lists it.

# dag-workflow: verification, review, and merge

Covers stages 10-19 of the flow (see `SKILL.md`, The stage map).

### Work types and required lanes

The plan states its work type in one line: `code`, `design`, `research`, `audit`, or `mixed`. The type
fixes which lanes the unit must run at its frozen head, and what its end state is. The frozen head is the
one the plan records as under review - a commit SHA, or a content hash where the deliverable is an artifact.
Every lane below writes one receipt: a file in the evidence dir that names the head it judged and the one
observable that decided it. A receipt stays valid only while the tree it judged still matches; a receipt
whose tree moved is stale, and only stale lanes re-run.

| type | end state | required lanes |
| --- | --- | --- |
| `code` | a merged PR whose post-merge verification passes | `tests`, `qa`, `sweep`, `code-review`, plus `adversarial` at tier L or on a `HIGH-RISK` plan row |
| `design` | a merged PR whose post-merge verification passes and whose visual completion gate holds | `draft-guard`, `capture`, `vqa-passA`, `vqa-passB`, `code-review`, `qa` |
| `research` | the artifact delivered at the frozen content hash, with every delivery gate passed | `fact-verify`, `claim-gate`, `skeptic`, `execution-verify`, `delivery-gate` |
| `audit` | the register and the report delivered at the frozen register hash, every rule x surface cell judged | `lint`, `spot`, `register-schema` |
| `mixed` | the primary type's end state | the primary's and the secondary's lanes united; the secondary type adds lanes, never a second end condition |

A type's lane set is closed. A finding class outside that type's set keeps its row and its note but
carries no class, so a receipt can never hold a class the contract rejects. A `HIGH-RISK` row is legal
only on a `code` or `mixed` plan, because no other type's lane set contains `adversarial`.

#### `design`

Run the six lanes in two batches at one head, because the review passes need the captures.

- Batch 1, all four at the head under review: `draft-guard` runs the draft-guard checker on the declared
  targets and passes at exit 0 (exit 1 is findings, exit 2 is usage or an unreadable target);
  `capture` takes the full matrix on the **post-edit** build; `code-review` runs a reviewer with
  `remove-ai-slops` and `programming` loaded over the implementation diff; `qa` drives the real
  interactions and state transitions.
- Batch 2 runs only after batch 1's captures exist, at that same head: `vqa-passA` and `vqa-passB`, two
  fresh read-only reviewers dispatched in the same wave. Pass A carries the design-system and functional
  integrity charter and owns checklist sections G-J (motion, states, keyboard and accessibility, platform
  specifics); Pass B owns sections A-F (layout, hierarchy, text, targets, contrast and themes, consistency)
  and opens every screenshot before judging. Each checks every visual condition the plan carries.
- A capture older than the last edit is not evidence. A re-review after a fix is a fresh double oracle on
  fresh captures, and no pass reviews its own fix.
- Watch the budget ceiling: an open blocking defect at the ceiling triggers an approach switch. The
  register, never a round count, closes the unit. A `NEEDS HUMAN REVIEW` return is a finding plus a switch,
  never an end.
- The capture matrix follows the surface kind: web at 390 and 1440 px, adding 1920 for page layouts; a
  terminal at the column counts it supports, such as 80 and 120; paged output at each page size it prints
  to; each case in light and dark; plus the scroll end and each interaction frame. A terminal surface is
  captured through a real terminal renderer; a pane dump is not visual evidence.
- Merge needs `APPROVED` and the visual completion gate: every page's fresh captures passed a reviewer,
  the defect count is 0, and only taste rows remain.
- The plan carries one visual device per IS row, in the form
  `vqa <item ids> @ <matrix cells> pair <case>-<state>-<width>-<theme>`, so no visual condition is
  unowned. An unchecked condition is a finding.
- Three moves are forbidden: a pass reviewing its own fix, a pass dispatched with no fresh captures, and
  an unreachable platform recorded as a pass. Record it as unverified instead.

#### `research`

Run all five lanes at one head. They are gates, not style checks.

- `fact-verify` checks every number against its traceable source, every quote against its source text
  word for word, and every sentence for the claim that binds it.
- `claim-gate` locks each claim at its declared gate: at least 2 independent source domains, at least 2
  independent observation groups (or a recorded primary-only exception), one counter-search that found no
  stronger refutation, a primary source, and explicit observation timestamps. A claim is `unresolved` or
  `refuted` until that gate passes; `supported` needs the gate record, never the prose.
- `skeptic` attacks each claim with a fresh `reviewer`, a family other than the one that produced the
  claim, and every attack names the sentence or claim and the source that contradicts it.
- `execution-verify` settles a claim by running code where code can settle it.
- `delivery-gate` runs the five gates in order: static, fidelity, layout, visual, proofread. Each records
  pass, fail, or `not_run` with a reason, followed by one decision: repair, deliver, or block. A missing
  harness capability is `not_run` with its reason, and `fidelity not_run` requires a reason.
- A number with no source, a value that differs from its source, a quote that is not verbatim, or a
  sentence bound to no evidence blocks. Those are gate codes, not style.
- A `deliver` verdict that ships with residual defects is not an approval. The residuals become switch
  input, and an unresolved fidelity defect is already refused by the delivery gate.
- This type has no `code-review` lane, so its round has no code-review gate. Its frozen head is the
  artifact's 64-hex content hash, not a commit; after the merge the hash must still match, and a mismatch
  runs the full gate set again.

#### `audit`

The audit has no build step. Its three lanes prove the register **correct** rather than proving a fix,
and they run in one batch.

- `lint` re-runs the audited corpus's own linter and diffs its findings against the register.
- `spot` reproduces a random sample of n register rows. The register is a claim; an unreproducible row is
  a defect.
- `register-schema` checks the register's columns, its one-row-per-rule x surface pairing, and that every
  row has a decider.
- Completeness is the deliverable. A rule never judged on a surface is a hole, and `N/A` is a judgment,
  never a default.
- Three things block: a row that does not reproduce, a missing rule x surface judgment, and a schema
  break. A disagreement with the rule itself is a note or an owner question, not a defect.
- A fix edits the register or the report, never the product. A product fix belongs to its own unit.
- This type has no `code-review` lane, so its round has no code-review gate. The round judges coverage and
  spot accuracy, not product quality. The usual switch kind is `rediscover`, because a missed surface
  group is the failure mode, not a miswritten patch.
- Forbidden: sampling the surface list, treating a linter exit 0 as coverage, writing a fix into the
  audit's branch, leaving a row without a decider.

#### `mixed`

A mixed unit names a concrete primary type and a concrete secondary type. Its required lanes are the union
of the two lane sets, and it ends on the primary type's end state. The secondary type adds lanes and never
a second end condition. A `HIGH-RISK` row is legal on a mixed plan because the `code` lane set is present.

### Tiers

The tier is decided once, from the LIGHT/HEAVY facts, and is never lowered. A HEAVY fact found mid-run
raises it at once.

| tier | decided by | what the tier adds |
| --- | --- | --- |
| S | at most 2 files and 150 changed lines by the discovery estimate, and no HEAVY fact | one scout; a short plan; the plan review may start with the build and a blocker amends the run; at most 3 mutations, and never more than one per guard row |
| M | more than S, at most 1 HEAVY fact, at most 3 components | stages serial by default; the full pre-PR verification wave; one mutation per guard row |
| L | at least 2 HEAVY facts, at least 4 components, or the requester asked for thoroughness | M plus the `adversarial` lane even with no `HIGH-RISK` row, the state and lifetime transition table run inside QA, and the mutation cap of 12 |

The `adversarial` lane is conditional otherwise: it runs only for a plan that flags a `HIGH-RISK` row, and
only on a `code` or `mixed` plan. The row names one of `concurrency`, `persistence`, or `state` /
`lifetime`; the lane probes five transitions - start, success, reject, abort before start, abort while
pending - and each probe either holds or produces a reproduced counterexample. It timeboxes at 15 minutes,
runs a model family other than the author's, and gets no second pass. The tier only decides when the lane
runs; its probe list and timebox do not change with tier.

Mutation cap by tier: 3 for S, one per guard row for M, 12 for L. The source states S two ways - its tier table
says "at most one per guard row" and its tests-lane prompt says 3 - and the two combine as the stricter of the
pair, so an S unit gets at most 3 and never more than one per guard row. A mutation is killed only when its
guard test passes unmutated and fails under the mutation; a run that fails for any other reason is not a kill.
A survivor means a regression would pass unnoticed: strengthen that guard test, or record a `no-test` reason
with the QA scenario that covers it. Run at most 8 mutation processes at once, keep every mutant in its own
throwaway copy, and leave no mutant directory behind.

### The five design-only checklist ids

The design class set accepts the visual-QA checklist item ids (`A1`-`J2`, 74 items across ten families),
the nine draft-guard and accent-stripe rule ids, and `taste`. The pack's visual-qa skill routes the two
review passes and owns their charters, but it does not print the checklist body, so this flow names the ids
and states each of the five below in one line. Those five are the ones a reader cannot recover from the pack
without a second document, and they belong to the design lanes, where the captures are read against them:

- **A13** - spacing rhythm, read from computed values: the space above a section heading is at least 1.5x
  the space below it, and the gap between groups is at least 2x the gap inside a group.
- **B8** - type scale floor: each heading step in use differs by at least 1.25x in size, body-family roles
  that sit closer differ by weight, colour, or case, a display heading stays at or under 6rem, and letter
  spacing never goes below -0.04em unless the chosen style route sets its own scale.
- **E7** - secondary text on a tinted or coloured surface is a shade of that hue or the foreground at
  reduced alpha, never neutral gray; a shadow carries a y-offset and a soft blur, never a zero-offset
  coloured glow unless the brief asked for it.
- **F8** - browser surfaces carry the palette in both themes: text selection, caret, visible scrollbars,
  focus ring, link underline offset, and tabular numerals in changing or aligned numbers; none shows the
  browser default.
- **F9** - none of the generated scaffolds: a kicker label above a heading, an icon tile stacked over a
  heading in a grid of same-size cards, a hero metric with no decision behind it, a card nested in a card,
  or monospace used as a technical costume. One the brief or its chosen route asked for, recorded as such,
  passes.

Pass ownership for these five follows the family letter: A13 and B8 belong to Pass B with the rest of A and B;
E7, F8 and F9 also belong to Pass B, with E and F.

A capture matrix cell that no checklist id covers is a note, not a class. `taste` rows are listed so the
register is complete, never block, and may only ride a defect fix on the same surface. A reviewer that
treats taste as a defect is wrong; the finding is filed as a note.

## Stage 10: Verify lanes

### Finite contract

The plan's IS and COMPANION rows are the request, INVARIANT rows say what must keep holding, and LIMIT rows say what is knowingly not handled. Only an undelivered IS or COMPANION row, or a listed INVARIANT shown violated by a failing test, blocks. For a behavior the plan marks `no-test`, its failing QA scenario supplies that proof. A listed LIMIT is accepted, not a finding. Everything else is a note or follow-up, including style, desired coverage, and evidence wording or format. Severity does not decide whether a finding blocks.

For a program, a unit is one worktree, branch, and PR; its PR contract is its own IS rows only. A reviewer cannot demand another unit's delivery, and a unit's REVISE does not stop another unit's merge. The whole-request completeness register remains separate.

### Verification lanes

Dispatch independent lanes for one candidate head in one host task batch or one eval `parallel()` batch of `agent()` nodes. Use dependencies for work that cannot run together. Every lane follows `SKILL.md`, Delegation prompts, and writes its own receipt outside the task worktree.

| Work type | Required lanes |
| --- | --- |
| `code` | `tests`, `qa`, `sweep`, `code-review`; also `adversarial` for tier L or any HIGH-RISK plan row |
| `design` | `draft-guard`, `capture`, `vqa-passA`, `vqa-passB`, `code-review`, `qa` |
| `research` | `fact-verify`, `claim-gate`, `skeptic`, `execution-verify`, `delivery-gate` |
| `audit` | `lint`, `spot`, `register-schema` |
| `mixed` | The union of the primary and secondary work types' lanes |

The tier, the mutation caps by tier, and the `adversarial` lane's conditions live in Work types and required lanes above; the tier is never lowered, and a heavier fact found mid-run raises it. The `tests` lane uses a `quick` task node for the repository suite and the hand-applied mutations its tier's cap allows. A mutation counts as killed only when the unmutated guard passes and that guard fails under the mutation. Apply mutations in a throwaway copy, away from any review reader, at most eight mutation processes at once, and leave no mutant directory behind. A survivor requires a stronger guard or a justified `no-test` row with its QA scenario; a different failure is not a kill. A valid `no-test` row receives QA rather than a mutation.

The QA executor runs the plan's happy and failure cases on the real surface, naming the artifact for each QA row. The code reviewer owns `code-review`; the code-review section defines its discipline. Use a `deep-high` task node for `adversarial`. The `sweep` lane records one row per applicable class of the defect-class checklist (`references/orchestration.md`, Defect classes and review axes): the literal command or `no command`, the one binary observable, the verdict, and the artifact. Keep the discovery variant sweep in stage 1 rather than adding a separate merge or synthesis node.

### Evidence and reuse

Use the evidence directory recorded in the plan, outside the task worktree (`SKILL.md`, Follow-up record). The lead alone updates the plan, todo, findings, register, and transition records; each lane writes only its own receipt. Each file has one writer.

A receipt records `kind`, `type`, `unit`, `program_id` (or `null`), `lane`, `stage` for a lane receipt, full `head`, `tree`, nonempty path/glob `scope`, UTC `started_at` and `ended_at`, `status`, `rows`, `artifacts`, and `cleanup`. Mixed work also records `primary` and `secondary`. Each check row carries `id`, literal `command` (or `no command` for a read-through), one binary `observable`, `verdict`, `artifact` (path or `null`), and applicable `class` and `note`. Preserve applicable `gap`, `name`, `pass`, and `env_sha` fields.

For code, design, and audit, `head` is the full 40-hex commit identity and `tree` is the full tree identity. For research, `head` is the frozen artifact's 64-hex sha256 and `tree` is `null`. Seven-character prefixes are display and filename anchors, never identity comparisons.

An evidence receipt remains valid while its tree matches; research receipts match the artifact hash instead. A fix's reuse assessment intersects changed files with each receipt's scope and checks any recorded surface/build `env_sha`; a changed `env_sha` makes the receipt stale. Record each reuse decision as `receipt`, `VALID` or `STALE`, `reason`, and current `head`; rerun stale lanes only. Pre-edit `before` captures are historical and exempt from stale checks. This evidence reuse never substitutes for the exact-head code-review requirement in the round gate, or for a verdict on the current head.

| Receipt status | Flow rule |
| --- | --- |
| `PASS` | Every check row passed. |
| `FAIL` | A claimed failure inside the finite contract; the lead reproduces it before filing a blocking finding. |
| `WARN` | A correction memo or note; never blocks. |
| `SKIP` | Not applicable, with its reason recorded in `note`; cannot satisfy a required lane. |
| `INVALID` | Check-row status only: a probe could not decide. It is unproved, never PASS. |

A required lane is satisfied only by a valid PASS or WARN receipt. A missing, stale, skipped, or undecided required check remains unproved; do not convert it into a code defect without the finite-contract proof. Triage FAIL claims at stage 11 rather than believing the receipt alone.

Transition records carry the unit and program, work type, plan path, applicable full head/tree, timing, commands, artifact, cleanup, and the stage-specific fields named below. Keep append-only evidence of triage, fix, reuse, freeze, dispatch decisions, rounds, verdicts, switches, merge, post-merge verification, and completion. The plan and todo expose the current stage, valid/stale evidence, blockers, and next unmet prerequisite. These records are prose obligations enforced by the lead, without helper scripts or a second orchestrator.

### Receipt names and gap pairing

Store receipts under `<evidence dir>/receipts/`. Anchors are the first seven hex characters of the receipt's own full identity.

| Receipt family | Filename |
| --- | --- |
| Lane | `<stage>-<lane>-<head7>.json` or `.md` |
| Before/after gap capture | `before-<gap>-<tree7>.<ext>` or `after-<gap>-<tree7>.<ext>`; research uses `<head7>` |
| Visual QA | `vqa-passA-<head7>.<ext>`, `vqa-passB-<head7>.<ext>`, `vqa-capture-<head7>.<ext>` |
| Claim gate | `claim-gate-<sha7>.json`, anchored to the research head |
| Lint | `lint-<name>-<tree7>.json`; research uses `<head7>` |

Use a stage name for `<stage>`, a kebab-case lane, and a `G<n>` gap ID. The filename anchor must agree with the receipt body; refuse mismatches. Markdown lane receipts use the same fields in YAML front matter, `rows: []`, and the report below. Before/after extensions are `.json`, `.md`, `.png`, `.jpg`, `.jpeg`, `.webp`, or `.txt`; visual-QA extensions are the same except `.txt`; claim-gate and lint receipts use `.json` only.

The completeness register carries `id`, `area`, `surface`, `rule`, `current`, `ideal`, `before_artifact`, `severity`, `kind`, `class`, `type`, `unit`, `status`, `pr`, and `fixed_head`. Every before/after receipt names a register gap. Every defect gap has a pre-edit before receipt; when fixed it also has an after receipt and `fixed_head`. Capture before the first edit, including rows that change existing UI. A before artifact is required when a defect row leaves `open`. Taste rows stay visible but do not block. Use the cleanup section's register closure rule for whole-request completion.

## Stages 11-12: Code review, triage, and fix

Every reviewer lane uses a locked read-only review worktree. Never inject mutations into a worktree a reviewer reads. Every re-review uses a new reviewer, never the previous child continued. The code-review prompt follows `SKILL.md`, Delegation prompts, loads `remove-ai-slops` and `programming`, and states whether those checks ran. It reports CRITICAL, HIGH, MEDIUM, and LOW, but only the finite-contract test of the verify section determines blocking.

Collect the stage 10 lane reports, including `code-review` when required. The lead triages their findings, reproduces claimed failures on the stated head, and files only reproduced contract failures as blocking. A FAIL receipt alone is not proof. Notes and evidence correction memos do not require another review. If code fixes change the reviewed head, obtain a new code-review receipt at the resulting candidate head.

### Findings and dispatch table

Each finding records `id`, `round`, `source`, `class`, `severity`, `file_line`, `blocking`, `repro_cmd`, `head_found`, `status`, and `fixed_head`. Use stable IDs, `round: 0` before the first final round, and the most recently completed round otherwise. Use the same work-type defect-class names in findings and review axes. The `source` identifies code-review, QA, sweep, final reviewer, architect, or adversarial review. Severity is descriptive; `note` and owner-decision rows always have `blocking: 0`.

A blocking finding needs a reproduction command on `head_found`. Before the next final dispatch, rerun each prior blocker's reproduction on the new candidate head and record its result. If it still reproduces, mark `not-fixed` and refuse dispatch. If no reproduction exists, mark `no-command` and write one before the gate. Mark a resolved finding `fixed` with its `fixed_head`; a change of status never erases its earlier blocking class from round history.

Run fixes as one dependency-ordered correction run of the host workflow tool or eval `agent()`/`parallel()` nodes under `references/execution.md`, Stage 9: Run the plan. Fix records name `round` and `head`: round 0 is pre-PR triage/fix, later rounds name the REVISE being corrected. Apply the reuse rule and rerun stale lanes. Keep `fix` in todo with `skip: <reason>` when it truly does not apply.

The required order is **triage -> fix -> freeze -> pr_open -> round**. Steps 7-9 enforce that sequence on first review and every correction cycle. Code review and final review are distinct and are never dispatched in the same wave.

## Stages 13-14: Freeze and open the PR

### Freeze

After triage and applicable fixes, record a freeze with full `head`, `tree`, and `pr` (or `null` before opening). Confirm that the worktree is clean and no commit is pending. Freeze binds both identities for the whole final round. Nothing commits after the freeze: evidence and correction memos go to the external evidence directory. A fix lands only after the verdict, then requires a fresh freeze and another round.

The required code-review lane must cover this exact frozen head and matching tree. A receipt already produced at that unchanged head may satisfy it; otherwise run a fresh code reviewer there. The round gate refuses final review until this holds.

### PR and monitor

Open one PR per unit to the repository's main branch. The body states the delivered behavior, test and QA captures, before/after evidence for the unit, and real limits. Derive numbers and identities from captures rather than retyping them. Record `pr_open` with the PR number and start the host's monitor on the PR. Use event delivery rather than a foreground polling loop. An unreadable check or unknown PR state is not ready.

For a correction cycle, append commits to this same PR, freeze the new head, and update the existing body; record that the existing PR satisfies `pr_open`. Never open a second PR for that unit's fix commits.

## Stage 15: The round

### Refused dispatch gate

Before dispatching or recording a final round, the lead checks the gate below and records its outcome. A failed prerequisite is a refused gate and a refused round record: do not start a reviewer, record a completed round, or merely leave a reminder. Resolve the earliest unmet prerequisite first.

| Prerequisite | Required observation |
| --- | --- |
| Freeze | A freeze exists for this unit, with the full head and tree. |
| Observed head | The actual current worktree head equals the frozen head; research compares its frozen artifact hash. Refuse a moved head before reproduction runs. |
| Code-review order | If the required lanes include `code-review`, a structurally valid receipt for this same unit has `kind: lane`, `stage: verify_lane`, `lane: code-review`, exact frozen `head`, matching `tree`, and status PASS or WARN. |
| Required evidence | The work type's required lanes are valid and satisfied under the verify section. |
| Prior blockers | Every prior blocking reproduction has been rerun; none is `not-fixed` or `no-command`. |
| Correction prerequisites | After REVISE, the cited problem has round-tagged definition, updated plan, and plan-grammar validation records, plus any required switch. |
| PR | This unit's PR exists, with its current body and freeze recorded. |

A same-tree code-review receipt from another head, a sibling unit's receipt, a reuse decision, FAIL, or SKIP cannot satisfy the code-review order gate. Research and audit units with no code-review lane are exempt from that prerequisite only. Check freeze and exact-head code review before running the reproduction table.

### Reviewer and verdict

After the gate passes, dispatch one fresh `ultrabrain` final reviewer, never a worker on the task, in a locked read-only review worktree. Its prompt follows `SKILL.md`, Delegation prompts, and the evidence rule. Round 1 reads the full change; round 2 and later read the delta since the last reviewed commit plus prior findings. It reports all contract defects together rather than stopping at the first.

Number each unit's rounds 1, 2, 3, and onward without gaps. Save the report as `<evidence dir>/receipts/final-r<n>-<head7>.md`. Its last nonempty line has exactly this form, substituting real values:

```text
VERDICT: APPROVED round <n> head <full-head>
```

The other allowed verdict is REVISE. Normalize CRLF, choose the last line whose trimmed text is nonempty, trim trailing whitespace, and require `VERDICT: (APPROVED|REVISE) round ([1-9][0-9]*) head ([0-9a-fA-F]{40}|[0-9a-fA-F]{64})`. The complete line must match; reject an empty report, malformed line, zero/leading-zero round, abbreviated head, or head of the wrong length for the work type. Lowercase the parsed head and compare the complete identity with the frozen and observed heads; seven-character displays never decide coverage. The round number has no upper bound.

When the reviewer returns, check the observed head and verdict coverage again before accepting or recording the round and its verdict, full head, and report artifact. A verdict is valid only for the head it reviewed. If the head moves while the round is in flight, refuse coverage of the new head and re-review after a fresh freeze, gate, and fresh reviewer; do not record the moved-head report as an accepted APPROVED. Never carry the old verdict forward. REVISE is never approval.

## The evidence rule

Every code, final, architect, gate, and adversarial reviewer prompt carries this paragraph:

> Evidence problems are never a REVISE reason. Typos, number errors, and wording or format problems in evidence or reports do not cause REVISE. Write each one as a correction memo in your report; do not fix the evidence yourself and do not request a re-review for it. Only a problem in CODE can cause REVISE, and only inside the plan's finite contract: a listed invariant violated, shown by a failing test (or, for a behavior the plan marks no-test, by its failing QA scenario), or an IS or COMPANION row not delivered. Report every other finding as a note or a follow-up, never as a blocker; a known limit listed in the plan is not a finding. The plan review in `references/planning.md`, Stage 6: Plan review, judges the contract itself.

The lead handles correction memos in the external evidence directory and updates the PR body as needed. Nothing commits after freeze to repair a report or its formatting.

## Stage 16: APPROVED or REVISE

### APPROVED and merge

APPROVED is the only end of review. The lead merges only while the approved verdict's head equals both the frozen head and observed head, the gates hold, and the PR is ready. Record the merge's `sha`, `merged_at`, `pr`, and reviewed `head`.

No further round follows a recorded APPROVED for that unit. If its head drifts afterwards, refuse merge and restore the head the approval judged; an old approval never covers the moved head. Head movement during an unfinished round follows the round's re-review rule instead.

### Correction path

On REVISE, revisit stage 1 (discovery) for the cited problem: define it again and sweep its defect-class variants. Then update the plan (stages 4-5) and validate its grammar before checking lanes, findings, freeze, and switch obligations. Record the definition, plan, and validation against the completed REVISE round number. The plan review, the initial decision batch, and the existing goal are not repeated.

For every in-scope variant, add a COMPANION row only if it is one hop from a request IS row, introduces no new owner decision, stays in this task and PR, and records `COMPANION: <item> <- <request IS row> : <why expected>`. Same-pattern sibling bugs passing those guards are fixed here. Record everything else in `<evidence dir>/follow-ups.md` and the final report without fixing it in this task.

Run the fix under stage 9 in the same worktree, branch, and PR. Append commits to that PR. Then apply the reuse rule, rerun stale lanes, and run stages 10-15 with a fresh freeze and existing-PR body update. The code-review order gate still needs an exact-head receipt even when other same-tree evidence can be reused. After an approach switch, this same path is mandatory: fix run, reuse decisions, stale lanes, freeze, gate table, and a fresh final reviewer on the delta plus prior findings.

### Escalation and switches

Two consecutive REVISE rounds on the same component **or** the same defect class stop the patch loop and force one `architect` premise review of the assumption the failed fixes shared. Record that premise review as a switch for the REVISE round; it consumes a switch kind even when the round is not a repeat.

A third-or-later REVISE that repeats a previously cited blocking defect class requires an approach switch for that same round before the next round. There is no review-round ceiling. A cap forces a switch, never a blocked or terminal outcome, and never permission to stop.

#### Exact repeat test

For round n, collect that unit's findings with `round = n` and `blocking = 1`. The round is nonrepeat only if this set is nonempty and **none** of its classes appears on any earlier blocking finding, including round 0, regardless of the earlier finding's current status. Otherwise it is a repeat. Thus a mixture of new and old blocking classes is a repeat, and a round with no blocking rows is also a repeat.

At the next-round transition, compute and record `prior_repeat` once from that history. Only `prior_repeat: false` removes the third-or-later switch obligation; absent or true retains it. Do not accept an asserted false value in place of computing it. A nonrepeat round needs the normal fix path but does not require a switch.

#### Switch kinds

| Kind | Required change |
| --- | --- |
| `premise` | Run the architect premise review if it has not run. |
| `family` | Move the fix node to a model family different from the one that produced the failed fix, using host routing; use a `deep-high` fix node. |
| `strategy` | Write `SWITCH: <failed premise> -> <new approach>` in the plan and redesign the component rather than adding another patch. |
| `split` | Program mode only: make the failing component its own unit and PR; keep its gap row open. |
| `rediscover` | Rerun collection with the judging rules and sweep variants. |

Record a switch with `round`, `kind`, `premise`, and `new_approach`, and record the changed premise and approach as a `SWITCH:` plan row. It follows that round's REVISE and precedes the next round. Each further repeat uses one more kind not yet used in the current cycle. Once every applicable kind has been used, the cycle may repeat; exhaustion never ends review. Single-unit runs have four applicable kinds because `split` is program-only. A voluntary switch also consumes its kind.

Ordinary correction commits always stay on the existing unit's PR; a program-only `split` is a recorded change of unit structure, not a second PR for those correction commits.

Ask the requester only for decisions they own: irreversible or destructive actions, spending, or accepting a contract-level LIMIT. Never ask whether to keep reviewing. Keep each question, options, recommended default, status, and eventual answer in the external evidence directory; only its affected lane parks while independent lanes and units continue. Every unresolved owner question and refused dispatch gate remains effective independently; resolving one does not clear the other. A question open longer than 15 minutes is recorded in the plan so a restart reports the wait.

### The revise path

Enter this path on a `REVISE` verdict, or on a gate row that came back not fixed. The round rule above is
the binding text; this is how it runs.

1. **Read the verdict as filed.** Take the findings table - class, `file:line`, reproduction command,
   blocking - and file every blocking row. A blocking row with no reproduction command needs one written
   before the next gate: a missing command is a defect of the finding, not a permission to skip it. If the
   flow kept no findings table because the round only returned a verdict, write the table from the verdict's
   rows before starting the fix; a fix list nobody can re-run is not a revise path.
2. **Sweep variants before editing.** Sweep the same defect class across the component's siblings: the
   sibling location, the same transition, the same input shape. File what the sweep finds as its own
   findings, and re-run the lane that owns the defect, because a fix that leaves a sibling broken returns
   as the same class.
3. **Return to discovery and the plan for the cited problem only.** Update the plan's gap rows and the
   affected IS rows, adding a COMPANION row for each in-scope variant the sweep found and a risk row for each
   fix. The plan review and the goal are not repeated. The fix commits go to the same PR, never a second one.
4. **Fix in one node per component.** Each node recreates the reported failure, captures it, fixes it,
   captures the pass, and commits serially onto the same branch.
5. **Reuse, then freeze.** Judge every receipt against the new head: tree match means valid, otherwise a
   changed-file intersection with the receipt's scope means stale. Re-run only the stale lanes and record
   which lanes were saved. Then freeze the new head and confirm nothing moved.
6. **Re-run the prior reproductions at the new head.** Every prior blocking finding's reproduction command
   runs again. A row that does not reproduce any more passes; a row still failing sends the run back to the
   fix step with that row as the next component's target.
7. **Review with a new reviewer.** The final review is always a new task, never the previous reviewer
   continued. Its inputs are the delta diff since the last reviewed commit, the prior findings that must now
   fail to reproduce, and the gate table. A round that only re-reads the old report is not a review.
8. **Read the verdict line.** `APPROVED` on the frozen head ends the loop and the lead merges. `REVISE`
   returns to step 1 of this path with the new findings.

## Stage 17: Post-merge verification

Compare the merged result's full tree with the verified frozen tree. When identical, the QA executor runs a smoke check and reuses the valid evidence. When different, run full QA and the repository suite, typecheck, and build where they exist on the merged result. For artifact work, use its artifact identity rather than inventing a git tree.

Post-merge per type: `code` and `design` run every QA scenario plus the suite, typecheck, and build where
they exist; `design` also runs what the tree comparison calls for; `research` re-checks that the artifact
hash equals the frozen one; `audit` re-checks that the merged register equals the frozen one and that every
`FAIL` row still reproduces. A failure follows the pre-PR rule and a fix goes through the full flow again
from the merged base, never as a direct patch to the main branch.

---

Record `post_merge` with full `head`, `tree`, commands, outcomes, captures, and cleanup, using `post_merge-<tree7>.*` evidence for tree-based work. Every QA row names its artifact. A failure follows the finite-contract and reproduction rules of the verify and triage sections. A required fix goes through stages 9-16 from the merged base, never a direct patch to main.

## Stages 18-19: Checkpoint, cleanup, and final report

The request is complete only when every defect row in the register is `fixed`, `accepted-limit` backed by a plan LIMIT row, or `out-of-scope`; every unit's PR has merged and has post-merge verification recorded; and the evidence record supports completion. Fixed defects have their before/after receipts and fixed head. Taste rows do not block closure.

Use the host's goal/checkpoint equivalent to record completion, with a gate reviewer reading the evidence record. Complete the existing goal only after the merged result passes post-merge verification (stage 17). Remove the worktrees and branches, stop owned processes and monitors, and keep a teardown receipt for each; cleanup records include at least one receipt. Record the defect classes caught through the host's memory capability.

Deliver the final report with results, evidence locations, limits, and every out-of-scope finding with its follow-up path, or "none". Finish only after the register, merged units, post-merge verification, completion checkpoint, cleanup receipts, and final report all hold. Stop conditions and the report shape: see `SKILL.md`, Finish.

### Restart after a death or a compaction

The state is the authority, never memory. The plan file, the todo list, and the receipts survive a killed
session, so a restart re-runs nothing that is still valid. Follow the steps in order; never re-plan from
scratch and never re-derive a decision the receipts already record.

1. **Rebind first.** Confirm the evidence dir in the plan is the one the receipts live in, that the worktree
   still exists, and that the current branch is the branch the plan names. If any of the three moved, stop
   and say so rather than starting a second state.
2. **Read the whole state.** Recover the step, type, tier, frozen head, round, the valid-receipt list, the
   stale-receipt list, the blockers, and the one next action. The plan file, the todo list, and the evidence
   dir are the only inputs; a summary in the conversation is not.
3. **Judge, do not trust.** A receipt valid at the current tree is not re-run; a stale one is. Never re-run
   a lane, a build, or a check to "make sure" - that habit is the cost this design removes.
4. **Read the live state before repeating anything that acts outside the worktree.** A push, a PR, a merge,
   a deploy, a message, or a paid call may already have landed. `git ls-remote`, the PR's own state, and the
   deploy's own status are the receipts here: query them before acting. Never repeat a side effect that
   already landed, and never start a second worktree, branch, PR, or state root.
5. **Judge dead children by their receipts.** A lane whose receipt exists and validates at the current head
   is done, whatever its child's fate. A lane with no receipt, or one the state calls stale, is re-spawned
   once. File existence is not completion.
6. **Resume from the first invalid step.** Dispatch only what the state names. A parked owner question
   parks only its own lane.
7. **Retry once per failure mode, then switch.** A provider error, a timeout, or a child that died without a
   receipt: the same lane once, then record the lane as failed. A context or memory ceiling: narrow the
   scope and retry once. A tool error that looks like the tool rather than the work: another agent or model
   family. Unknown: once, then a switch - never a third identical attempt. Two identical failures at one
   step is a signal to change the approach, never a reason to loop the same call; cap concurrent processes
   in every node prompt and say the cap.
8. **A late result is adopted only when its head or tree still matches.** Otherwise discard it and re-run
   the lane. Never adopt a receipt from a head that has moved.
9. **A restart never** re-plans a plan that exists, edits a plan row to match what the code now does,
   re-opens a resolved gate, re-asks a question the owner already answered, or trusts a stale head.
10. **Pause safely before a long wait.** Before a final-review dispatch, a CI wait, or an owner question,
    write a resume note with the intent, the current step, the valid receipts, and the one next action, and
    leave nothing uncommitted that the restart would lose.
