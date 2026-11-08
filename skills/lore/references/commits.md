Read this when writing or reviewing a commit message for a non-trivial change.

# Lore Commits

Lore trailers add decision context to a commit message. They sit after your repository's own
subject and body style; they never replace it. Follow the repository's existing subject
convention first (check `git log --oneline -20`), then append trailers.

## The format

```text
<imperative summary line>

<optional body explaining the change>

Constraint: <external constraint that shaped this decision>
Rejected: <alternative> | <reason it was rejected>
Confidence: <high | medium | low>
Scope-risk: <narrow | moderate | broad>
Reversibility: <clean | moderate | difficult>
Directive: <warning or instruction for future modifiers>
Tested: <what was verified>
Not-tested: <known coverage gaps>
Related: <commit hash or description of related commit>
```

Trailers are optional, repeatable, and may be extended with custom keys when needed.
They must form the last paragraph of the message, one `Key: value` per line, with no blank
line between them. A line indented under a trailer continues that trailer's value.

## Trailer vocabulary

| Trailer | Purpose | Example |
|---|---|---|
| `Constraint:` | External limit that shaped the decision | `Auth service does not support token introspection` |
| `Rejected:` | Alternative considered and why it was dropped | `Extend token TTL to 24h | security policy violation` |
| `Confidence:` | How sure the change is right | `high` |
| `Scope-risk:` | Blast radius of the change | `narrow` |
| `Reversibility:` | How hard it is to undo | `clean` |
| `Directive:` | Warning or instruction for future modifiers | `Do not narrow 4xx handling without verifying upstream behavior` |
| `Tested:` | What was verified | `Single expired token refresh (unit)` |
| `Not-tested:` | Known coverage gaps | `Auth service cold-start > 500ms behavior` |
| `Related:` | Linked commits forming a decision chain | `abc1234 (initial auth interceptor)` |

## Complete example

```text
Prevent silent session drops during long-running operations

The auth service returns inconsistent status codes on token expiry, so the interceptor catches all 4xx responses and triggers an inline refresh.

Constraint: Auth service does not support token introspection
Constraint: Must not add latency to non-expired-token paths
Rejected: Extend token TTL to 24h | security policy violation
Rejected: Background refresh on timer | race condition
Confidence: high
Scope-risk: narrow
Reversibility: clean
Directive: Error handling is intentionally broad (all 4xx)
  -- do not narrow without verifying upstream behavior
Tested: Single expired token refresh (unit)
Not-tested: Auth service cold-start > 500ms behavior
```

## Workflow

1. Harvest context: what constrained the work, what was rejected, what remains fragile.
2. Write the summary line around the decision, not the diff.
3. Add a body only when the how needs explanation.
4. Append trailers, one per decision fact; keep only signal. To add them without editing the
   message by hand: `git commit --trailer "Confidence: high" --trailer "Rejected: alt | reason"`.
5. Self-check: would a future modifier benefit from this context?
6. Confirm the trailers parse: `git log -1 --format='%(trailers:only)'` must list each one.

Reading trailers back is in `references/query.md`.

## Common mistakes

| Mistake | Fix |
|---|---|
| Writing trailers as prose paragraphs | Use `Key: value` on separate lines |
| Putting trailers before the body | Put trailers after the body, separated by a blank line |
| Blank line between trailers, or text after them | Keep them as one final paragraph, or git will not parse them |
| Omitting the reason in `Rejected:` | Use `alternative | reason` |
| Adding trailers to trivial commits | Reserve them for non-trivial decisions |
| Duplicating diff content in trailers | Capture the why, not the what |
| Using `Confidence: yes` | Use `high`, `medium`, or `low` |
