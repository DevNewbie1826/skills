<system-notice>
This task involves multi-step reasoning. Think carefully through the problem before responding.

Drive this task as a deterministic multi-subagent workflow (see SKILL.md for the fan-out/schema/adversarial-verify contract). Author the orchestration in the `eval` tool. This overrides any default tendency to do the whole task inline when fanning out would be more thorough.

<when>
Worth it when the task benefits from decomposition + parallel coverage, or from independent/adversarial cross-checking before you commit. For trivial work, stay inline (see SKILL.md Routing) — don't spin up agents. Scout inline FIRST (list the files, scope the diff, find the call sites) to discover the work-list, then fan out over it — you don't need to know the shape before the *task*, only before the *fan-out*. Common shapes, each a well-scoped `eval` call you can chain across turns:
- **Understand** — parallel readers over subsystems → structured map
- **Design** — judge panel of N independent approaches → scored synthesis
- **Review** — split into dimensions → find per dimension → adversarially verify each finding
- **Research** — multi-modal sweep → deep-read the hits → synthesize
- **Migrate** — discover sites → transform each → verify
</when>

<helpers>
State persists across eval calls (see `<when>` for the scout-first principle). Every eval call has:

- `agent(prompt, *, agent="task", label=None, schema=None, isolated=None, apply=None, merge=None, handle=False)` — run ONE subagent; returns its final text, or the validated object when `schema` (a JSON Schema dict) is given. With `schema` the subagent is forced to emit structured output that is validated for you — branch on the object, not on parsed prose. `agent` picks a discovered agent ("scout", "reviewer", …); `label` names the artifact. Shared background goes in a `local://` file referenced from each prompt, not a parameter. Subagents are told their final text IS the return value, so they hand back raw data. `agent()` blocks until the subagent finishes. Recursion follows `task.maxRecursionDepth` (default 2; a negative value disables the cap); deeper calls require `handle=True` and manual re-invocation via the returned handle.
- `parallel(thunks)` — runs zero-arg callables concurrently (bounded pool = harness subagent concurrency cap — don't hand-tune; fan out as wide as the work divides), preserving order, returning when all finish. A raising thunk propagates — wrap risky work in `try/except` inside it to keep partial results. **Closure trap (Python):** loop lambdas capture *by reference* — bind **every** variable the thunk reads (`lambda a=a, b=b: …`), or all thunks see the last iteration's values. Safer: bind one per-thunk record alone (`lambda d=d: …`) — a tuple (or dict never mutated after capture) holding label+prompt, one capture target; default args snapshot the *reference* — later dict mutation leaks (use a tuple, or don't). JS `.map((d) => async () => …)` fixes late binding only, not later mutation.
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
    found = agent(d["prompt"], agent="reviewer", label=f"review:{d['key']}", schema=FINDINGS_SCHEMA)
    return parallel([lambda f=f: {**f, "verdict": agent(
        f"Refute if you can: {f['title']} [severity={f['severity']}, detail: {f['detail']}] (confident it's wrong→original_claim_status=refuted; if genuinely unsure→keep your best-guess status/severity but set verification_confidence=low)",
        agent="reviewer", label=f"verify:{f['file']}", schema=VERDICT_SCHEMA)} for f in found["findings"]])
phase("Review")
results = parallel([lambda d=d: review_and_verify(d) for d in DIMENSIONS])
confirmed = [f for group in results for f in group if f["verdict"]["actionable_severity"] != "none" and f["verdict"]["verification_confidence"] != "low"]  # real = actionable AND confirmed (Q2+Q3) — see finder→verifier contract
```

**JavaScript (`eval`, JavaScript backend):**

```js
async function reviewAndVerify(d) {
    const found = await agent(d.prompt, {
        agent: "reviewer",
        label: `review:${d.key}`,
        schema: FINDINGS_SCHEMA,
    });
    return await parallel(found.findings.map((f) => async () => ({
        ...f,
        verdict: await agent(
            `Refute if you can: ${f.title} [severity=${f.severity}, detail: ${f.detail}] (confident it's wrong→original_claim_status=refuted; if genuinely unsure→keep best-guess status/severity but set verification_confidence=low)`,
            { agent: "reviewer", label: `verify:${f.file}`, schema: VERDICT_SCHEMA },
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
found = parallel([lambda d=d: agent(d["prompt"], agent="reviewer", schema=FINDINGS_SCHEMA) for d in DIMENSIONS])
findings = dedupe([f for r in found for f in r["findings"]])   # needs everything at once
phase("Verify")
verdicts = parallel([lambda f=f: {"id": f["id"], "verdict": agent(verify_prompt(f), agent="reviewer", schema=VERDICT_SCHEMA)} for f in findings])  # carry the join key, never positional
```

**JavaScript (`eval`, JavaScript backend):**

```js
phase("Find");
const found = await parallel(DIMENSIONS.map((d) => async () =>
    await agent(d.prompt, { agent: "reviewer", schema: FINDINGS_SCHEMA }),
));
const findings = dedupe(found.flatMap((r) => r.findings)); // needs everything at once
phase("Verify");
const verdicts = await parallel(findings.map((f) => async () => ({
    id: f.id, verdict: await agent(verifyPrompt(f), { agent: "reviewer", schema: VERDICT_SCHEMA }),
}))); // carry the join key, never positional
```
Use ordinary code between calls to flatten/map/filter; don't add a barrier just for that. Nested `parallel()` pools each cap independently, so keep total fan-out sane.

**f-string caveat (Python).** The f-strings in the examples above interpolate only plain identifiers (`d['key']`, `f['title']`, `i`), so their literal text stays brace-free and safe. Carry the pattern further, though, and drop CSS, JS, or JSON straight into an f-string: every literal `{`/`}` collides with f-string replacement-field syntax. If the braces don't form a valid replacement field, Python rejects the whole prompt at parse time with a `SyntaxError`; if they accidentally do parse (e.g. `{color}` or `{display}` reads as an expression), the prompt either raises a runtime error (`NameError`/`AttributeError` when the expression references an undefined name) or, when the name happens to be in scope, silently substitutes it — wrong content that only surfaces at runtime.

When a prompt must embed such content, prefer one of: (1) plain string concatenation (adjacent literals or `+`) so the braces never meet f-string syntax; (2) a non-f template with `textwrap.dedent` and `.format()`, escaping every literal brace as `{{`/`}}`; or (3) a plain (non-f) triple-quoted string, where braces stay literal (prefix with `r` if backslashes must stay untouched too). If you must use an f-string, escape each literal brace as `{{`/`}}`.

The point of this note: the examples here are safe as written — every f-string in this file is text/label-only — but the pattern invites embedding CSS/JS/JSON, which is exactly where the collision appears. Keep literal braces out of f-strings and the hazard never triggers.

**Finder→verifier contract.** Define the schemas once (shared prelude below); each field answers exactly ONE question, and you aggregate on the field(s) whose question matches your decision. Every example above and below runs after this prelude.

**Shared prelude** — run once; the examples assume these are in scope (`DIMENSIONS`, the three schemas, `dedupe`, `verify_prompt`/`verifyPrompt`, and a sample joined `entries` for the `real` aggregation snippet):

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
entries = [{"id": "sec:5", "file": "src/auth.py", "title": "plaintext transport", "severity": "high", "detail": "uses HTTP not HTTPS for auth tokens", "verdict": {"original_claim_status": "refuted", "actionable_severity": "low", "verification_confidence": "high", "reason": "downgraded residual"}},
           {"id": "y", "file": "src/cache.ts", "title": "stale cache entry", "severity": "medium", "detail": "cache TTL not enforced on eviction", "verdict": {"original_claim_status": "refuted", "actionable_severity": "none", "verification_confidence": "high", "reason": "nothing actionable"}}]
findings = entries  # finder output joined with verdicts
real = [f for f in entries if f["verdict"]["actionable_severity"] != "none" and f["verdict"]["verification_confidence"] != "low"]
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
const entries = [{ id: "sec:5", file: "src/auth.py", title: "plaintext transport", severity: "high", detail: "uses HTTP not HTTPS for auth tokens", verdict: { original_claim_status: "refuted", actionable_severity: "low", verification_confidence: "high", reason: "downgraded residual" } },
                 { id: "y", file: "src/cache.ts", title: "stale cache entry", severity: "medium", detail: "cache TTL not enforced on eviction", verdict: { original_claim_status: "refuted", actionable_severity: "none", verification_confidence: "high", reason: "nothing actionable" } }];
const findings = entries;
const real = entries.filter((f) => f.verdict.actionable_severity !== "none" && f.verdict.verification_confidence !== "low");
```

- **Q1** `original_claim_status` — does the CLAIM hold AS STATED, at its original severity? `upheld` / `refuted` / `partial` (`partial` = the claim *partly* holds — a property of the claim, NOT a proxy for "I'm unsure"; uncertainty is Q3).
- **Q2** `actionable_severity` — what severity would you actually act on? `none` = nothing to act on (whether that's then dropped or borderline depends on Q3 — see convergence). (The orchestrator attaches the finding's `id` in the wrapper when collecting each verdict — the collection examples above do — so the join never depends on output position.)
- **Q3** `verification_confidence` — how confident is the VERIFIER in this verdict (`high`/`medium`/`low`)? An epistemic axis independent of Q1/Q2 — keep it separate so a "partly-true claim" and an "I'm unsure" verdict stay distinguishable.
Give the verifier what Q1 asks for: pass `title`, `severity`, **and** `detail`/evidence into the prompt — Q1 judges the claim "at its original severity" and needs the claim body, so the verifier must see all three. (The sketch prompts in the examples show the short form `[title | severity | detail]`; in real use, expand them with the full finding context.)

Aggregate on **Q2 + Q3**, never Q1 alone — "is there confirmed work to do" is Q2∧Q3:

```python
real = [f for f in entries if f["verdict"]["actionable_severity"] != "none" and f["verdict"]["verification_confidence"] != "low"]   # real = actionable AND confirmed; a downgraded residual (refuted + low severity + high confidence) still ships
```

JavaScript:

```js
const real = entries.filter((f) => f.verdict.actionable_severity !== "none" && f.verdict.verification_confidence !== "low"); // real = actionable AND confirmed
```

Walkthrough — a high-severity "dangerous substitution" claim that's really a benign preempt-DoS: the refuter returns `original_claim_status="refuted"` (the high claim rejected) + `actionable_severity="low"` (a real low residual) + `verification_confidence="high"`. Aggregating on Q2 keeps it as `low` — correct. Aggregating on `original_claim_status == "upheld"` would have **dropped** real low-severity work.

Do **NOT** impose `refuted ⟹ severity:none`. That invariant deletes legitimate downgraded residuals (the case above) — claim status (Q1) never decides discard on its own. A finding is dropped only when it's *confidently* non-actionable: `actionable_severity == "none"` AND `verification_confidence != "low"`; if it's non-actionable but uncertain (`verification_confidence == "low"`) it's borderline and reported, not discarded. (`REFUTE_SCHEMA` is the Q1-only variant for pure majority-vote refutation, used when you don't track a residual — don't aggregate a mixed Q1/Q2 field from it.)

**Finding `id` is the join key.** Make it globally unique across the WHOLE fan-out — `<lens>:<n>` (e.g. `sec:3`) or a uuid — never per-lens local indices like `S1`. Lens-initial IDs collide (`security`↔`streaming` both `S`; `concurrency`↔`contract` both `C`); collisions silently merge findings or drop verdicts at the join. **Attach the finding's `id` in the wrapper when you collect each verdict** — `{**f, "verdict": …}` or `{"id": f["id"], "verdict": …}`; the orchestrator owns the join key. Never reconstruct the pair by zipping `parallel()` output by position, and don't rely on a verifier to echo an `id` it wasn't given.

**Cross-stage ID namespace (single registry).** Uniqueness within one fan-out isn't enough — when stages run as separate `eval` calls or turns, each can mint its own scheme (`sec:3` one round, `f7` the next), and the manual merge mis-pairs or collides silently. Keep ONE namespace: the orchestrator owns a single ID registry of **canonical** finding ids — assigned once at first discovery, persisted, and immutable. The `(file, title, detail, severity)` fingerprint the `dedupe` function matches on is NOT the identity: it is duplicate-*candidate* matching only, because verify mutates those attributes (a downgraded severity, a refined detail) and the id must not move. Anchor ids to something stable — a rule or location, e.g. `sec:plaintext-transport` (`<lens>:<stable-identifier>`); a monotonic `<lens>:<n>` minted once by the registry and never re-derived also works — never to mutable attributes, and never to the round: `r<N>:<lens>:<n>` mints a fresh id on every re-find, so SEEN-based dedupe (see loop-until-dry) sees a "new" finding forever and convergence never triggers. Discovery history stays provenance metadata (e.g. `occurrences: [{"round": 2, "lens": "sec"}]`), and when a re-find's refined description no longer fingerprints identically, reconcile it to the existing canonical id via candidate matching, recording an alias if the descriptions genuinely diverge. `dedupe()` handles same-round exact duplicates only; cross-round SEEN tracking and reconciliation use the canonical ID registry. The orchestrator tracks SEEN by canonical id: a re-find is an occurrence, never a new finding. Later stages (verify, merge) receive the registry or the previous round's persisted findings — they never mint a new scheme, so the ids established in round 1 stay the join key all the way through.
</structure>

<patterns>
Compose the harness the task calls for:
- **Adversarial verify** — N independent skeptics per finding, each prompted to REFUTE; keep it only if a majority survive. `votes = parallel([lambda i=i: agent(f"Refute: {claim}. refuted=true if unsure.", agent="reviewer", schema=REFUTE_SCHEMA) for i in range(3)])`, then keep when `sum(not v["refuted"] for v in votes) ≥ 2`. (Q1-only majority vote; pair with `VERDICT_SCHEMA` when you also track a residual — see finder→verifier contract.)
- **Perspective-diverse verify** — give each verifier a distinct lens (correctness, security, perf, does-it-reproduce) instead of N identical refuters. If you build the lenses in a loop, a partial-binding bug (above) can make the **labels** look distinct while every thunk sends the same (last) **prompt**. Verify on what was **actually sent** — not the labels, and not the prompts you built (late binding defeats both): have each thunk capture the exact prompt it passes to `agent()` at call time and return it, then assert the returned prompts are distinct; or, where the runtime exposes it, read each agent's received prompt from the roster/history.
- **Judge panel** — N attempts from different angles, scored by parallel judges; synthesize from the winner, graft the best of the rest.
- **Parallel writes (fixes/migrations)** — dispatch each implementation slice as a separate eval `agent(agent='task')` (implementation runs inside eval — per Step 2's eval execution rule). Pin the shared interface (a widened type, a header) as its OWN preemptive slice — land it first via eval `agent(agent='task')`, confirm it compiles — THEN fan out the consumer slices as concurrent eval `agent(agent='task')` agents with isolated workspace enabled (Python: `isolated=True`, JavaScript: `{ isolated: true }`); files that share a contract line stay in ONE slice. Concurrent implementation agents MUST use ISOLATED workspaces (isolated workspace enabled — Python: `isolated=True`, JavaScript: `{ isolated: true }` — gives each writer its own worktree); the orchestrator applies/merges the isolated results after all writers return — apply each isolated result via the apply/merge mechanism (isolated=true agents return their workspace diff; the orchestrator applies it to the main workspace). Concurrent eval task agents must own DISJOINT files (no two agents edit the same file in the same round); shared paths or contract lines are SERIALIZED — the preemptive interface slice lands and compiles first, then consumer slices fan out. After all slices land and their results are applied/merged, verify with `git diff`/`git status` plus the workspace stability guard — capture the stability-guard baseline AFTER all accepted implementation writes have been applied/merged, not before dispatch. Close the residual gap with an integrated eval cross-slice review pass (eval `agent(agent='reviewer', …)`/`parallel()`) after all slices land.
- **Shared context handoff** — Build ONE shared `local://` packet (see the `agent()` helper above) and reference it from every prompt; never paste copies, which waste tokens and drift. Include the user's goal, acceptance criteria/non-goals, exact baseline commit, changed-file allowlist, upstream decisions, and FULL VERBATIM, baseline-aware change view: `git diff <baseline>..<target>` for a committed range or `git show --patch <commit>` for one commit, plus `git diff HEAD`, `git status --short`, and task-relevant untracked TEXT files for the worktree overlay. Never substitute a bare commit pointer, bare `git diff HEAD` (empty after commit), or hand-summary: subagents otherwise assume "change = last commit" and guess goal/scope, wasting rounds. Keep only allowlisted files (exclude/redact secrets/binaries/oversized; `log()` each exclusion); never sweep the whole repo. If `local://` is unresolvable, keep one packet copy on a real filesystem path and reference that path from each prompt; inline into prompts only as last resort, but still generate once from the same allowlisted source.
- **Pre-code gates** — satisfy the project's pre-code requirements BEFORE dispatch, not after: the mandatory AGENTS.md (or equivalent) read, compliance with the project's coding standards, and confirmation that required build/lint config exists. A gate that is not met is resolved before fan-out — never dispatch past it; and state the gates explicitly in every subagent prompt so no agent bypasses them. The harness's advisor can enforce pre-code gates (blocking an edit until they're met); the skill anticipates this by treating gates as a dispatch precondition, so a gate failure surfaces as a pre-dispatch fix instead of a mid-round blocker that breaks the flow.
- **No-git fallback** — all of the above assumes a `.git`. In a workspace without `.git` (e.g. a remote directory, a deployed snapshot) the git commands are unavailable, so the orchestrator can't diff — then the changed-file list must come from the USER (or a baseline snapshot the orchestrator keeps), and the orchestrator reads those files VERBATIM into the same `local://` packet (same allowlist/redaction/exclude/`log()` guards). Packet source = git-when-available, else user/baseline-provided file list — never a hand-summary. The packet and the **Workspace stability guard** are separate concerns: the guard's content hash rescans the same frozen owned-root scope regardless of git — see that pattern for the scan contract.
- **Pinned-content review** — Immediately before fan-out, snapshot file contents at dispatch into the same `local://` packet per **Shared context handoff** / **No-git fallback**; it is the round's truth. Agents review pinned paths VERBATIM only from it, never live, avoiding mixed snapshots. Derive the packet and **Workspace stability guard** pre-round digest from one byte map captured in one read, closing any change-and-revert gap. The guard covers the full frozen owned-root scope; the packet renders its change-view subset, so their scopes stay distinct but share one capture. Live out-of-packet reads are for NAVIGATION only (locating code/mapping call sites), never finding EVIDENCE. If evidence needs an out-of-packet caller or dependency, add it to the capture/packet and restart the round, or mark it unverified. Rescan afterward per **Workspace stability guard**; drift makes results suspect: the pin fixes WHAT was reviewed, while the guard checks WHETHER the workspace moved. This includes git: `git diff` may build the packet, but agents review its pinned content, not live files.
- **Loop-until-dry (discovery)** — keep spawning finders until **K consecutive rounds surface nothing new** (default K=2); dedup against everything SEEN, not just what was confirmed, or it never converges.
- **Persist round findings** — right after `dedupe`, write the round's findings to a `local://` file so you can re-read the results without re-running the finder (the expensive step): Python `write(f"local://round{N}_findings.json", json.dumps(findings))`, JavaScript `await write(\`local://round${N}_findings.json\`, JSON.stringify(findings))`. Merge the round's findings into the cumulative canonical registry/SEEN set, then persist the cumulative set (optionally keeping per-round snapshots separately) — a per-round file alone can't serve as the registry, since SEEN must span every prior round or re-finds read as "new" and convergence never triggers. This feeds the cross-stage ID namespace, so canonical ids and SEEN tracking survive across `eval` calls without re-finding.
- **Convergence rule + termination (what resets K, and when to stop)** — Classify by verdict, not feel, into three disjoint buckets: **real** = `actionable_severity != "none"` AND `verification_confidence != "low"`; **borderline** = `verification_confidence == "low"` (report, never lose); **dropped** = `actionable_severity == "none"` AND `verification_confidence != "low"` (log; **No silent caps**). Uncertainty is a separate axis: `partial` is claim status, not “unsure.” Convergence is **K consecutive rounds with zero actionable findings**: `len(to_act) == 0`, where `to_act = [f for f in real if f.id not in accepted]` (A4’s test; never `len(real) == 0`; default K=2). A zero-actionable round advances K; only a **real, unaccepted** finding resets it. Deduped (see **Cross-stage ID namespace**), accepted (see **Accepted tradeoffs**), dropped, and borderline findings never reset K; a round containing only them advances it. All complement; none conflict. Per **LOW severity is still verified**, a verified actionable LOW is real and resets K unless accepted; a LOW that is deduped, accepted, dropped, or borderline does not. If the user sets N rounds, run exactly N despite early convergence and report what remains. External blocker stop: if all remaining real findings are blocked beyond the orchestrator’s control (physical device, external API, or user decision), stop spinning; park each as `blocked`, record its dependency, and report it for resumption when cleared. K-dry means no new findings; parked-blocked means real work cannot proceed. Neither abandons findings; the final report includes unresolved borderlines and parked/blocked items.
- **LOW severity is still verified (severity is not a skip gate)** — `actionable_severity` never decides whether a finding reaches the verifier: every finding, LOW included, is sent for verification — skipping a finding because it looks trivial would silently lose it before the three buckets ever run. Severity only weights the vote, per A6: a LOW finding gets a single-vote verify, not a council — but the vote still runs. A confirmed actionable LOW (`actionable_severity == "low"` AND `verification_confidence != "low"`) is **real**, exactly like any other confirmed finding, and resets K unless accepted under A4 (an accepted finding drops out of `to_act` and never resets K).
- **Fix-regression resets K (a fix's side effects extend convergence)** — a fix applied in round N that surfaces a NEW real finding in round N+1 (a regression introduced by the fix) is a real finding like any other (unless accepted under A4), so it resets K; convergence holds only after K consecutive rounds with zero actionable findings *following* the fix. A regression is an unexpected side effect, so extending convergence is the safe direction — do NOT treat it as expected churn under the **Convergence rule + termination** rule.
- **Severity-weighted verification + light/full mode (mode-state contract, A6)** — Mode is per-task state, not a per-finding choice: A6 selects it once per task, fixing verifier count and convergence K. **FULL (default):** HIGH/CRITICAL findings get a 3–5-vote adversarial council (see **Adversarial verify**); MEDIUM/LOW get one vote; K=2. **LIGHT:** select explicitly before round 1 only for small, low-risk tasks; all severities get one vote, no council, and K=1 (one clean round). LIGHT is provisional: a round-1 HIGH/CRITICAL finding triggers **Sticky escalation to FULL (A7)**; only A7 changes the effective mode, which persists across rounds. Per **LOW severity is still verified**, severity weights vote count, never whether verification runs: both modes verify every finding. Vote counts by severity:

```python
def vote_count(mode, severity):
    # Severity weights the VOTE, not the SKIP: it picks how many verifiers judge a
    # finding, never whether verification runs — every finding is verified (B15).
    if mode == "light":
        return 1                                          # light: single-vote verify for ALL findings, no council
    return 3 if severity in ("high", "critical") else 1   # full: 3–5-vote council for HIGH/CRITICAL, single-vote for MEDIUM/LOW
```

```js
function voteCount(mode, severity) {
    // Severity weights the VOTE, not the SKIP: it picks how many verifiers judge a
    // finding, never whether verification runs — every finding is verified (B15).
    if (mode === "light") {
        return 1;
    }
    return ["high", "critical"].includes(severity) ? 3 : 1;
}
```
- **Sticky escalation to FULL (A7)** — a LIGHT-mode round that surfaces a HIGH/CRITICAL finding escalates the task to FULL immediately: the escalation is **sticky** (once FULL, always FULL — LIGHT is never re-selected), and the K counter resets to FULL's K=2 so convergence restarts under the stricter bar. The trigger is a provisional verdict upgrade — when a verifier raises a finding's `actionable_severity` to HIGH/CRITICAL mid-round, that finding is re-verified under FULL by the adversarial council, and the effective mode (`effective_mode` in the run state) persists across all subsequent rounds.
- **Accepted tradeoffs (policy, not a fourth bucket)** — `accepted_tradeoffs` is durable, cross-round POLICY. Entry: `{tradeoff_id, finding_id, rationale, owner}`; per **Cross-stage ID namespace**, `tradeoff_id` is stable and never re-minted, and `finding_id` is the canonical join key. Optional `inject_selector` is context only: finders do not suppress matches, and acceptance never matches selectors. Each round derives `accepted_this_round(findings, approved)` only from explicit orchestrator/user `{finding_id: tradeoff_id}` approvals validated against the registry; silently reject unknown/mismatched pairs (no error, warning, or observable rejection path). Acceptance suppresses ACTION only: per **LOW severity is still verified**, verification runs; findings stay in `real`, are reported/logged apart from it, visible, and nonblocking. Thus `accepted` is a policy overlay, not a fourth `real`/`borderline`/`dropped` verdict bucket (see **Convergence rule + termination**). Exclude it from convergence: `to_act = [f for f in real if f.id not in accepted]`; require `len(to_act) == 0`, never `len(real)`, so recurrence cannot reset K. Only the orchestrator/user may accept; reviewer/scope claims of acceptance are scope violations, not verdicts or policy changes.

```python
accepted_tradeoffs = [  # DURABLE registry — orchestrator/user POLICY; survives rounds
    {"tradeoff_id": "sec-plaintext", "finding_id": "sec:5", "rationale": "intentional: plaintext transport accepted for internal-only deployment", "owner": "user"},
]
def accepted_this_round(findings, approved):
    # approved = explicit {finding_id: tradeoff_id} from orchestrator/user this round
    registry_by_tid = {t["tradeoff_id"]: t for t in accepted_tradeoffs}
    accepted_ids = {t["finding_id"] for t in accepted_tradeoffs}  # persisted entries
    for fid, tid in approved.items():
        if tid in registry_by_tid and registry_by_tid[tid]["finding_id"] == fid:   # validate tradeoff_id exists and finding_id matches — reject unknown or mismatched
            accepted_ids.add(fid)
        # unknown tid or mismatched finding_id → silently rejected (not added)
    return {f["id"] for f in findings if f["id"] in accepted_ids}
accepted = accepted_this_round(findings, {})
to_act = [f for f in real if f["id"] not in accepted]  # exclude accepted from action AND convergence
# convergence checks len(to_act) == 0, NOT len(real) == 0
```

```js
const acceptedTradeoffs = [  // DURABLE registry — orchestrator/user POLICY; survives rounds
    { tradeoff_id: "sec-plaintext", finding_id: "sec:5", rationale: "intentional: plaintext transport accepted for internal-only deployment", owner: "user" },
];
function acceptedThisRound(findings, approved) {
    // approved = explicit {finding_id: tradeoff_id} from orchestrator/user this round
    const registryByTid = new Map(acceptedTradeoffs.map((t) => [t.tradeoff_id, t]));
    const acceptedIds = new Set(acceptedTradeoffs.map((t) => t.finding_id));
    for (const [fid, tid] of Object.entries(approved)) {
        if (registryByTid.has(tid) && registryByTid.get(tid).finding_id === fid) acceptedIds.add(fid);  // validate tradeoff_id exists and finding_id matches — reject unknown or mismatched
    }
    return new Set(findings.filter((f) => acceptedIds.has(f.id)).map((f) => f.id));
}
const accepted = acceptedThisRound(findings, {});
const toAct = real.filter((f) => !accepted.has(f.id));  // exclude accepted from action AND convergence
// convergence checks toAct.length === 0, NOT real.length === 0
```

Five cases: (1) **persisted canonical acceptance** — `sec:5` is in the registry, so it derives accepted every round (no re-approval) and is excluded from convergence; (2) **unknown tradeoff rejection** — a finding absent from both `approved` and the registry is NOT accepted and stays in `real`; (3) **to_act/convergence exclusion** — accepted findings drop out of `to_act` and out of the convergence count; (4) **unknown tradeoff_id rejection** — an approval whose `tradeoff_id` is not in the registry (e.g. `{"new:id": "unknown"}`) is silently rejected: the finding is NOT accepted and stays in `real`; (5) **mismatched pair rejection** — an approval whose `tradeoff_id` IS in the registry but whose `finding_id` does not match that entry's `finding_id` (e.g. `{"other:id": "sec-plaintext"}` where the registry maps `sec-plaintext` to `sec:5`, not `other:id`) is silently rejected: the finding is NOT accepted and stays in `real`.

- **Evidence registry (accepted facts, distinct from policy)** — Maintain durable `accepted_facts` beside, but distinct from, `accepted_tradeoffs`. Tradeoffs are POLICY (“risk accepted; won’t fix”); evidence-facts are evidence-backed advisor judgments that no risk exists. Store them separately or use a typed `kind` (`"policy"`/`"evidence"`); never conflate them because they answer different questions. Inject `accepted_facts` (EVIDENCE) into REFUTE/verifier prompts so verifiers weigh findings against proof rather than inherit a conclusion. Inject `accepted_tradeoffs` (POLICY) only into finder prompts; keep verifiers policy-blind because “won’t fix” context can bias Q2. Route advisor “not a risk” corrections through this registry per **Advisor corrections (captured via the evidence registry)**.

- **Advisor corrections (captured via the evidence registry)** — advisor input arrives mid-round, inline, and is one kind of evidence-fact: when the advisor says a finding is "NOT a risk, WITH evidence," record it in `accepted_facts` and inject it into the verifier's REFUTE prompt on the next round (A8 injection rule: evidence goes to the verifier, policy never does). Timing: the running round finishes as-is — the correction is reflected in the NEXT round's `accepted_facts`, so the registry update takes effect at the next round boundary (mid-round advisor → next-round registry). Reopens: an advisor correction is also a reopen trigger — if the advisor finds a defect in work already marked done, completion is NOT permanent: request/guide a goal reopen for that item, cancel its completion, and re-run its verification before it can converge again.

- **Multi-modal sweep** — parallel finders each searching a different way (by-container, by-content, by-entity, by-time), each blind to the others.
- **Completeness critic** — a final agent that asks "what's missing — modality not run, claim unverified, file unread?"; its answer is the next round.
- **Budget/count loops** — Python: `while len(bugs) < 10:`; JavaScript: `while (bugs.length < 10) { … }`. In Python, gate an explicit budget with `budget.total` and `budget.remaining()`; in JavaScript, use `await budget.total()` and `await budget.remaining()`. `log()` each round.
- **No silent caps** — if you bound coverage (top-N, no-retry, sampling), `log()` what you dropped; silent truncation reads as "covered everything" when it didn't.
- **Vacuous verification** — if a round surfaces 0 findings, the adversarial-verify step never runs; report "no findings to verify," NOT "passed verification." A gate that didn't fire is not a gate that passed.
- **Scope discipline for scanners** — give a review/slop scanner the EXACT changed-file list and "outside this list: one-line note only, never edit." Mark recent intended changes (a bug-fix or guard you just added) as in-scope-but-intentional so they aren't relitigated as slop. A scanner that flags untouched files or pre-existing code is scope creep, not a finding — re-prompt with the file list rather than chasing the noise.
- **Workspace stability guard** — DEFAULT, mandatory: content-hash scope pre/post fan-out, git-free; diff=mid-round edit→suspect evidence. Re-scan SAME owned-root/matcher scope, excluding logs/build; original-file-only misses creates/renames. Crash-safe existence/type/digest: `def file_digest(f): p = pathlib.Path(f); return "MISSING" if not p.exists() else ("DIR" if p.is_dir() else hashlib.sha256(p.read_bytes()).hexdigest()[:12])`; `digests = {f: file_digest(f) for f in <scope paths>}`; `rev = hashlib.sha256(repr(sorted(digests.items())).encode()).hexdigest()[:12]`; diff maps: created/deleted/modified. Drift: reverify paths + dependency/verification closure; unknown→rerun. FIRST audit/reverify drift TERMINAL: discard, STOP, report. Fan-out write=mixed snapshot; land expected fixes BEFORE audit (pre-map=baseline); no exemption.
- **Audit-only path (pure re-verify)** — For zero-implementation audits, use only read-only finders and verifiers: no implementation slices, edits, patches, or fixes; output only findings joined to verdicts. Claim only “verified the issues found within the provided scope,” never “complete audit” or “no other issues”; completeness needs a separate finder/critic phase (see **Completeness critic**). Apply **Workspace stability guard** (B1) and **Pinned-content review** (B3) in full; per the guard’s terminal-drift rule, discard and report any drifted round. Report joined findings as results, not Step 3 remediation (see SKILL.md audit/review exit). Acting on them requires a separate implementation DAG.

- **Functional/UI verification lane (browser QA)** — code review (adversarial verify) proves the CODE is correct; it does not prove a UI/feature change actually WORKS. For UI/feature changes, run a functional verification lane in the Step 3 quality loop as an additional round alongside (or after) the code-review round: drive the real surface with the browser tool (puppeteer/Chromium) — render, click, type, submit — and confirm the visual output with the visual-qa skill or `inspect_image`. Claim boundary: code review proves "the code is right," functional verify proves "it actually works" — BOTH are required for "done"; either alone is insufficient. Run the two rounds in parallel when the slices are independent, sequentially when the functional round depends on the review round's fixes.
- **Advisory/council overlap** — If the harness advisor performs inline adversarial verification, adding the DAG council duplicates verdict work, roughly doubling cost for no signal; in the 197k-token retro, duplication dominated cost and the council added zero findings. The advisor may replace the council only when it emits the council's complete per-finding Q1/Q2/Q3 contract: `original_claim_status`, `actionable_severity`, and `verification_confidence` (see **finder→verifier contract**). Otherwise retain the council as the only structured verdict source and pass advisor output to its finders/verifiers as evidence. This is a format, not independence, gate: contract-complete advisor verdicts enter the existing finding-ID join, Q2∧Q3 aggregation, and convergence pipeline but do not reduce the mode's vote weight. In FULL, HIGH/CRITICAL still require a 3–5-vote adversarial council, where the advisor counts as at most one vote; one advisor verdict may replace only single-vote verification (MEDIUM/LOW in FULL; every severity in LIGHT).

Scale to the ask: "find any bugs" → a few finders, single-vote verify. "thoroughly audit / be comprehensive" → larger finder pool, 3–5-vote adversarial pass, a synthesis stage.
</patterns>

<execution>
- Decompose the surface first; capture it in `todo` when it spans phases.
- Prefer `schema=` (per SKILL.md contract).
- After a fan-out returns, YOU own correctness: read the artifacts, run the gate, verify before acting. Subagents do the legwork; they don't get the last word.
- **Checkpoint discipline** — Commit one independently specified, independently verifiable change per atomic commit as soon as it passes; never let uncommitted edits accumulate across rounds. Without git, snapshot each verified change to a `local://` file as the checkpoint equivalent (see **No-git fallback**); the principle holds regardless. Tangled uncommitted edits are hard to recover: the last clean commit is the primary recovery point. Prefer rolling back one commit at a time, though reverting a range or restoring a known-good checkpoint is valid when an entire run is invalid.
- **Todo stability across turns** — Keep the task content stable — it IS the identifier: the harness targets tasks by exact content, not a separate ID. If you must reword a task, `init` a fresh list rather than trying to update by the old text. Embed any stable identifier you need IN the content string itself, and always `view` the latest todo list before mutating — a continuation turn may show a stale snapshot.
- **Model visibility** — A subagent's exact model is not exposed at runtime, so don't assert more than "harness default (assumed same)" from the roster alone; the precise model lives in the session JSONL's `model_change` events. The orchestrator can read those records to report which model each subagent actually ran: look under `~/.omp/agent/sessions/<workspace>/<session>/*.jsonl` for each subagent's `model_change` entries — the `resolvedModelIsFallback` field tells you whether the resolved model was a fallback. When reporting, distinguish the **specified agent type** (what the orchestrator asked for) from the **actual model** (what the session file shows), and note when a model is only inferred from the session file rather than observed live.
- Keep going until the task is closed — a returned fan-out is a step, not a stopping point.
- **quality_checks contract** — each Step 1 slice carries ≥1 quality_check: a shell command (e.g. `python -m pytest tests/test_parser.py`, `tsc --noEmit`) or an eval `agent(agent='reviewer', …)` call. Execution: run the command or agent; exit 0 = pass for shell commands; to_act == 0 (zero unaccepted real findings — accepted and borderline don't fail) = pass for reviewer calls; non-zero exit or to_act > 0 = fail. A failed check's findings enter the convergence loop as real findings (Q2/Q3 classified) — they are NOT separate from the review findings.
- **Node acceptance** — Accept/commit an implementation node only if (1) eval task agent output compiles/runs, (2) `quality_checks` pass (see **quality_checks contract**), and (3) eval finds `to_act == 0` (see **Convergence rule + termination**). On failure, spawn a fresh agent(agent='task', isolated=True) [or {isolated:true}] with the original implementation prompt PLUS the combined diagnostics/findings as feedback: compile/run diagnostics; failed shell checks as `{id: 'qc:<name>', file: '<quality-check>', title: 'quality_check failed: <command>', severity: 'high', detail: 'exit: <code>, stderr: <output>'}` (`high` is conservative initial severity pending Q2/Q3 verification); and review findings (`id`/`file`/`title`/`severity`/`detail`, plus the verdict's `reason`). Each fresh invocation counts against the two-retry bound. After 2 failed retries, fail node, skip dependents, and report unresolved failures. Never retry review/verification nodes; consume their verdict.
</execution>
</system-notice>
