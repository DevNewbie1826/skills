Read this when you change an existing UI: the fixed case list, the `before` captured ahead of the first edit, and the composed pairs a reviewer judges.

# Before/after mode

A redesign nobody can see beside its baseline cannot be judged, and a regression hidden in it ships. This mode starts BEFORE the first edit and feeds the visual review pass in [Independent review passes](independent-review.md).

1. **Fix the cases before editing** and do not change them afterwards: the states that matter (typically empty, loading, populated, error, plus any state the change targets) x the widths (web: 390 and 1440, plus 1920 for page layouts; a TUI: the column counts it supports, such as 80 and 120; paged output: each page size it prints to) x the theme(s) the surface ships. A case discovered mid-work is added to both sides, never to `after` alone.
2. **Capture `before` on the pre-edit build**, one PNG per case with the tooling in [Capture evidence](capture-evidence.md), named `<case>-<state>-<width>-<theme>-before.png`. Seed or mock the data so every state is reachable on demand; the same seed produces `after`.
3. **Capture `after` under identical conditions** on the current build (tooling, viewport, scroll position, theme, data, state), named `<case>-<state>-<width>-<theme>-after.png`.
4. **Compose each pair** side by side into `<case>-<state>-<width>-<theme>-pair.png` (before left, after right, same scale, a one-line caption naming the case), and run `image-diff <before.png> <after.png>` to aim the reviewer at what moved.
5. **Hand the pairs to the visual pass** (its BEFORE/AFTER PAIRS field) with the brief and the required-content list; its pair check judges improvement and regression. The pairs go into the report and the PR body. `before` is never reconstructed after the fact; if the pre-edit build is gone, say so and report the comparison as unavailable.

The `before` set is the one deliberately old artifact: it is dated to the pre-edit build on purpose and is exempt from the freshness rule.
