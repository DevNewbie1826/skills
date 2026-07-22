# Ultrawork Notepad — hazard QA round (instruction wording that drives bad agent behavior)
Started: 2026-07-22
## Tier: HEAVY (user demanded 깐깐하게; reviewer loop)
## Missed-angle analysis: previous round covered consistency/disclosure/intent/slop — none asked 'what behavior does this wording INDUCE'. The 75-agent incident class = hazard wording.
## Hazard lexicon (seed for auditor + checker):
H1 spawn/delegation terms (spawn|subagent|worker|delegate|parallel|fan.?out|reviewer) in a paragraph with NO unit word (per file|per batch|per angle|per lane|one worker)
H2 explicit per-finding/per-question/per-item spawning
H3 uncapped iteration (continue|keep|until) without stop/cap/max in the same instruction
H4 destructive default (rm -rf|--force|reset --hard|checkout <file>|delete) without a scoping guard
H5 subject-less directives (review/verify/audit with no actor named) in delegating skills
## Criteria: (1) hazard audit delivered with classifications; (2) real hazards fixed at wording level; (3) checker HAZARDS check live (fixture-proven both directions) + pack GREEN; (4) reviewer verdict.
## Now: spawn audit-hazards + audit-regression + fix-checker-hazards
## FINAL — hazard round APPROVED
verdict-hazard: APPROVED, blockers none, coherence 8/8, SAFE untouched 5/5.
## Meta (user: '이런건 미리 발견했어야해')
Durable prevention now two-layered: (1) checker HAZARDS lint — original-source run flags exactly 3 HAZARDS hits = the bait class that produced the 75-agent incident, pack run exit 0; (2) hazard lexicon H1-H5 recorded for future audits. Previous QA round lacked the 'what behavior does this induce' angle entirely — now a standing audit angle.
## Learnings
- Instruction hazards ≠ factual drift: a text can be consistent, disclosed, intent-faithful, slop-free AND still induce runaway behavior. Behavioral reading is its own audit angle.
- pkill -f <generic> in guidance text = kill-other-sessions hazard; the journaled-PID idiom fixes it without losing the cleanup doctrine.
- Grammar-coherence check after surgical line edits: one splice error slipped through (image-gen-concepts-mobile) — re-read the paragraph, not just the line.
## Cleanup receipts
No temp resources this round (audits read-only; fixtures inside children's own mktemp, self-reported).
