---
name: git-master
description: "MUST USE for ANY git operation: a commit, a git-history investigation, or working-tree/diff inspection. Load it before running git yourself, and assign it by name to any delegated node that commits. Covers atomic commits, staging, commit-message style, rebase, squash, fixup/autosquash, blame, bisect, reflog, git log -S/-G, branch/diff/status inspection, PR-body evidence attachments, and questions like 'who wrote this', 'when was X added', 'find the commit that'. Also covers WORKTREE mode: provision an isolated worktree on explicit request, with ignore handling and merge/PR/cleanup lifecycle. Do not use for ordinary code edits unless the user asks for git work."
---

# Git Master

Be exact, conservative, and evidence-led. Read the repository state before you infer anything.

## Mode Gate

Classify the request first:

- `COMMIT`: stage and commit local changes.
- `REBASE`: rebase, squash, fixup, autosquash, reorder, split, or otherwise rewrite branch history.
- `HISTORY`: answer when, where, who, why, or which commit changed something.
- `STATUS`: inspect branch, diff, or working-tree state without changing it.
- `WORKTREE`: provision an isolated worktree for work the user explicitly asked to do in a worktree.

`WORKTREE` is a setup overlay: when paired with `COMMIT` or `REBASE`, provision the worktree first and run the other mode inside it. `STATUS` stays read-only and never triggers provisioning.

Do not commit, rebase, push, force-push, reset, stash-pop, or delete anything unless the user explicitly asked for that operation. When a workflow the user started mandates one of them (a goal loop that commits each verified unit, a plan executor that lands its branches), that workflow's instruction is the ask. If the request is only investigative, report findings and stop.

## Ground Truth

Gather independent facts in parallel when the tools allow it:

```bash
git status --short
git diff --stat
git diff --staged --stat
git branch --show-current
git log -30 --oneline
git rev-parse --abbrev-ref @{upstream}
git merge-base HEAD origin/main
git merge-base HEAD origin/master
```

Missing upstream or missing `main`/`master` is normal. Fall back to the best available branch or report the missing fact. Never treat a failed lookup as proof.

## PR Body Evidence Attachments

When a PR body needs screenshots or terminal PNGs, use the host's authenticated attachment flow if available; otherwise skip attachments and say so. Never commit temporary images, never use release assets for PR evidence, and never use external image hosts. Do not log session cookies, anti-forgery tokens, upload form fields, or upload headers. The step-by-step flow is in [PR evidence attachments](references/pr-evidence.md); read it only when a PR body needs images.

## Commit Mode

Commit only the user's requested changes. Preserve unrelated dirty work.

For decision-context trailers in commit messages, use the `lore` skill.

The staging, grouping, and message-style procedure is in [Commit procedure](references/commit.md); read it when the mode is COMMIT.

## Rebase Mode

History rewriting is a shared-impact operation.

- Never rebase or rewrite `main`, `master`, `dev`, release branches, or a protected branch unless the user explicitly named that exact operation.
- If commits may already be pushed, ask before force-pushing. Use `--force-with-lease`, never plain `--force`.
- If the worktree is dirty, preserve it intentionally before rebasing. Do not stash-pop over conflicts without checking what changed.
- For fixups, prefer `git commit --fixup=<hash>` followed by `GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash <base>`.
- For conflicts, read the conflicting files and resolve by intent. Do not choose ours/theirs blindly.
- If a rebase goes wrong, use `git rebase --abort` first. Use reflog only after explaining the recovery path.

After rewriting, show the new branch log from base to HEAD.

## History Mode

Choose the Git tool by the question:

- `git log -S "text"`: when the count of an exact string changed.
- `git log -G "regex"`: when diffs touched lines matching a pattern.
- `git blame -L start,end -- file`: who last changed specific lines.
- `git log --follow -- file`: history across renames for one file.
- `git bisect`: find the first bad commit when there is a deterministic pass/fail command and known good/bad bounds.
- `git reflog`: recover or explain recent local history movement.

Always cite the exact command evidence in the answer: commit hash, subject, file path, and line or diff context when relevant. If the evidence is ambiguous, say what remains unproven.

## Status Mode

Read-only inspection: gather Ground Truth and report the state; change nothing.

## Worktree Mode

Provision an isolated worktree only when the user explicitly asks to work in one. Never create one for read-only or investigative work. The full provisioning, ignore handling, merge/PR, and cleanup lifecycle is in [Worktree lifecycle](references/worktree.md).

Core rules: anchor to the repository root and the base worktree; decide the start point and merge eligibility before provisioning; run merge and cleanup from the base worktree, never inside the feature worktree; never `git worktree remove --force`.

## Safety Checks

Before any write to Git history:

- Current branch is known.
- Dirty work is accounted for.
- Upstream/pushed status is known or explicitly unknown.
- The operation matches the user's request.
- Recovery path is known (`rebase --abort`, reflog hash, or untouched worktree).

Before finishing:

- Run the most relevant verification available for the changed behavior or history operation.
- Report commands that passed and any command you could not run.
