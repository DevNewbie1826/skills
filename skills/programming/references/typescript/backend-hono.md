# Hono Backend Stack Reference (2026)

> Read this when implementing a TypeScript HTTP service with this framework lane.

> **Canonical stack**: `hono` + `hono-openapi` + `@scalar/hono-api-reference` + `@hono/swagger-ui`
> **Runtime**: Bun (TypeScript-first)
> **Validator**: Zod v4 (Standard Schema compliant, zero extra deps for OpenAPI)

---

## 1. Package Versions (Latest Stable)

| Package | Version |
|---------|---------|
| `hono` | `^4.12.5` |
| `hono-openapi` | `^1.3.0` |
| `@scalar/hono-api-reference` | `^0.10.11` |
| `@hono/swagger-ui` | `^0.6.1` |
| `zod` | `^4.4.1` |

### `package.json` dependency block

```json
{
  "dependencies": {
    "hono": "^4.12.5",
    "hono-openapi": "^1.3.0",
    "@scalar/hono-api-reference": "^0.10.11",
    "@hono/swagger-ui": "^0.6.1",
    "zod": "^4.4.1"
  },
  "devDependencies": {
    "typescript": "^5.8.0",
    "@types/bun": "latest"
  }
}
```

> **Peer dependencies auto-installed by `hono-openapi`**:
> - `@hono/standard-validator@^0.2.0`
> - `@standard-community/standard-json@^0.3.5`
> - `@standard-community/standard-openapi@^0.2.9`
> - `openapi-types@^12.1.3`

---

## 2. Complete `app.ts` — Copy-Pasteable

```typescript
import { Hono } from 'hono'
import { describeRoute, openAPIRouteHandler, resolver, validator } from 'hono-openapi'
import { Scalar } from '@scalar/hono-api-reference'
import { swaggerUI } from '@hono/swagger-ui'
import { z } from 'zod'

// ───────────────────────────────────────────────────────────────
// 1. Schema definitions (Zod v4 — Standard Schema native)
// ───────────────────────────────────────────────────────────────

const QuerySchema = z.object({
  name: z.string().optional(),
})

const ResponseSchema = z.object({
  message: z.string(),
})

const JsonBodySchema = z.object({
  name: z.string(),
  age: z.number().int().min(0),
})

// ───────────────────────────────────────────────────────────────
// 2. Hono app with described routes
// ───────────────────────────────────────────────────────────────

const app = new Hono()

// Health check (no validation)
app.get('/health', (c) => c.json({ status: 'ok' }))

// A fully-documented route
app.get(
  '/hello',
  describeRoute({
    tags: ['Greetings'],
    summary: 'Say hello',
    description: 'Returns a greeting message',
    responses: {
      200: {
        description: 'Successful greeting',
        content: {
          'application/json': {
            schema: resolver(ResponseSchema),
          },
        },
      },
    },
  }),
  validator('query', QuerySchema),
  (c) => {
    const query = c.req.valid('query')
    return c.json({ message: `Hello ${query.name ?? 'Hono'}!` })
  },
)

// A POST route with JSON body validation
app.post(
  '/users',
  describeRoute({
    tags: ['Users'],
    summary: 'Create a user',
    responses: {
      200: {
        description: 'User created',
        content: {
          'application/json': {
            schema: resolver(ResponseSchema),
          },
        },
      },
    },
  }),
  validator('json', JsonBodySchema),
  (c) => {
    const body = c.req.valid('json')
    return c.json({ message: `Created user ${body.name}` })
  },
)

// ───────────────────────────────────────────────────────────────
// 3. OpenAPI spec endpoint
// ───────────────────────────────────────────────────────────────

app.get(
  '/openapi.json',
  openAPIRouteHandler(app, {
    documentation: {
      info: {
        title: 'Hono API',
        version: '1.0.0',
        description: 'Example Hono API with OpenAPI',
      },
      servers: [
        { url: 'http://localhost:3000', description: 'Local server' },
      ],
    },
  }),
)

// ───────────────────────────────────────────────────────────────
// 4. Scalar API Reference UI
// ───────────────────────────────────────────────────────────────

app.get(
  '/scalar',
  Scalar({
    url: '/openapi.json',
    theme: 'saturn',
    pageTitle: 'Hono API Reference',
  }),
)

// ───────────────────────────────────────────────────────────────
// 5. Swagger UI (parallel mount)
// ───────────────────────────────────────────────────────────────

app.get(
  '/swagger',
  swaggerUI({
    url: '/openapi.json',
    title: 'Swagger UI',
  }),
)

// ───────────────────────────────────────────────────────────────
// 6. Bun canonical entrypoint
// ───────────────────────────────────────────────────────────────

export default app
```

---

## 3. `hono-openapi` API

Everything is exported from the package root; there are no subpath exports such as `hono-openapi/zod`. The package uses Standard Schema and detects the validator vendor itself.

```typescript
import {
  describeRoute,      // middleware to annotate a route with OpenAPI metadata
  describeResponse,   // attach response schemas directly to a handler
  validator,          // validation middleware (wraps @hono/standard-validator)
  resolver,           // wrap a Zod/Valibot/etc schema for OpenAPI responses
  openAPIRouteHandler, // serve the generated OpenAPI JSON document
  generateSpecs,      // programmatically generate the spec (for build-time caching)
} from 'hono-openapi'
```

`validator('query' | 'json' | 'param' | 'form', Schema)` validates the target and injects the request schema into the OpenAPI document, so `describeRoute()` needs no manual `request` block. For signatures and options, see the [hono-openapi repository](https://github.com/rhinobase/hono-openapi).

---

## 4. `@scalar/hono-api-reference` Setup

```typescript
import { Scalar } from '@scalar/hono-api-reference'

app.get('/scalar', Scalar({ url: '/openapi.json' }))
```

`apiReference` is still exported but deprecated in favor of `Scalar`. The middleware accepts every Scalar API-reference option plus the Hono-specific `pageTitle` and `cdn` overrides, and it also takes a function `(c) => config` for request-aware configuration. The option list lives in the [Scalar configuration reference](https://github.com/scalar/scalar/blob/main/documentation/configuration.md).

---

## 5. `@hono/swagger-ui` Setup

```typescript
import { swaggerUI } from '@hono/swagger-ui'

app.get('/swagger', swaggerUI({ url: '/openapi.json' }))
```

Any standard Swagger UI option (`title`, `version`, `presets`, `plugins`, `urls`) also works; see the [middleware README](https://github.com/honojs/middleware/tree/main/packages/swagger-ui).

---

## 6. Bun Runtime Entrypoint

Bun serves a module whose default export is the app (`export default app`, as in section 2). To change the port, export an object instead:

```typescript
export default {
  port: 3000,
  fetch: app.fetch,
}
```

### `package.json` scripts for Bun

These match what `new-project.ts` generates (see [bootstrap](bootstrap.md)):

```json
{
  "scripts": {
    "dev": "bun --hot src/index.ts",
    "start": "bun src/index.ts",
    "build": "bun build src/index.ts --target bun --outdir dist"
  }
}
```

---

## 7. OpenAPI Version

`hono-openapi` emits **OpenAPI 3.1.0**, hardcoded and not configurable at runtime. A 3.0.x document requires post-processing the generated spec or using `@hono/zod-openapi` instead.

---

## 8. Common Pitfalls

1. **Using `openAPISpecs` instead of `openAPIRouteHandler`**
   Some docs (e.g. HONC) use `openAPISpecs` — this is **not** the current export name. The correct function is `openAPIRouteHandler` ([source](https://github.com/rhinobase/hono-openapi/blob/10f45a66ede3764b5e6065805fb60fd5df090466/src/index.ts#L1)).

2. **Importing from `hono-openapi/zod`**
   There are **no subpath exports**. Always import from `hono-openapi` directly.

3. **Forgetting `@hono/standard-validator`**
   It is a peer dependency of `hono-openapi`. Modern package managers (npm ≥ 7, pnpm, bun) auto-install it. If you see validation errors, ensure it is present in `node_modules`.

4. **Using `@hono/zod-openapi` (the OLD package)**
   This lane uses `hono-openapi` (the newer, middleware-based, Standard Schema package). Do not confuse it with `@hono/zod-openapi` which wraps the `Hono` class into `OpenAPIHono`.

5. **Swagger UI `spec` option**
   `@hono/swagger-ui` does **not** accept a `spec` option to embed the document directly. It only accepts `url` (or `urls`) pointing to an external spec endpoint. If you need embedded specs, use Scalar's `content` option instead.
