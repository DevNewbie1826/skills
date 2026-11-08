Read this when you define, check, run, recover or resume any of the flow's three graphs (context, build, verify); SKILL.md, The three graphs, routes here at stage 1.

# dag-workflow: running the three graphs

Every phase of this flow runs as a dependency graph: a definition of nodes and the edges that order them, launched in waves, closed by reducing verified outputs into the phase's checkpoint. This file holds the discipline those graphs share: how they are defined and checked before launch, how work crosses through handoff files, how a running graph is run and supervised on omp, and how it is picked back up after a death. The stage files name each graph's own nodes; the rules for running any graph are here.

## One graph per phase

A graph covers exactly one phase: the unit the flow checkpoints. In this flow the phases are collect (the context graph),
build and each round's fix (the build graph), and verify_lane (the verify graph). Everything that phase will need and that
can already be foreseen goes into the graph before the first node starts: the slices to read, the checks on what they
found, the reducer that merges them. Not yet knowing what an upstream node will report is no reason to open a second graph;
the downstream node reads that report from its handoff file. A new phase gets a new graph.

- Changing a node's definition after launch invalidates that node and every node downstream of it, and nothing else.
  Finished nodes upstream or on other branches keep their results.
- A graph never carries a goal of its own. The run's one goal (SKILL.md, The stage map) owns the objective and the
  success criteria; the graph's state tracks nodes only.
- A graph that would mix two phases (for example, building and judging the build) is two graphs: the judging graph
  starts from the first graph's handoff files once that graph has settled.

## Before launch: the graph checks

The lead runs these checks on the definition and launches nothing until every one passes:

1. Every node id is unique; a duplicate id is a definition error, never an overwrite.
2. Every id named in a node's dependencies exists in the same graph.
3. There is no cycle.
4. No two nodes that can run at the same time have overlapping write scopes. Shared files get one owner, or an edge
   that orders the writers.
5. Every node names an acceptance check with one binary observable, and every node names the handoff file it writes.
6. A graph that changes code or docs ends in verification nodes that depend on every producer.
7. Every edge stands for a consumed output or a real write ordering. An edge that orders without consuming slows the
   graph and hides the true dependencies.
8. When every node of one wave would depend on every node of the previous wave, one review or reduce node sits between
   the waves instead of every-to-every edges; a branch that consumes only part of a wave depends only on that part.

```js
function checkGraph(nodes) {
  const ids = new Set();
  for (const n of nodes) {
    if (ids.has(n.id)) throw new Error(`duplicate node id: ${n.id}`);
    ids.add(n.id);
  }
  for (const n of nodes) {
    for (const d of n.deps) if (!ids.has(d)) throw new Error(`${n.id} depends on missing node ${d}`);
    if (!n.out || !n.accept) throw new Error(`${n.id} lacks a handoff file or an acceptance check`);
  }
  const byId = new Map(nodes.map((n) => [n.id, n]));
  const state = new Map();
  const visit = (id, path) => {
    if (state.get(id) === "done") return;
    if (state.get(id) === "open") throw new Error(`cycle: ${[...path, id].join(" -> ")}`);
    state.set(id, "open");
    for (const d of byId.get(id).deps) visit(d, [...path, id]);
    state.set(id, "done");
  };
  for (const n of nodes) visit(n.id, []);
  const ancestors = (id, seen = new Set()) => {
    for (const d of byId.get(id).deps) if (!seen.has(d)) { seen.add(d); ancestors(d, seen); }
    return seen;
  };
  for (const a of nodes) for (const b of nodes) {
    if (a.id >= b.id || ancestors(a.id).has(b.id) || ancestors(b.id).has(a.id)) continue;
    const shared = a.writes.filter((w) => b.writes.includes(w));
    if (shared.length) throw new Error(`${a.id} and ${b.id} can run together and both write ${shared.join(", ")}`);
  }
  return true;
}

checkGraph([
  { id: "read-code", deps: [], writes: ["/tmp/run/read-code.md"], out: "/tmp/run/read-code.md", accept: "file has a Findings section" },
  { id: "read-history", deps: [], writes: ["/tmp/run/read-history.md"], out: "/tmp/run/read-history.md", accept: "file lists commits" },
  { id: "reduce", deps: ["read-code", "read-history"], writes: ["/tmp/run/collect.md"], out: "/tmp/run/collect.md", accept: "no source left unnamed" },
]);
```

## Handoff files

An edge orders; it never carries data. Two nodes exchange work through a handoff file at an absolute path the lead assigns: the producer writes it, the consumer opens it and checks it before using anything in it. The edge says who must wait; the file says what crosses. An edge is never justified by a shared topic or by a hope that two nodes will agree.

**What crosses an edge, and what does not.**

- Data never travels in a prompt, in a worker's memory, or in the lead's summary. The path is the interface: a fact a consumer needs lives in a file the consumer can open.
- A finished dependency proves neither that its handoff exists nor that it is correct. "Done" describes the worker's turn, not the artifact; the consumer's own read is the only evidence that the file is usable.
- A missing file, an unreadable file, a missing required section, a file over its bound, or a fact with no source anchor is a failure of the consumer's input. The consumer records `BLOCKED: <absolute path>` and names the failed check beside it; it never guesses the missing content, accepts the producer's final message in place of the file, or reads a sibling's output instead.
- A dependency counts as complete only after its handoff passes that check. The consumer's first act is the check, not the work.

**The producer names the path, the sections, and the bound.** The producer's prompt fixes the file before the node starts:

- the exact absolute path it writes, under the evidence dir outside the worktree, with no glob, no directory-only target, and no "somewhere in the evidence dir";
- the required section headings, in order, each with the facts it must hold;
- a size bound in bytes or lines, so one consumer's read stays bounded however much the producer found;
- the evidence and source anchors each fact needs: the command and its output, or the file and line range, so the consumer can re-check a fact without re-running the producer;
- the owned files. The handoff path is one of them, and SCOPE permits no write outside the node's declared set.

A producer that writes the right facts to the wrong path, or writes outside its owned set, has failed even when its report reads well.

**The consumer names the same literal path.** The consumer's prompt repeats the producer's path as the same literal string. It is copied, never retyped from memory or rebuilt by joining a directory with a guessed file name; a path that is "the same in spirit" is a different path.

The consumer also states which facts it uses: the sections, and inside them the specific rows or anchors, so it reads what it needs and no more. Its first check is binary:

- the file opens at that path;
- every required section is present and in order;
- the size is at or under the bound;
- every fact the consumer uses carries a source anchor.

Any failed check is a node failure, not a warning. The node stops with the path and the failed check in its report, and the lead records a failed attempt, never a completed dependency.

**The per-handoff record.** For every edge with a file, the lead records both sides before launch. The producer's half and the consumer's half must agree on the path and on the sections.

| Side | Item | What the brief states | What it prevents |
|---|---|---|---|
| Producer | output path | one absolute path under the evidence dir | a consumer guessing where the result landed |
| Producer | required sections | headings in order, each with the facts it holds | a partial file passing as complete |
| Producer | size bound | a byte or line ceiling | one consumer reading an unbounded pile |
| Producer | evidence and sources | per fact, the command or file:line that proves it | a consumer trusting an unanchored claim |
| Consumer | input path | the same literal string, copied | a silently empty or wrong read |
| Consumer | facts used | the sections and rows it consumes | the producer not knowing what must be exact |
| Consumer | rejection rule | a missing or malformed file is a node failure | a bad handoff becoming an empty input |

**The brief keeps its five fields.** Every node prompt keeps the five fields TASK, DELIVERABLE, SCOPE, VERIFY, STOP WHEN, in the shape set by `SKILL.md`, Delegation prompts. Four parts carry the handoff and cannot be terse:

- **DELIVERABLE: the output path and shape.** The absolute output path, the section headings, and the size bound.
- **SCOPE: the owned files.** Every file the node may write, with the handoff path among them; anything else is out of scope.
- **SCOPE: the input files.** The absolute paths the node may read, including every handoff it consumes.
- **VERIFY: one binary acceptance check.** One command or one surface action with a pass or fail observable, not a list of hopes and not "looks right".

The rest of the prompt can be short. These four are where a node quietly stops being part of a graph.

**Recorded output proves the deliverable.** When a node ends, the lead records the output it produced and the judgement on it only after opening the declared path and observing the acceptance check. A worker's final message is a claim; the file at the path and the check's result are the proof. A node that returned without its named artifacts is a failed attempt, not a completed dependency, and the graph does not advance on it.

```text
handoff: collect-baseline -> define-ideal-state
path: /tmp/wf-evidence/handoffs/collect-baseline.md
sections: Scope | Facts | Sources | Open questions
bound: 24,000 bytes
```

The two prompts quote the same path and the same sections:

```text
PRODUCER
DELIVERABLE: /tmp/wf-evidence/handoffs/collect-baseline.md — sections Scope, Facts,
  Sources, Open questions; at most 24,000 bytes; every fact carries a file:line or
  a command anchor.

CONSUMER
SCOPE: read /tmp/wf-evidence/handoffs/collect-baseline.md and the files it cites.
VERIFY: the handoff opens, all four sections are present in order, the size is at
  most 24,000 bytes, and every fact used carries an anchor; any miss is BLOCKED.
```

The consumer's gate is code, not prose, and it runs before the consumer's first step:

```js
const HANDOFF = "/tmp/wf-evidence/handoffs/collect-baseline.md";
const SECTIONS = ["## Scope", "## Facts", "## Sources", "## Open questions"];
const MAX_BYTES = 24_000;

async function checkHandoff(path, sections, maxBytes) {
    const text = await read(path);                       // a missing file throws here
    const size = new TextEncoder().encode(text).length;
    if (size > maxBytes) {
        throw new Error(`${path}: ${size} bytes, over the ${maxBytes}-byte bound`);
    }
    const lines = text.split("\n").map((line) => line.trimEnd());
    let at = -1;
    for (const heading of sections) {
        const next = lines.indexOf(heading, at + 1);
        if (next < 0) throw new Error(`${path}: missing or out of order: ${heading}`);
        at = next;
    }
    return text;
}

// The consumer's first step. A failed check ends the node here, with the path and the failed check recorded.
try {
    const handoff = await checkHandoff(HANDOFF, SECTIONS, MAX_BYTES);
    log(`handoff ok: ${HANDOFF} (${handoff.length} chars)`);
} catch (err) {
    // The lead records a failed attempt; nothing downstream reads this file.
    log(`BLOCKED: ${HANDOFF} - ${err instanceof Error ? err.message : String(err)}`);
}
```

The path is fixed at dispatch, and the file is judged before it is believed.

## Running a graph on omp

omp has no graph tool, and the flow needs none: a graph is a definition plus a loop. `agent()` starts one child and returns at once, `wait()` settles a whole wave, and `read()`/`write()` carry every handoff through an absolute file. The runner below is the lead's own code in one eval cell. It writes the same lead-owned records as `graphs.md, Lead-owned graph state`, so a killed session can pick the graph back up without guessing.

The definition is data: one record per node with a stable `id`, the `agent` that runs it, the `deps` it consumes, the absolute `out` path it owns, and its `prompt`. The loop keeps one state per node, launches only the nodes whose dependencies are verified `done`, and lets the rest wait. Two attempts per node, one `wait()` per wave, and an append-only log through `write()` are the whole machinery.

```js
// One cell, one graph. The IIFE keeps a re-run in the same kernel from redeclaring names.
await (async () => {
// Six nodes, two branches, one reduce node. `out` is absolute and is repeated in the prompt.
const GRAPH = [
  {
    id: "n1",
    agent: "scout",
    deps: [],
    out: "/tmp/dag-evidence/build/graph/n1-scope.md",
    prompt: "Inventory the parser's entry points and every call site that must change. Cite file and line; list open questions.",
  },
  {
    id: "n2",
    agent: "task",
    deps: ["n1"],
    out: "/tmp/dag-evidence/build/graph/n2-contract.md",
    prompt: "Draft the parser contract: accepted input grammar, error shape, and two worked examples. Use only facts n1 verified.",
  },
  {
    id: "n3",
    agent: "task",
    deps: ["n1"],
    out: "/tmp/dag-evidence/build/graph/n3-rollout.md",
    prompt: "Draft the rollout plan: ordered steps, rollback, and the check that proves each step landed.",
  },
  {
    id: "n4",
    agent: "reviewer",
    deps: ["n2"],
    out: "/tmp/dag-evidence/build/graph/n4-contract-review.md",
    prompt: "Review the contract against n1's inventory. Reject any claim n1 did not verify and list every gap that would block a build.",
  },
  {
    id: "n5",
    agent: "security-reviewer",
    deps: ["n3"],
    out: "/tmp/dag-evidence/build/graph/n5-rollout-security.md",
    prompt: "Audit the rollout plan for credential handling, data retention, and unsafe defaults. Report each finding with severity and a counterexample.",
  },
  {
    id: "n6",
    agent: "reviewer",
    deps: ["n4", "n5"],
    out: "/tmp/dag-evidence/build/graph/n6-decision.md",
    prompt: "Reduce the two reviews into one go/no-go: accepted items, blocking items, and the next action. Add no new findings.",
  },
];

const LOG = "/tmp/dag-evidence/build/graph/build.events.jsonl";
const MAX_WAVE = 8; // far below async.maxJobs (100)
const MAX_WAVES = GRAPH.length * 3;

const state = new Map(
  GRAPH.map((node) => [node.id, { state: "waiting", attempts: 0, callFailures: 0, problem: "", handle: null }]),
);

let logText = "";
try {
  logText = await read(LOG);
} catch {
  logText = "";
}

async function append(event) {
  logText += JSON.stringify({ at: new Date().toISOString(), graph: "build", ...event }) + "\n";
  await write(LOG, logText);
}

async function setState(node, to, detail, attempt) {
  const rec = state.get(node.id);
  const from = rec.state;
  rec.state = to;
  await append({
    node: node.id,
    event: "state",
    attempt: attempt ?? rec.attempts,
    detail: `${from} -> ${to}; ${detail}`,
  });
}

const deadEnd = (depId) => {
  const rec = state.get(depId);
  return rec.state === "blocked" || (rec.state === "failed" && rec.attempts >= 2);
};

for (let waveNo = 1; waveNo <= MAX_WAVES; waveNo += 1) {
  // One replacement per failed node: reopen it while an attempt remains.
  for (const node of GRAPH) {
    const rec = state.get(node.id);
    if (rec.state === "failed" && rec.attempts < 2) {
      await setState(
        node,
        "waiting",
        rec.attempts === 0 ? `call failure; retrying (call failure ${rec.callFailures})` : `replacement after attempt ${rec.attempts}`,
      );
    }
  }

  // A dead-end ancestor holds only its own descendants.
  let changed = true;
  while (changed) {
    changed = false;
    for (const node of GRAPH) {
      if (state.get(node.id).state !== "waiting") continue;
      const held = node.deps.filter(deadEnd);
      if (held.length > 0) {
        await setState(node, "blocked", `ancestor ${held.join(", ")} cannot finish`);
        changed = true;
      }
    }
  }

  const wave = GRAPH.filter((node) => {
    const rec = state.get(node.id);
    return rec.state === "waiting" && node.deps.every((dep) => state.get(dep).state === "done");
  }).slice(0, MAX_WAVE);

  if (wave.length === 0) break;

  // Launch the whole wave before waiting on any of it.
  const launches = [];
  for (const node of wave) {
    const rec = state.get(node.id);
    const attempt = rec.attempts + 1;
    const prior = rec.problem
      ? `\nThe previous attempt failed: ${rec.problem}\nFix the cause before writing again.`
      : "";
    const prompt = [
      node.prompt,
      `Attempt ${attempt} of 2.`,
      `Write the deliverable to ${node.out}. That exact absolute path is the handoff file every consumer opens.`,
      "Do not spawn subagents.",
    ].join("\n") + prior;

    await setState(node, "running", `attempt ${attempt} launching`, attempt);
    try {
      const handle = await agent(prompt, { agent: node.agent, label: `${node.id}-attempt-${attempt}` });
      rec.attempts = attempt;
      rec.handle = handle;
      await append({
        node: node.id,
        event: "launched",
        attempt,
        detail: `${node.agent} ${handle.handle}`,
      });
      launches.push({ node, handle });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      rec.callFailures += 1;
      // No handle means no work was done, so this is not a consumed attempt; retry once, then park.
      const to = rec.callFailures >= 2 ? "blocked" : "failed";
      await setState(node, to, `attempt ${attempt} produced no handle: ${message}`, attempt);
    }
  }

  if (launches.length === 0) continue;

  // One wait per wave. A failed slot holds an Error; it does not throw.
  const values = await wait(launches.map((item) => item.handle), { raiseErrors: false });
  for (let i = 0; i < launches.length; i += 1) {
    const node = launches[i].node;
    const rec = state.get(node.id);
    const value = values[i];
    rec.handle = null;

    if (value instanceof Error) {
      rec.problem = value.message;
      await setState(node, "failed", `attempt ${rec.attempts} raised: ${value.message}`, rec.attempts);
      continue;
    }

    let body = "";
    try {
      body = await read(node.out);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      rec.problem = `output unreadable: ${message}`;
      await setState(node, "failed", rec.problem, rec.attempts);
      continue;
    }

    if (typeof body !== "string" || body.trim().length === 0) {
      rec.problem = `output is empty: ${node.out}`;
      await setState(node, "failed", rec.problem, rec.attempts);
      continue;
    }

    rec.problem = "";
    await setState(node, "done", `output checked at ${node.out} (${body.length} chars)`, rec.attempts);
  }
}

const finished = [...state.values()].filter((rec) => rec.state === "done").length;
await append({
  node: "-",
  event: "settled",
  attempt: 0,
  detail: `graph settled: ${finished}/${GRAPH.length} done; ${[...state.entries()].filter(([, r]) => r.state !== "done").map(([id, r]) => id + "=" + r.state).join(", ") || "no leftovers"}`,
});
log(`build graph: ${finished}/${GRAPH.length} nodes done; log at ${LOG}`);
})();
```

The log is append-only in content: `write()` has no append mode, so the runner keeps the text it read and writes it back with one new line, and a crash costs at most the last line. The wave is launched whole and settled whole. A returned value is not the proof: the runner opens `out` with `read()` and marks the node `done` only when the file exists and is not empty. Anything else is `failed`, and that failure text goes into the next attempt's brief. A node that runs gets exactly two attempts. With this graph, if `n2` fails both times, `n4` is blocked and `n6` is blocked through it, while `n3` and `n5` run to `done`; the log shows two `failed` lines for `n2`, then `blocked` for its descendants. A launch that throws before a handle exists did no work, so it consumes no attempt: it is retried once and, if it throws again, the node is parked as blocked with the exact gap, which holds only its descendants.

The same loop on the Python backend. Handles are synchronous there, so `.handle` is read without an extra await, and the wait keyword is `raise_errors`.

```python
import json
import time

GRAPH = [
    {"id": "n1", "agent": "scout", "deps": [], "out": "/tmp/dag-evidence/build/graph/p1-scope.md",
     "prompt": "Inventory the parser's entry points and the call sites that must change. Cite file and line."},
    {"id": "n2", "agent": "task", "deps": ["n1"], "out": "/tmp/dag-evidence/build/graph/p2-contract.md",
     "prompt": "Draft the parser contract from the verified inventory. State the error shape and two examples."},
    {"id": "n3", "agent": "task", "deps": ["n1"], "out": "/tmp/dag-evidence/build/graph/p3-rollout.md",
     "prompt": "Draft the rollout plan: ordered steps, rollback, and the check that proves each step landed."},
    {"id": "n4", "agent": "reviewer", "deps": ["n2", "n3"], "out": "/tmp/dag-evidence/build/graph/p4-review.md",
     "prompt": "Review both drafts against the inventory. List blocking gaps and add no new claims."},
]

LOG = "/tmp/dag-evidence/build/graph/build-python.events.jsonl"
MAX_WAVE = 8
STATE = {n["id"]: {"state": "waiting", "attempts": 0, "call_failures": 0, "problem": ""} for n in GRAPH}

try:
    LOG_LINES = read(LOG).splitlines()
except Exception:
    LOG_LINES = []


def append_event(node_id, event, attempt, detail):
    LOG_LINES.append(json.dumps({
        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "graph": "build",
        "node": node_id,
        "event": event,
        "attempt": attempt,
        "detail": detail,
    }))
    write(LOG, "\n".join(LOG_LINES) + "\n")


def set_state(node, to, detail, attempt=None):
    rec = STATE[node["id"]]
    before = rec["state"]
    rec["state"] = to
    append_event(node["id"], "state", rec["attempts"] if attempt is None else attempt, f"{before} -> {to}; {detail}")


def dead_end(dep_id):
    rec = STATE[dep_id]
    return rec["state"] == "blocked" or (rec["state"] == "failed" and rec["attempts"] >= 2)


for _ in range(len(GRAPH) * 3):
    for node in GRAPH:
        rec = STATE[node["id"]]
        if rec["state"] == "failed" and rec["attempts"] < 2:
            set_state(node, "waiting", f"replacement after attempt {rec['attempts']}")

    changed = True
    while changed:
        changed = False
        for node in GRAPH:
            if STATE[node["id"]]["state"] != "waiting":
                continue
            held = [dep for dep in node["deps"] if dead_end(dep)]
            if held:
                set_state(node, "blocked", "ancestor " + ", ".join(held) + " cannot finish")
                changed = True

    wave = [
        n for n in GRAPH
        if STATE[n["id"]]["state"] == "waiting"
        and all(STATE[dep]["state"] == "done" for dep in n["deps"])
    ][:MAX_WAVE]
    if not wave:
        break

    launched = []
    for node in wave:
        rec = STATE[node["id"]]
        attempt = rec["attempts"] + 1
        prompt = (
            node["prompt"]
            + f"\n\nAttempt {attempt} of 2. Write the deliverable to {node['out']}."
            + "\nDo not spawn subagents."
        )
        set_state(node, "running", f"attempt {attempt} launched", attempt)
        try:
            handle = agent(prompt, agent=node["agent"], label=f"{node['id']}-attempt-{attempt}")
        except Exception as exc:
            # No handle means no work was done; retry once, then park the branch.
            rec["call_failures"] += 1
            target = "blocked" if rec["call_failures"] >= 2 else "failed"
            set_state(node, target, f"attempt {attempt} produced no handle: {exc}", attempt)
            continue
        rec["attempts"] = attempt
        append_event(node["id"], "launched", attempt, handle.handle)
        launched.append((node, handle))

    if not launched:
        continue

    values = wait([handle for _, handle in launched], raise_errors=False)
    for (node, _handle), value in zip(launched, values):
        rec = STATE[node["id"]]
        if isinstance(value, Exception):
            rec["problem"] = str(value)
            set_state(node, "failed", f"attempt {rec['attempts']} raised: {value}", rec["attempts"])
            continue
        try:
            body = read(node["out"])
            problem = "" if body.strip() else "output is empty"
        except Exception as exc:
            problem = f"output unreadable: {exc}"
        rec["problem"] = problem
        set_state(node, "failed" if problem else "done", problem or f"output checked: {node['out']}", rec["attempts"])
```

Five rules keep the runner honest:

- **A wave is every node whose dependencies are verified `done`.** Not every node whose dependency attempt returned: the lead opens each dependency's `out` file first, because a finished attempt proves neither that the file exists nor that it is right.
- **Prefer one `wait()` per wave.** Launch the whole wave, settle it with a single `wait(handles, { raiseErrors: false })`, judge every slot, then compute the next wave; several waits inside one wave serialize work that could have overlapped.
- **Cap a wave.** Every `agent()` handle counts against `async.maxJobs` (default and maximum 100), so a wide graph launches in slices instead of one unbounded batch; the cap here is 8.
- **No node prompt may spawn.** `task.maxRecursionDepth` (default 2) would let a child fan out again, so every brief says "Do not spawn subagents." in as many words, and the lead is the only fan-out point.
- **Await before you read a JS handle.** `agent()` returns a pending handle at once: `wait()`, `.status()`, and `.send()` work on it, but `.id`, `.agent`, and `.handle` exist only on the resolved handle, so `const handle = await agent(...)` before recording `agent://<id>`.

The same runner serves every graph in the flow; only the node definitions and the phase name in the log change.

## Wide graphs: shards, reducers, bounded reports

A graph is wide when a wave holds many nodes: one read per file, one check per lane, one angle per question. Width is cheap to launch and expensive to read. Each node adds a report, and a reducer asked to read every raw report at once turns width into a context problem. Two shapes keep a wide graph honest: a pool for many items of one shape, and bounded reports behind staged reduction. Both exist so that no consumer ever reads an unbounded pile.

### Bounded reports

Every node in a wide wave leaves two artifacts: a full working file at its own path, and a report of at most 2,000 tokens. The report is a routing document; the working file is the evidence. The lead fixes the bound in the node brief, records it in the snapshot, and checks it the same way it checks the path, per `graphs.md`, Handoff files.

- **The bound is a ceiling with a check.** The lead measures the report and rejects one over its bound as a failed attempt. It never trims the report itself, because a trimmed report hides whichever fact did not fit.
- **The report states the answer, the anchor, and the residue.** Per assigned question: the answer, the file and line range or the command and its output that proves it, what was checked and how, and what the node could not resolve by exact path. Long quotations, raw command output, and the full source list stay in the working file.
- **Anchors point down, not sideways.** A report cites the source it read, never another node's report. A reducer that needs the long form opens the cited file at the cited line; it does not accept a paraphrase from a peer.
- **Unresolved is content, not omission.** An unread source, a refused page, and a dead-end lead are named with what was tried. A report that quietly drops them tells every later layer that the question was closed.
- **The bound does not grow with the finding.** A node that finds a great deal writes more in its working file and keeps the report at the same ceiling. When the bound cannot hold the answer, the assignment is too wide and splits into two nodes, not into one larger report.

### Staged reduction

Reduction runs in layers, and each layer reads only the layer below it.

```text
wide wave:        R1  R2  R3  R4  R5  R6  R7  R8   (bounded reports, each with anchors)
cluster layer:    C1 <- R1..R3          C2 <- R4..R6          C3 <- R7..R8
phase layer:      P  <- C1, C2, C3      (reads the cluster digests only)
```

- **A reducer reads its declared inputs, then only the anchors it must verify.** It never re-reads the raw wave. Its brief names the exact digest files it consumes and the files it may open to check a cited fact.
- **A reducer adds no claim.** It merges, dedupes, resolves a conflict against the cited anchor, or names the conflict as unresolved. A gap becomes a reopen request naming the node whose report is missing; the reducer does not fill it from memory.
- **A digest cites the checked files.** Every fact in a digest names the path and line or the command that proves it, and carries its state: checked, refuted, or unresolved. Only checked facts cross into the next layer; unresolved ones cross named.
- **Each layer has its own ceiling.** A cluster digest is at most 1,500 tokens; the phase digest is at most 2,000. The phase digest is a merge, never a concatenation: if three cluster digests would push it over, the phase reducer drops restatement and keeps the decision, the anchor, and the residue.
- **Reduction is staged, never a wider brief.** When the verified reports exceed one reducer's input limit, add a layer or split the cluster. Widening one reducer's brief past its limit is how a report is silently truncated, and truncation is indistinguishable from agreement.
- **Cluster size is measured, not quota'd.** The lead records how many bounded reports a reducer actually read without dropping one, and how many items the pool actually kept in flight; those observed numbers set the next wave's width and the next cluster's size. A number copied from an example is a guess wearing a rule's clothes. A cluster that fits is evidence; a cluster that overflowed is split and rerun as a revision.
- **One reducer per layer, one writer per file.** Two reducers over the same cluster would race on one digest. The lead either gives each cluster its own reducer and file or adds a layer until the width fits.

An over-bound digest, a digest whose citations do not open, and a digest that repeats a raw report instead of reducing it are all failed attempts. The reducer is re-briefed with the measured limit and the failure text, under the two-attempt rule in `graphs.md`, Failure, attempts, and revisions.

### Shards: one pool per wave

Many items of one shape — the same mechanical extraction over a known list of paths, the same checker over many files, the same read over many documents — are one pool, not N hand-written nodes. The lead names the pool, picks the agent that fits the shape, writes the shared context every item needs, and pushes one string per item. Items are strings only: the string is the item's identity, and the pool context carries the brief that all items share.

```js
// One shard shape repeated over known paths. Items are strings: one absolute path per item.
const items = [
  "/abs/repo/src/parser/lexer.ts",
  "/abs/repo/src/parser/parser.ts",
  "/abs/repo/src/parser/errors.ts",
  "/abs/repo/src/parser/tokens.ts",
];

const pool = await workpool("sonic", {
  name: "collect-symbols",
  context: [
    "Read /tmp/wf-evidence/collect/packet.md first; it holds the question, the repository root, the evidence dir, and the report shape.",
    "One item is one absolute path. For each path, list every exported symbol, its signature, and its call sites.",
    "Write /tmp/wf-evidence/collect/symbols-<basename>.md, at most 2,000 tokens, every fact anchored with file and line.",
    "Do not spawn subagents and do not write outside your own symbols file.",
  ].join("\n"),
  tools: ["read", "grep"],
});

for (const path of items) {
  await pool.push(path);
}

log(`collect-symbols queued ${items.length} paths; the aggregate arrives once when the pool first drains`);
```

The pool's aggregate result is delivered to the session once, when the pool first drains, and there is no `pool.wait()`; the reducer cell starts on that delivery rather than on a status check. The first drain also closes the pool, so a second wave gets a new name.

- **The pool is one wide wave, not a graph.** Items that depend on each other, or that differ in shape, are nodes with edges. A pool item that would need its own downstream chain belongs in the graph instead.
- **Waiting is the delivery, not a poll.** `.status()` and `.peek()` are for diagnosing a stuck pool, never for waiting; the aggregate lands on its own and the kernel stays free for other calls meanwhile.
- **An item can fail alone.** A worker answers an item with `yield({ key, error })`; that item, not the pool, is failed. The lead retries only the failed items in a new named pool, and the two-attempt bound applies.
- **The pool's ceiling is the runtime's, not a target.** Each pool caps live workers at `task.maxConcurrency` (32 by default). The lead records what the pool actually held in flight and sizes the next wave from that observation, not from the ceiling.

### Research angles: collect, chase, counter-check

Research is a wide graph with a chain per angle. An angle is one independent way the question can be answered; the number of angles is discovered while the context graph runs and recorded in the snapshot. There is no fixed number of angles, and no target to pad to.

```text
angle A:  collect -> chase leads -> counter-check     (three files)
angle B:  collect -> chase leads -> counter-check     (three files)
angle C:  collect -> chase leads -> counter-check     (three files)

cluster 1 reducer: digest-1.md  cites every checked file from A and B
cluster 2 reducer: digest-2.md  cites every checked file from C
final reducer:     digest.md    merges digest-1 and digest-2, after both exist
```

Each step in a chain is its own node and writes its own file, so a later step can be re-run without repeating the one before it.

- **Collect** reads the angle's sources once and writes `<angle>-collect.md`: each fact, its anchor, and every lead the reading opened. A lead is a pointer to a source not yet read, named precisely enough for the chase node to open it without guessing.
- **Chase** follows every lead from the collect file and writes `<angle>-chase.md`: what each lead said, its anchor, and the leads it opened in turn. A dead lead is named with what was tried. The angle closes when a chase adds no new lead, or when the remaining leads are recorded as unread with a reason.
- **Counter-check** tries to refute the angle's claims from sources the collector did not use, and writes `<angle>-check.md`: each claim marked confirmed, refuted, or unresolved, with the independent source that decided it. A counter-check that only re-reads the collector's own sources has not checked anything.

Clusters form by subject, not by count, and converge separately. A cluster's reducer runs as soon as every angle in it has a verified check file, without waiting for the other clusters; it writes `digest-<cluster>.md` at most 1,500 tokens, citing the checked files rather than the collectors' prose, and carrying each refuted or unresolved claim forward by name. One final reducer merges the cluster digests into the phase digest at most 2,000 tokens, after every cluster digest is verified. It resolves conflicts by opening the cited anchors, never by majority vote, and it lists what the research did not settle.

A new angle found mid-chase becomes a new chain in the graph, with its own three nodes and its own reducer path, recorded as a revision. It never becomes an extra paragraph inside an existing report, because a paragraph cannot be re-run, scoped, or checked on its own. Adding an angle invalidates only the cluster digest above it and the final digest, never the angles that already converged.

The two shapes compose across all three graphs: the context graph pools its mechanical extractions and chains its outside research by angle; the build graph pools only same-shaped edits and keeps every differing change its own node; the verify graph pools same-shaped checker runs and reduces lane receipts in layers. Which graph owns which nodes is in `graphs.md`, The flow's three graphs; the wide-graph rule is the same in each: a bounded report per node, measured cluster sizes, and a staged reduction that ends in one digest no larger than its ceiling.

The context graph and its angle chains are specified stage by stage in `planning.md`, Stage 1: Collect — the context graph. The build graph's same-shaped edit waves are in `execution.md`, Stage 9: Build — the build graph.

## Lead-owned graph state

The lead — the session running the graph — is the only writer of two files per graph. Both live in the evidence dir outside the worktree, beside the plan and the receipts, and both outlive a killed session or a compaction. Nodes write their own output and report; they never write either file.

- **The snapshot** (`graph-<phase>.snapshot.md`) holds the definition frozen at launch plus one entry per node, rewritten in place as the graph runs. It answers what is true right now in one read.
- **The event log** (`graph-<phase>.events.jsonl`) is append-only, one JSON object per line. It answers how the graph got here and is the record a wrong snapshot is checked against. Never rewrite, reorder, or compact a line mid-phase; a correction is a new line that names the line it corrects.

Write the log line first, then the snapshot. A crash between the two then leaves an event the next session can finish from, never a state change with no trace. On a restart the lead reads the snapshot, then the log tail, then reconciles every live reference against the handle that actually exists; the full order is `graphs.md, Picking a graph back up`.

### Per-node entry

A node entry carries these fields.

| field | what it records |
|---|---|
| `id` | Stable for the phase, minted when the graph is defined, never reused or renumbered; a revised node keeps its id. |
| `assignment` | One imperative sentence naming the work. |
| `latitude` | What the node may decide for itself (internal order, names inside its own files, examples) and what its brief fixes (output path, required sections, the checks it must leave behind). |
| `agent` | The agent name from the resolved handle. |
| `model` | The model identifier the runtime reports for that attempt, or `unreported`; never transcribed from the plan or a tier label. |
| `depends_on` | The ids whose outputs this node consumes or whose writes must land first. No other edges. |
| `state` | One of `waiting`, `ready`, `running`, `settling`, `done`, `failed`, `blocked`. |
| `attempts` | Handles observed for this node: `0` before the first launch resolves, `1` after it, one more per replacement. A spawn that dies before a handle exists is a dispatch problem, not an attempt. |
| `live_handle` | The handle reference `agent://<id>` of the attempt that is running or settling; `-` once it settled. A settled reference is never reused. |
| `output` | The absolute path the node owns, written as the same literal string in the node's brief and in every consumer's brief; a missing or malformed file there is a node failure. |
| `verdict` | `pending` until the lead checks the output against the node's one binary acceptance check, then one line of judgement plus the evidence path. A returned handle is not a verdict. |

The states mean exactly this: `waiting` — a dependency is not verified complete. `ready` — every dependency is verified and the node waits for a slot. `running` — a handle is recorded. `settling` — an attempt was cancelled or failed and its terminal state and cleanup are not yet confirmed. `done` — evidence was accepted and the verdict recorded. `failed` — the attempt is diagnosed and no handle is live. `blocked` — the branch is parked on an exact gap.

Agent and model are recorded only once seen. Before the handle resolves both fields are absent rather than guessed, and a tier word in the plan is a label, not a callable switch.

A running node's entry:

```text
### N3 - draft the journey-page contract
assignment: draft the page contract the builder implements
latitude: section order and worked examples; the required rows are fixed
agent: task
model: unreported
depends_on: N1, N2
state: running
attempts: 1
live_handle: agent://n3-7c1e
output: /tmp/dag-evidence/build/journey-contract.md
verdict: pending
```

The definition lines change only through a recorded revision; the bookkeeping lines change only on a launch, a settle, or a checked result.

The event log has one line per event, in time order, with at least `at`, `graph`, `node`, `event`, `attempt`, and `detail`. `event` is one of `state` (a transition, with the from and to in `detail`), `launched`, `evidence`, `failed`, `settled`, `replaced`, `revised`, or `blocked`. A revision line carries the reason and the invalidated ids; a failure line carries the diagnosis and the last output. One line:

```text
{"at":"2026-11-08T09:14:03Z","graph":"build","node":"N3","event":"launched","attempt":1,"detail":"agent://n3-7c1e agent=task model=unreported"}
```

### Launch and completion

At launch the lead appends the `launched` line with the node, the attempt number, the observed agent, and the handle; writes `state: running`, `attempts`, and `live_handle: agent://<id>` into the snapshot; and keeps the resolved handle itself, not the text it returned, so the attempt can still be steered or cancelled. A launch that never yields a handle is a call failure of the graph, leaves the attempt counter alone, and is recorded as such; two such failures at one node mean the definition or the environment is wrong, so the branch parks with the spawn error instead of resending a third time.

Before `state: done` and any verdict other than `pending`, two things exist: the node's bounded report at its declared path, and the output path the lead opened and checked. The `evidence` line records both paths and the one binary observable that decided the check; the report stays bounded, and the snapshot stores its path and a short extract, never its body. An output that is missing, empty, or off its declared shape leaves the node `failed`, whatever the final text said. A node is done when its deliverable is checked, not when its attempt returns.

## Failure, attempts, and revisions

Failure is an ordinary graph event, not an exception. The lead keeps the graph honest rather than merely moving: every failed, cancelled, or invalidated attempt leaves a record, no replacement starts over a live handle, and a branch that cannot proceed is parked with its exact gap.

### Call failures and work failures

A **call failure** is the host or the call failing before the work can be judged: the spawn raised, the return was empty or off its schema, a provider or tool error killed the attempt, or the node ended without its declared artifacts. Re-run the same definition. A call failure that produced no handle consumes no attempt; one that produced a handle and then died does.

A **work failure** is the node running and failing its acceptance check. Diagnose the cause before writing anything new: a wrong brief, a wrong split, a wrong output path, or a real defect in the work. Fix the cause, then replace the attempt with a corrected brief. Re-sending the same prompt after a work failure is a wasted replacement, not a retry.

Both get a failure record. The difference decides whether the definition changes; neither buys a third attempt.

### One replacement, two attempts

One replacement per node, two attempts total: the original and one replacement. `attempts` in the snapshot is the only counter, and every attempt that got a handle increments it, including one that later died as a call failure. The replacement carries the failure context into its brief: the diagnosis, the last output, what the previous attempt proved, and what it did not. The deliverable and the acceptance check stay the same unless a revision says otherwise. Without a resumable handle, the lead rebuilds the replacement brief from the durable handoffs and the log, never from the previous turn's conversation.

Before a replacement launches, the old attempt settles. If its handle is still live and the work is close enough, steer it with `handle.send(...)`: a correction inside the same attempt is not a replacement and keeps its context. If the approach or the brief is wrong, cancel the attempt and wait until it reports a terminal state. Then confirm the cleanup actually ran — its private worktree, scratch files, an injected test file restored — and append the `settled` line naming what was cancelled and what cleanup ran. Only after that line may the `replaced` line and the new launch follow. Two writers never run for one node.

Successful siblings are kept. A failed node does not invalidate a sibling that already passed, and a replacement does not re-run its wave. A sibling's result is reused while the inputs it read and the check it passed still match; only a node whose inputs moved is re-run.

### Blocked branches

A node that cannot proceed is marked `blocked`, and only its descendants are held: the nodes whose `depends_on` reaches it. Each held descendant becomes `waiting` and gets one log line naming the blocking id and the reason; unrelated branches keep running. Edges exist per consumed output, so a branch outside that reach is not held. When the block clears, descendants return to `ready` in dependency order, and one is re-checked only if the revised output changed an input it read.

If a node is blocked because its attempts are spent or because an owner decision is missing, the lead records the exact gap and parks that branch. The gap names the node, the attempts and their diagnoses, what was tried, what is needed (a decision, an input, a capability), and the last output. From then on the branch does nothing until an explicit instruction or the missing input arrives. Waiting never implies permission, and the plan's recommended default is not an answer.

The decide rule of `SKILL.md, The stage map` governs this: genuine owner decisions are asked once, at decide, as one batch with a recommended default each, and a decision that appears mid-run parks only its own lane. A parked branch is not a failed phase, and the rest of the graph continues.

### Revisions

A revision is a change to a node's definition after launch: a corrected brief, a narrowed output, a fixed path, a split. The lead appends a `revised` line with the node, the new definition or its path, the reason, and the invalidated ids; rewrites the definition in the snapshot; and marks the node and every descendant `waiting`. Nothing outside that subtree changes: siblings keep their state and their evidence, and the other branches keep running.

The old attempt settles or is steered before the revision lands, exactly as for a replacement, and any output path that changes is changed in the producer's brief and in every consumer's brief in the same edit. A revision does not reset `attempts`: the counter belongs to the node, not to the version of its brief. A revised node with an attempt left launches as the next attempt carrying the revision reason; one with no attempt left parks with the revision as its gap. A split mints new node ids with their own counters and closes the old node with the revision as its reason.

### Failure records

A failure record has five parts, and none is optional:

- **node** — the stable id.
- **attempt** — the number that failed or was cancelled.
- **diagnosis** — which check failed, against which head, tree, or input, and where the evidence lives.
- **last output** — the path the attempt left, or `none` when it left nothing usable.
- **blocked descendants** — the ids now held, or `none` when no branch is held.

A cancellation record adds why it was cancelled and what cleanup actually ran. "Cancelled" with no reason is not a record. A failure record is appended to the event log and mirrored in the snapshot's verdict line; it is never written by the node whose attempt failed.

## Picking a graph back up

A resumed graph is read, never remembered. The conversation is not state; the snapshot of the graph's definition and the append-only event log are. Read both before touching a handle or a handoff file.

The snapshot carries each node's stable id, assignment, dependencies, status, attempt count, live-handle reference, and the output and judgement recorded for it. The log carries the history in order: dispatches, steers, verdicts, failures, revisions. When the two disagree, resolve the disagreement before dispatching anything; a difference is a state defect, not a detail to average.

Then reconcile in one pass. For every node the snapshot calls live, find its handle in the current session and ask it for its state with `handle.status()`, or with `handle.done()` when only the settled-or-not reading is needed. Where no handle can be found, the node is unowned rather than running. The handle, not the snapshot's age, decides what happens next.

| Snapshot and handle | Resume decision |
| --- | --- |
| The snapshot says running and the handle still reports an unfinished attempt. | Leave it running and record that it was seen. Launch nothing for that node. |
| The snapshot says running and no handle survives in this session. | The node is unowned. Check its handoff path and the log for a late result; if the output is absent or unverified, rebuild the brief from those files and dispatch one fresh attempt. |
| The handle reports a settled attempt and the output exists. | Run the node's binary acceptance check and compare the tree its evidence names with the current one. Reuse it only if both hold. |
| The handle reports a failed or cancelled attempt. | Let it settle, record the failure, then dispatch one replacement with the failure context in its brief. |

Never launch a duplicate of a node whose handle is still running. Two copies of one node write the same paths, spend the phase's budget twice, and break the premise that concurrently runnable nodes have disjoint write scopes. An absent handle means no live child to wait on; a running handle means one. Nothing else needs guessing.

A finished output is not reusable because its file exists. Reuse rests on the tree rule: a receipt is valid while the tree it judged still matches, and a moved tree makes it stale, so only the stale lanes re-run. The tree rule and the receipt fields are owned by `verification.md`, Stage 10: Verify — the verify graph. On resume, apply it before counting any completed node: match the tree, read the output, run the acceptance check. An output that fails the check is a failed attempt, not a finished node.

When no child is alive, rebuild the brief; never rewrite it. The snapshot states what the node owes and which nodes consume it, the handoff files hold its inputs at the absolute paths the original brief named, and the log states what earlier attempts did and where they stopped. The rebuilt brief keeps the node's id, owned paths, deliverable, VERIFY and STOP WHEN exactly as recorded, and adds the recorded failure context when this is the second attempt. Its consumer still treats a missing or malformed handoff file as a failure; resume does not soften an input check.

The rebuild is mechanical, and the log decides whether a dispatch is even allowed:

```js
// Resume one graph. The snapshot below is the definition plus per-node state read back from the evidence dir;
// live is what status() reported for the handles this session still holds.
const evidence = "/tmp/dag-evidence/unit-7";
const node = (id, status, attempts, task, deliverable, scope, verify, stop) => ({
  id, status, attempts, task, deliverable, scope, verify, stop,
});
const snapshot = {
  nodes: [
    node("collect-slice-a", "settled", 1, "Collect the billing call sites", "notes/slice-a.md",
      ["notes/slice-a.md"], "`grep -c invoice src/billing` is at least 1", "notes/slice-a.md exists and is non-empty"),
    node("collect-slice-b", "settled", 1, "Collect the invoice tests", "notes/slice-b.md",
      ["notes/slice-b.md"], "`bun test test/invoice` prints pass", "notes/slice-b.md exists and is non-empty"),
    node("collect-slice-c", "running", 1, "Collect the invoice git history", "notes/slice-c.md",
      ["notes/slice-c.md"], "`git log --oneline -- src/billing` prints at least one commit", "notes/slice-c.md exists and is non-empty"),
  ],
};
const live = new Map(); // node id -> recovered handle, filled from status() checks before this block
const isLive = async (h) => h !== undefined && !(await h.done()); // done() is the binary reading of status()
const logPath = `${evidence}/events.jsonl`;
const logText = await read(logPath);
const dispatches = [];

for (const n of snapshot.nodes) {
  if (await isLive(live.get(n.id))) {
    log(`seen-live ${n.id}`); // nothing is launched for a live node
    continue;
  }
  if (n.status !== "running") continue; // a settled output is judged, not relaunched
  if (n.attempts >= 2) throw new Error(`node ${n.id} used its two attempts; record the gap and hold its descendants`);

  const handoff = `${evidence}/handoff/${n.id}.md`;
  await read(handoff); // a missing input throws here, before anything is dispatched
  const brief = [
    `TASK: ${n.task}`,
    `DELIVERABLE: ${n.deliverable}`,
    `SCOPE: ${n.scope.join(", ")}`,
    `INPUT: ${handoff}`,
    `VERIFY: ${n.verify}`,
    `STOP WHEN: ${n.stop}`,
  ].join("\n");

  // agent() returns at once; awaiting it resolves the handle, it does not wait for the work.
  const h = await agent(brief, { agent: "scout", label: n.id });
  dispatches.push({ node: n.id, attempt: n.attempts + 1, live: h.handle });
}

const added = dispatches.map((d) => JSON.stringify({ event: "dispatch", ...d })).join("\n");
if (added) await write(logPath, `${logText}${added}\n`);
```

An example. A collect phase died with three slices in flight. The snapshot shows slice A completed, slice B with its output written but not judged, and slice C running. If C's handle still reports a running attempt, resume leaves C alone. It matches B's tree and runs B's check before counting it. It does not relaunch A. If C's handle is gone, resume rebuilds C's brief from C's input file and the log and dispatches it once. Nothing in that pass reads the old conversation.

If the snapshot already records two attempts for a node, resume does not make a third. Record the exact gap at that node and stop there; the node and its descendants are held, and unrelated branches keep moving. A replacement never discards a successful sibling's verified output. The attempt bound and its records are in `graphs.md`, Failure, attempts, and revisions.

Resume never re-plans a plan that exists, never re-runs a valid node to be sure, and never adopts a result whose tree moved. Each of those spends the phase's budget to recreate state the files already hold.

## Supervising a running graph

The lead supervises the graph; nothing else does. There is no status widget and no automatic recovery service, so the graph is observed only as far as the lead's next read. Supervision happens at wakes: a handle settles, a background job reports, a message arrives, and the lead reads the graph before dispatching anything new.

At every wake, compare each live node with its own SCOPE. SCOPE is the node's authority: the paths it may write, the worktree its commands pin, and the one deliverable it owes. Read the work, not the report. Changed paths go against the write scope, commands against the pin, artifacts against DELIVERABLE, and the confirming device against VERIFY. A node's summary is a claim about its work; the worktree and the handoff files are the evidence.

Drift is any work outside SCOPE: a write to a path another node owns, a change larger than the one deliverable, a skipped confirming device, or a command run somewhere other than the pinned worktree. Steer it at once with `handle.send(msg)`, and name the boundary crossed, the path to restore, and the one thing the node must finish. "Stay in scope" steers nothing; "you wrote `src/billing/tax.ts`, your SCOPE is `src/cart/`; restore that file and return only the cart change" steers the node. The lead does not clean the file up in parallel: a second writer on one path is the race the disjoint write scope exists to prevent.

A steer reaches a live node. Once a node has returned, its result is final, and a correction is a new attempt rather than a message; record what the first attempt produced before dispatching the replacement.

A node that drifts again after a named steer has a brief problem, not a work problem. Its second attempt gets a tightened prompt: the exact owned paths, the sibling paths it must not touch, the one binary acceptance check, and the boundary in the opening paragraph rather than buried at the end. The second attempt is never the first prompt resent unchanged. Two attempts is the bound; a node still drifting after its second attempt is a graph failure to record and park, not a third dispatch.

Most wakes need nothing. If every live node is inside its scope and no completed node waits for a judgement, there is nothing to do; polling for change does not make change arrive.

Supervision also keeps the state current. Each dispatch, steer, verdict, failure and revision goes into the log as it happens, and each change to a node's status, attempt count, output or judgement updates the snapshot. That bookkeeping is what makes a resume read state instead of reconstruct it; the rules are in `graphs.md`, Picking a graph back up.

Supervision never rewrites a node's definition mid-phase. A definition that must change is a revision: record the reason, settle or steer the running node first so two writers never overlap, and invalidate only that node and its downstream. `graphs.md`, Failure, attempts, and revisions owns the records.

A phase does not end because every node returned; it ends by reducing verified results into its checkpoint. Child completion is not graph success. Reducer and review nodes merge the outputs, the lead confirms that each recorded verdict proves the deliverable the node declared, and the checkpoint records the verified results with their evidence and the gaps that remain. The next phase is designed from that checkpoint's evidence, not from the plan's original assumption. A finding that changes the definition goes back through define before the next plan is drawn.

## The flow's three graphs

Every phase of this flow is one of three graphs. All three use the same discipline — nodes, edges that only order, handoff files, per-node confirming devices, and a reduction at the end — and differ in what a node is.

| Graph | Stage | A node is | How it closes |
| --- | --- | --- | --- |
| Context graph | Stage 1: Collect | One open question or one slice of context: the code the request touches, the git history of the touched paths, memory, earlier session evidence, outside sources; one check node per slice confirms that slice's claims against its source. | One reducer writes `collect.md`, with a source per fact and every unread source named; define starts from it. |
| Build graph | Stage 9: Build, Stage 12: Fix | One smallest independent change, with a disjoint write scope; each node owns its confirming device, and a fix node owns a fix device calibrated to fail before the fix and pass after it. | One serialized commit node captures the verified files in one commit; freeze binds the head. |
| Verify graph | Stage 10: Verify | One required lane: a test run, a QA scenario, a guard mutation with its confirming device, a review lane. | One reducer writes the phase's receipt set from the lane receipts. |

The context graph is Stage 1: Collect. It treats collection as a graph of questions rather than one pass over the repository: every open question and every slice — the code, the git history of the touched paths, memory, earlier evidence, outside sources — gets its own node, and each slice's note passes a check node that re-reads the source before anything downstream may use it. Width comes from the number of independent questions, not from a fixed fan-out. One reducer writes `collect.md`; define starts from that file. The graph, its slices and its stopping rule are in `planning.md`, Stage 1: Collect — the context graph.

The build graph is Stage 9: Build. A correction run runs the same graph again at Stage 12: Fix, with one fix node per reported failure. Its atom is the smallest independent change that can be made and proved on its own, not a file and not a layer. A change that cannot be proved on its own is merged into a sibling node rather than sharing a file. Two nodes run together only when their write scopes are disjoint, so no two concurrently runnable nodes write the same path. Each node owns its confirming device and captures the evidence itself; proof is never deferred to the verify phase. A fix node owns a fix device that fails on the code before the fix and passes on the head, so the fix appears as a verdict that changed, not as a sentence in a report. One commit node stages the verified files and records the commit identity once `git cat-file -t <sha>` prints `commit`; commits are serialized because the nodes share one git index. The graph is in `execution.md`, Stage 9: Build — the build graph.

The verify graph is Stage 10: Verify. Every required lane for the work type is a node: a test run, a QA scenario, a guard mutation with the confirming device that judges it, a sweep, a code review, and the type-specific lanes the plan requires. Each node writes its own receipt naming the head and tree it judged and the one observable that decided it; a required lane that did not run leaves a hole no other lane's green result fills. The devices that prove a fix are calibrated here too: they fail on the base, pass on the head, and a device that passes on both proves nothing. One reducer writes the phase's receipt set: it joins each receipt to the candidate head and tree, flags stale entries, and names what remains unproved. The lane set, the receipts and the calibration are in `verification.md`, Stage 10: Verify — the verify graph.

The three are one sequence. The context graph feeds define; the plan drawn from define feeds the build graph; the build graph's head feeds the verify graph; the verify graph's record feeds triage and the round. A correction run replaces the build graph for one round and returns to the verify graph. They are separate graphs because each is one phase with one checkpoint, and each phase's checkpoint is the evidence from which the next is designed. When a graph is interrupted, the resume and supervision rules are the same for all three: `graphs.md`, Picking a graph back up and `graphs.md`, Supervising a running graph.
