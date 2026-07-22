# Ultrawork Notepad — merge StyleGallery content into ported frontend skill (permission granted)
Started: 2026-07-21

## Tier
HEAVY — ~80-file content integration into the verified pack; user-directed; reviewer loop required.

## Provenance
User stated 2026-07-21: StyleGallery author granted permission for anyone to use the content. Recorded in frontend/ATTRIBUTION.md. Recommendation given once: ask author to add upstream LICENSE file for durability.

## Success criteria
1. Content domains merged per layout map (layout-patterns, layout-recipes, motion, design-engineering, game-ui, platform-guides); governance files excluded (justified).
2. Dead links/generation-metadata surgery complete — pack checker GREEN (RED captured first).
3. Routing wired (SKILL.md <=200 lines, design/README.md, _INDEX.md) without governance-model conflict.
4. ATTRIBUTION.md entry with permission provenance.
5. Reviewer unconditional approval; evidence recorded to ulw-loop.

## Now
RED captured on raw import -> delegate surgery
## Findings
- RED result below.
## Learnings
(pending)
## RED captured: /Volumes/storage/workspace/skills/.omo/ulw-loop/evidence/red-stylegallery-import.txt (exit 1, 754 lines; LINKS=373 + TIER-A=4 + rest)
TIER-A hits: TIER-A (4)
  frontend/references/design/game-ui/unity/data/unity-technologies-public-repositories.json:16587: TIER-A: banned token "prometheus"
  frontend/references/design/game-ui/unity/data/unity-technologies-public-repositories.json:22071: TIER-A: banned token "prometheus"
  frontend/references/design/game-ui/unity/data/unity-technologies-public-repositories.json:23003: TIER-A: banned token "pr
90 files copied (79 md + guides extras). Clone kept at /var/folders/v0/g2h4nhxd64j63j7tnr3rc87c0000gn/T/tmp.0re568acdp/sg (surgery reference; cleanup at end).
## Path-map for surgery
patterns/<cat>/x.md: '../../CATALOG.md'->'../CATALOG.md'; '../../recipes/...'->'../../layout-recipes/...'; quality/DOMAINS/GOVERNANCE/consumer-reference/scripts refs -> DELETE/genericize; generated-file HTML comments -> strip; GUIDE.md->planning-guide.md; intra-pattern cat links unchanged.
## Now
delegate 2 surgery children + attribution done + goal added

## Delegation wave 2 (surgery)
merge-layout (patterns+recipes link surgery) + merge-aux (motion/de/game-ui/platform + dataset exclusion) spawned in background. Then: wire-routing child -> checker GREEN -> reviewer.
## Now
awaiting surgery children
## Surgery GREEN (frontend scope, exit 0, SUPPRESSED=59 pre-existing brand entries)
merge-layout: 71 files fixed, deleted refs quality/=45 scripts/=208 DOMAINS=4 README=3 GOVERNANCE=2 AGENTS=3 others=4. merge-aux: 8 files + dataset unity-technologies-public-repositories.json deleted (26,654 lines). Both scopes LINKS=0.
## Now
wire-routing child (SKILL.md <=200 + design/README.md + _INDEX.md)
## Review round 1 (merge): BLOCKED — Rule 4 cue-form
Ruling: frontmatter description and 'Primary role:' are functionally equivalent routing cues -> PORTING.md Rule 4 amended to name the three acceptable forms. The 42 cue-less files (list computed by scan) are REAL violations -> one-line cue additions delegated.
NIT: permission grant lacks durable citation -> will ask user for the issue/comment/DM link; ATTRIBUTION records maintainer-attested provenance meanwhile.
## FINAL — verdict-merge APPROVED (cue-less=0, leftover-refs=0, checker=0, attribution=yes)
Note: review-pack epoch-6 died mid-verdict (completed without output) -> respawned small verdict-merge child per ulw-loop fallback. Evidence recorded on G007 (3/3). Clone removed.
## Cleanup receipts
- rm -rf /var/folders/v0/g2h4nhxd64j63j7tnr3rc87c0000gn/T/tmp.0re568acdp (StyleGallery clone); no servers/ports/node_modules spawned this task.
## Learnings
- Generated docs-as-code corpora: exclude generator+governance, import rendered docs, strip generation markers, retarget links by explicit path-map.
- Rule amendments must preserve intent and be announced to the reviewer (Rule 4 cue forms); reviewer acceptance is part of the loop.
- 'Unsupported Absolutes' sections: read headings before flagging contradictions.
