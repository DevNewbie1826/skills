---
name: lore-setup
description: "Read this when you want to configure Lore commit formatting in a project or global instruction file."
---

# Lore Setup

Read this when you want all future commit messages in a scope to follow the Lore protocol.

## Setup flow

Ask two questions:

1. **Scope:** project or global?
2. **Target file:** which instruction file should receive the rules?

Defaults:

| Scope | Default target |
|---|---|
| Project | `AGENTS.md` |
| Global | your runtime's user-level instruction file |

If the global instruction file name is unknown, ask the user before writing anything.

## Config content

Append this block to the chosen file. If a Lore section already exists, skip the write and say so.

````markdown
## Commit Messages: Lore Format

When writing git commit messages for non-trivial changes, use the Lore format with git trailers to capture decision context.

Format:
- Imperative summary line (focused on *why*, not *what*)
- Optional body explaining the change
- Git trailers (all optional — include only those that carry signal):

| Trailer | Purpose |
|---------|---------|
| `Constraint:` | External limit that shaped the decision |
| `Rejected:` | Alternative considered and why (`alt \| reason`) |
| `Confidence:` | `high` / `medium` / `low` |
| `Scope-risk:` | `narrow` / `moderate` / `broad` |
| `Reversibility:` | `clean` / `moderate` / `difficult` |
| `Directive:` | Warning or instruction for future modifiers |
| `Tested:` | What was verified |
| `Not-tested:` | Known coverage gaps |
| `Related:` | Linked commits forming a decision chain |

Trailers are repeatable. Do NOT add trailers to trivial commits (typo fixes, formatting).

Example:
```
Prevent silent session drops during long-running operations

The auth service returns inconsistent status codes on token expiry, so the interceptor catches all 4xx responses and triggers an inline refresh.

Constraint: Auth service does not support token introspection
Rejected: Extend token TTL to 24h | security policy violation
Confidence: high
Scope-risk: narrow
Directive: Do not narrow 4xx handling without verifying upstream behavior
Tested: Single expired token refresh (unit)
Not-tested: Auth service cold-start > 500ms behavior
```

Reference: https://arxiv.org/abs/2603.15566
````
