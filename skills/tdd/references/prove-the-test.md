> Read this when a new or reshaped test is written and you must show it can fail, or a mutation survives.

# Prove the Test Can Fail

A test earns its place by failing. After writing it, break the production owner on purpose and watch the test go red. The mutation check in [the cycle](cycle.md) is the quick mental version; this is the executed version.

## Procedure (per new or reshaped test)

1. **Break the owner**: flip the condition, drop the branch, return a constant, or skip the write. Confirm the mutated bytes are really in the file before reading the result (diff or grep it) — a no-op edit "passes" exactly like the original.
2. **Red for the intended reason?** Read the failure message. A loose assertion can match an unrelated generic error and give a false red; a fake that simulates the failure by a different mechanism than the guard reads can fail with the fix present.
3. **Still green?** One of four causes:
   - the test is vacuous — fix the assertion;
   - the mutant is equivalent (a try/catch, fallback, or normalization maps it back to the same outcome) — retarget the mutation at the observable claim;
   - a second rule already produces the same outcome — make the input exercise only the rule under test and assert the recorded reason;
   - the mutated code is dead — delete the code, not the test's teeth.
4. **Restore byte for byte.** Never commit a mutation. If your tooling has a mutation runner, use it; otherwise use a scratch branch or stash and verify a clean diff afterwards.

## Vacuous assertion shapes

| Vacuous shape | Why it passes with the bug present | Discriminating shape |
|---|---|---|
| expected value derived from the output under test | compares a projection of the output to itself | derive the expected value from the test's input |
| override fixture equal to its fallback | precedence is never exercised | every value the code must select or override differs from the fallback |
| lower bound (`>= n`, `> 0`) over independently produced items | removing one item still satisfies the bound | pin the exact set |
| count after deduplication where duplicates are byte-identical to a mandatory item | dropping all duplicates gives the same count | distinct payloads; assert retention and placement |
| the argv, flags, URL, or request handed to a child component | an input transcript, not the child's outcome | drive the real component and assert the state it resolved, with a control case |
| counter or filter keyed on a value the code path never produces | both sides count zero | count the operation itself |
| a copy of the production component, props, or allowlist | the copy passes while the shipped one is broken | import or mount the real one |
| timing assertion for an off-thread or performance claim | passes on the base at fixture size | prove performance on a realistic harness; keep the unit test to behavior |
| a gated or fallback path tested without forcing it | the base's own error path produces the same side effect | force the path (flag, crash limit) and assert the reason the new path records |

## Briefing another test author

When someone else writes the tests, hand them the behavior the test must distinguish ("fails if override precedence breaks"), never a ready-made assertion string or marker to copy: a prescribed mechanism that is wrong gets implemented as written and ships behind a green suite.
