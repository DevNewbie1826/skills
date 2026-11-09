# PORTING CONTRACT — OMP skill pack (ported skills neutralized)

This repository is an **OMP skill pack** (used in Oh My Pi). It holds two kinds of skills:
**ported** skills brought from other agents, and **OMP-native** skills written for OMP.

**Ported** skills MUST be neutralized per the rules below to strip origin-agent branding
(Rules 1–3). **OMP-native** skills are exempt from the agent/model-neutrality rules
(Rule 8) — they may name and use OMP mechanisms (`eval`, `task`, `hub`, `local://`, goal
mode).

`tools/check-skills.py` (stdlib-only) enforces the machine-checkable subset; the rest is
enforced by review. A skill is done only when the checker passes AND a QA-by-read
confirms the expertise survived.

## Rule 1 — Agent neutrality (Tier A, banned in ported skills)
Banned in prose, code, comments, and (where feasible) filenames of **ported** skills
(OMP-native skills are exempt — see Rule 8):
- Names of other agent products and runtimes, their state directories and their skill names
  (a Layer-B brand design file named after a product is CONTENT).
- Other runtimes' API names and named subagent personas (the testing concept "test oracle" stays).
- This rule is enforced by review; the checker carries no name list.
- Replacement pattern: describe the CAPABILITY, not the product.
  "spawn <persona>s from orthogonal angles" ->
  "get independent adversarial reviews from orthogonal angles - parallel subagents if your
  runtime supports delegation, otherwise fresh-eyes self-review passes, one per angle".

## Rule 2 — Model neutrality (Tier A)
- No model names or families as presuppositions (enforced by review).
- No model-routing advice ("use model X for step Y").
- Layer-B brand design references named after products are CONTENT and allowed. Guidance
  files named after a model or product are NOT content - rename and generalize them
  (e.g. cinematic-taste-skill.md, image-gen-concepts-*.md, design-mockup-export-skill.md)
  and update every inbound link.
- Naming external tools as one option among several ("an image-generation model, if
  available") is neutral; presupposing one is not.

## Rule 3 — Framework & language neutrality (Tier B, routing files)
- A SKILL.md (and any routing README) must never presuppose ONE framework or ONE language.
  Allowed: enumerations of >=2 options; clearly-labeled optional lanes
  ("if your stack is React, also read references/perfection/react-perf-tooling.md").
  Banned: mandates ("React tooling installed by default", "use gin for servers").
- Per-framework/per-language deep-dives are welcome as references/ loaded on demand.
  The programming skill's per-language layout is the model to imitate.
- Where a rule is stack-shaped, phrase it stack-first: "install framework-matched dev
  tooling (react-grab/react-scan for React; the equivalent for your stack)".

## Rule 4 — Progressive disclosure (structure)
- SKILL.md <= 200 lines, frontmatter with `name` + `description` (description carries the
  triggers), body is a ROUTER: tables/bullets that say when to read which reference.
  No long tutorials, checklists, or category dumps inline - move them to references/.
- references/: each file opens with a one-line routing cue and is self-contained.
  Acceptable cue forms: a frontmatter `description` field, a line containing
  "Primary role:", or a line starting with "Read this when ..." (case-insensitive;
  a leading Markdown `>` is fine), within the first 15 lines after any frontmatter.
  A frontmatter description counts as a cue only when it is a single-line plain or simply quoted value (no escapes, no block or multi-line scalars; YAML comments after the value or on their own lines are ignored) containing at least one letter or digit; otherwise add a 'Read this when ...' line.
  `tools/check-skills.py` enforces this as ROUTING-CUE on every `*.md` under
  `references/` (any depth) for every checked skill, including OMP-native skills.
  SKILL.md and files outside `references/` are not checked. Files with none of the
  three violate.
- scripts/: bundled, self-contained, invoked via paths relative to the skill dir
  ($SKILL_DIR or "from the skill directory").

## Rule 5 — Portability
- No origin-host or user-specific paths (`/Volumes/...`, `/Users/<name>/...`,
  `/home/<user>/...`, `C:\Users\...`), no paths into the producing repository.
  Standard OS locations used as
  EXAMPLES in guidance (`/tmp`, `/etc`, `/usr`, `/Library`, `C:\Windows`) are content
  and allowed. No host-specific state dirs inside skill content.
- External tools are named with a fallback: "if X is unavailable, do Y or skip and say so".
- Cross-references may only target skills IN THIS PACK (frontend, debugging,
  remove-ai-slops, visual-qa, programming, tdd, git-master, lore, dag-workflow, seo-html) or be
  generic capability text.
  References to tools or skills outside this pack must be
  rewritten generically (e.g. "a browser-driving capability", "your planning workflow").

## Rule 6 — Fidelity
- Rewrite presuppositions, not expertise. Routing tables, triggers, checklists, and
  domain substance survive. If a rewrite weakens the guidance, keep the guidance and
  neutralize harder.

## Verification
- `python3 tools/check-skills.py` must exit 0 (tier A host paths, tier B routing balance,
  frontmatter, SKILL.md length, reference routing cues (ROUTING-CUE: non-empty
  frontmatter `description`, a "Primary role:" line, or a "Read this when ..." line
  within the first 15 lines after frontmatter), link integrity including escaping
  `..` paths, script self-containment, dangling skill refs). Allowlists, when needed, live in `tools/allowlist/*.json`
  — add only CONTENT exceptions with a reason per entry, never to silence real violations.
- Smoke: every bundled script entrypoint runs (`--help` or a tiny fixture invocation).

## Rule 7 — Host adapters live outside skill content

- Host-specific packaging (`.pi/` directories, `package.json` manifests) is allowed at the repo root as an adapter layer.
- Banned-token and neutrality rules still apply inside every **ported** skill directory (OMP-native skills are exempt per Rule 8).
- Adapters must never be referenced from skill content.

## Rule 8 — OMP-native skills are exempt from neutrality rules

- This is an OMP pack. Skills written **for OMP** are OMP-native and
  EXEMPT from Rules 1–3 (agent/model/framework neutrality): they may name and use OMP
  mechanisms (`eval`, `task`, `hub`, `local://`, goal mode, skills, extensions).
- Rules 1–3 still apply in full to **ported** skills (brought from other agents) — that is
  exactly what "neutralize on port" means.
- An OMP-native skill MUST mark itself with `omp-native: true` frontmatter so
  reviewers know the exemption applies. `tools/check-skills.py` skips Tier-A token
  checks for `omp-native: true` skills via `is_omp_native()`; never use this to silence
  real violations in ported skills.
- An OMP-native skill may ship a reference as a symlink to a prompt omp installs (it
  dangles where omp is not installed): a symlink in `references/` whose target ends in
  `@oh-my-pi/pi-coding-agent/src/prompts/<path>.md`. The checker accepts that link and does
  not read the file behind it; any other symlink that points outside the skill fails LINKS.
