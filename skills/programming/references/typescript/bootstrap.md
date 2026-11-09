# Bootstrap — Runtime, Package Manager, Tooling

> Read this when starting a TypeScript project or configuring its runtime, package manager, and tooling.

## Runners

Bun is the default, but adapt commands to Node/npm/pnpm/yarn when the project standardizes on them; the contract is the config, not the runner.

## Runtime decision tree

```
Is this a CLI / script / single-binary tool?
└─ Yes → Bun (single executable, hot reload, native TS)
        Use `bun run script.ts` directly. No build step.

Is this a backend service?
├─ Edge (Cloudflare Workers / Vercel / Deno Deploy) → match the platform
├─ Node-only production platform (no Bun support yet) → Node + Hono
├─ Need Node-only deps (sharp, native modules Bun can't load) → Node + Hono
├─ Existing Node-only project       → Node, keep its conventions
└─ Otherwise                        → Bun + Hono (hot reload via `bun --hot`)

Is this a frontend?
└─ Vite (regardless of framework). Bun for the package manager.

Is this a library to publish to npm?
└─ tsdown (or unbuild). Targets Node 20+. Use pnpm for monorepo workspaces.

Tests: `bun test` (built in). `bunx` replaces `npx`; `bun create` scaffolds projects.
```

## Package manager — pnpm as the primary Node fallback

Prefer pnpm for new Node projects; npm or yarn are valid when project conventions or platform support require them. pnpm's strict `node_modules` layout makes phantom dependencies fail at install time, not at runtime.

To convert an npm or yarn project, run the `rm -rf` step only inside the project being migrated, after confirming via git status (or a snapshot) that no uncommitted work depends on the current install state:

```bash
pnpm import   # reads package-lock.json or yarn.lock and produces pnpm-lock.yaml
rm -rf node_modules package-lock.json yarn.lock
pnpm install
```

## Backend framework — Hono

Use Hono for any new HTTP service. It is type-safe end-to-end (request/response types flow through middleware) and runs on Bun, Node, Cloudflare Workers, Deno, and AWS Lambda.

When Hono → ALWAYS pair with `hono-openapi` + `@scalar/hono-api-reference` + `@hono/swagger-ui`. Full setup with copy-pasteable `app.ts`: [backend-hono.md](backend-hono.md).

NEVER for new services: Express, Fastify, NestJS, or bare `Bun.serve` / `node:http` without a specific reason. With bare servers you lose middleware, routing, and validation, and you reinvent everything.

## Frontend tooling — Vite

Vite for any frontend. Replaces webpack, parcel, rollup-as-app-bundler. Works with React, Vue, Svelte, Solid, Preact, vanilla.

```bash
bun create vite my-app -- --template react-ts
cd my-app
bun install
bun run dev
```

## Lint + format — Biome

Biome replaces ESLint + Prettier with one tool. The `biome.json` config lives in [TypeScript strict configuration](tsconfig-strict.md).

```bash
bun add --dev @biomejs/biome
bun biome init
```

Use ESLint only when:
- You have an ESLint plugin Biome doesn't replicate (rare in 2026)
- You're contributing to an existing ESLint project

Never run both — pick one.

## Test runner — bun test or vitest

| Runner | Use when |
|---|---|
| `bun test` | Bun project, simple unit tests, no TypeScript path aliases that need vite-style resolution |
| `vitest` | Vite-based frontend, complex test infrastructure (DOM testing, snapshot, in-browser tests), or you need vitest-specific features |

NEVER Jest for a new project. Jest's CommonJS-first design fights every modern Node/TS project.

## TypeScript

The canonical `tsconfig.json` is in [TypeScript strict configuration](tsconfig-strict.md). `noEmit: true` because the selected runner and build tool handle compilation; `tsc` is a typechecker only.

## Quick-start: Bun + Hono backend

Scaffold with the invocation in the [lane README](README.md) (Bun by default, `--runtime node` for Node), then wire the `app.ts` from [backend-hono.md](backend-hono.md).
