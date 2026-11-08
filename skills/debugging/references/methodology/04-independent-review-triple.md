Read this when two consecutive hypothesis rounds have failed and you need to break out of the current mental model.

# Phase 4 — Independent Review Triple

After two consecutive failed hypothesis rounds, stop investigating and reframe. Continuing past two failures usually means the real cause is in a category you have not imagined, so more work inside the current mental model is wasted time.

Use **independent adversarial review passes from orthogonal angles (parallel subagents if your runtime supports delegation, otherwise fresh-eyes self-review passes, one per angle)**. The goal is not a vote on a fix; it is a new set of decisive runtime queries.

> **Wrong tool for non-debugging tasks.** This triple is for *stuck root-cause hunts*. If the task is producing an artifact (extraction, reverse engineering, audit, or compliance documentation) and needs a skeptical check before completion, use the [verification review pattern](partial-runtime-evidence.md#verification-review-pattern-for-non-debug-tasks). A broad triple on a finished artifact produces tangents instead of an audit.

---

## When to invoke

| Situation | Invoke? |
|---|---|
| One round failed and you have new distinguishing evidence | No — run one more round with a refined hypothesis set. |
| Two rounds failed and hypotheses now feel like variations of each other | **Yes — invoke now.** |
| Two rounds failed and no new evidence angles remain | **Yes — invoke now.** |
| You have investigated the same bug for more than two hours | **Yes — invoke now regardless of round count.** |
| One round failed but the user is watching and wants speed | No — one round is not enough to justify the review cost. |

---

## Why three independent passes and orthogonal framings

One review tends to inherit the framing of its brief, including its blind spots. Three passes with orthogonal framings force alternatives to diverge. Agreement across independently framed passes is signal; disagreement identifies what runtime evidence must resolve.

The framings cover distinct cause categories:

- **A — obvious-but-missed:** embarrassingly simple causes the investigator walked past.
- **B — system-boundary:** causes at integration seams, not in the code being read.
- **C — invariant-violation:** load-bearing assumptions behind the current hypotheses that may be false.

Run all three in parallel if delegation is available. Otherwise conduct three fresh-eyes self-review passes serially: start each with the same evidence dossier, do not reuse a prior pass's conclusion until its own report is complete, and label the lens clearly in the journal.

---

## The three review briefs

Give one brief to each independent reviewer or self-review pass.

### Review A — obvious-but-missed

```text
[CONTEXT: bug description and captured evidence so far, verbatim, with file:line references]

What is the most embarrassing, obvious cause a senior engineer would spot in 30 seconds that we have overlooked? Consider:
- typos, off-by-one errors
- wrong variable, constant, or import
- stale cache, wrong file edited, wrong process inspected
- attachment to the wrong service instance
- a test harness running different code than the application
- editing src/ while running dist/

Return exactly three candidate causes ranked by likelihood. For each, state in one sentence why the captured evidence is consistent with it.
```

### Review B — system-boundary

```text
[CONTEXT: bug description and captured evidence so far]

What if the bug is not in the code we have been reading, but at a boundary? Consider:
- third-party SDK behavior that contradicts its documentation
- middleware that mutates a request or response
- a proxy, gateway, or load balancer that rewrites headers or bodies
- build-time versus runtime environment-variable resolution
- module-load-order issues
- shared-library version mismatch
- ABI differences (native extensions, libc variants)
- wrong transport or protocol negotiation

Return three candidate causes. Each must name the boundary and the contract assumption that might be violated.
```

### Review C — invariant-violation

```text
[CONTEXT: bug description and captured evidence so far]

Which assumptions behind the current hypotheses might be false?

Enumerate the five most load-bearing assumptions. For each:
- describe the smallest runtime query that would falsify it
- predict the observable if the invariant holds
- predict the observable if it fails

At least one query must be decisive.
```

---

## Synthesize the three passes

**Do not select the highest-ranked candidate from a single pass.** That defeats the point of independent framing.

### 1. Agreement scan

Note candidate causes appearing in at least two reports. Independent agreement across orthogonal framings is strong signal: when the obvious-but-missed and system-boundary lenses land on the same cause, prioritize a query that can confirm or refute it.

### 2. Disagreement scan

Note where reports disagree. Disagreement is genuine uncertainty that runtime evidence, not more reasoning, must resolve. Turn each disagreement into a candidate distinguishing query for the next round.

### 3. New falsification queries

Review C supplies concrete deciding queries. Pull them verbatim into the new evidence-gathering plan.

### 4. Build the new hypothesis set

Create at least three hypotheses using both agreement (likely causes) and disagreement (alternatives that must be resolved). Record this in the journal:

```markdown
## Independent review triple — Round <N>
- Invoked at: <ISO timestamp>
- Review A summary: <top three candidates, one line each>
- Review B summary: <top three candidates>
- Review C summary: <five load-bearing assumptions and falsification queries>

### Cross-framing agreement
- <candidate> appeared in A + B
- <candidate> appeared in B + C

### New hypothesis set
1. <hypothesis> — evidence to gather: <one line>
2. ...
```

### 5. Reset the counter

Reset the consecutive-failed-round counter to zero. Return to Phase 3 with the new set.

---

## If another two rounds fail after the triple

You are genuinely stuck. Escalate to the user using [Phase 5](05-escalate.md), including every hypothesis tried, every captured observation, and the synthesis from both independent-review triples. Do not guess a fix.
