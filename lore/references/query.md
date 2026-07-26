---
name: lore-query
description: "Read this when you need to query Lore trailers from git history."
---

# Lore Query

Read this when you need to query decision context from git history.

## Usage forms

Run via your runtime's shell tool.

| Ask for | Do this |
|---|---|
| A specific trailer type | Query that trailer name |
| A file or directory scope | Add the path to the git log command |
| A summary of recent Lore context | Use the summary-mode command |

The user may say the trailer name in Korean, English, or the full trailer key. Map the shortcut to the trailer before querying.

## Trailer shortcuts

| Shortcut | Trailer |
|---|---|
| 제약조건, constraints | `Constraint:` |
| 리젝, rejected | `Rejected:` |
| 디렉티브, directive | `Directive:` |
| 미테스트, not-tested | `Not-tested:` |
| 테스트, tested | `Tested:` |
| 신뢰도, confidence | `Confidence:` |
| 범위위험, scope-risk | `Scope-risk:` |
| 가역성, reversibility | `Reversibility:` |
| 관련, related | `Related:` |

## Queries

Specific trailer:

```bash
git log -n 20 --all --grep="^TRAILER_NAME:" --format="%h %s%n%b" -- [PATH]
```

Summary mode:

```bash
git log -n 20 --format="%h %s%n%b"
```

Replace `TRAILER_NAME` with the mapped trailer key. Omit `-- [PATH]` when no path scope is needed.

## Output format

Return a compact list grouped by commit:

```text
a1b2c3d Prevent silent session drops
  Constraint: Auth service does not support token introspection
  Constraint: Must not add latency to non-expired-token paths

f4e5d6c Add rate limiter to external API calls
  Constraint: Rate limit 100 req/s on external API
```

If no Lore trailers are found, say so clearly.

## Read-only note

This skill only reads git history. It does not modify commits, refs, or the working tree.
