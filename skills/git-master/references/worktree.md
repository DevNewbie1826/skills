Read this when the user explicitly asks to work in a worktree. It is the detail behind the `WORKTREE` mode in [SKILL.md](../SKILL.md). Never use this for read-only or investigative work.

`WORKTREE` is a setup overlay: when paired with `COMMIT` or `REBASE`, provision the worktree first and run the other mode inside it. `STATUS` is read-only and never triggers provisioning.

The commands below are a procedure, not a script. Read each block, adapt the variables, and run the lines in order. They anchor to the repository root and the base worktree (the checkout you started in), so they stay correct from a subdirectory or from inside an existing linked worktree. Branch refs are always fully qualified (`refs/heads/...`) to avoid ambiguity with tags or other ref namespaces.

**Operating principle:** after every state-changing command, verify the result against the expected state; on any mismatch or failure, stop and preserve the worktree rather than guessing. This catches partial failures (e.g. a `post-checkout` hook that exits nonzero after the worktree and branch are already created) and stale refs (work committed on a detached HEAD).

# Worktree lifecycle

## Entry condition

Enter only on an explicit user request: "work in a worktree", "isolate this in a worktree", or equivalent. A task that merely touches files is not a worktree request. When unsure, ask once; do not provision speculatively.

## 0. Preconditions — capture and guard the base

```bash
root=$(git rev-parse --show-toplevel 2>/dev/null) \
  || { echo "no working tree here (bare repo?); cannot provision a worktree." >&2; exit 1; }
base_worktree=$(git rev-parse --show-toplevel)
git rev-parse --verify -q HEAD >/dev/null \
  || { echo "HEAD does not resolve (unborn branch / no commits). Commit first, then retry." >&2; exit 1; }
base_branch_ref=$(git symbolic-ref -q HEAD || true)          # refs/heads/<branch>, empty if detached
```

- `base_branch_ref` is the full `refs/heads/<name>`; record it. The worktree will live under `$root/.worktrees/<name>`.
- Warn if the base worktree is dirty. Use `--untracked-files=all` so a `status.showUntrackedFiles=no` config does not hide content:

```bash
git -C "$base_worktree" status --untracked-files=all --short
```

Uncommitted changes do **not** follow into the worktree; proceed only after the user confirms.

## 1. Start point and merge eligibility — decide before provisioning

The **Merge** outcome can only update the branch captured in `base_branch_ref`, and only when the worktree was started from a branch (not a commit or remote ref). A worktree cannot merge into a branch checked out elsewhere.

Choose `start_point` and set `can_merge`:

- User named a **branch** → `start_point` is that branch; `can_merge=yes` when `base_branch_ref` is non-empty, else `no`.
- User named a **commit** or remote ref → `start_point` is that ref; **`can_merge=no`** (no local base branch to merge into); offer only PR or Keep.
- `base_branch_ref` is empty (detached HEAD) → `start_point=HEAD`; **`can_merge=no`**; offer only PR or Keep.
- Otherwise → `start_point=$base_branch_ref`; `can_merge=yes`.

## 2. Ignore `.worktrees/` — local-first, then verify

Resolve the **common** exclude path absolutely (works from a subdirectory and inside a linked worktree), append the pattern on its own line, then **verify with `git check-ignore`** — a tracked-root `.gitignore` negation (`!.worktrees/`) can override `info/exclude`, so the append alone is not a guarantee:

```bash
exclude=$(git -C "$base_worktree" rev-parse --path-format=absolute --git-path info/exclude)
grep -qxF '.worktrees/' "$exclude" 2>/dev/null || printf '\n.worktrees/\n' >> "$exclude"
git -C "$root" check-ignore ".worktrees/" >/dev/null \
  || echo "WARNING: .worktrees/ is not ignored (a .gitignore negation may override info/exclude). Add an ignore rule before proceeding, or expect the worktree to show as untracked." >&2
```

Commit to `.gitignore` only when the user **separately and explicitly** asks to commit that change for a team-wide convention. Agreement to the convention is not agreement to commit; without an explicit commit request, leave the `.gitignore` edit uncommitted and report it.

## 3. Provision — probe, then create once, verify state

`<name>` is a short meaningful slug the user supplies or you derive from the task. Probe for a free name, then create in a single `git worktree add`. Do not auto-retry: if creation fails, report the error and let the user choose a different name — a blind retry loop cannot distinguish a collision from a bad start point or a failing hook.

First check the prefix is usable, then probe path and exact branch ref (test the path with `-e` **or** `-L`, since a dangling symlink still blocks the add):

```bash
git -C "$root" show-ref --verify --quiet refs/heads/worktree \
  && { echo "refs/heads/worktree exists; the worktree/ prefix is unusable. Choose a different prefix." >&2; exit 1; }

name="$1"   # slug
path="$root/.worktrees/$name"
if git -C "$root" show-ref --verify --quiet "refs/heads/worktree/$name" \
   || { [ -e "$path" ] || [ -L "$path" ]; }; then
  echo "name '$name' is taken (branch ref or path). Choose another." >&2; exit 1
fi
```

Create, then verify the resulting state. A `post-checkout` hook can exit nonzero **after** the worktree and branch are created, so on failure check whether they exist and preserve rather than telling the user to try another name:

```bash
if ! git -C "$root" worktree add "$path" -b "worktree/$name" "$start_point"; then
  if git -C "$root" show-ref --verify --quiet "refs/heads/worktree/$name" || git -C "$root" worktree list --porcelain | grep -Fxq -- "worktree $path"; then
    echo "provisioning reported failure but the worktree/branch were created (likely a hook). Preserving; inspect $path and refs/heads/worktree/$name." >&2
  else
    echo "provisioning failed; not retrying. Check start_point and name." >&2
  fi
  exit 1
fi
git -C "$root" show-ref --verify --quiet "refs/heads/worktree/$name"
```

Never use a timestamp suffix.

## 4. Switch the working directory explicitly

`git worktree add` does **not** change the caller's working directory. Set the session/tool cwd to `$path`, then confirm you are inside the new worktree. `git rev-parse --show-toplevel` canonicalizes the path, so if `.worktrees` is a symlink it prints the resolved target — compare against the resolved path, not the lexical one:

```bash
# set the tool/session cwd to "$path", then:
top=$(git rev-parse --show-toplevel)
[ "$top" = "$path" ] || [ "$top" = "$(cd "$path" && pwd -P)" ] \
  || { echo "cwd is not the new worktree ($top != $path)" >&2; exit 1; }
```

State the new working directory. All `COMMIT` rules apply to commits made here. `base_branch_ref` is untouched until the user chooses an outcome.

## 5. Outcome — verify everything, then act

Present the choices; do not pick silently. Run each against `$base_worktree`, never inside the feature worktree. Use fully-qualified refs so a tag like `worktree/<name>` cannot resolve ahead of the branch.

**Before any outcome, run the pre-outcome verification gate.** It re-checks the refs that may have drifted during task work. If the feature worktree left its branch (work committed on a detached/other HEAD), `refs/heads/worktree/$name` is stale and a merge/push would succeed while the real commit dangles — so stop and preserve:

```bash
# feature worktree still on its branch?
[ "$(git -C "$path" symbolic-ref -q HEAD)" = "refs/heads/worktree/$name" ] \
  || { echo "feature worktree HEAD is no longer refs/heads/worktree/$name; work may be on a detached/other HEAD. Preserve the worktree and reconcile before any outcome." >&2; exit 1; }
# base worktree still on its branch?
[ "$(git -C "$base_worktree" symbolic-ref -q HEAD)" = "$base_branch_ref" ] \
  || { echo "base worktree HEAD is no longer $base_branch_ref; not proceeding." >&2; exit 1; }
```

- **Merge** — only when `can_merge=yes`. The base working tree must be clean of **tracked** changes (`git merge` refuses a dirty tracked tree). **Clobber risk to be aware of:** a merge silently overwrites or deletes an ignored/untracked base file (e.g. an ignored `.env`, or a directory collision where a tracked file replaces an ignored `config/` dir) if the feature branch introduces that path as tracked. Before merging, confirm no ignored base file shares a path the feature adds; if one does, move it aside first.

  ```bash
  [ "$can_merge" = "yes" ] || { echo "Merge not available for this start point; use PR or Keep." >&2; exit 1; }
  base_dirty=$(git -C "$base_worktree" status --short --untracked-files=no 2>&1) || { echo "base status check failed: $base_dirty" >&2; exit 1; }
  [ -z "$base_dirty" ] || { echo "base worktree has tracked changes; commit or stash before merge." >&2; exit 1; }
  git -C "$base_worktree" merge --ff-only "refs/heads/worktree/$name"
  ```

  For a non-fast-forward merge, use `git -C "$base_worktree" merge "refs/heads/worktree/$name"`; if it exits nonzero (conflict), resolve the conflicts or run `git -C "$base_worktree" merge --abort`, then preserve the worktree and report — do not proceed to cleanup with the base worktree in a conflicted state.

  Never check the base branch out inside the feature worktree — Git refuses the same branch in two worktrees.

- **PR** — confirm the remote does not already have a branch of the same name (a push would fast-forward a stranger's branch instead of opening a fresh PR), then push the fully-qualified ref. Treat a remote-probe failure as a stop, not permission:

  ```bash
  ls_rc=0; git -C "$base_worktree" ls-remote --exit-code origin "refs/heads/worktree/$name" >/dev/null 2>&1 || ls_rc=$?
  case "$ls_rc" in
    0) echo "origin already has refs/heads/worktree/$name; choose a different name or coordinate." >&2; exit 1 ;;
    2) ;;  # ref absent — proceed
    *) echo "remote probe failed (exit $ls_rc); not pushing blindly." >&2; exit 1 ;;
  esac
  git -C "$base_worktree" push -u origin "refs/heads/worktree/$name:refs/heads/worktree/$name"
  ```

- **Keep** — leave the worktree and branch in place; skip cleanup.

## 6. Cleanup — from the base worktree, outcome-dependent

First return the session cwd to `$base_worktree`. Then take stock with `--untracked-files=all --ignored` so a `status.showUntrackedFiles=no` config does not hide content:

```bash
git -C "$path" status --untracked-files=all --ignored --short
```

`git worktree remove` without `--force` **refuses** modified, staged, or untracked (non-ignored) content, but **silently deletes ignored content** (`.env`, secrets, build output). So:

- If modified/staged/untracked content appears, require the user to commit, stash, or choose Keep — confirmation alone will not let a no-force removal proceed.
- If only ignored content appears, warn and require the user to confirm or choose Keep before removing.

Remove the worktree (never `--force` over user data):

```bash
git -C "$root" worktree remove "$path"
```

Delete the branch **only after a successful Merge**, as separate steps so a failed ancestry check cannot be misread as success:

```bash
if [ -n "$base_branch_ref" ] \
   && git -C "$root" merge-base --is-ancestor "refs/heads/worktree/$name" "$base_branch_ref"; then
  git -C "$root" branch -d "worktree/$name" \
    || echo "branch -d refused (often the upstream has not advanced). The merge into the base branch is confirmed by the ancestry check; delete with -D only on an explicit user request."
else
  echo "ancestry check failed or no base branch; retaining refs/heads/worktree/$name." >&2
fi
```

After a **PR**, **retain** the branch — it is not merged into the base branch. A `push -u` may set its upstream to its own remote twin, which can make `branch -d` succeed without base integration, so do not use `-d` after a PR. A later deletion requires the full cleanup sequence — **remove the worktree first** (a checked-out branch cannot be deleted), then `git -C "$root" branch -D "worktree/$name"` on an explicit user request with confirmation.

On merge/PR failure or user cancellation, **preserve** the worktree. State that it remains for recovery and show `git -C "$root" worktree list`.

> Note on `git branch -d`: it checks integration into the configured upstream (or `HEAD` with none), never the base branch directly. Do not infer base integration from it — verify with `merge-base --is-ancestor` before deleting after a Merge.

## Safety invariants

- Never `git worktree remove --force` over uncommitted or ignored changes.
- Never delete the base branch or a branch you did not create in this mode.
- Never provision without a captured, non-empty `root`, a resolvable `HEAD`, known `base_branch_ref`, and a chosen `start_point` with its `can_merge` flag.
- Never assume a failed command left no state — verify worktree/branch existence after a provisioning failure and preserve if they exist.
- Never run merge, removal, or branch deletion from inside the feature worktree; target `$base_worktree` / `$root`.
- Never run an outcome without the pre-outcome verification gate (feature worktree still on its branch; base worktree still on `base_branch_ref`).
- Never merge unless `can_merge=yes` and the base is clean of tracked changes. Before merging, confirm no ignored base file shares a path the feature branch adds (clobber risk).
- Never push a PR branch without first confirming the remote lacks `refs/heads/worktree/$name`.
- Never proceed to cleanup with the base worktree in a conflicted merge state; abort the merge first.
- Never auto-retry provisioning on failure; report and let the user choose a new name.
- Never use short branch names in merge, push, or ancestry checks; fully qualify `refs/heads/...`.
- Never assume `.worktrees/` is ignored just because you appended to `info/exclude`; verify with `check-ignore`.
- Never assume `git branch -d` proves base integration; verify with `merge-base --is-ancestor`.
- Never use `git branch -d` after a PR; the push-upstream can make it succeed without base integration. Remove the worktree first, then `-D` on explicit request.
- Delete the worktree branch only after a successful Merge with a passing ancestry check; retain it after PR.
- Every provisioning must end with a stated outcome (merged / PR / kept / preserved-on-failure); an unaccounted worktree is a leak.
- Leave the worktree state explicit at the end: `git -C "$root" worktree list` and the final branch status.
