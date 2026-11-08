Read this when you need to query Lore trailers from git history.

# Lore Query

Run the commands with your runtime's shell tool, from inside the repository.

## Usage forms

| Ask for | Do this |
|---|---|
| A specific trailer type | Query that trailer name |
| A file or directory scope | Add the path after `--` in the git log command |
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

Specific trailer (`--grep` pre-selects candidates, `%(trailers:key=...)` prints only that trailer and joins folded lines, and the `awk` filter drops commits whose trailer block came out empty):

```bash
git log -n 20 --all --grep="^TRAILER_NAME:" --format="%h %s%n%(trailers:key=TRAILER_NAME,unfold)" -- [PATH] | awk 'BEGIN{RS="";FS="\n";ORS="\n\n"} NF>1'
```

Summary mode (every commit that carries at least one Lore trailer, with all its trailers):

```bash
git log -n 20 --all -E --grep="^(Constraint|Rejected|Confidence|Scope-risk|Reversibility|Directive|Tested|Not-tested|Related):" --format="%h %s%n%(trailers:key=Constraint,key=Rejected,key=Confidence,key=Scope-risk,key=Reversibility,key=Directive,key=Tested,key=Not-tested,key=Related,unfold)" -- [PATH] | awk 'BEGIN{RS="";FS="\n";ORS="\n\n"} NF>1'
```

Replace `TRAILER_NAME` with the mapped trailer key. Omit `-- [PATH]` when no path scope is needed.
`--grep` also matches a trailer-looking line inside the body, but `%(trailers)` reads only the final paragraph; such a commit prints a heading with no trailer lines, and the `awk` filter removes it. Without the filter, report only commits that show a trailer line.
Summary mode prints only the nine Lore keys, so unrelated trailers such as `Signed-off-by:` never appear and cannot hide a body-only lookalike.

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
