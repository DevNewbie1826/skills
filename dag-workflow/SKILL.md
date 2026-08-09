---
name: dag-workflow
description: "Use for a task genuinely too big for one pass: decompose and cover in parallel via eval-based subagents (requires the `eval` tool — `parallel()`/`agent()`), apply independent/adversarial cross-checking before you commit, or take on scale one context can't hold. Triggers: parallelize, fan out, decompose this task, split work across agents, orchestrate subagents, big task, too large for one pass, broad sweep, large refactor, large migration, audit sweep, DAG, workflow. Do NOT use for a single edit, a quick lookup, or a task one agent can finish — do those directly."
---

# dag-workflow

Read [references/orchestration.md](references/orchestration.md) in full before Step 1. **You MUST follow its primitives and patterns at every step — fan out via `parallel()`, branch on `schema=`, adversarially verify before you commit. Fan out when the task clears the scale gate; a quick lookup, a single edit, or anything one agent finishes stays inline (see orchestration.md `<when>`).**
orchestration.md is sectioned (`<when>`, `<helpers>`, `<structure>`, `<patterns>`, `<execution>`). Read it in full on first use; on subsequent runs, skim the section headers and deep-read only the section your step needs — `<when>` for the scale gate, `<structure>` for schemas/examples, `<patterns>` for review/convergence patterns, `<execution>` for dispatch discipline. If the reference grows past ~400 lines, split `<patterns>` into its own file (deferred per project decision).

## Step 1 — Plan

Design one monolithic DAG workflow for the task. Follow orchestration.md. Steps 1–4 below are the **execution-slice** path (work with real cross-step dependencies). A **parallel review/sweep** is an edge-less DAG instead — one node per lens, empty `depends_on`, no slicing: keep step 1 (scope) and step 4 (per-lens `agent`/`skills`/`quality_checks`), skip the slice/`depends_on` steps (2–3).

1. Fan out parallel agents to define full task scope — every file, subsystem, call site.
2. Break the task into small slices.
3. Record `depends_on` between slices. Parallelism is derived from `depends_on` at execution time.
4. Per slice, assign: `agent` (who runs it — see [references/agents.md](references/agents.md)), `skills` (skill names to inject into the prompt), `quality_checks` (≥1 per slice, consumed by Step 3).

A **single-slice** task is the third path — the work is one cohesive change (a single file or a tightly related cluster) where slicing would be ceremony. Confirm it at the scope/scale gate: larger than a quick lookup or single edit (those stay inline), yet with no real cross-step dependencies to record — decomposition would invent boundaries, not find them. The single-slice path omits decomposition only:

1. Keep step 1 (scope) and step 4 (per-slice `agent`/`skills`/`quality_checks`); skip the slice and `depends_on` steps (2–3) — one node covers the whole change.
2. Dispatch **one** implementation agent via the session `task` tool (Step 2 delegation discipline: target files, acceptance criteria, skills, non-goals — the orchestrator never implements inline).
3. Verify through the normal machinery — Step 2 eval council (`agent(agent='reviewer', …)`/`parallel()`) refutes the single slice's output, then Step 3 quality loop runs its `quality_checks` plus the integrated whole-output pass.

Single-slice is a shortcut in **decomposition** only, never in **verification**: one session task agent implements, eval agents verify, and the same agent never plays both roles.

A **small task** — roughly ≤3 files and ≤50 lines of change — is the fourth path: it shortens the whole loop, not just decomposition. The single-slice path still runs the full machinery (Step 2 eval council, Step 3 K-round loop); a small task skips most of it:

1. **Skip decomposition entirely** — no slice table, no `depends_on`. Confirm it at the scope/scale gate, then dispatch one session task agent with the Step 2 delegation discipline (target files, acceptance criteria, skills, non-goals).
2. **Scope with targeted search, not a completeness fan-out** — two or three focused searches (`grep` + `read` on the touched files and their call sites) are faster and more accurate than a full completeness sweep for a small task: the sweep exists to catch unknown unknowns in broad work, and a small change has few. Run targeted first; fan out only if a search reveals an unexpected surface.
3. **One completeness sweep round and one review pass** — collapse the Step 3 loop to a single round: run the slice's `quality_checks` once, then one independent reviewer (eval `agent(agent='reviewer', …)`) refutes the whole output. That single pass stands in for both the council and the K-round loop.

The small path pairs with **LIGHT mode (K=1)** from the verification state contract: a small, low-risk task is the natural light-mode candidate — single-vote verify for every finding, no council, one clean round converges. Escalate to FULL only if a HIGH/CRITICAL finding surfaces (sticky escalation, see orchestration.md). If a small task keeps needing full council scrutiny, it is not actually small. If a task qualifies as both single-slice and small, the small-task path takes precedence — it is the more specific shortcut and subsumes the single-slice path's one-agent shape with a lighter verification loop.

## Step 2 — Execute

Execute the DAG. At each decision run a council-of-subagents (independent reviewers in parallel) and keep only what survives an adversarial refute. For a Q1-only `REFUTE_SCHEMA` vote, default to `refuted` when unsure; for a structured `VERDICT_SCHEMA` verdict, encode uncertainty as `verification_confidence="low"` — never as claim status. Follow orchestration.md.

**Delegation discipline.** Implementation — writing code, editing files — is delegated, never done inline by the orchestrator: dispatch every implementation node via the session `task` tool. Only orchestrator-side adjustments that don't touch the deliverable code (a prompt fix, a config tweak, a quick lookup) stay inline — implementation that writes or edits deliverable code always goes through the session task tool. Delegation prompts are explicit: target files, acceptance criteria, skills to read, non-goals — no vague "implement this" handoffs. The subagent never has the last word: the orchestrator verifies each result (adversarial review, compile/run check) before committing it.

**Eval is evaluation-only.** eval `agent()`/`parallel()` exist to verify, review, council, and sweep — never to implement. Implementation — writing or editing code — goes through the session `task` tool only. eval's `agent(agent='task')` is the eval-internal general-purpose worker for analysis and multi-step verification that needs tool access, not for code-editing implementation. Handoff: a session task agent implements, then an eval agent verifies (`agent(agent='reviewer', …)`/`parallel()`); the same agent never plays both roles.

1. Dispatch each ready node (deps satisfied) by role: implementation nodes via the session `task` tool; planning/review/verification/council nodes via eval `agent()`/`parallel()`. Inject upstream outputs and assigned skill names into the prompt (instruct the subagent to read and follow those skills). Run independent nodes concurrently. The same agent never plays both roles in one node.
2. Results that survive the council are committed. Results that get refuted retry with feedback (bounded). Unconverged nodes fail — their dependents are skipped.

## Step 3 — Quality loop

Outside the DAG. Follow orchestration.md.

1. For code, establish green regression-test baseline first.
2. One round = run every slice's `quality_checks` once, then one integrated whole-output pass across all slices (cross-slice consistency, duplication, conflicts, overall slop).
3. Classify each finding from its verdict (not by feel): **real** = actionable & confirmed (`actionable_severity != "none"` and `verification_confidence != "low"`); **borderline** = verifier uncertain (`verification_confidence == "low"`). Resolve real findings before the next round; record borderlines. Accepted tradeoffs (orchestrator/user policy) stay real but skip remediation — see orchestration.md for the accepted registry.
4. Repeat until **K consecutive rounds surface zero unaccepted real findings** (default K=2). Borderlines and accepted findings don't reset K. If the user specified N rounds, run exactly N and stop, reporting unresolved findings.
5. Report each round's output. Never declare done unless the final round surfaced zero unaccepted real findings.
