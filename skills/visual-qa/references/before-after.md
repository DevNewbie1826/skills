Read this when you change an existing UI: it covers the fixed case list, the `before` captured ahead of the first edit, and the composed pairs a reviewer judges.

# Before/after mode

A redesign nobody can see beside its baseline cannot be judged, and a regression hidden in the redesign ships. This mode starts BEFORE the first edit and feeds both review passes in [Independent review passes](independent-review.md).

1. **Fix the cases before editing** and do not change them afterwards: the states that matter (typically empty, loading, populated, error, plus any state the change targets) x the widths and themes of the capture matrix in [Capture evidence](capture-evidence.md). A case discovered mid-work is added to both sides, never to `after` alone.
2. **Capture `before` on the pre-edit build**, one PNG per case with the tooling in [Capture evidence](capture-evidence.md), named `<case>-<state>-<width>-<theme>-before.png`. Seed or mock the data so every state is reachable on demand; the same seed produces `after`.
3. **Capture `after` under identical conditions** on the current build ([Capture evidence](capture-evidence.md) defines what identical means), named `<case>-<state>-<width>-<theme>-after.png`.
4. **Compose each pair** side by side into `<case>-<state>-<width>-<theme>-pair.png` (before left, after right, same scale, with a one-line caption naming the case).
5. **Hand the pairs to both review passes** (Pass B's BEFORE/AFTER PAIRS field) with the brief and the required-content list. `before` is never reconstructed after the fact; if the pre-edit build is gone, say so and report the comparison as unavailable.
