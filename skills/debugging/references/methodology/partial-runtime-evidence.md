Read this when the real operation cannot run but you still need defensible runtime evidence.

# Partial Runtime Evidence — When You Cannot Execute the Real Operation

Use this reference when **runtime truth beats code reading** conflicts with an operation you cannot run. The actual call may require paid access, unavailable hardware, network access through a corporate proxy, a production secret, or a customer dataset.

**Partial runtime evidence is still runtime evidence.** This reference explains which partial signals to collect and how to combine them into a defensible conclusion. If a named interception tool or preload mechanism is unavailable, use the strongest available lower tier and explicitly record the limitation; do not invent a capture.

---

## When this applies

Use this reference when all are true:

1. The bug or extraction question requires runtime confirmation.
2. You attempted the obvious "just run it" path and it failed for a reason unrelated to the bug, such as:
   - 401/402/403 from a paid API
   - "device not found," "permission denied," or a platform security block
   - production-only credentials
   - network isolation or unavailable VPN access
   - time-of-day or quota limits
3. Mocking the entire system would defeat verification because you need evidence about the *real* code rather than a stub.

If a clean mock preserves the contract under test, use it. This reference is for cases where mocking would invalidate the answer.

---

## The hierarchy of partial evidence (strongest first)

When you cannot capture the full outbound payload and full response, collect as much as possible from this list. Higher tiers are closer to ground truth and require less inference.

### Tier 1 — Pre-send / post-receive logs

The system builds a request, then sends it. A log of the assembled request **before** transmission is ground truth for everything except wire-level transformations such as TLS and headers added by the HTTP library.

```bash
# Maximize application debug logging when the application supports these variables.
APP_DEBUG=1 APP_LOG_LEVEL=debug APP_LOG_FILE=/tmp/trace.log ./target -x "minimal valid input" 2>&1 | head -200
```

Look for lines such as:

- `Building request: model=X, params={...}`
- `[provider] payload: {...}`
- `Sending to <url>: <serialized body>`

**Strength:** approximately 95% of ground truth for request construction. The remaining gap is wire-level transformation.

### Tier 2 — Local interception via proxy or shim

Run the real binary against a local proxy that records and optionally returns a canned response.

```bash
# One proxy option, if installed and permitted by the target.
mitmproxy --listen-host 127.0.0.1 --listen-port 8888 --mode regular &
HTTPS_PROXY=http://127.0.0.1:8888 SSL_CERT_FILE=~/.mitmproxy/mitmproxy-ca-cert.pem ./target ...
# The proxy logs the TLS-decrypted request.
```

```bash
# Preload shim option on platforms that support it.
# Wrap the network call to log the payload and optionally return a controlled response.
# See ../tools/pwntools.md for scripting examples when that tool is available.
```

If a proxy, certificate setup, or preload shim is unavailable or blocked, do not treat it as evidence. Fall back to Tier 1, Tier 3, or an application-supported trace facility.

**Strength:** wire-level ground truth, provided the target actually honors the proxy or preload.

### Tier 3 — Static extraction x runtime fingerprint cross-check

When you cannot send a request at all, cross-check static analysis with behavior that does not require the real call:

- The binary builds the request even if sending fails; trace that build step with Tier 1.
- The binary writes a state file or cache; inspect it.
- The binary emits version-specific user-agent strings; verify they match the static extraction.
- The binary's `--help` or `--version` output reveals build metadata; verify feature flags.

**Strength:** disjoint evidence sources confirming the same fact. Two independent partial signals that agree are nearly as strong as one full observation.

### Tier 4 — Contrastive runtime under different inputs

If input variant A works but B cannot run, execute A and reason about B from the shared code path:

```bash
# A: minimal trial input works.
./target --action=read --resource=local-file
# B: full call requires paid access and is blocked.
# Capture A's logs, then inspect B's path and verify the only differences.
```

**Strength:** confirms shared code paths; the remaining gap is limited to the difference between A and B.

### Tier 5 — Provider-published logs or dashboards

If the operation succeeded before access was revoked, the provider's dashboard or audit log may show the request. This is lower fidelity but still observed behavior.

**Strength:** real wire data, often summarized as status codes or counts rather than full payloads.

### Tier 6 — Code reading with independent skeptical review

If none of the above is available, read the code carefully and submit it to one [independent skeptical review pass](#verification-review-pattern-for-non-debug-tasks). This is the weakest tier. Mark conclusions as **unverified** in the journal.

---

## How to combine partial signals

A defensible conclusion prefers two independent signals from different tiers. One exception: a complete Tier 2 wire capture can stand alone for request-shape claims because the wire bytes are exactly what the remote received. For behavioral claims about later state or side effects, still add another signal.

| Available evidence | Defensibility |
|---|---|
| Tier 1 + Tier 1 (same log, different lines) | Weak: one source. |
| Tier 1 + Tier 2 (debug log + proxy capture) | **Strong:** independent confirmation. |
| Tier 1 + Tier 3 (debug log + version-output cross-check) | **Strong:** disjoint sources. |
| Tier 2 alone (full proxy capture) | Strong **for request-shape claims only**. Add another signal for response handling or state claims. |
| Tier 3 + Tier 4 (cross-check + contrastive run) | Medium: both are partial. |
| Tier 6 alone (code reading only) | **Insufficient:** escalate or mark unverified. |

Record the assessment in the journal:

```markdown
## Partial runtime evidence
### Question being verified
<the specific claim, e.g. "the provider's default request effort is high">

### Available signals
- Tier 1: debug log /tmp/trace.log line 47-49 shows `effort: "high"`
- Tier 3: static extraction of the request builder returns "high" for the selected mode
- Tier 6: code path inspected and skeptically reviewed

### Independence assessment
Tier 1 and Tier 3 are independent: the log comes from a different code path than
request construction and would diverge if the static reading were wrong.

### Conclusion
VERIFIED via Tier 1 + Tier 3 agreement. No escalation needed.
```

If you cannot achieve a complete Tier 2 capture **or** two independent non-Tier-6 signals, include an explicit note in the deliverable:

> Partial-evidence finding. The full outbound payload could not be captured because [reason]. The conclusion rests on [signal A] and [signal B]. A future verification should attempt [the missing tier] when [condition].

---

## Verification review pattern (for non-debug tasks)

The [independent review triple](04-independent-review-triple.md) is for **stuck debugging**: two failed rounds and a need to break out of a mental box.

For a deliverable that is an **artifact rather than a bug fix** — reverse engineering, extraction, audit, or compliance documentation — use a single independent skeptical review late in the process, with the deliverable in hand.

### When to invoke

- Immediately before declaring an extraction or audit complete.
- After each significant revision of the deliverable, not after every small edit.
- At most three or four iterations before escalating to the user.

### Review brief

Give this brief to a delegated reviewer if available. Otherwise perform it as a fresh-eyes self-review pass: set aside the draft, reopen the cited evidence, and answer the checklist without assuming the conclusion is correct.

```text
SKEPTICAL FINAL VERIFICATION — look for reasons the task is incomplete or wrong.

## Original task
<verbatim user request>

## What was produced
<list of artifacts with paths and brief descriptions>

## Specific claims to verify
<every concrete claim in the deliverable>

## Where to look
<paths, source material, and evidence to inspect>

## Review job
1. Read the deliverables.
2. Spot-check each claim against the cited source or evidence.
3. Identify unsubstantiated claims, missing pieces, or factual errors.
4. End with PASS, FAIL, or PARTIAL and specific gaps.
```

### Why this differs from the independent review triple

| | Independent review triple (debug) | Verification review (artifact) |
|---|---|---|
| Trigger | Two failed hypothesis rounds | About to declare completion |
| Count | Three orthogonal passes, parallel if possible | One focused skeptical pass |
| Goal | Break out of a mental box | Catch unsubstantiated claims |
| Tone | Brainstorm wide alternatives | Skeptical audit |
| Iteration | Reset the hypothesis set | Fix gaps, then review again until PASS |

Do not conflate them. Use the triple for a stuck root-cause hunt. Use the verification review for an artifact that needs auditing.

---

## Common partial-evidence anti-patterns

| Anti-pattern | Why it fails | Replacement |
|---|---|---|
| "It looks right in the code, so it works" | Tier 6 alone, unverified | Add at least one Tier 1-3 signal. |
| "I ran it once, did not error, so it is correct" | Absence of error is not proof of correctness | Capture and verify the actual output. |
| "The mock returns the value I wrote, so the code is fine" | Tautology: the mock loops back the assumption | Use Tier 2 or cross-check with Tier 3. |
| "The provider dashboard shows my call worked" | A dashboard often shows status, not behavior | Combine with Tier 1 when available. |
| "I will trust a recent online answer" | It may describe another version or context | Verify against the actual binary or source. |

---

## Cleanup additions for partial-evidence work

```bash
# Proxy artifacts, if a proxy was used.
# Kill by the PID recorded in this session's journal at spawn; use a pattern-kill only after `pgrep -af mitmproxy` confirms it is this session's process.
kill <journaled-mitmproxy-pid> 2>/dev/null || true
# Delete only cache paths this session created and journaled; verify ownership before rm.
rm -f <journaled-mitmproxy-cache-path> 2>/dev/null

# Debug logs.
rm -f /tmp/trace.log /tmp/*-debug-trace.log

# Preload shim libraries.
rm -f /tmp/*.dylib /tmp/*.so

# Current-shell overrides.
unset HTTPS_PROXY APP_DEBUG APP_LOG_LEVEL APP_LOG_FILE 2>/dev/null
```
