# Design Debt Tracker

Read this when critique or review defers findings — the living register that captures minor issues, conscious compromises, and accessibility debt so deferred promises stay visible.

Back-link: [Lane D — Design Record, Debt & Handoff](../lane-d-memory.md)

Design debt is every conscious compromise the team makes and every minor issue deferred to "next time." Like technical debt, it compounds. Unlike technical debt, most teams don't track it — so it disappears into the gap between what was shipped and what was intended.

This skill maintains a living register that captures debt as it's created, tracks it across iterations, and surfaces it when decisions are being made.

## Why This Exists

Review classifies findings on the scale owned by [design-review.md](../review/design-review.md#step-5-classify-issues). Critical and Major get fixed. Minor and Note get a shrug and "fix if time allows." They rarely get fixed because no one remembers them.

Accessibility findings follow the same path — Minor issues with specific fixes never happen when they are buried in a report no one reopens.

Every "fix if time allows" is a promise to a persona. This skill makes those promises visible.

## When to Use

- **After critique** — when review produces Minor or Note findings that won't be fixed this round
- **After accessibility review** — when that review flags Minor issues that are deferred
- **After a fix round** — when not all issues were addressed and some were consciously deferred
- **At project start** — to review accumulated debt from previous iterations
- **Before planning** — to decide which debt items to address in the next cycle
- **On user request** — "show me the design debt" or "what did we defer?"

## The Register

Design debt lives in a `## Design Debt Register` section of the project design record — the optional one described in [orchestration.md](../orchestration.md#shared-state), used only when the project already has a record or the user asks for durable state. One register per project. It persists across iterations.

### Register Format

```markdown
## Design Debt Register

_Items: [count] | Critical: [count] | Oldest: [date]_

| ID | Date | Source | Severity | What | Who is affected | Suggested fix | Status | Notes |
|----|------|--------|----------|------|----------------|---------------|--------|-------|
| DD-001 | 2025-01-15 | critique | Minor | Settings form shows all fields at once — cognitive load | Persona: Jamie (cognitive disability) | Progressive disclosure with sections | Open | Deferred from v1 — setup is one-time flow |
| DD-002 | 2025-01-15 | accessibility review | Minor | Category color strips lack icon backup | Users with color vision deficiency | Add icon per category alongside color | Open | |
| DD-003 | 2025-01-16 | critique | Note | Empty state illustration is placeholder | All users | Commission illustration that matches brand | Open | Low priority — functional without it |
| DD-004 | 2025-01-15 | accessibility review | Minor | Toast notifications auto-dismiss before screen reader finishes | Screen reader users | Extend timeout to 8s or add persistent log | Resolved | Fixed in v1.1 |
```

### Field Definitions

| Field | What goes here |
|-------|---------------|
| **ID** | Sequential identifier (DD-001, DD-002, ...). Never reuse IDs |
| **Date** | When the debt was recorded |
| **Source** | Which review identified it (critique, accessibility review, heuristic evaluation, usability testing, or user) |
| **Severity** | The original severity classification: Minor or Note (Critical and Major should be fixed, not deferred) |
| **What** | Specific description of the issue — not "needs improvement" but "form shows 12 fields at once" |
| **Who is affected** | Which personas or user groups bear the cost of this debt. Be specific |
| **Suggested fix** | Actionable recommendation from the original review |
| **Status** | Open, Resolved, Accepted, or Escalated |
| **Notes** | Why it was deferred, context, related items |

### Status Definitions

| Status | Meaning |
|--------|---------|
| **Open** | Identified, not yet addressed. This is a promise to come back |
| **Resolved** | Fixed in a subsequent iteration. Record which iteration |
| **Accepted** | Consciously decided this is not worth fixing. Requires user approval and a rationale |
| **Escalated** | Was Minor, but accumulated evidence or changing context makes it Major. Needs attention |

## Process

### Step 1: Capture Debt (After Review)

When critique or accessibility review completes:

1. Read their findings
2. Identify all Minor and Note severity items that will NOT be fixed in this round
3. For each deferred item, create a register entry with all fields populated
4. Append to the Design Debt Register in the project design record
5. Update the summary line (item count, critical count, oldest date)

**Do not capture items that are being fixed.** The register tracks debt, not the fix list. If it's getting fixed now, it doesn't belong here.

### Step 2: Review Debt (At Project Start or Before Planning)

When starting a new iteration or planning cycle:

1. Read the current Design Debt Register
2. Check for escalation triggers (see below)
3. Present a debt summary to the user:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DESIGN DEBT SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Open items: [count]
  By severity: [X] Minor, [Y] Note
  Oldest unresolved: [date] ([age])

  ACCESSIBILITY DEBT:
  • [count] items affecting users with disabilities
  • Most affected: [persona or user group]

  TOP CANDIDATES FOR THIS CYCLE:
  1. [DD-XXX] [description] — [why now]
  2. [DD-XXX] [description] — [why now]
  3. [DD-XXX] [description] — [why now]

  ESCALATED (was Minor, now needs attention):
  • [DD-XXX] [description] — [escalation reason]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

4. Ask the user which items to include in the current cycle's plan
5. Items the user selects get added to the design plan as tasks

### Step 3: Escalation Check

Debt items should be escalated from Minor to Major when:

| Trigger | Example |
|---------|---------|
| **Age** | Item has been Open for 3+ iterations without resolution |
| **Accumulation** | Multiple debt items affect the same persona or the same screen |
| **Context change** | A new persona or use case makes the issue more impactful |
| **User complaint** | The user or stakeholder mentions the issue independently |
| **Compound effect** | Two Minor items together create a Major experience gap |

When escalating:
1. Change Status to "Escalated"
2. Add a note explaining why
3. Flag it in the debt summary
4. Present it to the user as needing attention

### Step 4: Resolve Debt

When a debt item is fixed:

1. Update Status to "Resolved"
2. Add a note: "Fixed in [iteration/date] by [who fixed it]"
3. Add the resolution to the record's Decisions and rationale
4. Do NOT delete the row — resolved items are history

### Step 5: Accept Debt

When the user consciously decides an item is not worth fixing:

1. Confirm with the user: "This affects [personas]. Are you sure you want to accept this?"
2. Update Status to "Accepted"
3. Add the user's rationale in Notes
4. Add the acceptance to the record's Decisions and rationale

**Accessibility debt requires explicit acknowledgement.** If a debt item affects users with disabilities, the user must explicitly accept the trade-off. Do not silently accept accessibility debt.

## Integration

- **Receives from:** critique (Minor/Note findings), accessibility review (Minor findings), and final verification (deferred items)
- **Feeds into:** planning (debt items become plan tasks) and [design-retrospective.md](design-retrospective.md) (debt trends are retrospective data)
- **Updates:** the Design Debt Register section of the project design record, when one exists

## Anti-Patterns

| Pattern | Why It Fails |
|---------|-------------|
| Capturing Critical issues as debt | Critical issues block access. They get fixed now, not tracked for later |
| Deferring the same item 3+ times | That's not debt management, that's avoidance. Escalate it |
| Accepting accessibility debt without user acknowledgement | Accessibility compromises affect real people. The user decides, not the system |
| Deleting resolved items | Resolved items are history. They show the team addresses its promises |
| Not reviewing debt at project start | Starting a new iteration without checking old promises means those promises are broken |
| Tracking everything | Not every observation needs tracking. Notes that are genuinely informational ("consider X someday") can stay in the critique report. Debt is for specific, actionable items that affect specific people |
