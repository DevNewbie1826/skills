Read this when the fix is complete and you need to remove artifacts and assemble evidence before reporting done.

# Phase 9 + 10 — Cleanup & Final Verification

After the session, the target and source (if any) must differ from the pre-session baseline only by the real fix and its test. Anything else is a process failure.

---

## Phase 9 — Cleanup & Revert

### The walk

Open the journal's "Artifacts to revert" list. Walk it top to bottom. Revert **only** artifacts the journal recorded before they were created or changed; leave every other user change alone. Check each box only after the recorded revert succeeds and produces no error.

> **Safety check before any revert:** was this file dirty before I touched it? then snapshot-restore, not checkout.

For a journaled source edit, reverse only its recorded hunk. When the whole pre-change state must be restored, copy the matching journal snapshot back so unrelated user edits survive; never use a blanket checkout or whole-file version-control restore.

### Standard revert operations

Most sessions create some combination of these artifacts. The journal, not a broad version-control command, authorizes each revert. Run a command only for an exact path, session, process, or override recorded by this session.

```bash
# --- Temporary source edits (instrumentation statements, debug prints) ---
# Reverse only the journaled instrumentation hunk. For a journaled whole-file restore:
cp -a .debug-journal/snapshots/src/foo.py src/foo.py
# In a Git worktree, inspect the result; do not use version control as the revert:
git diff -- src/foo.py

# --- Terminal-multiplexer sessions, if you created them ---
# Use the journaled session name and the matching stop/list commands for the multiplexer used.
tmux kill-session -t <journaled-session-name>
tmux ls                                          # confirm gone

# --- Temp fixtures / scratch scripts ---
rm -f <journaled-temp-fixture>
test ! -e <journaled-temp-fixture>               # confirm gone

# --- Background processes created by this session ---
ps -p <journaled-pid> -o pid=,command=           # confirm it is the recorded process
kill <journaled-pid>

# --- Debug-relevant ports opened by this session ---
lsof -iTCP:9229 -sTCP:LISTEN -nP 2>/dev/null     # Node inspector default
lsof -iTCP:5678 -sTCP:LISTEN -nP 2>/dev/null     # debugpy default
lsof -iTCP:2345 -sTCP:LISTEN -nP 2>/dev/null     # dlv default
lsof -iTCP:9999 -sTCP:LISTEN -nP 2>/dev/null     # pwndbg/gdb-server default

# --- Env var overrides in current shell ---
# Restore the journaled prior value; unset only an override created by this session.
unset <journaled-env-var>

# --- Ghidra scratch projects created by this session ---
rm -rf <journaled-ghidra-scratch-project>

# --- Core dumps created by this session ---
rm -f <journaled-core-dump>

# --- Playwright artifacts created by this session ---
rm -rf <journaled-playwright-artifact-dir>
```

### Browser sessions

When browser work is complete, close every browser, tab, or driver you opened for it. If you launched a browser process, record its PID in the journal at launch and, during cleanup, verify and stop only that recorded process; never close a user-owned browser.

### Verify the baseline

In a Git worktree, this is the single most important check of the whole skill:

```bash
git status
git diff --stat
```

The diff must contain **only**:

1. The real fix.
2. The new failing-first test.
3. Nothing else.

For a standalone target with no Git worktree, use each journaled pre-change snapshot and the completed artifact list to confirm that only the intended fix and test remain.

### Detector checklist — scan the diff for these

In a Git worktree, if `git status` shows any untracked debug file or `git diff` shows any of the patterns below, **you are not done**. Without Git, scan the files named in the journal against the same patterns and their snapshots. Remove only the journaled artifact.

| Pattern | Usually means |
|---|---|
| `debugger;` | Node debug statement left behind |
| `breakpoint()` | Python debug statement left behind |
| `dbg!(...)` | Rust debug macro left behind |
| `fmt.Println("DEBUG: ...")` | Go ad-hoc print |
| `console.log("[DEBUG]` | Node ad-hoc log |
| `print(f"DEBUG: ` | Python ad-hoc print |
| `// TODO DEBUG`, `// HACK`, `// XXX` | Stale debug marker |
| `// <PROJECT>-DEBUG` | Session-specific marker from this skill's edits |
| Commented-out code blocks near the fix | Dead code from trial fixes |
| Reordered imports or formatting in unrelated files | Drift from your editor's autoformat during the session |

### Remove the journal

Only once the baseline check is clean and every journaled artifact is checked off:

```bash
rm -rf .debug-journal .debug-journal.md
```

In a Git worktree, remove only the `.git/info/exclude` entries this session added; if that file already had user edits, restore its journal snapshot or reverse just the recorded hunk. The journal is not part of the fix and does not belong in the commit or the git exclude list.

---

## Phase 10 — Final Verification

Last gate before reporting done. All four gates must be true, and all four must have **evidence in your final message** to the user. Passing a gate without evidence is the same as failing it.

### The four gates

1. **Red→green toggle confirmed** — show the failing test output from before the fix and passing output after. Both outputs visible in the reply or the journal.

2. **Full test suite green** — show the suite's final pass line (e.g. `42 passed in 3.14s`). Not just the new test.

3. **Manual QA reproduced the fix** — show the command or scenario that originally failed and its now-correct output. Verbatim, not paraphrased.

4. **Debug artifacts removed and baseline preserved** — in a Git worktree, show `git diff --stat` containing only fix + test and `git status` clean of untracked debug files; without Git, show the completed journal artifact list and snapshot-based baseline check.

If any of the four lacks evidence, you have not finished — return to the appropriate phase.

### Final message template

Keep it short. Evidence-dense. The user should be able to skim it in 30 seconds.

```markdown
Fixed.

**Root cause**: <one sentence — the mechanism, not the symptom>
**Fix**: `<file:line>` — <two words>
**Test**: `<test file>::<test name>` — red without fix, green with fix
**QA**: <one line describing what you ran and what you saw>

Diff / baseline check:
```
<git diff --stat output (Git worktree) or journal snapshot-based baseline check (standalone target)>
```

**Next steps I didn't take** (awaiting your decision):
- <follow-up 1, if any — from QA silent-failure scan or refactor opportunities noted during Phase 7>
- <follow-up 2 — or "none" if nothing else surfaced>
```

### Example (from a real session)

```markdown
Fixed.

**Root cause**: The client library hardcoded `model.baseUrl` to `https://provider.example`, so the `SERVICE_BASE_URL` override was ignored. The proxy key was rejected upstream with 401, but the library stored the error in the response's `errorMessage` field instead of throwing, so the route's error handler never ran and the client received HTTP 200 with empty content.

**Fix**: `core/model-bridge/modelResolver.ts:117` — honor base URL
**Test**: `__tests__/core/modelResolver.test.ts::resolves_env_override` — red without fix, green with fix
**QA**: `curl -X POST /api/refinement/chat` with proxy settings, observed non-zero usage and non-empty content

Diff:
```
 core/model-bridge/modelResolver.ts           | 3 +++
 __tests__/core/modelResolver.test.ts         | 42 ++++++++++++++++++++++
 2 files changed, 45 insertions(+)
```

**Next steps I didn't take** (awaiting your decision):
- The client library silently stores upstream errors in `errorMessage`; adding a throw-on-error wrapper at the integration layer would surface them
- Same silent-failure pattern exists in the planning route — likely the same fix applies
```
