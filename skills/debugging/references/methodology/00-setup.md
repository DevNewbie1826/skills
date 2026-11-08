Read this when you are beginning a debugging session and need a reliable environment snapshot and artifact ledger.

# Phase 0 + 1 — Environment Assessment & Journal Setup

Before a debugger touches anything, you need a map of what's running and a ledger of what you'll touch. Skipping either phase is how debug sessions turn into "why is my repo dirty a week later" sessions.

---

## Phase 0 — Environment Assessment

Map the ground truth before you attach. Attaching the wrong way wastes the first hour.

### 1. Identify the runtime

Read the actual manifest file, don't guess from extensions:

- Python → `pyproject.toml`, `requirements*.txt`, `setup.py`, `uv.lock`, `.python-version`
- Node → `package.json` (check `scripts`, check `engines`, check `type: module`)
- Rust → `Cargo.toml`, `rust-toolchain*`
- Go → `go.mod`, `go.sum`
- Native / mixed → `Makefile`, `CMakeLists.txt`, the binary itself (`file <path>`)

### 2. Load the matching runtime reference

The moment you know the runtime, open its listed `references/runtimes/<runtime>.md`. If no runtime reference is listed, name the missing reference in the journal and apply the phase loop with your runtime's analogous debugger, tracer, and logger. The commands in this phase (and every phase after) are runtime-specific. The shape of the answers is the same; the commands are not.

### 3. Gather observable environment state

The shape of the answers you need (commands in the runtime reference):

| Question | Why it matters |
|---|---|
| What binary/interpreter/runtime actually launches the process? | Determines debugger flag plumbing. Wrappers (`tsx`, `poetry run`, `cargo run`, `bun`, supervisor scripts) change how flags propagate. |
| Is there already a debug-relevant port in use, or another instance of the service running? | Either attach to it or kill it deliberately — never silently compete. |
| Are symbols / source maps / debug info present and correct? | This determines whether breakpoints land on the right lines. Compiled-but-not-debug builds, stripped binaries, and incomplete source maps all silently misplace breakpoints. |
| Does the code path require env vars, config files, or auth tokens to reach the bug? | Missing env often produces early-return paths that masquerade as the bug itself. |
| Is there an existing failing test or known repro? | Prefer amplifying an existing repro over inventing one. |
| Are watchers (file watchers, hot reloaders, supervisors) going to restart the process mid-session? | If yes, turn them off before attaching. Restarts drop inspector connections and invalidate breakpoints. |

### 4. Gate check

If any answer is "I'm not sure", investigate at most three investigation rounds on the same question; if still uncertain, proceed to the hypothesis phase with the uncertainty recorded. Guessing here cascades into false-positive hypotheses in Phase 2.

---

## Phase 1 — Journal Setup

Open **one** journal file: `.debug-journal.md`. Put it at the project root when there is one, or beside the standalone binary and its working files otherwise. It is the single source of truth for every artifact this skill creates and the contract that you can undo everything.

### Establish a reversible baseline

A journal file plus pre-change snapshot copies is the baseline mechanism for every session, including standalone binary debugging with no Git worktree. Before touching an existing file, record it in the journal and copy its current state into the journal directory:

```bash
snapshot_root=.debug-journal/snapshots
file=src/foo.py
mkdir -p "$snapshot_root/$(dirname "$file")"
cp -a "$file" "$snapshot_root/$file"
```

Record the snapshot path and whether the file already had user edits in the journal. The snapshot preserves pre-existing user edits, so it is the safe source for any whole-file restoration later.

### Git-worktree upgrade

When a Git worktree exists, also record `git status --short`, `git diff --`, and `git diff --cached --` before editing. These checks make pre-existing changes visible and supplement snapshots; they never authorize a blanket checkout.

### Exclude journal files from git (when a Git worktree exists)

```bash
grep -qx '.debug-journal.md' .git/info/exclude || echo '.debug-journal.md' >> .git/info/exclude
grep -qx '.debug-journal/' .git/info/exclude || echo '.debug-journal/' >> .git/info/exclude
```

`.git/info/exclude` is per-clone and not committed — useful for local-session journal artifacts. Journal any lines you add and, if the file already exists, snapshot it before editing so Phase 9 can reverse only your changes.

### Journal template

```markdown
# Debug Journal — <short bug name>
Started: <ISO timestamp>
Goal: <one-sentence user request>

## Environment snapshot (Phase 0)
- Runtime: <language + version + launcher>
- Entry: <command that starts the process>
- Ports / sockets: <app=..., debugger=..., etc>
- Baseline snapshots: `.debug-journal/snapshots/` — <paths copied before edits; note any pre-existing user edits>
- Git baseline (if worktree): HEAD <sha>, `git status --short` and diffs recorded? <yes/no>
- References read: <list the files from references/ you loaded — proves you did the gate>

## Hypotheses
1. [STATUS] <hypothesis> — distinguishing evidence: <what would confirm/refute> — if true, fix is: <two words>
2. ...

## Failed hypothesis round counter
- Round 1: <result>
- Round 2: <result>
<!-- At two consecutive failures, invoke the independent review triple (see 04-independent-review-triple.md). -->

## Artifacts to revert
<!-- Every temp edit, terminal-multiplexer session if used, fixture, env override, and saved debugger session goes here
     BEFORE it is created. The rule is journal-then-modify. -->
- [ ] `.debug-journal/` — pre-change snapshots. Remove only after all journaled reverts and verification.
- [ ] `.git/info/exclude` (if modified) — added journal exclusions. Pre-change snapshot: `.debug-journal/snapshots/.git/info/exclude`. Revert: remove only the lines this session added.
- [ ] `src/foo.py` — added `breakpoint()` on 2 lines. Pre-change snapshot: `.debug-journal/snapshots/src/foo.py`. Revert: reverse only the recorded `breakpoint()` hunk; restore the snapshot only if the file has no retained fix.
- [ ] terminal-multiplexer session (for example, tmux) `debug-server`. Kill with the command for the multiplexer used.
- [ ] `/tmp/debug-payload.json`. Remove: `rm /tmp/debug-payload.json`
- [ ] env var in current shell: `FOO_BASE_URL=...`. Unset when done.
- [ ] GDB session save: `~/ghidra-projects/scratch.gzf`. Remove if not promoting.

## Findings
<!-- Append observed values here with timestamp. Verbatim only, no paraphrasing. -->

## Independent review triple (if invoked)
<!-- One subsection per review round, with the synthesized new hypothesis set. -->

## Final fix
<!-- File paths + test path. Filled during Phase 7. -->
```

### The journal-then-modify rule

Before any modification to the target, shell, or system state, append to "Artifacts to revert" first. This one discipline is what prevents debug sessions from becoming cleanup sessions.

If you catch yourself about to run a command that creates a file, opens a port, or modifies source — stop, journal the intended artifact with its revert command, then run the command. Not the other way around.

### Why a single journal (not scattered TODO comments)

- One journal-led list of targeted reversals, `rm`, and `tmux kill-session` commands — simple Phase 9 walk.
- Survives interruptions. If you get pulled away mid-session, the next agent (or you later) can continue or revert without guessing.
- Prevents the most common failure: leaving `console.log`/`print()`/`dbg!` scattered across the tree.
