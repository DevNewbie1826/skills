---
name: dag-workflow
description: "Use for any nontrivial task that benefits from implementation delegation or independent verification — from a single focused change to a large migration: dispatch eval-based subagents (requires the eval tool), apply independent/adversarial cross-checking before you commit. Triggers: parallelize, fan out, decompose this task, split work across agents, orchestrate subagents, big task, too large for one pass, broad sweep, large refactor, large migration, audit sweep, DAG, workflow. Do NOT use for a trivial edit, a quick lookup, or a one-step answer — work needing no verification machinery"
---

# dag-workflow

Read [references/orchestration.md](references/orchestration.md) in full before Step 1. **You MUST follow its primitives and patterns at every step — fan out via `parallel()`, branch on `schema=`, adversarially verify before you commit. Fan out when the task clears the scale gate; trivial work stays inline; everything else follows the Routing decision tree below (see orchestration.md `<when>` for the scale gate).**
orchestration.md is sectioned (`<when>`, `<helpers>`, `<structure>`, `<patterns>`, `<execution>`). Read in full on first use; on later runs, skim headers and deep-read only the relevant section.

## Routing — pick a path before Step 1

Ask in order:
1. **Inline** — trivial work needing no verification machinery (quick lookup, single trivial edit, one-step answer). Not "anything one agent finishes" — single-slice also uses one agent but needs the quality loop.
2. **Review/sweep** — analysis-only (finder + verifier, zero implementation): produces findings, not code changes. Work-kind branch, orthogonal to size.
3. **Implementation** — size-based, in precedence order: small > single-slice > full-DAG:
   - **Small** (≤3 files, ≤50 lines, low-risk) → LIGHT mode, K=1; if not low-risk, use single-slice or full-DAG with FULL mode
   - **Single-slice** (one cohesive change, no cross-step deps)
   - **Full-DAG** (multi-slice — real cross-step dependencies get `depends_on`; multiple independent slices with no cross-step dependencies route here too, with empty `depends_on` and parallelism derived at execution time)

## Step 1 — Plan

Design one monolithic DAG workflow for the task. Follow orchestration.md. Steps 1–4 below are the **execution-slice** path (work with real cross-step dependencies). A **parallel review/sweep** is an edge-less DAG instead — one node per lens, empty `depends_on`, no slicing: keep step 1 (scope) and step 4 (per-lens `agent`/`skills`/`quality_checks`), skip the slice/`depends_on` steps (2–3).

1. Fan out parallel agents to define full task scope — every file, subsystem, call site (scout inline first per orchestration.md `<when>`).
2. Break the task into small slices at boundaries that maximize parallelism — the goal is the SHORTEST critical path (longest dependency chain), not the fewest edges: a large zero-dependency slice still bottlenecks a wave if it's the only node in it. Cut at stable interface seams (type signatures, API contracts, file boundaries) where one slice's output feeds another's input without shared mutable state. Preserve real data/state dependencies; eliminate artificial ones by widening a slice or introducing a preemptive interface slice. Balance slice sizes so no single slice straggles behind a parallel wave. When two slices would edit the same file, merge them or pin the shared surface as a preemptive interface slice (see orchestration.md Parallel writes).
3. Record `depends_on` between slices. The orchestrator runs all ready nodes (deps satisfied) concurrently each wave; fewer edges on the critical path means fewer waves and more parallelism.
4. Per slice, assign: `agent` (eval agent type that RUNS this node — `task` for implementation, `reviewer` for review/verification — see [references/agents.md](references/agents.md)), `skills` (skill names to inject into the prompt), `quality_checks` (≥1 per slice, consumed by Step 3) (a shell command or eval reviewer call; pass = exit 0/zero unaccepted real findings (to_act==0), fail = findings enter the convergence loop — see orchestration.md).

A **single-slice** task is the third path — the work is one cohesive change (a single file or a tightly related cluster) where slicing would be ceremony. Confirm it at the scope/scale gate: larger than trivial inline work (see Routing), yet with no real cross-step dependencies to record — decomposition would invent boundaries, not find them. The single-slice path omits decomposition only:

1. Keep step 1 (scope) and step 4 (per-slice `agent`/`skills`/`quality_checks`); skip the slice and `depends_on` steps (2–3) — one node covers the whole change.
2. Dispatch **one** implementation agent via eval `agent(agent='task')` (Step 2 delegation discipline) — only after the pre-implementation baseline from the end of Step 1 is established.
3. Verify through the normal machinery — Step 2 eval verification (`agent(agent='reviewer', …)`/`parallel()`) refutes the single slice's output, then Step 3 quality loop runs its `quality_checks` plus the integrated whole-output pass.

Single-slice is a shortcut in **decomposition** only, never in **verification**: one eval task agent implements, eval agents verify, and the same agent never plays both roles.

A **small task** — roughly ≤3 files and ≤50 lines of change — is the fourth path: it shortens the whole loop, not just decomposition. The single-slice path still runs the full machinery (Step 2 eval verification, Step 3 K-round loop); a small task skips most of it:

1. **Scope with targeted search, not a completeness fan-out** — two or three focused searches (`grep` + `read` on the touched files and their call sites) are faster and more accurate than a full completeness sweep for a small task: the sweep exists to catch unknown unknowns in broad work, and a small change has few. Run targeted searches first; fan out only if a search reveals an unexpected surface.
2. **Skip decomposition entirely** — no slice table, no `depends_on`. Confirm it at the scope/scale gate. Record the one node's skills and quality_checks before dispatch, then dispatch one eval `agent(agent='task')` (per Step 2 delegation discipline).
3. One reviewer per round (not a council) — run the slice's `quality_checks`, then one independent eval reviewer (`agent(agent="reviewer", ...)`) refutes the whole output. LIGHT K=1 means repeat this single-reviewer round until one CLEAN round (`to_act==0`): if the reviewer confirms a real finding (any severity), remediate and re-run. Escalation to FULL only triggers on HIGH/CRITICAL.

The small path pairs with **LIGHT mode (K=1)** from the mode-state contract: a small, low-risk task is the natural light-mode candidate — single-vote verification for every finding, no council, one clean round converges. Escalate to FULL only if a HIGH/CRITICAL finding surfaces (sticky escalation, see orchestration.md).

**Pre-implementation baseline:** For code tasks, establish a green regression-test baseline NOW (before Step 2 dispatches any implementation). A red baseline observed after implementation cannot distinguish pre-existing failures from regressions. If the baseline is already red, STOP and report the blocker — do not dispatch implementation against a broken baseline.

## Step 2 — Execute

Execute the DAG. At each decision, verify via the mode-appropriate adversarial pass — FULL mode uses a multi-vote council for HIGH/CRITICAL findings and single-vote verification for MEDIUM/LOW; LIGHT mode uses single-vote verification for all findings (see orchestration.md vote_count). Keep only findings that survive refutation. For a Q1-only `REFUTE_SCHEMA` vote, default to `refuted` when unsure; for a structured `VERDICT_SCHEMA` verdict, encode uncertainty as `verification_confidence="low"` — never as claim status. Follow orchestration.md.

**Delegation discipline.** Nontrivial implementation — writing deliverable code, editing deliverable files — is delegated, never done inline by the orchestrator: dispatch every implementation node via eval `agent(agent='task')` (trivial edits like a typo fix or a one-line config change are exempt per Routing Inline). Only orchestrator-side adjustments that don't touch the deliverable code (a prompt fix, a config tweak, a quick lookup) stay inline. Delegation prompts are explicit: target files, acceptance criteria, skills to read, non-goals — no vague "implement this" handoffs. The subagent never has the last word: the orchestrator verifies each result (adversarial review, compile/run check) before committing it.

**Eval is the execution engine.** All delegated work — implementation, finder, verifier, review, council, and sweep — runs through eval `agent()` calls; no external subagent mechanisms. Orchestrator-side routing, searches, baselines, and shell gates remain direct. Implementation runs via `agent(agent='task')`, verification via `agent(agent='reviewer')`; the same agent never plays both roles.

1. Dispatch each ready node (deps satisfied) by role (per Step 2 delegation discipline): implementation via eval `agent(agent='task')`, planning/review/verification/council via eval `agent(agent='reviewer')`/`parallel()`; security-lens review via eval `agent(agent='security-reviewer')` (see agents.md). Inject upstream outputs and assigned skill names into the prompt. Run independent nodes concurrently. The same agent never plays both roles in one node.
2. Results that survive the eval verification are committed. Implementation nodes that fail ANY acceptance gate (compile/run, quality_checks, or review) retry with combined diagnostics/findings as feedback (up to 2 retries). Review/verification nodes are single-attempt — their verdicts are consumed as-is; a crashed or invalid review node blocks the Step 2→3 gate. Unconverged nodes fail — their dependents are skipped. Node acceptance = ALL gates pass (compile + quality_checks + to_act==0); retry limit is 2, with findings as feedback; see orchestration.md.

## Step 3 — Quality loop

Outside the DAG. Follow orchestration.md.

**Step 2→3 gate:** Enter Step 3 only after ALL required DAG nodes are accepted; if any required node FAILED after retries are exhausted, STOP — report the failed nodes and unresolved findings; never quality-check incomplete work. One-node paths (single-slice/small) pass when that node is accepted; review/sweep, when all required finder/verifier/synthesis nodes return structured output (findings/verdicts) — a crashed or empty node blocks Step 3.

**Audit/review exit (replaces items 1–5 for review/sweep paths):** For review/sweep paths (zero implementation), canonical findings joined with their verifier verdicts are reported — items 1–5 do NOT apply. Instead, each convergence round runs: (1) per-lens quality_checks, (2) integrated synthesis (cross-lens consistency/coverage), (3) completeness critic (what's unverified?). Each subsequent review round turns the prior critic's uncovered gaps into new finder prompts. New findings per round are deduped against the cumulative SEEN set. Convergence = K consecutive rounds surfacing zero NEW findings (default K=2); if the user specified N rounds, run exactly N and stop. Findings are never remediated inline — acting on them starts a SEPARATE implementation DAG.

1. Confirm the green regression-test baseline (established at Step 1→2 transition) still passes.
2. One round = run every slice's `quality_checks` once, then one integrated whole-output pass across all slices (cross-slice consistency, duplication, conflicts, overall slop).
3. Classify each finding from its verdict (not by feel): **real** = actionable & confirmed (`actionable_severity != "none"` and `verification_confidence != "low"`); **borderline** = verifier uncertain (`verification_confidence == "low"`). Resolve real findings before the next round; record borderlines. Accepted tradeoffs (orchestrator/user policy) stay real but skip remediation — see orchestration.md for the accepted registry.
4. Repeat until **K consecutive rounds surface zero unaccepted real findings** (default K=2). Borderlines and accepted findings don't reset K. If the user specified N rounds, run exactly N and stop, reporting unresolved findings.
5. Report each round's output. Never declare done unless the final round surfaced zero unaccepted real findings.
