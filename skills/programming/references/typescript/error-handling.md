# Error Handling

> Read this when designing, returning, converting, or handling typed errors in TypeScript.

Typed errors, exhaustive matching, the Result pattern, and catch discipline.

---

## Typed errors — no bare strings

Error classes carry structured data. Callers know exactly what can go wrong.

```typescript
class UserNotFoundError extends Error {
  readonly name = "UserNotFoundError"
  constructor(readonly userId: UserId) {
    super(`user ${userId} not found`)
  }
}

class PermissionDeniedError extends Error {
  readonly name = "PermissionDeniedError"
  constructor(
    readonly userId: UserId,
    readonly requiredRole: string,
  ) {
    super(`user ${userId} needs role ${requiredRole}`)
  }
}
```

```typescript
// BAD
throw new Error("user not found")
throw new Error("permission denied")

// GOOD
throw new UserNotFoundError(userId)
throw new PermissionDeniedError(userId, "admin")
```

Always set `readonly name` explicitly: `instanceof` survives minification, and a stable `error.name` keeps logs and serialized errors readable.

---

## Result pattern — expected failures without exceptions

For failures that are **expected** and handled within 1-2 call levels (not found, a domain rule), return a discriminated union instead of throwing.

```typescript
type Result<T, E = Error> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E }

function ok<T>(value: T): Result<T, never> {
  return { ok: true, value }
}

function err<E>(error: E): Result<never, E> {
  return { ok: false, error }
}
```

### Usage

```typescript
type UserError =
  | { readonly kind: "not_found"; readonly id: UserId }
  | { readonly kind: "forbidden"; readonly reason: string }

function getUser(id: UserId): Result<User, UserError> {
  const user = db.find(id)
  if (!user) return err({ kind: "not_found", id })
  if (!user.active) return err({ kind: "forbidden", reason: "deactivated" })
  return ok(user)
}

// Caller must handle both cases
const result = getUser(userId)
if (!result.ok) {
  switch (result.error.kind) {
    case "not_found":
      log.warn(`missing: ${result.error.id}`)
      break
    case "forbidden":
      log.error(`denied: ${result.error.reason}`)
      break
    default:
      assertNever(result.error)
  }
  return
}
const user = result.value  // narrowed to User
```

### When to use which

| Scenario | Pattern | Why |
|---|---|---|
| Repository → service (caller handles it) | Result | Caller is right there, must handle both |
| Validation at boundary (parsing input) | throw (Zod throws) | Propagates up to HTTP handler |
| Infrastructure failure (network, OOM) | throw | Can't handle locally |
| Service → service (deep internal) | throw (typed Error subclass) | Result boilerplate across many layers is worse |
| HTTP handler → response | Catch errors, convert to response | Boundary code catches and translates |

Use Result when the caller is 1-2 levels away and must handle the failure; a typed Error subclass when it would propagate through 3+ layers unchanged.

### Library or roll your own?

Roll your own with the `Result`, `ok`, `err` above. It's 10 lines. Libraries like `neverthrow` add chaining (`.map`, `.andThen`) — use them only if you actually chain results frequently.

---

## Error cause — chain context

Use the `cause` option to chain errors without losing the original stack.

```typescript
try {
  await db.query(sql)
} catch (error) {
  throw new DatabaseError("query failed", { cause: error })
}
```

The `cause` is available on `error.cause` and shows up in stack traces.

---

## Catch blocks — narrow or re-throw

Every `catch` receives `unknown`. The language gives you no type safety in catch blocks; you earn it with `instanceof`. A bare `catch (e) { console.error(e) }` swallows `TypeError`, `RangeError`, and your domain errors identically, and when a new error type appears nothing warns you.

```typescript
// BANNED — empty catch
try { await fetchData() } catch {}
try { await fetchData() } catch (e) { /* will fix later */ }

// BANNED — catch-and-swallow (no narrowing, no rethrow)
try {
  const data = await api.get("/users")
} catch (e) {
  console.error("failed", e)
}

// GOOD — narrow with instanceof
try {
  const data = await api.get("/users")
} catch (e) {
  if (e instanceof HttpError) {
    logger.warn(`API ${e.status}: ${e.message}`)
    return fallback
  }
  throw e  // unknown errors propagate
}

// GOOD — top-level boundary (only place catch-all is acceptable)
async function main(): Promise<void> {
  try {
    await run()
  } catch (e) {  // no-excuse-ok: catch
    console.error("unhandled:", e)
    process.exit(1)
  }
}
```

---

## Exhaustive error handling at boundaries

HTTP handlers catch and translate:

```typescript
app.onError((error, c) => {
  if (error instanceof UserNotFoundError) {
    return c.json({ error: error.message }, 404)
  }
  if (error instanceof PermissionDeniedError) {
    return c.json({ error: error.message }, 403)
  }
  console.error("unhandled:", error)
  return c.json({ error: "internal server error" }, 500)
})
```

---

## Async error patterns

```typescript
// Promise.allSettled — when partial failure is OK (ky is the lane's HTTP client)
const results = await Promise.allSettled(urls.map((url) => ky.get(url)))
const successes = results
  .filter((r): r is PromiseFulfilledResult<Response> => r.status === "fulfilled")
  .map((r) => r.value)

// AbortSignal — cancellation
async function getWithTimeout(url: string, ms: number): Promise<Response> {
  return ky.get(url, { signal: AbortSignal.timeout(ms) })
}
```

---

## Sources

- MDN: [Error cause](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error/cause)
- MDN: [Promise.allSettled](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/allSettled)
