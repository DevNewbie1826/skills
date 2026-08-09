<system-notice>
This task involves multi-step reasoning. Think carefully through the problem before responding.

Drive this task as a deterministic multi-subagent workflow. Author the orchestration in the `eval` tool and fan out subagents — to be comprehensive (decompose and cover in parallel), to be confident (independent perspectives and adversarial checks before you commit), or to take on scale one context can't hold (audits, migrations, broad sweeps). This overrides any default tendency to do the whole task inline when fanning out would be more thorough.

<when>
Worth it when the task benefits from decomposition + parallel coverage, or from independent/adversarial cross-checking before you commit. For a quick lookup or single edit, just do it directly — don't spin up agents. Scout inline FIRST (list the files, scope the diff, find the call sites) to discover the work-list, then fan out over it — you don't need to know the shape before the *task*, only before the *fan-out*. Common shapes, each a well-scoped `eval` call you can chain across turns:
- **Understand** — parallel readers over subsystems → structured map
- **Design** — judge panel of N independent approaches → scored synthesis
- **Review** — split into dimensions → find per dimension → adversarially verify each finding
- **Research** — multi-modal sweep → deep-read the hits → synthesize
- **Migrate** — discover sites → transform each → verify
</when>

<helpers>
State persists across eval calls, so scout in one call and fan out in the next. Every eval call has:

- `agent(prompt, *, agent="task", label=None, schema=None, isolated=None, apply=None, merge=None, handle=False)` — run ONE subagent; returns its final text, or the validated object when `schema` (a JSON Schema dict) is given. With `schema` the subagent is forced to emit structured output that is validated for you — branch on the object, not on parsed prose. `agent` picks a discovered agent ("scout", "reviewer", …); `label` names the artifact. Shared background goes in a `local://` file referenced from each prompt, not a parameter. Subagents are told their final text IS the return value, so they hand back raw data. `agent()` blocks until the subagent finishes. Recursion follows `task.maxRecursionDepth` (default 2; a negative value disables the cap); deeper calls require `handle=True` and manual re-invocation via the returned handle.
- `parallel(thunks)` — run zero-arg callables concurrently through a bounded pool, preserving input order; returns once all finish. The pool is bounded by the session's `task` concurrency — don't hand-tune it; fan out as wide as the work divides. A thunk that raises propagates — wrap risky work in `try/except` inside the thunk to keep partial results. **Closure trap (Python):** a lambda in a loop captures loop variables *by reference* — bind **every** variable the thunk reads (`lambda a=a, b=b: …`), not just the one feeding the label, or all thunks run on the last iteration's values. Safer shape: keep each job as a single per-thunk record — a tuple (or a dict you do **not** mutate after capture) — bind that record alone (`lambda d=d: …`), and derive label *and* prompt from its fields (one capture target, not many). The default arg snapshots the *reference*, so post-capture mutation of a dict still leaks; use a tuple/namedtuple/frozen dataclass for true immutability, or simply don't mutate it. JS `.map((d) => async () => …)` avoids loop-variable late binding only — not later mutation of `d`.
- `pipeline(items, *stages)` — map items through `stages` left-to-right. There is a BARRIER between stages: ALL items clear stage N before stage N+1 begins. Each stage is a one-arg callable; stage 1 gets the original item, later stages get the previous result. Same pool width as `parallel()`.
- `completion(prompt, *, model="default", system=None, schema=None)` — oneshot, stateless model call (no tools, no history). Tiers: "smol", "default", "slow". Cheap classification/scoring inside a fan-out.
- `log(message)` — emit a progress line above the status tree. `phase(title)` — start a phase; the status lines that follow group under it.
- `budget` — `budget.total` (output-token ceiling, or `None` when none is set), `budget.spent()` (tokens spent this turn — main loop + eval subagents), `budget.remaining()` (`math.inf` when total is `None`), `budget.hard` (whether it's enforced). A ceiling is set by the user: `+Nk` in their message is advisory (you self-limit via `budget.remaining()`), `+Nk!` (or Goal Mode) is hard — `agent()` refuses to spawn once spent reaches it. Gate loops on `budget.total` first, since it's `None` when the user set no budget.

Everything runs INLINE and synchronously inside the eval call — no background mode, no resume, no separate progress app. You cannot reliably reach a subagent after `agent()` returns (this run's post-return `hub send` returned `Unknown agent`, and the synchronous call can't answer a mid-run question): front-load any evidence or answer a subagent might need into the INITIAL prompt, and report a caveat that only surfaces after return as unresolved/evidence-only — never "resolved." Each eval call is one well-scoped fan-out; chain several across calls and turns for multi-phase work, reading each result before you decide the next phase.

Because a subagent is unreachable after `agent()` returns, its final text must carry everything the orchestrator will read — nothing arrives afterward. Enforce that at the prompt level with a **return-once instruction** baked into every subagent prompt: "Return your result ONCE via the schema return value. Do not re-read files, re-check, or send IRC messages after returning — your result is final when agent() returns it." This stops a finished agent from voluntarily re-reading files or re-verifying after the round ends — the stale-agent pattern that otherwise keeps re-reading and floods the round with post-return IRC noise (a finding re-sent after the round closed is stale by definition, and the orchestrator has no way to reach the agent to stop it). Pair that with an **IRC dedup rule**: "If your result is returned via schema, do not also broadcast it via IRC — the orchestrator reads the schema return, not the IRC channel." The schema return value is the single delivery channel for results; IRC exists for live coordination only, and the same finding delivered both ways is duplicate noise the orchestrator must filter.
</helpers>

<structure>
For independent per-item chains (review → verify, fetch → extract → score), wrap the WHOLE chain in one function and run it with `parallel()` — then each item flows through its own steps without waiting for the others. (The examples here reference schemas + fixtures defined by the **shared prelude** in the finder→verifier contract below — every example is runnable *after that prelude*.)

**Python (`eval`, Python backend):**

```python
def review_and_verify(d):
    found = agent(d["prompt"], label=f"review:{d['key']}", schema=FINDINGS_SCHEMA)
    return parallel([lambda f=f: {**f, "verdict": agent(
        f"Refute if you can: {f['title']} [severity={f['severity']}, detail: {f['detail']}] (confident it's wrong→original_claim_status=refuted; if genuinely unsure→keep your best-guess status/severity but set verification_confidence=low)",
        label=f"verify:{f['file']}", schema=VERDICT_SCHEMA)} for f in found["findings"]])
phase("Review")
results = parallel([lambda d=d: review_and_verify(d) for d in DIMENSIONS])
confirmed = [f for group in results for f in group if f["verdict"]["actionable_severity"] != "none" and f["verdict"]["verification_confidence"] != "low"]  # real = actionable AND confirmed (Q2+Q3) — see finder→verifier contract
```

**JavaScript (`eval`, JavaScript backend):**

```js
async function reviewAndVerify(d) {
    const found = await agent(d.prompt, {
        label: `review:${d.key}`,
        schema: FINDINGS_SCHEMA,
    });
    return await parallel(found.findings.map((f) => async () => ({
        ...f,
        verdict: await agent(
            `Refute if you can: ${f.title} [severity=${f.severity}, detail: ${f.detail}] (confident it's wrong→original_claim_status=refuted; if genuinely unsure→keep best-guess status/severity but set verification_confidence=low)`,
            { label: `verify:${f.file}`, schema: VERDICT_SCHEMA },
        ),
    })));
}
phase("Review");
const results = await parallel(DIMENSIONS.map((d) => async () => reviewAndVerify(d)));
const confirmed = results.flat().filter((f) => f.verdict.actionable_severity !== "none" && f.verdict.verification_confidence !== "low"); // real = actionable AND confirmed (Q2+Q3) — see finder→verifier contract
```
Reach for `pipeline()` only when a stage genuinely needs ALL of the previous stage first — dedup/merge across the whole set, early-exit on zero, or "compare against the other findings" — because its inter-stage barrier makes every item wait for the slowest peer:

**Python (`eval`, Python backend):**

```python
phase("Find")
found = parallel([lambda d=d: agent(d["prompt"], schema=FINDINGS_SCHEMA) for d in DIMENSIONS])
findings = dedupe([f for r in found for f in r["findings"]])   # needs everything at once
phase("Verify")
verdicts = parallel([lambda f=f: {"id": f["id"], "verdict": agent(verify_prompt(f), schema=VERDICT_SCHEMA)} for f in findings])  # carry the join key, never positional
```

**JavaScript (`eval`, JavaScript backend):**

```js
phase("Find");
const found = await parallel(DIMENSIONS.map((d) => async () =>
    await agent(d.prompt, { schema: FINDINGS_SCHEMA }),
));
const findings = dedupe(found.flatMap((r) => r.findings)); // needs everything at once
phase("Verify");
const verdicts = await parallel(findings.map((f) => async () => ({
    id: f.id, verdict: await agent(verifyPrompt(f), { schema: VERDICT_SCHEMA }),
}))); // carry the join key, never positional
```
Use ordinary code between calls to flatten/map/filter; don't add a barrier just for that. Nested `parallel()` pools each cap independently, so keep total fan-out sane.

**f-string caveat (Python).** The f-strings in the examples above interpolate only plain identifiers (`d['key']`, `f['title']`, `i`), so their literal text stays brace-free and safe. Carry the pattern further, though, and drop CSS, JS, or JSON straight into an f-string: every literal `{`/`}` collides with f-string replacement-field syntax. If the braces don't form a valid replacement field, Python rejects the whole prompt at parse time with a `SyntaxError`; if they accidentally do parse (e.g. `{color}` or `{display}` reads as an expression), the prompt either raises a runtime error (`NameError`/`AttributeError` when the expression references an undefined name) or, when the name happens to be in scope, silently substitutes it — wrong content that only surfaces at runtime.

When a prompt must embed such content, prefer one of: (1) plain string concatenation (adjacent literals or `+`) so the braces never meet f-string syntax; (2) a non-f template with `textwrap.dedent` and `.format()`, escaping every literal brace as `{{`/`}}`; or (3) a plain (non-f) triple-quoted string, where braces stay literal (prefix with `r` if backslashes must stay untouched too). If you must use an f-string, escape each literal brace as `{{`/`}}`.

The point of this note: the examples here are safe as written — every f-string in this file is text/label-only — but the pattern invites embedding CSS/JS/JSON, which is exactly where the collision appears. Keep literal braces out of f-strings and the hazard never triggers.

**Finder→verifier contract.** Define the schemas once (shared prelude below); each field answers exactly ONE question, and you aggregate on the field(s) whose question matches your decision. Every example above and below runs after this prelude.

**Shared prelude** — run once; the examples assume these are in scope (`DIMENSIONS`, the three schemas, `dedupe`, `verify_prompt`/`verifyPrompt`, and a sample joined `entries` for the `to_act` snippet):

```python
DIMENSIONS = [{"key": "bugs", "prompt": "…"}, {"key": "perf", "prompt": "…"}]
FINDINGS_SCHEMA = {                       # finder emits this
    "type": "object",
    "properties": {"findings": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "id":       {"type": "string", "minLength": 1},   # globally unique (see below)
            "file":     {"type": "string", "minLength": 1},
            "title":    {"type": "string", "minLength": 1},
            "severity": {"enum": ["low", "medium", "high", "critical"]},
            "detail":   {"type": "string", "minLength": 1},   # claim body / evidence — nonempty; pass to the verifier
        },
        "required": ["id", "file", "title", "severity", "detail"],
    }}},
    "required": ["findings"],
}
VERDICT_SCHEMA = {                         # per-finding refuter; the ORCHESTRATOR attaches the finding's id in the wrapper
    "type": "object",
    "properties": {
        "original_claim_status":   {"enum": ["upheld", "refuted", "partial"]},              # Q1 — does the CLAIM hold (partial = partly holds; NOT "I'm unsure")
        "actionable_severity":     {"enum": ["none", "low", "medium", "high", "critical"]}, # Q2 — severity to act on
        "verification_confidence": {"enum": ["high", "medium", "low"]},                     # Q3 — the VERIFIER's own confidence (separate axis)
        "reason":                  {"type": "string"},
    },
    "required": ["original_claim_status", "actionable_severity", "verification_confidence", "reason"],
}
REFUTE_SCHEMA = {"type": "object", "properties": {"refuted": {"type": "boolean"}, "reason": {"type": "string"}}, "required": ["refuted", "reason"]}
def dedupe(xs):
    # Same-round exact-duplicate merge: within ONE fan-out, two finders that report the
    # same issue (identical file+title+detail+severity) collapse to one. Cross-round
    # reconciliation is registry-mediated (see cross-stage ID namespace), not this helper.
    by_id, by_content, out = {}, {}, []
    for x in xs:
        if x["id"] in by_id: raise ValueError(f"duplicate finding id (collision): {x['id']} — ids must be globally unique (see finder→verifier contract)")
        by_id[x["id"]] = x                        # record EVERY id right after the collision check (before content dedup)
        sig = (x.get("file"), x.get("title"), x.get("detail"), x.get("severity"))    # duplicate-CANDIDATE fingerprint — same-round exact-duplicate match only, not an identity claim
        if sig in by_content: continue            # same-round exact duplicate — auto-merge (cross-round reconciliation is registry-mediated, not this helper)
        by_content[sig] = x; out.append(x)
    return out
def verify_prompt(f): return f"Refute if you can: {f['title']} [severity={f['severity']}, detail: {f['detail']}]"
entries = [{"id": "x", "verdict": {"original_claim_status": "refuted", "actionable_severity": "low", "verification_confidence": "high", "reason": "downgraded residual"}},
           {"id": "y", "verdict": {"original_claim_status": "refuted", "actionable_severity": "none", "verification_confidence": "high", "reason": "nothing actionable"}}]  # joined finding+verdict list (e.g. results/verdicts from above)
```

```js
const DIMENSIONS = [{ key: "bugs", prompt: "…" }, { key: "perf", prompt: "…" }];
const FINDINGS_SCHEMA = {                       // finder emits this
    "type": "object",
    "properties": { "findings": { "type": "array", "items": {
        "type": "object",
        "properties": {
            "id":       { "type": "string", "minLength": 1 },   // globally unique (see below)
            "file":     { "type": "string", "minLength": 1 },
            "title":    { "type": "string", "minLength": 1 },
            "severity": { "enum": ["low", "medium", "high", "critical"] },
            "detail":   { "type": "string", "minLength": 1 },   // claim body / evidence — nonempty; pass to the verifier
        },
        "required": ["id", "file", "title", "severity", "detail"],
    }}},
    "required": ["findings"],
};
const VERDICT_SCHEMA = {                         // per-finding refuter; the ORCHESTRATOR attaches the finding's id in the wrapper
    "type": "object",
    "properties": {
        "original_claim_status":   { "enum": ["upheld", "refuted", "partial"] },              // Q1 — does the CLAIM hold (partial = partly holds; NOT "I'm unsure")
        "actionable_severity":     { "enum": ["none", "low", "medium", "high", "critical"] }, // Q2 — severity to act on
        "verification_confidence": { "enum": ["high", "medium", "low"] },                     // Q3 — the VERIFIER's own confidence (separate axis)
        "reason":                  { "type": "string" },
    },
    "required": ["original_claim_status", "actionable_severity", "verification_confidence", "reason"],
};
const REFUTE_SCHEMA = { "type": "object", "properties": { "refuted": { "type": "boolean" }, "reason": { "type": "string" } }, "required": ["refuted", "reason"] };
function dedupe(xs) {
    // Same-round exact-duplicate merge: within ONE fan-out, two finders that report the
    // same issue (identical file+title+detail+severity) collapse to one. Cross-round
    // reconciliation is registry-mediated (see cross-stage ID namespace), not this helper.
    const byId = new Map(), byContent = new Map(), out = [];
    for (const x of xs) {
        if (byId.has(x.id)) throw new Error(`duplicate finding id (collision): ${x.id} — ids must be globally unique (see finder→verifier contract)`);
        byId.set(x.id, x);
        const sig = JSON.stringify([x.file, x.title, x.detail, x.severity]);  // duplicate-CANDIDATE fingerprint — same-round exact-duplicate match only, not an identity claim
        if (byContent.has(sig)) continue;  // same-round exact duplicate — auto-merge (cross-round reconciliation is registry-mediated, not this helper)
        byContent.set(sig, x); out.push(x);
    }
    return out;
}
function verifyPrompt(f) { return `Refute if you can: ${f.title} [severity=${f.severity}, detail: ${f.detail}]`; }
const entries = [{ id: "x", verdict: { original_claim_status: "refuted", actionable_severity: "low", verification_confidence: "high", reason: "downgraded residual" } },
                 { id: "y", verdict: { original_claim_status: "refuted", actionable_severity: "none", verification_confidence: "high", reason: "nothing actionable" } }];
```

- **Q1** `original_claim_status` — does the CLAIM hold AS STATED, at its original severity? `upheld` / `refuted` / `partial` (`partial` = the claim *partly* holds — a property of the claim, NOT a proxy for "I'm unsure"; uncertainty is Q3).
- **Q2** `actionable_severity` — what severity would you actually act on? `none` = nothing to act on (whether that's then dropped or borderline depends on Q3 — see convergence). (The orchestrator attaches the finding's `id` in the wrapper when collecting each verdict — the collection examples above do — so the join never depends on output position.)
- **Q3** `verification_confidence` — how confident is the VERIFIER in this verdict (`high`/`medium`/`low`)? An epistemic axis independent of Q1/Q2 — keep it separate so a "partly-true claim" and an "I'm unsure" verdict stay distinguishable.
Give the verifier what Q1 asks for: pass `title`, `severity`, **and** `detail`/evidence into the prompt — Q1 judges the claim "at its original severity" and needs the claim body, so the verifier must see all three. (The sketch prompts in the examples show the short form `[title | severity | detail]`; in real use, expand them with the full finding context.)

Aggregate on **Q2 + Q3**, never Q1 alone — "is there confirmed work to do" is Q2∧Q3:

```python
to_act = [f for f in entries if f["verdict"]["actionable_severity"] != "none" and f["verdict"]["verification_confidence"] != "low"]   # real = actionable AND confirmed; a downgraded residual (refuted + low severity + high confidence) still ships
```

JavaScript:

```js
const toAct = entries.filter((f) => f.verdict.actionable_severity !== "none" && f.verdict.verification_confidence !== "low"); // real = actionable AND confirmed
```

Walkthrough — a high-severity "dangerous substitution" claim that's really a benign preempt-DoS: the refuter returns `original_claim_status="refuted"` (the high claim rejected) + `actionable_severity="low"` (a real low residual) + `verification_confidence="high"`. Aggregating on Q2 keeps it as `low` — correct. Aggregating on `original_claim_status == "upheld"` would have **dropped** real low-severity work.

Do **NOT** impose `refuted ⟹ severity:none`. That invariant deletes legitimate downgraded residuals (the case above) — claim status (Q1) never decides discard on its own. A finding is dropped only when it's *confidently* non-actionable: `actionable_severity == "none"` AND `verification_confidence != "low"`; if it's non-actionable but uncertain (`verification_confidence == "low"`) it's borderline and reported, not discarded. (`REFUTE_SCHEMA` is the Q1-only variant for pure majority-vote refutation, used when you don't track a residual — don't aggregate a mixed Q1/Q2 field from it.)

**Finding `id` is the join key.** Make it globally unique across the WHOLE fan-out — `<lens>:<n>` (e.g. `sec:3`) or a uuid — never per-lens local indices like `S1`. Lens-initial IDs collide (`security`↔`streaming` both `S`; `concurrency`↔`contract` both `C`); collisions silently merge findings or drop verdicts at the join. **Attach the finding's `id` in the wrapper when you collect each verdict** — `{**f, "verdict": …}` or `{"id": f["id"], "verdict": …}`; the orchestrator owns the join key. Never reconstruct the pair by zipping `parallel()` output by position, and don't rely on a verifier to echo an `id` it wasn't given.

**Cross-stage ID namespace (single registry).** Uniqueness within one fan-out isn't enough — when stages run as separate `eval` calls or turns, each can mint its own scheme (`sec:3` one round, `f7` the next), and the manual merge mis-pairs or collides silently. Keep ONE namespace: the orchestrator owns a single ID registry of **canonical** finding ids — assigned once at first discovery, persisted, and immutable. The `(file, title, detail, severity)` fingerprint the `dedupe` function matches on is NOT the identity: it is duplicate-*candidate* matching only, because verify mutates those attributes (a downgraded severity, a refined detail) and the id must not move. Anchor ids to something stable — a rule or location, e.g. `sec:plaintext-transport` (`<lens>:<stable-identifier>`); a monotonic `<lens>:<n>` minted once by the registry and never re-derived also works — never to mutable attributes, and never to the round: `r<N>:<lens>:<n>` mints a fresh id on every re-find, so SEEN-based dedupe (see loop-until-dry) sees a "new" finding forever and convergence never triggers. Discovery history stays provenance metadata (e.g. `occurrences: [{"round": 2, "lens": "sec"}]`), and when a re-find's refined description no longer fingerprints identically, reconcile it to the existing canonical id via candidate matching, recording an alias if the descriptions genuinely diverge. `dedupe()` handles same-round exact duplicates only; cross-round SEEN tracking and reconciliation use the canonical ID registry. The orchestrator tracks SEEN by canonical id: a re-find is an occurrence, never a new finding. Later stages (verify, merge) receive the registry or the previous round's persisted findings — they never mint a new scheme, so the ids established in round 1 stay the join key all the way through.
</structure>

<patterns>
Compose the harness the task calls for:
- **Adversarial verify** — N independent skeptics per finding, each prompted to REFUTE; keep it only if a majority survive. `votes = parallel([lambda i=i: agent(f"Refute: {claim}. refuted=true if unsure.", schema=REFUTE_SCHEMA) for i in range(3)])`, then keep when `sum(not v["refuted"] for v in votes) ≥ 2`. (Q1-only majority vote; pair with `VERDICT_SCHEMA` when you also track a residual — see finder→verifier contract.)
- **Perspective-diverse verify** — give each verifier a distinct lens (correctness, security, perf, does-it-reproduce) instead of N identical refuters. If you build the lenses in a loop, a partial-binding bug (above) can make the **labels** look distinct while every thunk sends the same (last) **prompt**. Verify on what was **actually sent** — not the labels, and not the prompts you built (late binding defeats both): have each thunk capture the exact prompt it passes to `agent()` at call time and return it, then assert the returned prompts are distinct; or, where the runtime exposes it, read each agent's received prompt from the roster/history.
- **Judge panel** — N attempts from different angles, scored by parallel judges; synthesize from the winner, graft the best of the rest.
- **Parallel writes (fixes/migrations)** — `agent()`'s `isolated`/`apply`/`merge` integrate writes in separate workspaces and surface a *mechanical* merge/apply conflict as a cell error — but that does NOT catch a *semantic* omission across differently-owned files (a worker says "not my slice" and makes no competing edit → applies cleanly while the contract stays broken). So ownership comes first: pin the shared interface (a widened type, a header) as its OWN preemptive slice — land it, confirm it compiles — THEN fan out the consumers; files that share a contract line stay in ONE slice. Close the residual gap with an integrated cross-slice test/review pass.
- **Shared context handoff** — build the shared background as ONE `local://` packet (per the `agent()` helper above) and REFERENCE it from each prompt, not paste it into every one — a large diff duplicated across prompts wastes tokens and drifts on copy. Subagents default to "change = last commit" AND to guessing the goal/scope; both burn rounds (pestering for `git diff HEAD~1`, or wandering off-task). The packet = the user's goal + acceptance criteria/non-goals, the exact baseline commit and changed-file list, any upstream decisions, and the FULL change view — generated VERBATIM and baseline-aware: `git diff <baseline>..<target>` for a committed range (or `git show --patch <commit>` for a single commit), PLUS `git diff HEAD` + `git status --short` + task-relevant untracked TEXT files for any uncommitted worktree overlay on top (bare `git diff HEAD` is empty once the work is committed — that's exactly when bare pointers creep in). A bare commit POINTER or a hand-summary is NOT a substitute — they hide the exact changed lines and drift; only the verbatim patch output (range diff or `git show --patch`) is drift-free. Scope it to the task changed-file allowlist: exclude/redact unrelated, secret, binary, or oversized files and `log()` the exclusions (don't sweep in the whole repo — that leaks secrets and bloats tokens). `local://` is the official shared-background channel but resolution is harness-dependent — if an eval `read()` can't resolve the `local://` path, keep ONE packet on a real filesystem path and reference that; inline the content into each prompt only as a last resort, still generated once from the same allowlist/redaction/size-scoped source.
- **No-git fallback** — all of the above assumes a `.git`. In a workspace without `.git` (e.g. a remote directory, a deployed snapshot) the git commands are unavailable, so the orchestrator can't diff — then the changed-file list must come from the USER (or a baseline snapshot the orchestrator keeps), and the orchestrator reads those files VERBATIM into the same `local://` packet (same allowlist/redaction/exclude/`log()` guards). Packet source = git-when-available, else user/baseline-provided file list — never a hand-summary. The packet and the **Workspace stability guard** are separate concerns: the guard's content hash rescans the same frozen owned-root scope regardless of git — see that pattern for the scan contract.
- **Pinned-content review** — snapshot the file contents into the `local://` packet AT DISPATCH (immediately before fan-out, same packet as **Shared context handoff** / **No-git fallback**) and make that packet the version of truth for this round: agents review the packet VERBATIM and never re-read the PINNED paths (the files already in the packet) — a live re-read can catch a mid-round edit and hand the agent a stale or mixed snapshot that matches neither the packet nor the final workspace. Build the packet and the **Workspace stability guard**'s pre-round digest from ONE captured byte map — one read, not two — so a file can't change after the pre-round hash and flip back before packet capture with the guard none the wiser. The packet is a subset/rendering of that same capture: the guard captures the full frozen owned-root scope, the packet renders the change view from it — the packet allowlist (change view) and the guard's broader scope (all owned roots) stay distinct but share one capture. Live reads outside the packet are for NAVIGATION only (finding where code is, mapping call sites) — never as EVIDENCE for a finding: if a finding relies on an out-of-packet caller or dependency, either expand the captured packet to include it and restart the round, or mark that evidence as unverified. Prevention, not detection: this composes with the **Workspace stability guard**, which still rescans the workspace after the round — when the guard reports drift, that round's results are suspect even though every agent saw the pinned copy (the pin fixes WHAT was reviewed; the guard checks WHETHER the world moved under it). Applies to git workspaces too: `git diff` may build the packet, but agents still review pinned paths from the packet, not the live files.
- **Loop-until-dry (discovery)** — keep spawning finders until **K consecutive rounds surface nothing new** (default K=2); dedup against everything SEEN, not just what was confirmed, or it never converges.
- **Convergence rule (quality / slop loops)** — classify each finding from its verdict, not by feel. Three disjoint, schema-only buckets: **real** = `actionable_severity != "none"` AND `verification_confidence != "low"` (confirmed, actionable now); **borderline** = `verification_confidence == "low"` (the verifier is genuinely uncertain — REPORTED, never silently lost); **dropped** = `actionable_severity == "none"` AND `verification_confidence != "low"` (confidently nothing to do — log it, *no silent caps*). Convergence = **K consecutive rounds with zero real findings** (default K=2). Borderlines do NOT reset the counter — but the final report lists every unresolved borderline. (Uncertainty is its OWN axis: `partial` stays a claim-status value, not a proxy for "unsure".) If the user set N rounds, run exactly N regardless of early convergence, and report what's left.
- **Multi-modal sweep** — parallel finders each searching a different way (by-container, by-content, by-entity, by-time), each blind to the others.
- **Completeness critic** — a final agent that asks "what's missing — modality not run, claim unverified, file unread?"; its answer is the next round.
- **Budget/count loops** — Python: `while len(bugs) < 10:`; JavaScript: `while (bugs.length < 10) { … }`. In Python, gate an explicit budget with `budget.total` and `budget.remaining()`; in JavaScript, use `await budget.total()` and `await budget.remaining()`. `log()` each round.
- **No silent caps** — if you bound coverage (top-N, no-retry, sampling), `log()` what you dropped; silent truncation reads as "covered everything" when it didn't.
- **Vacuous verification** — if a round surfaces 0 findings, the adversarial-verify step never runs; report "no findings to verify," NOT "passed verification." A gate that didn't fire is not a gate that passed.
- **Scope discipline for scanners** — give a review/slop scanner the EXACT changed-file list and "outside this list: one-line note only, never edit." Mark recent intended changes (a bug-fix or guard you just added) as in-scope-but-intentional so they aren't relitigated as slop. A scanner that flags untouched files or pre-existing code is scope creep, not a finding — re-prompt with the file list rather than chasing the noise.
- **Workspace stability guard** — DEFAULT (not optional): snapshot the workspace BEFORE fan-out and again AFTER it returns; any difference means a mid-round edit landed and the round's evidence is suspect. Git-agnostic — hash file contents, not git state, so it works in a `.git`-less workspace. Use ONE frozen scan scope for BOTH snapshots: before fan-out, freeze the owned roots / path matcher (e.g. `owned_roots = ["dag-workflow/", "src/"]`, or the directories of `changed_files`); pre-round and post-round both re-scan that SAME scope — not the whole workspace (logs/build artifacts would be false drift), not just the original `changed_files` list (created/renamed paths would be invisible). Snapshot three axes per path — existence, type, content digest — via a crash-proof helper: `def file_digest(f): p = pathlib.Path(f); return "MISSING" if not p.exists() else ("DIR" if p.is_dir() else hashlib.sha256(p.read_bytes()).hexdigest()[:12])` (deleted paths yield `"MISSING"` — evidence, not a crash). Build the map `digests = {f: file_digest(f) for f in <scope paths>}` and derive aggregate `rev = hashlib.sha256(repr(sorted(digests.items())).encode()).hexdigest()[:12]` from it; diff the two maps — created (key only in post), deleted (key only in pre), modified (digest differs) — to pinpoint what changed. On drift, re-verify the drifted file(s) AND their dependency/verification closure — every consumer/dependent that could observe the change; unknown closure → fall back to re-running the whole round. On audit/re-verify paths drift is TERMINAL: discard the round, STOP, and report — with a circuit breaker that halts and escalates after N consecutive drifts (default 2) instead of looping. Any fan-out-time write — orchestrated or not — is a mixed snapshot: land expected fixes BEFORE the guarded audit so the pre-round map captures the new baseline; no mid-round exemption.

Scale to the ask: "find any bugs" → a few finders, single-vote verify. "thoroughly audit / be comprehensive" → larger finder pool, 3–5-vote adversarial pass, a synthesis stage.
</patterns>

<execution>
- Decompose the surface first; capture it in `todo` when it spans phases.
- Prefer `schema=` for any agent whose output you branch on.
- After a fan-out returns, YOU own correctness: read the artifacts, run the gate, verify before acting. Subagents do the legwork; they don't get the last word.
- **Checkpoint discipline** — Commit one independently specified, independently verifiable change per atomic commit as soon as it passes; never let uncommitted edits accumulate across rounds. Uncommitted changes that tangle are extremely hard to recover: once you can't tell which change broke what, disentangling the edits ranges from difficult to impossible, and a backup restores saved state but can't tell you which of the tangled edits was correct — the last clean commit is the primary recovery point. Prefer rolling back one commit at a time, though reverting a range or restoring a known-good checkpoint is valid when an entire run is invalid.
- Keep going until the task is closed — a returned fan-out is a step, not a stopping point.
</execution>
</system-notice>
