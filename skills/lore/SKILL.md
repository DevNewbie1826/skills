---
name: lore
description: "Records and queries decision context in git history. Captures constraints, rejected alternatives, confidence, directives, and test gaps as structured git trailers (the Lore protocol) and reads them back with standard git log. Use when writing commit messages for non-trivial changes, configuring a project to always use the format, or answering why a change was made. Triggers: commit message, lore, decision context, trailer, why was this changed, rejected alternatives, show constraints, show directives."
---

# Lore

Every commit casts a decision shadow: the diff survives, but the reasons do not.
Lore preserves that shadow as git trailers, so constraints, rejected alternatives,
confidence, directives, and test gaps stay queryable with plain `git log`.

## When to use

- non-obvious decisions
- rejected alternatives
- external constraints
- fragile assumptions or warnings
- known test gaps

## When not to use

- trivial commits: typo fixes, formatting-only changes, mechanical updates
- work with no decision context

## Trailer keys

`Constraint:` `Rejected:` `Confidence:` `Scope-risk:` `Reversibility:` `Directive:`
`Tested:` `Not-tested:` `Related:`. All are optional and repeatable; add one only when it
carries signal. Values, ordering, and examples live in `references/commits.md`.

## Routing

| Need | Read |
|---|---|
| writing a Lore commit message | `references/commits.md` |
| querying trailers from history (a trailer, a path, a summary) | `references/query.md` |
| making every future commit in a project or user scope use Lore | `references/setup.md` |
| commit mechanics: staging, atomic commits, rebase, history search | the `git-master` skill |
