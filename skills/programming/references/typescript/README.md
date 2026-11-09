
# TypeScript Programmer

> Read this when writing or reviewing TypeScript source, packages, configuration, or services.

Modern TypeScript: type-strict, boundary-aware, and async-correct.

## Philosophy

The compiler is your proof system. Make illegal states unrepresentable. Parse at boundaries. Every function has a contract; the type system enforces it.

## Hard rules

These are deliberate project choices. Violations are always wrong, not "style preferences".

### Tooling

| Category | Use | Constraints |
|---|---|---|
| Runtime | Bun, Node, tsx, or ts-node | Match the project's deployment target and existing runtime |
| Package manager | bun, npm, pnpm, or yarn | Preserve the project's lockfile and package-manager convention |
| Linter + formatter | Biome | ESLint, Prettier |
| Type checker | `tsc --noEmit` with strict config | do not skip type checking |
| Web framework | Hono | Express |
| Validation | Zod | joi, yup, class-validator |
| Testing | `bun test` or vitest | jest |
| ORM | Drizzle | TypeORM, Prisma (unless already in project) |

### The iron list

1. **Readonly by default** — all `type`/`interface` properties are `readonly`. Arrays are `readonly T[]`. Exceptions: [data modeling](data-modeling.md).
2. **Branded types for distinct IDs** — `type UserId = Brand<string, "UserId">`. Never pass raw `string` where a branded type exists.
3. **Exhaustive switch** — every `switch` on a discriminated union ends with `default: assertNever(x)`. No fall-through.
4. **No any** — `any` is banned in annotations, returns, and parameters. Use `unknown` and narrow.
5. **No type assertions** — `as any`, `as unknown` banned. `as const` and `satisfies` are fine.
6. **No non-null assertion** — `x!` is banned. Use narrowing or optional chaining (`x?.y`).
7. **No @ts-ignore / @ts-expect-error** — fix the type.
8. **No enum** — use `as const` objects + literal union types.
9. **Zod at boundaries** — external input (API, user, file) → Zod schema. Internal → plain types.
10. **Typed errors** — Error subclasses with typed fields. No `throw new Error("bare string")` for domain errors. Use Result for expected failures within 1-2 call levels; throw for propagation across many layers.
11. **as const for constants** — module-level constant objects and arrays use `as const`.
12. **import type** — type-only imports use `import type`. Enforced by `verbatimModuleSyntax`.
13. **Named exports only** — no `export default`. Exception: framework entrypoint requirement (e.g. Hono's `export default app`, Next.js pages).
14. **No empty catch, no catch-and-swallow** — every `catch` block must either (a) narrow the error with `instanceof` and handle each case, or (b) re-throw. Empty catch blocks and `catch (e) { console.error(e) }` without narrowing or re-throw are banned — they hide bugs. At top-level boundaries (CLI entry, HTTP handler), opt out with `// no-excuse-ok: catch`. Rationale and examples: [error handling](error-handling.md).

### Data modeling — which construct, when

| Situation | Use |
|---|---|
| User input, API request/response | Zod schema + `z.infer` |
| Internal value object | `type` with `readonly` properties |
| Function with multiple outcomes | Discriminated union (`kind` field) |
| Contract for implementations | `interface` |
| Fixed constants | `as const` + literal union |
| Distinct primitive (UserId vs OrderId) | Branded type |
| Key-value map | `Record<K, V>` or index signature |

**The one rule**: data crosses a trust boundary → Zod. Everything else → plain `type` with `readonly`.

Load [data modeling](data-modeling.md) for the full decision flowchart and comparison.

### Libraries

| Domain | Library | Why |
|---|---|---|
| HTTP framework | Hono | Lightweight, multi-runtime, middleware, OpenAPI |
| Validation | Zod | Runtime validation + type inference |
| ORM | Drizzle | Type-safe SQL, no codegen |
| HTTP client | `ky` | Thin fetch wrapper (5KB); auto-throw on non-2xx, retry, timeout, hooks, prefixUrl. Browser + Node + Bun + Deno |
| HTTP client (perf) | `undici` (direct API) | When a Node backend needs connection pooling, HTTP/2, or pipelining |
| Testing | `bun test` / vitest | Fast, ESM-native |
| Logging | `pino` | Structured JSON, fast |
| CLI | `@clack/prompts` + `commander` | Interactive + parsing |

> **HTTP client rule**: production code must not use bare `fetch()`. It has no retry, timeout, or error-handling policy and causes silent failures during incidents. Install **`ky`** by default, and use the **`undici`** direct API when a Node backend needs high-volume requests, connection pooling, HTTP/2, or pipelining. ~~`axios`~~ is forbidden after the supply-chain compromise (2026-03). `node-fetch` is unnecessary because Node 18+ includes built-in fetch.

## Scaffolding

Scaffold a new project with all strict defaults pre-configured:

```bash
# Default Bun variant
bun run ../../scripts/typescript/new-project.ts my-api
bun run ../../scripts/typescript/new-project.ts my-api --path ./projects

# Node and npm variant
node ../../scripts/typescript/new-project.ts my-api --runtime node
```

The default emits Bun scripts and types; `--runtime node` emits npm scripts, `tsx`, Node types, and the Hono Node server adapter. Creates: `package.json` (Hono + Zod + Biome), `tsconfig.json` (ultra-strict), `biome.json`, `src/index.ts`, `.gitignore`, `README.md`, and `tests/smoke.test.ts` in the Bun variant.

The canonical `tsconfig.json` and `biome.json`, with what each extra flag catches, live in [TypeScript strict configuration](tsconfig-strict.md).

## Reference loading

Load on demand — not all at once.

| Need | Load |
|---|---|
| Strict tsconfig + Biome config | [tsconfig-strict.md](tsconfig-strict.md) |
| Type patterns (branded, as const, satisfies, narrowing, assertNever) | [type-patterns.md](type-patterns.md) |
| Data modeling (type vs interface vs Zod, readonly, parse-don't-validate) | [data-modeling.md](data-modeling.md) |
| Error handling (Result, typed errors, union vs throw) | [error-handling.md](error-handling.md) |
| Bootstrapping a new project (runner options, Hono, Vite) | [bootstrap.md](bootstrap.md) |
| Hono backend stack (hono-openapi, Scalar, Swagger) | [backend-hono.md](backend-hono.md) |
| Copy and suppression rules | [copy-rules.md](copy-rules.md) |

## No-excuse audit

Violations caught by `../../scripts/typescript/check-no-excuse-rules.ts`. Run after every edit session.

| Rule ID | Opt-out |
|---|---|
| `no-any-assertion` | None |
| `no-unknown-assertion` | None |
| `no-ts-ignore` | None |
| `no-ts-expect-error` | None |
| `no-enum` | None |
| `no-non-null-assertion` | None |
| `no-throw-literal` | None |
| `no-mutable-export` | None |
| `no-any-annotation` | `// no-excuse-ok: any` |
| `no-explicit-any-return` | `// no-excuse-ok: any` |
| `empty-catch` | `// no-excuse-ok: catch` |
| `catch-without-narrowing` | `// no-excuse-ok: catch` |

### Copy and suppression audit

Violations caught by `../../scripts/typescript/check-copy-rules.ts` (`no-em-dash-copy`, `require-suppression-reason`). Run after editing copy or a suppression comment; rules and messages: [copy rules](copy-rules.md).

Run: `bun ../../scripts/typescript/check-copy-rules.ts .`

## In tests

Tests are strict too, with these exceptions (configure in `biome.json` overrides):

| In tests you may | Why |
|---|---|
| Use `expect()` assertions | That's how testing works |
| Use magic numbers | Test data |
| Skip readonly on test fixtures | Mutable setup/teardown |

Tests still follow the iron list — branded types, typed errors, exhaustive switch — and the authoring gate in [`../testing/README.md`](../testing/README.md). Private members are reached through the public boundary, never by bracket notation: a test on internals is an implementation mirror.

## Existing codebases

When editing an existing file that doesn't follow these rules: **write new code in strict style, don't refactor existing code in the same change.**

## Activation

This reference applies to `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs`, and `.cjs`. JavaScript uses the same lint and formatting rules, while the copy checker scans only `.ts`, `.tsx`, `.mts`, and `.cts`; TypeScript-only syntax and compiler gates apply to TS or checked JS projects. Even one-off scripts get the strict treatment.
