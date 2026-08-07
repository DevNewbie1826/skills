---
name: dag-workflow
description: "Use for a task genuinely too big for one pass: decompose and cover in parallel via eval-based subagents (requires the `eval` tool — `parallel()`/`agent()`), apply independent/adversarial cross-checking before you commit, or take on scale one context can't hold. Triggers: parallelize, fan out, decompose this task, split work across agents, orchestrate subagents, big task, too large for one pass, broad sweep, large refactor, large migration, audit sweep, DAG, workflow. Do NOT use for a single edit, a quick lookup, or a task one agent can finish — do those directly."
---

# dag-workflow

Read [references/orchestration.md](references/orchestration.md) in full before Step 1. **You MUST follow its primitives and patterns at every step — fan out via `parallel()`, branch on `schema=`, adversarially verify before you commit. Never go inline when fanning out is possible.**

## Step 1 — Plan

Design full agentic one monolithic DAG workflow for the task. Follow orchestration.md.

1. Fan out parallel agents to define full task scope — every file, subsystem, call site.
2. Break the task into small slices.
3. Record `depends_on` between slices. Parallelism is derived from `depends_on` at execution time.
4. Per slice, assign: `agent` (who runs it — see [references/agents.md](references/agents.md)), `skills` (skill names to inject into the prompt), `quality_checks` (≥1 per slice, consumed by Step 3).

## Step 2 — Execute

Execute the DAG. At each decision run a council-of-subagents (independent reviewers in parallel) and keep only what survives an adversarial refute — default to refuted when unsure. Follow orchestration.md.

1. Dispatch each ready node (deps satisfied) via `agent()` with its assigned `agent`. Inject upstream outputs and assigned skill names into the prompt (instruct the subagent to read and follow those skills). Run independent nodes concurrently.
2. Results that survive the council are committed. Results that get refuted retry with feedback (bounded). Unconverged nodes fail — their dependents are skipped.

## Step 3 — Quality loop

Outside the DAG. Follow orchestration.md.

1. For code, establish green regression-test baseline first.
2. One round = run every slice's `quality_checks` once, then one integrated whole-output pass across all slices (cross-slice consistency, duplication, conflicts, overall slop).
3. Resolve every finding before the next round.
4. Repeat until zero findings. If user specified N rounds, run exactly N and stop, reporting unresolved findings.
5. Report each round's output. Never declare done unless the final round surfaced zero findings.
