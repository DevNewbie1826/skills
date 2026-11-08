> Read this when deciding whether a test is worth keeping, cleaning up a suite, or reviewing tests in a diff.

# Junk Test Classes and the Retention Bar

A test that matches a class below is junk unless the retention bar keeps it. A test that would be deleted in review is a test not to write. Deleting junk is a fix, not a coverage loss, but needs the proof rule at the end.

## Marks (one per test; one per row when table rows differ)

| Mark | Meaning | Record |
|---|---|---|
| `R` retain | guards a contract | the contract and the regression it catches |
| `F` fix | real contract, weak assertion | the repaired assertion |
| `C` consolidate | the assertion moves into a keeper (a table row, a stronger boundary test) | the keeper |
| `D` delete | no contract, or another test owns it | the owner test that still fails on the regression (or why no contract exists), plus a proof receipt |

## Junk classes

| Class | What it looks like | Proof that it is junk |
|---|---|---|
| Cannot fail | no assertion; value compared to itself; expectation computed by the code under test; assertion in a callback that never runs | a mutation of the owner the test survives |
| Change certificate | pins the diff, not a behavior: a constant, a string, a rename, a call | revert the change: it fails for the diff, not a regression |
| Mock echo | the mock returns the value the test then asserts | mutate the owner: stays green |
| Implementation mirror | asserts call order, call count, private helper arguments, internal state shape | a keeper at the real boundary catches the behavioral mutation |
| Prose pin | asserts wording, headings, section order, snapshots, or length of docs, prompts, or rule text | no runtime behavior to mutate |
| Copied inventory | a hard-coded list of exports, files, or keys mirroring the source | a generator, freshness check, or real consumer already owns it |
| Source grep | reads a source file and greps for a string or import | an identifier-only refactor turns it red; a behavior mutation it misses |
| Duplicate contract | same input and output asserted at two layers with no distinct transport or lifecycle risk | the mutation is caught by both: keep the stronger boundary |
| Layer replay | a shared helper re-tested through every wrapper that calls it | one helper test plus one wiring test per real wrapper |
| Seam keeper | exists to keep a test-only export, flag, getter, or reset hook alive | no production caller: delete test and seam together |
| Fabricated postcondition | the fixture supplies the state the owner should produce | mutate the writer: stays green |
| Capability restatement | asserts a flag or capability is true instead of the delivery it promises | a delivery test owns it, or none exists (then `F`, not `D`) |
| Input transcript | asserts the request handed to a child, not the state the child resolved; not junk when the emitted command or payload is itself the contract (one command, right collaborator, right payload) | mutate the child's handling of the input: stays green |
| Misnamed | the name promises a behavior its inputs never exercise | read the assertions; mark by what they check |
| Near-duplicate cases | N tests differing only in input literals | `C` into one table; every old assertion stays a row |

## Retention bar (stays `R` even when a class matches)

Keep a test that independently guards a public API or protocol, config schema or default, migration, storage format, security boundary, platform behavior, shipped-copy equality between real artifacts, a generated or cross-language contract, an install or release payload, or an architecture invariant — and say which one in the test. Also keep:

- **Issue regressions**: a test naming an issue stays until another test is shown to fail on that exact regression.
- **Machine-consumed text**: parsed fields, sentinel tokens, tool names, schema keys, a routing-bearing fragment of a parsed frontmatter description.
- **Baseline-red tests**: a test failing on the unchanged base is a product bug to fix at its owner, never a deletion.

Static or slow is never a reason to delete.

## Proof rule for `D` and `C`

Break the production owner and run the candidate and its named keeper on the unmodified tests ([the procedure](prove-the-test.md)):

| Candidate | Keeper | Verdict |
|---|---|---|
| green | red | candidate cannot catch this: `D` proven |
| red | red | candidate redundant for this behavior: `D` or `C` proven |
| red | green | candidate is the only proof: `R`, or `C` it into the keeper and re-run |
| green | green | the mutation missed the behavior: confirm the edit landed, then pick another mutation |

One shared red mutation is not enough to delete or consolidate: run the keeper against every mutation the candidate guards (each branch, boundary, and side effect it asserts), and fold in any the keeper misses before removing the candidate. Restore the owner byte for byte. A prose pin needs no mutation: the receipt is the assertion line plus the rule against pinning prose. Coverage diffs prove lines execute, not that anything asserts on them; pair one with at least one mutation per theme.
