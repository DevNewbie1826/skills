# Copy and Suppression Rules

> Read this when TypeScript copy text or suppression comments need checking.

Two checks keep user-facing copy readable and suppression comments honest. Both read source text only; neither runs the compiler.

## `no-em-dash-copy`

Flags an em dash (U+2014) in `.ts`, `.tsx`, `.mts`, or `.cts` copy outside comments.

In `.tsx` files, quoted text that sits between tags is JSX copy, not a string literal: a quote there does not hide the rest of the file, whether the text sits inside an element or directly inside a fragment. Attribute strings, expression containers, and plain `.ts` code keep their normal string handling.

A long dash reads as typographic decoration in CLI output, log lines, and error messages. A period, comma, colon, or parentheses carries the same meaning without the flourish.

Message: `em dash in copy: use a period, comma, colon, or parentheses instead`

```typescript
// BAD
console.log("build failed — retry with --force")

// GOOD
console.log("build failed. Retry with --force")
```

## `require-suppression-reason`

Flags a bare suppression directive in a comment. The directive matcher accepts generic `<word>-disable`, `<word>-enable`, `<word>-ignore`, and `<word>-suppress` forms, so it stays tool-neutral without naming any tool. A directive whose convention carries no reason text is still flagged: append the reason as a trailing phrase naming the constraint. The reason must sit on the directive's own line; a reason written on a later line of a block comment does not count.

A suppression is a claim that a rule does not apply here. Without a written reason the next reader cannot tell a deliberate exception from a stale workaround.

Message: `suppression directive without a reason: say why it does not apply`

```typescript
// BAD
// linttool-disable

// GOOD
// linttool-disable: generated table, spacing is fixed upstream
```

## Usage

Run from the skill directory:

```bash
bun scripts/typescript/check-copy-rules.ts [--json] <file-or-dir>...
```

- Exit `0`: no findings.
- Exit `1`: at least one finding. Findings print to stdout as `path:line rule message`.
- Exit `2`: input error, such as a missing path.

`--json` prints the same findings as machine-readable records. The script uses Node built-ins only and needs no third-party packages.

## Equivalence with the other lanes

An equivalent reason requirement already exists in this pack's Go checker (`nolint-no-reason` in `scripts/go/check-no-excuse-rules.sh`) and Rust checker (`expect-without-reason` in `scripts/rust/check-no-excuse-rules.py`). This TypeScript rule mirrors their posture: a reasoned suppression is legal, a bare one is not. The TypeScript no-excuse checker additionally bans `@ts-ignore` and `@ts-expect-error` outright in this pack's own TS lane, and that stricter rule is unchanged.
