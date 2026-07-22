# Ultrawork Notepad — feasibility: merge github.com/changeroa/StyleGallery into ported frontend skill
Started: 2026-07-21

## Tier
LIGHT — investigation only, zero edits to the pack; deliverable is a verdict report. Self-review in notepad.

## Skills in play
- ultimate-browsing (standby if github fetch blocked — not needed, git clone worked)
- frontend skill = SUBJECT of investigation (not executed)

## Success criteria
1. Verdict (merge fully / partially / not) grounded in: repo inventory + LICENSE terms + overlap map vs frontend/references/* + PORTING.md neutrality fit.
2. If partial/full: concrete placement plan + effort estimate + risks.

## Now
discovery wave 1: clone + census
## Findings
(pending)
## Learnings
(pending)
## Findings
- StyleGallery: 155f/2.4MB, 122md+26mjs. NO LICENSE (root find=0, GitHub API license:null) — default copyright, all rights reserved. Actively maintained (last push 2026-07-21, 137 stars).
- Mergeable core (layout/motion/design-engineering/guides/platform-guides/patterns/recipes): see size below. Governance (GOVERNANCE/DOMAINS/consumer-reference/quality/scripts/AGENTS.md/root manifests) = their internal docs-as-code machinery, NOT consumer content.
- Pattern docs are GENERATED from scripts/pattern-data.mjs (docs-as-code; 'do not hand-edit').
- Neutrality of content: tier-A hits 0; framework tokens in 1 file (motion/vocabulary.md). Fits PORTING.md.
- Frontend already has layout-skill.md (Layer A mechanics, philosophy-level); StyleGallery Layout = pattern-catalog level -> complementary, no direct duplication. But governance models differ (DESIGN.md gate vs governed domains) -> must slot UNDER existing routing, not as a 6th ruleset.
- Pack precedent (frontend/ATTRIBUTION.md): redistributes ONLY Apache-2.0 (brand corpus) + MIT (Leonxlnx taste skills) with notices. StyleGallery fails this bar today.
## Verdict
- Full merge ('다 녹이기'): NOT possible now — legal (no license) + structural (~40% is their internal governance/tooling).
- Path A (recommended): request license (MIT/Apache-2.0/CC-BY-4.0) via issue; if granted, merge patterns/recipes/guides/motion/design-engineering under frontend/references/design/ as a pattern-catalog layer beneath layout-skill.md, add ATTRIBUTION entry, checker re-verify. Est. ~100 files, 5-8 delegated subagent-hours.
- Path B (available today): link-not-copy as an external reference in frontend 'When to load something else' with fallback wording; no license needed, but network-dependent and against self-contained ethos.
- Path C (rejected): clean-room re-authoring — high cost, lower quality, unnecessary unless license refused.
## Cleanup receipts
- rm -rf clone tmp dir (see below); no servers/processes spawned.
## Self-review (LIGHT tier)
Verdict grounded in cloned-repo census + GitHub API + token scans + pack policy comparison; no pack edits made; tier held (investigation only).

