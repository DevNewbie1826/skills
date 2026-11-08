Read this when deciding whether a changed unit is slop, choosing a safe cleanup, or handling a module-size violation.

# Slop categories

## Safety frame

Work only within the agreed scope. First lock observable behavior with green regression tests; see [workflow.md](workflow.md) for the required sequence. When a change is not obviously behavior-preserving, keep the code and report the concern. Preserve public APIs, type information, intentional error handling, and project conventions.

Apply the deletion ladder before category work:

1. **Delete entirely** when behavior is unnecessary, speculative, or dead on arrival.
2. **Reuse** an existing project helper or established pattern when it already owns the behavior.
3. **Use platform, standard-library, runtime, or installed-dependency support** instead of a hand-rolled equivalent.
4. **Simplify in place** only when the code must remain.

For a bug-fix diff, inspect callers of each shared function it changes. Prefer a root-cause fix at the shared seam over repeated caller-side guards that leave sibling callers broken.

Evaluate all ten categories below in this order: obvious comments, dead code, over-defensive code, duplication, excessive complexity, needless abstraction and boundary violations, performance equivalences, missing tests, oversized modules. Keep separate changes reviewable; do not bundle unrelated refactors.

## 1. Obvious comments

Remove comments that merely restate the code, trivial docstrings, section dividers, commented-out code, and vague TODO or note comments.

Keep comments that explain **why**: business rules, edge cases, workarounds, ticket links, regular-expression or algorithm rationale, and behavior-driven test markers such as given/when/then. Do not remove rationale merely because the implementation looks obvious today.

## 2. Over-defensive code

Look for null checks on guaranteed values, exception handling around operations that cannot fail in context, runtime type checks on statically constrained parameters, defaults for required parameters, obsolete compatibility shims, and validation repeated at multiple layers. Also inspect broad exception catches and catch blocks that only log or suppress an unknown error.

Keep validation at system boundaries, including user input, external services, I/O, and nullable persisted fields. A top-level boundary catch-all can be valid when it logs explicitly and rethrows or otherwise preserves the contract.

Refactor broad handling to the specific expected failure. Narrow an unknown caught value before handling known cases, and rethrow unknown cases rather than silently absorbing them.

**Proof requirement:** before deleting validation or error handling at a trust boundary, add an adversarial regression using malformed or hostile input that would fail if the guard disappeared. Without that proof, the guard stays. A removable defense duplicates a check already enforced inside the boundary; an unproven guard may be load-bearing.

## 3. Excessive complexity

Look for nesting beyond three levels, nested ternaries, boolean expressions with four or more predicates, parameter lists longer than five values without a parameter object, functions longer than roughly fifty lines with multiple responsibilities, and clever one-liners that obscure intent.

Also inspect variant-discrimination chains such as repeated `if` / `else if` checks on type, enum, or literal values. Prefer an exhaustive match or switch with an explicit unreachable fallback appropriate to the language. In languages with broad `object`-style annotations, use a structural contract, generic type parameter, or explicit union when that more accurately expresses the accepted value.

Keep established local complexity patterns and intentional hot-path idioms. Ordinary boolean or range `if`/`else` decisions are not variant discrimination.

Refactor nested conditionals toward guard clauses or early returns, and expand complex ternaries into clear branches. Do not trade one opaque construct for another.

## 4. Needless abstraction

Remove pass-through wrappers, single-use helpers, speculative indirection, interfaces with one implementation that add no testability benefit, and factory functions that only call a constructor.

Keep abstractions with a real seam: multiple implementations, testability, a required framework boundary, or an established project convention. Do not introduce a replacement abstraction merely to shorten a local function.

## 5. Boundary violations

Look for imports that cross the wrong architectural layer, handlers containing domain work that belongs in a service layer, modules reading another module's private state, and side effects hidden in functions named as pure computations.

Keep pragmatic short-circuits already established by the project. When ownership is uncertain, flag the issue for human judgment instead of moving code speculatively.

## 6. Dead code

Remove unused imports, unused private functions or methods, unreachable branches, stale feature flags, debug output, and code that was removed conceptually but remains referenced or copied.

Keep code reached through reflection, dynamic dispatch, configuration, or string lookup. Verify with the owner before removing an intentional rollback path behind a feature flag.

## 7. Duplication

Consolidate copy-pasted branches with trivial differences, redundant helpers that implement the same behavior, and repeated literal or magic-number sequences when they represent one shared concept.

Keep incidental similarity when the pieces serve different intents or may need to diverge. Prefer separate clear code over a premature shared abstraction.

## 8. Performance equivalences

Apply only changes with obvious semantic equivalence and a clear time or space benefit. Typical candidates include:

- Replacing repeated linear membership scans with a set lookup when duplicate and ordering semantics remain correct.
- Hoisting invariant computation out of a loop.
- Avoiding an intermediate collection when a one-pass iterator suffices.
- Replacing loop-based string concatenation with an appropriate join operation.
- Batching redundant database or service calls made inside a loop.
- Removing redundant deep copies or clones.
- Caching a collection length that is repeatedly recomputed inside a loop when mutation cannot change it.

Do not alter an algorithm whose correctness has subtle implications. Do not micro-optimize a hot path without a benchmark. If equivalence requires a proof rather than direct inspection, skip the optimization.

## 9. Missing tests

For behavior exposed by changed source files, find existing coverage and add the narrowest regression test that pins observable output, side effects, errors, or edge cases before cleanup begins. Do not pin private implementation details.

A prose file, prompt, rule, or markdown document has no behavioral seam by itself. Do not add word-count or phrase-pinning tests for prose. Test only a machine-consumed value through its real parser, validator, or runtime behavior; otherwise rely on review.

## 10. Oversized modules

A source file over **250 pure LOC** is an architectural defect, not a style preference. Pure LOC means non-blank, non-comment lines. Use the project's configured size checker when available; otherwise count those lines with an available line-counting tool and state the method used.

When a file exceeds the limit, do not merely flag it:

1. Check the entire scope for other size violations using the project checker or a documented equivalent.
2. Identify distinct responsibilities using the single-responsibility principle.
3. Plan a split whose file names describe the concepts they own, never generic catch-all names such as `utils`, `helpers`, `common`, or numbered fragments.
4. Present the split plan before executing it.
5. Extract clean modules and keep package-entry files limited to exports where that packaging pattern applies.
6. Recheck every affected source file against the 250 pure-LOC limit, then run tests, type checking, and linting.

Forbidden escapes include counting blanks or comments toward the budget, splitting by token count rather than responsibility, hiding code in a catch-all module, and claiming generated status unless the file is actually in a build-output directory. A 230-line module that is about to grow should be split now.

Keep a genuinely self-contained, single-responsibility script when appropriate. Use the project's explicit size-exception convention only within the first five lines and only with a comment explaining why.

## Per-file cleanup brief

When another reviewer or delegated worker evaluates a file, give it the complete category context above and require this result:

- Run the deletion ladder first.
- Evaluate every category and respect its KEEP and proof rules.
- Work in the prescribed safest-to-riskiest order.
- Preserve behavior, public APIs, type information, and exception behavior.
- Add no dependency or speculative abstraction.
- For each edit, report the category, before/after, why it is slop, and why the change is safe.
- For each skipped issue, report the reason.
