---
description: "How to run multi-agent work on omp: workpool() first for independent items, agent() handles for dependency-coupled calls, the eval helpers, and the pool workflow. Read first, with ultrathink.md."
---

> Rendered from omp 18.18.1 `src/prompts/system/workflow-notice.md` by `renderWorkflowNotice` (`src/modes/magic-keywords.ts`) with this host's settings, all omp defaults: taskBatch, scoutAvailable, evalTools, py and js true; freshAgents and perCallModel false. To re-render, call that function with these values and keep this header.

<system-notice>
When using this skill → deterministic multi-subagent workflow. Default to `workpool()` for 2+ independent items; use individual `agent()` handles only for dependency-coupled or schema-returning calls.

<when>
Use for broad research, reviews, migrations, adversarial coverage, and open-ended work lists. Quick lookup/single edit: direct; no agents. Scout inline FIRST — scope files, call sites, and contracts before creating the pool.

Pool-first phases:
- **Understand**: queue subsystem readers → collect results → synthesize
- **Review**: queue one item per lens/file → collect results → verify survivors
- **Migrate**: discover sites → queue file-disjoint transforms → verify once
- **Research**: queue modalities/sources → deep-read hits → synthesize
- **Design**: queue independent proposals/judges → choose and integrate
</when>

<helpers>
State persists across `eval` calls. Every call provides:

- `workpool(agent=None, *, name=None, context=None, tools=None)`: pool of keep-alive workers, at most live `task.maxConcurrency` of them (0 = unlimited). Items dispatch in push order: to the idle worker using the least of its context window, else to a new worker while under the limit, else onto a busy worker's queue, round-robin. A worker keeps its conversation across items, so a later item sees everything its worker did before; items queued on a busy worker reach it together as one batch when it frees up. Reuse happens only once items outnumber the limit or one arrives while a worker is idle. `.push(*items)` returns item ids; `.status()` reports counts/workers; `.peek()` returns a non-consuming batch snapshot; `.close()` drops queued work. JS: `await workpool(agent, { name, context, tools })`; every pool method is async (`await pool.push(…items)`).
  - The pool name is its background job id and label. Push all items while it is active; its first full drain settles and closes that pool job. New phase/wave after drain → create a new named pool.
  - Results auto-deliver. Completely blocked? Leave `eval` and call the `wait` tool (not kernel `wait()`); NEVER poll.
- `agent(prompt, *, agent=None, label=None, schema=None, schema_mode=None, isolated=None, apply=None, merge=None, tools=None)`: immediate `AgentHandle`; use for a small fixed dependency graph or when the parent needs validated `schema` data. `.wait()` returns text/data; `.handle` is `agent://<id>`. Unwaited results auto-deliver. JS: `await agent(prompt, { agent, label, schema, schemaMode, isolated, apply, merge, tools })`; without `await`, `.id`/`.handle` are undefined; handle methods are async (`await h.wait()`).
- `completion(prompt, *, model="default", system=None, schema=None)`: immediate `CompletionHandle` for a tool-free one-shot call. Tiers: `"smol"`, `"default"`, `"slow"`. JS: `await completion(prompt, { model, system, schema })`; handle methods are async (`await h.wait()`).
- `await judge(state, questions)`: typed `choice`/`bool`/`score` questions over one state → `{id: answer}` with probabilities. Cheaper than `completion()` for classification.
- `judge_batch(states, questions, *, concurrency=32, retries=1, min_ok=1, intent=None)`: the same questions over many states, run by the host so it outlives the cell. Set nonempty `intent` for its progress/job label (default `"Judging"`). Returns a `JudgmentBatch` at once; per cell pull a bounded slice with `await b.drain(timeout)` (or `async for k, item in b.drain_iter(timeout)`), read `b.status()`/`b.results()`/`b.failed()`, and `b.close()` when done. Item failures are `item.error`, never exceptions; `b.id` is a background job id (results auto-deliver). Never loop `judge()` over a list. JS: `await judgeBatch(states, questions, { concurrency, retries, minOk, intent })`; `await b.drain({ timeout })` / `for await (const [k, item] of b.drainIter({ timeout }))`; every batch method except `drainIter` is async.
- `wait(handles, timeout=None, *, raise_errors=True)`: ordered barrier for agent/completion handles only; `raise_errors=False` keeps an error in its slot. JS: `await wait(handles, { timeout, raiseErrors })`.
- `@tool`: kernel-local tool exposed via `tools`. Use for shared caches, dedup sets, scoring, or structured accumulation across pool workers; calls execute in YOUR kernel and a raised exception returns to the caller without killing it. JS: `tool(fn, { name, description, parameters })`.
- `log(message)`: progress line. `phase(title)`: status-tree phase.
- `budget`: `budget.total` / `budget.spent()` / `budget.remaining()`. User `+Nk` = advisory; `+Nk!` = hard. JS: `await budget.total()` / `await budget.spent()` / `await budget.remaining()`.
</helpers>

<pool-workflow>
1. Scope the full independent work list before spawning.
2. Create ONE explicitly named pool per phase.
3. Push every known item in one cell; later discoveries MAY be pushed while the pool job is still running.
4. Continue useful local work. Results auto-deliver.
5. Completely blocked? Leave `eval` and call the `wait` tool (not kernel `wait()`); never poll.
6. Read every batch result; YOU verify and integrate.

**Python:**
```python
phase("Review")
review = workpool("scout", name="review", context="Return evidence with exact paths; do not edit.")
review.push(*[
    "Review authentication correctness",
    "Review authorization boundaries",
    "Review cancellation and cleanup",
    "Review performance regressions",
])
print(review.name)   # background job id; results auto-deliver
```
**JavaScript:**
```js
phase("Review");
const review = await workpool("scout", {
    name: "review",
    context: "Return evidence with exact paths; do not edit.",
});
await review.push(
    "Review authentication correctness",
    "Review authorization boundaries",
    "Review cancellation and cleanup",
    "Review performance regressions",
);
print(review.name); // background job id; results auto-deliver
```
Need a snapshot without consuming/delivering results? `review.peek()`. Need activity counts? `review.status()`. JS: `await` both.
</pool-workflow>

<dependencies>
Use handles only when work item B requires A's exact output before B can be written:

```python
spec = agent("Extract the protocol", agent="scout", schema=SPEC).wait()
impl = agent(f"Implement this protocol: {spec}")
result = impl.wait()
```
```js
const specHandle = await agent("Extract the protocol", { agent: "scout", schema: SPEC });
const spec = await specHandle.wait();
const impl = await agent(`Implement this protocol: ${JSON.stringify(spec)}`);
const result = await impl.wait();
```
Fixed independent handles are acceptable when each result must be returned directly into the kernel as structured data. Otherwise use a pool.
</dependencies>

<patterns>
- **Adversarial verify**: pool one REFUTE task per claim/lens; retain only evidence-backed survivors.
- **Perspective-diverse review**: distinct correctness/security/perf/reproduction items; NEVER clone one vague prompt.
- **Judge panel**: pool proposals, then a second named pool scores them after the first pool settles.
- **Loop-until-dry**: push newly discovered items while the pool remains active; dedup against all SEEN.
- **Multi-modal sweep**: queue by-container/by-content/by-entity/by-time items.
- **Completeness critic**: final pool item asks what modality/file/claim remains unchecked.
- **No silent caps**: if sampling/top-N drops work, `log()` what was omitted.

Scale: `"find any bugs"` → small pool. `"thoroughly audit"` → broad pool + a separate adversarial verification pool.
</patterns>

<execution>
- Multi-phase work: capture in `todo`.
- Each pool item: self-contained target, change/read scope, acceptance.
- Same-file mutation? One worker owns it; serialize shared boundaries.
- Pool output is evidence, not truth. Read artifacts, gate findings, run final verification yourself.
- Continue until closed; a drained pool is a phase boundary, not task completion.
</execution>
</system-notice>
