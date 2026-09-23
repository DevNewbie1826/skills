# Designpowers Bundling Evidence

Read this when verifying that the bundled designpowers reference corpus is present, self-contained, and neutralized for this skill pack.

designpowers bundles people-centered design-process guidance: personas, research planning, debate, voice, accessible content, cognitive accessibility, taste feedback, review and testing, debt, handoff, and retrospectives. Layout, motion, interaction, platform, and token guidance live in other frontend areas — see [README.md](README.md).

The corpus was restructured from the retired vendor layout into four lane directories; [UPSTREAM.md](UPSTREAM.md) records what was moved, merged, and removed, with reasons. The portability pass intentionally adapts metadata and wording, so byte-for-byte upstream comparisons are not a valid integrity check here.

## Portable checks

Run from `references/designpowers/`:

```sh
find . -name '*.md' | sort
```

Expected: 23 Markdown files — 5 root files (`README.md`, `routing.md`, `orchestration.md`, `EVIDENCE.md`, `UPSTREAM.md`), 4 lane indexes (`lane-a-direction.md` through `lane-d-memory.md`), and 14 leaves (direction 4, execution 3, review 4, memory 3) — plus the MIT `LICENSE`.

```sh
find . -type d -name vendor
grep -rn 'vendor' --include='*.md' .
```

The first command must print nothing. The second may show only historical prose in this file, `UPSTREAM.md`, and `README.md` naming the retired vendor tree; no path-form reference may appear.

## Content checks

- Every leaf opens with its H1, a specific `Read this when ...` line, and a back-link to its lane file.
- Every lane file links each leaf in its directory with a one-line read-when.
- No hooks, scripts, hidden state directories, or runtime-specific configuration are bundled; the material is reference-only and remains subordinate to `frontend`, project rules, and user instructions.
- Removed-topic routing (layout, motion, interaction, platform, tokens) points to `references/stylegallery/` and `references/design/design-system-architecture.md`.
- `LICENSE` carries the upstream MIT notice (Copyright (c) 2026 MC Dean).
