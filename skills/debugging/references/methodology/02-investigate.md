Read this when you need to turn competing explanations into decisive runtime evidence.

# Phase 2 + 3 — Hypothesis Formation & Parallel Investigation

One hypothesis is a hunch. Three hypotheses are a decision. Investigation turns that decision into runtime evidence.

---

## Phase 2 — Hypothesis Formation (Minimum Three)

### Why three, not one

A single hypothesis creates confirmation bias: you read runtime state looking for evidence that confirms it and unconsciously discount contradictions. Three hypotheses force you to design queries that *distinguish* between them, which is the only way runtime evidence becomes decisive.

### Generate across orthogonal axes

If your three hypotheses are all variations of "the handler has a bug", you do not actually have three hypotheses. Span the space:

| Axis | Example framing |
|---|---|
| **User-code logic** | "The handler early-returns because condition X is unexpectedly true" |
| **Library/SDK behavior** | "The third-party client swallows the error and returns a stub" |
| **Environment/config** | "The env var is read at module-load time before it gets populated, so it is empty" |
| **Async/timing** | "The promise rejects (or goroutine panics) after the response is already sent" |
| **Silent side-effect** | "An earlier turn mutated shared state that the current turn inherits" |
| **Observability gap** | "The error is raised but suppressed before logging; it only exists as an unawaited rejection or ignored signal" |
| **Binary-level** (when applicable) | "The function we think is running is actually jumped over by a patched thunk or a different version loaded" |
| **Build-vs-runtime** | "The code we are reading is not the code that is running: stale build, wrong symlink, cached wheel, or dist/ ahead of src/" |

### For each hypothesis, write in the journal

1. **Claim** — one sentence.
2. **Distinguishing evidence** — the exact value or state that confirms or refutes it, and where to read it (file:line, log source, breakpoint location, memory address).
3. **If true, the fix is** — two words. This forces you to think through fix cost before committing to the hunt.

### Collapse rule

If two hypotheses have identical distinguishing evidence, they are not actually different — collapse them and find a real alternative. If you cannot come up with a third distinct hypothesis, you do not understand the system well enough yet. Read more code before investigating.

---

## Phase 3 — Investigation

Choose the lane based on available capability, not a particular product interface. Assign one hypothesis to each independent line of inquiry. Keep every pass read-only until the investigator explicitly approves instrumentation.

### Delegated parallel investigation (if supported)

If your runtime supports delegation, run independent investigation passes in parallel. Do not assume a particular role name, task API, or state directory. Give each pass a bounded brief containing the bug summary, its owned hypothesis, the exact evidence to seek, and the requirement to report raw observations with locations.

| Pass | Scope | Report must contain |
|---|---|---|
| **Runtime-state inspection** | Attach to the live process; inspect variables, heap, goroutines, stack, or registers as appropriate. | Verbatim observed values, breakpoint/address or file:line, and whether they confirm or refute the hypothesis. |
| **Log and timeline analysis** | Inspect server logs, stderr, runtime debug output, and timestamps. Look for swallowed errors, ignored panics, and success-shaped failures. | Ordered timeline, latencies, raw log excerpts, and suspicious silent-failure signals. |
| **Reproduction minimization** | Build the smallest reliable repro through the real entry point: command, request, browser flow, or binary interaction. | Exact input, expected output, observed output, and a reproducible command or script. |
| **Trace correlation** | Cross-link evidence from the other passes and identify the next most decisive query. | Causal chain, missing evidence, and one proposed runtime query. |

Shared rules for delegated passes:

- Do not edit source, create persistent configuration, or run version-control commands without approval from the coordinating investigator.
- Journal any temporary artifact before creating it.
- Report facts separately from inferences. Quote values verbatim and include their source.
- Do not turn an inconclusive observation into a likely cause.

The coordinating investigator maintains the journal, approves instrumentation, synthesizes reports into hypothesis statuses, and decides whether another round is needed.

### Fresh-eyes self-review passes (if delegation is unavailable)

If your runtime cannot delegate, perform the same passes serially as separate fresh-eyes self-review passes. Use one lens at a time, complete its report before starting the next, and begin each lens from the evidence dossier rather than the prior lens's conclusion. This preserves the useful separation between runtime state, logs, reproduction, and correlation even when one person performs all four.

For each pass, write a short handoff in the journal:

```markdown
### Investigation pass — <lens> — <ISO timestamp>
- Hypothesis owned: H<n>
- Evidence sought: <specific observable>
- Source: <file:line | log source | command | address>
- Raw value: `<verbatim>`
- Interpretation: <one line>
- Confirms/refutes/inconclusive: H<n>
```

### Evidence capture discipline (both lanes)

For every piece of runtime state captured, record in the journal:

```markdown
### <ISO timestamp> — <what you looked at>
- Source: <file:line | log source | command | breakpoint address>
- Value: `<verbatim>`
- Interpretation: <one line — why this matters>
- Refutes/Confirms: H<n>
```

**Verbatim values only. No paraphrasing.**

- `messages.length=0` is evidence.
- "messages seemed empty" is not evidence — it is a memory of an observation, and memory of observations is where debug sessions go to die.

If you find yourself about to paraphrase, stop, go back, and copy the raw value.

---

## Round completion

A round is complete when every hypothesis has confirming or refuting evidence, or when you have exhausted the available evidence sources without a decisive result. If the round ends inconclusively, it counts as a failed round in the journal. After two consecutive failed rounds, use [Phase 4's independent review triple](04-independent-review-triple.md).
