---
name: dag-workflow
description: "Use for a task genuinely too big for one pass: decompose and cover in parallel via eval-based subagents (requires the `eval` tool — `parallel()`/`agent()`), apply independent/adversarial cross-checking before you commit, or take on scale one context can't hold. Triggers: parallelize, fan out, decompose this task, split work across agents, orchestrate subagents, big task, too large for one pass, broad sweep, large refactor, large migration, audit sweep, DAG, workflow. Do NOT use for a single edit, a quick lookup, or a task one agent can finish — do those directly."
---

# dag-workflow

Read [references/orchestration.md](references/orchestration.md) in full before Step 1. **You MUST follow its primitives and patterns at every step — fan out via `parallel()`, branch on `schema=`, adversarially verify before you commit. Fan out when the task clears the scale gate; a quick lookup, a single edit, or anything one agent finishes stays inline (see orchestration.md `<when>`).**

## Step 1 — Plan

Design one monolithic DAG workflow for the task. Follow orchestration.md. Steps 1–4 below are the **execution-slice** path (work with real cross-step dependencies). A **parallel review/sweep** is an edge-less DAG instead — one node per lens, empty `depends_on`, no slicing: keep step 1 (scope) and step 4 (per-lens `agent`/`skills`/`quality_checks`), skip the slice/`depends_on` steps (2–3).

1. Fan out parallel agents to define full task scope — every file, subsystem, call site.
2. Break the task into small slices.
3. Record `depends_on` between slices. Parallelism is derived from `depends_on` at execution time.
4. Per slice, assign: `agent` (who runs it — see [references/agents.md](references/agents.md)), `skills` (skill names to inject into the prompt), `quality_checks` (≥1 per slice, consumed by Step 3).

## Step 2 — Execute

Execute the DAG. At each decision run a council-of-subagents (independent reviewers in parallel) and keep only what survives an adversarial refute. For a Q1-only `REFUTE_SCHEMA` vote, default to `refuted` when unsure; for a structured `VERDICT_SCHEMA` verdict, encode uncertainty as `verification_confidence="low"` — never as claim status. Follow orchestration.md.

1. Dispatch each ready node (deps satisfied) via `agent()` with its assigned `agent`. Inject upstream outputs and assigned skill names into the prompt (instruct the subagent to read and follow those skills). Run independent nodes concurrently.
2. Results that survive the council are committed. Results that get refuted retry with feedback (bounded). Unconverged nodes fail — their dependents are skipped.

## Step 3 — Quality loop

Outside the DAG. Follow orchestration.md.

1. For code, establish green regression-test baseline first.
2. One round = run every slice's `quality_checks` once, then one integrated whole-output pass across all slices (cross-slice consistency, duplication, conflicts, overall slop).
3. Classify each finding from its verdict (not by feel): **real** = actionable & confirmed (`actionable_severity != "none"` and `verification_confidence != "low"`); **borderline** = verifier uncertain (`verification_confidence == "low"`). Resolve real findings before the next round; record borderlines.
4. Repeat until **K consecutive rounds surface zero real findings** (default K=2). Borderlines don't reset K. If the user specified N rounds, run exactly N and stop, reporting unresolved findings.
5. Report each round's output. Never declare done unless the final round surfaced zero real findings.
