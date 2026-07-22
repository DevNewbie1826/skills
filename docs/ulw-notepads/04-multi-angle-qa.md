# Ultrawork Notepad — multi-angle QA + deslop of the merged skill pack
Started: 2026-07-21
## Tier: HEAVY (user demanded 꼼꼼한 검수 + cleanup edits; reviewer loop)
## Angles (4 read-only auditors, parallel): consistency / progressive disclosure / intent fidelity / AI-slop (dogfooding pack's own remove-ai-slops categories)
## Criteria: see ulw-loop goal below. Fixes delegated after triage; auditors re-verify; final checker GREEN.
## Now: spawning auditors
## Baseline before audit: checker GREEN; SKILL.md sizes below
SUPPRESSED: 59
      94 debugging/SKILL.md
     154 frontend/SKILL.md
     104 git-master/SKILL.md
     116 programming/SKILL.md
      52 remove-ai-slops/SKILL.md
      52 visual-qa/SKILL.md
     572 total

## Auditors: audit-consistency st? audit-disclosure st? audit-intent st? audit-slop st? (spawned, background)
## Audit triage (4 angles)
intent: 5/6 OK; debugging MISMATCH (3 blockers: unlisted-runtime dead-end, git-assumed journal, git-checkout cleanup can erase user edits). NIT lighthouse-audit 1-run vs median docs.
disclosure: 3 blockers (ui-ux-db web/google-fonts/threejs+angular+laravel dead CSV routes) + 16 nits (INDEX euphemisms hide claude/cursor, missing entries, count lie 9v8, stale manifest claim, double-hop patterns index, ui-ux-db README/search.py drift).
slop: 14 blockers (37 designpowers vendor orphans, claude/cursor orphan labels, 46-copy pattern boilerplate, brand iteration preamble dup, philosophy/workflow/greenfield dups, motion axiom vs review-workflow conflict, taste-skill scope contradiction, bootstrap 6x verbatim fallback, image-to-code dup closing) + 5 nits (inflated prose, floor/fire vs --threshold 95, restated comments).
consistency: child died mid-run -> respawned audit-consistency-2 for verdict only.
## Overrules (reasons recorded)
- Reject splitting git-master(104)/remove-ai-slops(52)/visual-qa(52) further: already routers under cap; mode-gated single-file is the design.
- Reject moving programming lane topic tables out of SKILL.md: they ARE the pack-level router.
- Reject folding 9 StyleGallery sub-indexes into CATALOG: they carry category framing; instead route to CATALOG directly from routers.
- Keep remove-ai-slops invariant repetition: deliberate spine of the skill.
## Fix wave (7 children, disjoint ownership): fix-uiux, fix-design-router, fix-patterns-dedup, fix-designpowers, fix-programming, fix-debugging, audit-consistency-2
## FINAL — QA round closed
verdict-qa round 1: BLOCKED (design/README.md lost cue in compression; _INDEX taste oversell) -> 2 one-line fixes -> checker PASS.
Fix-perfection: --runs N default 3 + medians, README reconciled. fix-uiux: 73 font pairings corrected.
All criteria evidence recorded on G008. Final GREEN /Volumes/storage/workspace/skills/.omo/ulw-loop/evidence/green-qa-final.txt.
## Cleanup receipts
No clone/servers/node_modules spawned by QA round (fix-perfection's npm install was inside its own mktemp, self-cleaned; verified pack sweep clean). Auditors were read-only.
## Learnings
- Compression rewrites must re-verify Rule-4 cues (the 256->88 README rewrite dropped its cue).
- Deaths mid-report (2 children this session) -> small verdict respawns beat full re-runs.
- Residency eviction happens; final-gate reviewers should be spawned fresh, not relied on resident.
## Fan-out root-cause fix (user directive: fix wording, not guardrails)
Culprits: SKILL.md:29 unitless 'parallel subagents in small batches'; workflow.md Phase 4 mixed units (category passes/file reviews/each reviewer); Phase 5 'Then review these questions:' with no subject/granularity -> skeptic-per-finding reading.
Fix: file named as the ONLY parallel unit (one worker per file, <=5 per batch, never per category/finding/review question); Phase 5 marked non-delegated reasoning step. slop-categories.md:109 already file-unit (clean). debugging/visual-qa/frontend delegation is naturally bounded (3 hypotheses/3 angles/2 passes/3 lanes).
