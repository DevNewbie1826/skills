# PORTING CONTRACT — OMP skill pack (ported skills neutralized)

This directory is an **OMP skill pack** (used in Oh My Pi). It holds two kinds of skills:
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
- Agent products/runtimes: senpi, omo (incl. `.omo/`), sisyphus, codex, opencode,
  claude code, aider, windsurf, amp, droid, openclaw, codegraph, cursor-the-IDE
  (the Layer-B brand file `frontend/references/design/cursor.md` is allowlisted CONTENT),
  and omo-specific skill names: ulw-loop, ultrawork, ulw-plan, ulw-research, start-work,
  review-work, hyperplan, prometheus, boulder.
- Agent-runtime API names: subagent_type, fork_context, wait_agent, followup_task,
  interrupt_agent, list_agents, load_skills, team_create/team_wait, "Oracle" as a named
  subagent persona (the testing concept "test oracle" stays).
- Replacement pattern: describe the CAPABILITY, not the product.
  "spawn Oracles from orthogonal angles" ->
  "get independent adversarial reviews from orthogonal angles - parallel subagents if your
  runtime supports delegation, otherwise fresh-eyes self-review passes, one per angle".

## Rule 2 — Model neutrality (Tier A)
- No model names/families as presuppositions: gpt-*, claude, gemini, kimi, qwen, deepseek,
  opus, sonnet, haiku, o1/o3, dall-e, midjourney, imagen, stitch.
- No model-routing advice ("use model X for step Y").
- Layer-B brand design references named after products (claude.md, cursor.md) are CONTENT:
  allowed, allowlisted by path. Guidance files (e.g. gpt-tasteskill.md, imagegen-*.md,
  stitch-skill.md) are NOT content - rename and generalize them
  (e.g. cinematic-taste-skill.md, image-gen-concepts-*.md, design-mockup-export-skill.md)
  and update every inbound link.
- Naming external tools as one option among several ("an image-generation model such as
  Imagen, DALL-E, or Midjourney, if available") is neutral; presupposing one is not.

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
  Acceptable cue forms: a frontmatter `description` field, an opening "Primary role:"
  line, or a literal "Read this when ..." line. Files with none of the three violate.
- scripts/: bundled, self-contained, invoked via paths relative to the skill dir
  ($SKILL_DIR or "from the skill directory").

## Rule 5 — Portability
- No origin-host or user-specific paths (`/Volumes/...`, `/Users/<name>/...`,
  `/home/<user>/...`, `C:\Users\...`), no paths into the producing repository
  (`script/qa/...`, `packages/shared-skills/...`). Standard OS locations used as
  EXAMPLES in guidance (`/tmp`, `/etc`, `/usr`, `/Library`, `C:\Windows`) are content
  and allowed. No host-specific state dirs (`.omo/`, `.senpi/`) inside skill content.
- External tools are named with a fallback: "if X is unavailable, do Y or skip and say so".
- Cross-references may only target skills IN THIS PACK (frontend, debugging,
  remove-ai-slops, visual-qa, programming, tdd, git-master, lore, dag-workflow) or be
  generic capability text.
  References to open-design, agent-browser, ulw-plan, start-work, review-work etc. must be
  rewritten generically (e.g. "a browser-driving capability", "your planning workflow").

## Rule 6 — Fidelity
- Rewrite presuppositions, not expertise. Routing tables, triggers, checklists, and
  domain substance survive. If a rewrite weakens the guidance, keep the guidance and
  neutralize harder.

## Verification
- `python3 tools/check-skills.py` must exit 0 (tier A tokens, tier B routing balance,
  frontmatter, SKILL.md length, link integrity including escaping `..` paths, script
  self-containment, dangling skill refs). Allowlists live in `tools/allowlist/*.json`
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
