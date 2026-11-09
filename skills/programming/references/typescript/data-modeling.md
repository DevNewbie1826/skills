# Data Modeling

> Read this when modeling TypeScript boundary input, domain values, or serialized data.

Which construct to use, how to structure data, and why readonly is the default.

---

## Decision flowchart

```
Is it a fixed set of named constants?
  YES → as const object + literal union type
  NO ↓
Is it just branding a primitive (string, number)?
  YES → Branded type
  NO ↓
Is it an interface / contract?
  YES → interface (structural typing is the default in TS)
  NO ↓
Does the data cross a trust boundary (user input, API, file)?
  YES → Zod schema + z.infer<typeof schema>
  NO ↓
Is it a union of possible outcomes?
  YES → Discriminated union (kind/type field)
  NO ↓
Is it structured data with named fields?
  YES → type alias with readonly properties
  NO → you probably don't need a new type
```

---

## Container reference

### type alias — internal data

The default for structured data inside your codebase. Zero runtime cost.

```typescript
type User = {
  readonly id: UserId
  readonly name: string
  readonly email: string
}

type Point = {
  readonly x: number
  readonly y: number
}
```

All properties `readonly`. Mutable only when mutation is the documented purpose.

### interface — contracts and extension

Use when you need declaration merging or `extends`.

```typescript
interface Repository<T> {
  get(id: string): Promise<T | null>
  save(entity: T): Promise<void>
}

interface UserRepository extends Repository<User> {
  findByEmail(email: string): Promise<User | null>
}
```

### interface vs type — when to use which

| Use | When |
|---|---|
| `type` | Union types, intersections, mapped types, utility types, internal data shapes |
| `interface` | Contracts that will be `implements`ed or `extends`ed, declaration merging needed |
| **`type` (default)** | **Unless declaration merging or `implements` is needed** |

### Zod schema — trust boundary guardian

Use when data enters your system. Validates at runtime, infers types at compile time.

```typescript
import { z } from "zod"

const CreateUserSchema = z.object({
  name: z.string().min(1),
  email: z.email(),
  age: z.number().int().min(0),
})
type CreateUser = z.infer<typeof CreateUserSchema>

const UserResponseSchema = z.object({
  id: z.uuid(),
  name: z.string(),
  email: z.string(),
})
type UserResponse = z.infer<typeof UserResponseSchema>
```

**The one rule**: data crosses a trust boundary → Zod. Everything else → plain type/interface.
Never use Zod for internal-only data. The runtime validation cost and Zod coupling are unnecessary.

### as const and discriminated unions

Fixed constants use `as const` + a literal union (replaces `enum` entirely); multiple outcomes use a discriminated union with a `kind` field. Both are illustrated in [type patterns](type-patterns.md).

---

## Readonly by default

Every property is `readonly` unless mutation is the documented purpose.

```typescript
// DEFAULT — readonly
type Config = {
  readonly apiUrl: string
  readonly timeout: number
}

// Arrays too
function getUsers(): readonly User[] { ... }

// Utility for existing types
type ReadonlyUser = Readonly<User>
type ReadonlyConfig = Readonly<Config>  // shallow: one level only
```

Readonly does not apply to:

- **Framework state** (React `useState`, signals) — managed by framework.
- **Builder / accumulator** — object exists to be mutated (buffer, cache). Document why.
- **ORM mutations** — Drizzle insert/update objects.

For mutable state (rare), document why:

```typescript
/** Counter state — mutation is the entire purpose. */
type CounterState = {
  count: number  // intentionally mutable
}
```

---

## Parse, don't validate

Validate at the boundary. Inside the boundary, types are proof of validity.

```typescript
// BAD — validate then pass raw data
function processEmail(email: string): void {
  if (!email.includes("@")) throw new Error("invalid")
  // still a raw string downstream
}

// GOOD — parse into a branded value at the boundary
// (Zod brand recipe: "Branded types" in type-patterns.md)
const EmailSchema = z.email().brand("Email")
type Email = z.infer<typeof EmailSchema>

function sendWelcome(email: Email): void { ... }

// Boundary code
const parsed = EmailSchema.parse(rawInput)  // Email or throws
sendWelcome(parsed)  // no re-validation needed
```

---

## Sources

- TypeScript Handbook: [Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)
- Zod: [docs](https://zod.dev)
- Total TypeScript: [Type vs Interface](https://www.totaltypescript.com/type-vs-interface-which-should-you-use)
