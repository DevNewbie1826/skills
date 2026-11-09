# Code Smells — Full Reference

> Read this when a source file, function, verification step, or name triggers a design smell.

When any of these smells is detected, **STOP and re-examine your design.** A code smell is not a syntax error — it is a signal that the current structure deserves a second look. The correct response is to assess whether `/refactor` is warranted, fix the smell, or document a SPECIFIC justification for carrying it. "It's fine" is not a justification.

---

## Smell 1 — File exceeds 250 pure LOC

Two bands apply. Past 200 pure LOC, treat the file as a warning: name its responsibility and plan a split before the next growth. Past 250 pure LOC, it is a defect, handled by the rules below.

### Measuring pure LOC

```bash
# Quick (line-comment + blank exclusion):
awk '!/^[[:space:]]*$/ && !/^[[:space:]]*(\/\/|#|--)/' <file> | wc -l

# Authoritative (handles block comments correctly):
cloc --by-file <file>   # the "code" column is the number
```

### Required behavior when detected

**Creating a file that will exceed 250 pure LOC.** Split it before the first commit. Carve by responsibility, one cohesive unit per file. Use a barrel (`__init__.py`, `mod.rs`, `index.ts`) for re-exports ONLY — never for logic.

**Editing a file that already exceeds 250 pure LOC and your edit adds lines.** Refactor the unit you are touching into its own file BEFORE adding the new lines. The split is part of THIS task, not a follow-up someone will never do.

**Reading a file that exceeds 250 pure LOC while implementing a feature.** Surface the smell in your reply, propose a concrete split, and ask the user whether to split now or carry the smell.

### Forbidden escapes

- Counting comments and blank lines toward the budget. **Pure LOC means code lines.**
- Splitting by token count (`foo_1.py`, `module_part_A.rs`, `service-2.ts`). Split by what each file DOES.
- Catch-all dump files: `utils.py`, `helpers.ts`, `lib.rs` (as a logic dump), `common.py`, `shared.ts`.
- "It's generated, so it's fine." Only true if the file lives in `dist/`, `target/`, `__generated__/`.
- "It's a test file with many cases." Split by SUT or by behavior cluster.
- "230 pure LOC, close enough." A 230-LOC file about to grow is already at the limit. Split now.

### Acceptable exceptions (rare, require justification)

A file may legitimately exceed 250 pure LOC if **and only if** it is:

- A truly indivisible single-responsibility unit (e.g., a generated parser table, a state machine whose states share a single closure). Mark it in the first 10 lines with `# noqa: SIZE_OK — <reason>` in Python (the form `scripts/python/check-no-excuse-rules.py` reads) or `// allow: SIZE_OK — <reason>` in `//`-comment languages.
- A pure data table (translation strings, error code lookup, brand color palette).

A SIZE_OK marker without a justifying comment is itself slop.

### Concrete split examples

#### Python — BEFORE (`user_service.py`, 412 pure LOC)

```python
# user_service.py — DOES TOO MUCH
class UserRepository: ...        # 90 LOC of SQLAlchemy
class UserValidator: ...         # 60 LOC of Pydantic + business rules
class PasswordHasher: ...        # 40 LOC of bcrypt wrapper
class EmailSender: ...           # 50 LOC of httpx2 client
class UserService: ...           # 130 LOC orchestrating the four above
def _build_query(...): ...       # 25 LOC helper
def _format_email(...): ...      # 17 LOC helper
```

#### Python — AFTER (split by responsibility)

```
src/myapp/users/
├── __init__.py              # barrel: re-exports UserService only (5 LOC)
├── repository.py            # UserRepository                 (~95 LOC)
├── validator.py             # UserValidator                  (~65 LOC)
├── password.py              # PasswordHasher                 (~45 LOC)
├── notifier.py              # EmailSender (renamed — the role, not the verb)
├── service.py               # UserService (orchestrator)     (~135 LOC)
└── _queries.py              # _build_query (private)         (~30 LOC)
```

---

## Smell 2 — Function with more than three independent parameters

### Why 3

A function's parameters are its contract with every caller. More than 3 independent inputs overwhelm the caller's working memory and signal one of two design problems:

1. **The function does too much.** It should be two functions.
2. **Related parameters belong together.** They should be a typed struct/object — a domain concept, not a parameter bag.

### Workaround detection: these count as the same smell

Disguising parameter count does not fix the design. The following patterns are the same smell wearing a different hat:

**Dict/map smuggling:**
```python
# SMELL — hiding 6 args in a dict
def create_order(params: dict[str, Any]) -> Order: ...
```

**Variadic/kwargs catch-all:**
```python
# SMELL — hiding real params behind kwargs
def send_notification(recipient: str, **kwargs) -> None: ...
```

**Config object that wraps positional args:**
```python
# SMELL — "options" object that exists only to bundle what would be positional args
@dataclass
class CreateUserOptions:
    name: str
    email: str
    password: str
    role: str
    department: str
    manager_id: int
    # 6 fields, used by exactly one function, no defaults

def create_user(opts: CreateUserOptions) -> User: ...
```

**When the options object is NOT a smell:** when it represents a genuine domain concept reused across multiple call sites with sensible defaults for most fields (e.g., `HttpClientConfig`, `DatabaseConnectionOptions`, `RetryPolicy`).

### The fix

Group related parameters into typed value objects with domain names:

```python
# CLEAN — grouped by domain concept
@dataclass(frozen=True)
class UserIdentity:
    name: str
    email: str

@dataclass(frozen=True)
class OrgPlacement:
    role: str
    department: str
    manager_id: int

def create_user(identity: UserIdentity, placement: OrgPlacement, password: str) -> User: ...
# 3 params, each a meaningful concept
```

If 4+ truly independent inputs are required, justify it — the justification must name WHY these inputs cannot be grouped, not just "the function needs them all."

---

## Smell 3 — Redundant verification after a destructive or write action

### Why this is slop

**The contract of the operation IS the verification.** If a delete, remove, clear, drop, or write returns without error, the effect happened; a setter followed by its getter, a write read back, or an insert re-selected is the same defect. Re-querying to "confirm" is:

1. **Dead code.** The check can never fail unless the operation itself is broken — in which case fix the operation, not the caller.
2. **Misleading.** It teaches the next reader (human or AI) that the operation is unreliable.
3. **Performance waste.** An unnecessary round-trip to the database, filesystem, or data structure.

This pattern is the hallmark of AI-generated defensive bloat. LLMs produce it because they optimize for "looking thorough" over "being correct." **Recognize it. Delete it.**

### Examples

```python
# SLOP — delete then verify deletion
db.delete(user)
db.commit()
remaining = db.query(User).filter_by(id=user.id).first()
assert remaining is None  # the ORM already guaranteed this

# CLEAN
db.delete(user)
db.commit()
```

If you cannot trust the operation's return, the defect is in the operation — fix it there, not at the call site.

---

## Smell 4 — Negative-form names and conditions

### Why positive form wins

Every negation forces the reader to mentally invert. One negation is tolerable. Two (`if !isNotReady`) is a logic puzzle. Codebases that default to negative naming accumulate double and triple negations that nobody can review confidently.

Positive form reads in the direction of intent: "is this ready?" rather than "is this not-not-ready?"

### Naming

| Negative (SMELL) | Positive (CLEAN) |
|---|---|
| `isNotValid` | `isValid` (invert branch) |
| `isDisabled` | `isEnabled` |
| `noErrors` | `isClean` / `errorsResolved` |
| `notFound` | `found` (invert branch) |
| `isNotEmpty` | `hasItems` / `isPopulated` |
| `missingAuth` | `hasAuth` / `isAuthenticated` |
| `cannotProceed` | `canProceed` (invert branch) |

Name the **presence** of the quality you care about, not the absence of its opposite.

### Conditions

```python
# SMELL — double negative
if not is_invalid(token):
    proceed()

# CLEAN — single positive check
if is_valid(token):
    proceed()
```

### When negation IS appropriate

- **Early returns / guard clauses:** `if !authorized { return Err(...) }` — the negative form IS the intent (reject the bad case).
- **Filtering out:** `items.filter(|x| !x.is_expired())` — the negation describes the keep/discard decision directly.
- **Error state names:** `Error`, `Failed`, `Timeout` are negative concepts by nature — do not force them into positive wrappers like `isSuccessAbsent`.

The rule is not "never use negation." The rule is: **when you have a choice between naming the presence and naming the absence, name the presence.** The branch logic follows from the name, not the other way around.
