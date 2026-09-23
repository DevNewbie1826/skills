# Lane D: Design Record, Debt & Handoff

Read this when a project needs an optional design record, debt register, handoff, or retrospective after planning, implementation, or review.

Lane D records design context around frontend work. It can maintain a project-local design record, design debt, handoff notes, retrospective notes, and observational taste memory. It has no hooks or independent automation path.

## Leaves in this lane

| Leaf | Read when |
|---|---|
| [design-debt-tracker.md](memory/design-debt-tracker.md) | critique or review defers findings — maintain the living debt register so promises stay visible |
| [design-handoff.md](memory/design-handoff.md) | completed design work must be communicated to engineering with specs, rationale, and accessibility requirements |
| [design-retrospective.md](memory/design-retrospective.md) | after completion — reflect on what worked, debt health, and how the person's design decisions evolve (includes the longitudinal taste reflection) |

## Phase owner

| Capability | Owner | Mapping |
|---|---|---|
| Track deferred design and accessibility findings | [design-debt-tracker.md](memory/design-debt-tracker.md) | Maintain ID, date, source, severity, issue, affected users, suggested fix, status, and notes. |
| Package rationale for implementers or reviewers | [design-handoff.md](memory/design-handoff.md) | Record component, interaction, accessibility, content, and rationale notes. |
| Reflect after completion | [design-retrospective.md](memory/design-retrospective.md) | Record what worked, what did not, fix rounds, debt health, and lessons. |
| Maintain observational design memory | Authored memory guidance | Store observations descriptively; do not feed them back as future project constraints. |
| Produce a taste reflection on request | [design-retrospective.md](memory/design-retrospective.md) — longitudinal section | Summarize personal-layer observations only when evidence exists or the user asks. |
| Route concepts into frontend | Frontend reference context | Frontend owns routing and mode language; no separate runtime is available. |

Lane D records outputs when earlier phases contributed useful evidence.

## Optional project record

Use a project-local record only when the project already has one or the user requests durable context. Keep it scannable and append-friendly:

- current objective and locked decisions;
- source inputs and explicit exclusions;
- brief summary, personas, principles, taste signals, and success criteria;
- decisions and rationale;
- open questions and artifact index;
- design debt, handoff notes, retrospective notes, and evidence index.

## Prompt injection

Append this block when closing a planning, implementation, review, or handoff phase that uses a project design record:

```text
Apply Lane D Design Record, Debt & Handoff.

Update the project design record with:
- decisions made and rationale
- open design questions or owner decisions
- artifact and evidence paths
- deferred Minor or Note debt, including affected users and suggested fixes
- accessibility-debt status and explicit user acknowledgement when accepted
- handoff notes for the next owner
- retrospective observations when work is complete

Do not use design memory as a future-work rule source. Record observations as descriptive evidence only. Do not introduce hooks or independent automation.
```

## Evidence requirements

Lane D passes only when any record used is inspectable:

- the record exists before a lane claims durable state;
- debt entries include ID, source, severity, affected users, suggested fix, status, and notes;
- accessibility debt is resolved or explicitly acknowledged by the user;
- handoff notes cite concrete artifacts, decisions, constraints, and evidence paths;
- retrospective notes cite final verification artifacts, unresolved debt, and lessons; and
- the evidence index points to real planning, implementation, visual-QA, or review artifacts.

## Guardrails

- Lane D records state; it does not mutate implementation or run hidden work.
- Critical or Major blockers are not ordinary debt; they require repair, escalation, or explicit blocking status.
- Accepted debt needs a rationale; accepted accessibility debt needs explicit user acknowledgement.
- Design memory is a mirror, not a steering wheel.
- Handoff text serves the next owner, not a narrative transcript.
- No hooks, background schedulers, or extra runtime contracts belong to this lane.

## Pass / fail behavior

PASS when state, debt, handoff, retrospective, and evidence references are current enough for the project workflow to resume without guessing.

FAIL when deferred findings disappear, accessibility debt lacks acknowledgement, handoff omits artifact paths, state is stale, retrospective claims lack evidence, or memory becomes prescriptive design input.
