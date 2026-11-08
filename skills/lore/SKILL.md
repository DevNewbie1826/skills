---
name: lore
description: "Use when writing git commit messages for non-trivial changes, or when querying decision context from git history. Captures constraints, rejected alternatives, confidence, directives, and test gaps as structured git trailers (the Lore protocol), and queries them with standard git log. Triggers: commit message, lore, decision context, trailer, why was this changed, rejected alternatives, show constraints, show directives."
---

# Lore

Every commit casts a decision shadow: the diff survives, but the reasons do not.
Lore preserves that shadow by encoding decision context as git trailers, so
constraints, rejected alternatives, confidence, directives, and test gaps stay queryable.

## When to use

- non-obvious decisions
- rejected alternatives
- external constraints
- fragile assumptions or warnings
- known test gaps

## When not to use

- trivial commits
- typo fixes
- formatting-only changes
- mechanical updates
- work with no decision context

## Routing

| Need | Read |
|---|---|
| writing Lore commits | `references/commits.md` |
| querying trailers from history | `references/query.md` |
| configuring always-use | `references/setup.md` |
| commit mechanics, staging, atomic commits, or history work | `git-master` |
