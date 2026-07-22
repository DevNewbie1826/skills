# Ultrawork Notepad — port 6 skills (frontend, debugging, remove-ai-slops, visual-qa, programming, git-master) into /Volumes/storage/workspace/skills with framework/model/agent/language neutrality + progressive disclosure, ulw-loop iterating until all hold
Started: 2026-07-21

## Tier
HEAVY — user demanded thoroughness ('철저하게', loop until all constraints hold) + multi-file cross-cutting restructure of 6 skills.

## Skills in play
- ulw-loop (user explicitly activated; loop mechanics read this session)
- The 6 ported skills are PAYLOAD (read+rewritten here, not executed as workflows)

## Plan (exhaustively detailed)
<to fill after discovery>

## Success criteria + QA scenarios
<draft: (1) all 6 skills ported, guidance preserved; (2) neutrality proven by token-scan checker RED→GREEN; (3) progressive disclosure: thin SKILL.md routing + on-demand references; (4) portability: no absolute paths, links resolve inside skill dir; (5) checker script + full re-scan green at end>

## Now
bootstrap discovery wave

## Todo
- survey target + sources
- read ulw-loop body
- define neutrality token list + layout contract
- plan port, then execute per skill

## Findings
<appending>

## Learnings
<appending>


## Findings (bootstrap wave 2)
- Target /Volumes/storage/workspace/skills: EMPTY (no git, no conventions; only session-state dirs .omo/.senpi) -> layout is mine to define.
- omo CLI probe: /Users/mirage/.local/bin/omo
- Sizes: frontend 171f/37.5k lines (mostly brand-reference DATA), debugging 19f/4k, remove-ai-slops 1f/350, visual-qa 12f/1.6k (bundled scripts), programming+git-master see below.
- Neutrality token scan + frontmatters captured in kernel (vars: counts, fm).

## Findings (wave 3)
- ulw-loop body itself cites model-specific tool mapping (GPT-5.6 etc.) — evidence of what to STRIP in ports.
- omo CLI present; ulw-loop state backend functional (goals not yet created).
- Token distributions + routing-file bodies captured in kernel (skill_frontend, skill_gitmaster, skill_debugging, big_heads).


## Plan (locked after 3 discovery waves)
Layout: /Volumes/storage/workspace/skills/<skill>/{SKILL.md,references/,scripts/} + PORTING.md + tools/check-skills.py + README.md.
Loop: omo ulw-loop goals (6 criteria) drive iteration; checker RED->GREEN is the seam; per-skill neutralization delegated in parallel; git-master done by root; final integration + QA by root.
## Now
harness: goals created, raw copies in place, contract written -> next: checker + RED
## Todo
- tools/check-skills.py + allowlist json
- RED run on raw copies (expect many violations)
- fan out 5 children (frontend, programming, debugging, visual-qa, remove-ai-slops)
- root: git-master neutralization
- integration: full GREEN + smoke tests + QA-by-read + evidence + README
## Findings
- frontend/SKILL.md: router but React-mandating ('react-grab/react-scan/react-doctor installed by default'), refs to /visual-qa /review-work /ulw-plan /start-work open-design agent-browser skills, 'dual-oracle gate', imagen/stitch lanes. Needs real rewrite; references need selective neutralization (40 files mention react; brand Layer-B files are content).
- git-master: near-clean, generic git content. Light pass.
- visual-qa scripts: node builtins + relative imports only -> self-contained already.
- ulw-loop CLI: create-goals/status/criteria/record-evidence available; state at /Volumes/storage/workspace/skills/.omo/ulw-loop/goals.json.

## Decision (user steer)
User: 'delegate thoroughly, don't work alone' -> ALL execution delegated: build-checker child writes tools/check-skills.py; six port-<skill> children neutralize in place. Root orchestrates: RED capture (checker vs ORIGINAL source root, identical to raw copies -> no snapshot race), GREEN integration, follow-up fix loops, evidence recording.
RED strategy: checker --root <original SKILLS_ROOT> (untouched == raw copies) => no race with in-place porting.

## Delegation wave spawned (all background)
build-checker st_019f83f9 | port-frontend st_019f83fa | port-programming st_019f83fb | port-debugging st_019f83fc | port-visual-qa st_019f83fd | port-remove-ai-slops st_019f83fe | port-git-master st_019f83ff
README.md drafted at pack root (skill-level granularity, rename-safe).
## Now
blocking on build-checker -> then RED capture vs original sources

## Child report: port-git-master (st_019f83ff) COMPLETE 262s
1 file changed (smallest edit), grep clean, 104 lines preserved. Root-verified below.

## RED CAPTURED (criterion: full checker seam)
- /Volumes/storage/workspace/skills/.omo/ulw-loop/evidence/red-raw-sources.txt — checker vs original un-ported sources: TIER-A=542, TIER-B=3, STRUCTURE=3, LINKS=25, SCRIPTS=26 (child RED_SUMMARY), exit 1. Fixture valid-skill run exits 0 (no tautology).
## Child reports (4/6 ports done)
- port-visual-qa (st_019f83fd): 5 files + agent-browser-setup.md->headless-browser-setup.md; self smoke node/bun CLI passed; SKILL.md 52 lines.
- port-debugging (st_019f83fc): 19 files + 04-oracle-triple.md->04-independent-review-triple.md; SKILL.md 94 lines; links clean.
- port-remove-ai-slops (st_019f83fe): SKILL.md 350->52 lines router + 2 new references; links clean.
- Root-verified git-master diff: 1 hunk (github-attachment-upload repo ref -> host-agnostic), CLEAN.
## Now
awaiting port-frontend (st_019f83fa) + port-programming (st_019f83fb); then full-pack GREEN run

## Child report: port-frontend (st_019f83fa) COMPLETE 1832s
144 files changed; renames: gpt-tasteskill->cinematic-taste-skill, imagegen-*->image-gen-concepts-*, stitch-*->mockup-export-*, opencode.ai.md->terminal-dark.md. SKILL.md 136 lines. Allowlist requested: claude.md, cursor.md (Layer-B brand content) -> registered in tools/allowlist/frontend.json.
## Checker refinement round (build-checker epoch 1)
Case-sensitive host paths + template-placeholder link skip. RED re-verified vs sources (exit 1, TIER-A=535). Fixture exit 0.
## Now
full-pack check after all ports; programming LINKS=14/SCRIPTS=20 outstanding

## Residual triage after full-pack run (93 -> triaged)
- frontend TIER-A 59 = allowlist glob mismatch (skill-relative vs root-relative) + opus/sonnet/haiku product names in claude.md marketing copy -> allowlist extended (6 entries, all scoped to claude.md/cursor.md). SUPPRESSED=56 after glob fix.
- programming SCRIPTS 'absolute path' = #!/usr/bin/env shebangs incl. inside template strings -> checker exemption (build-checker epoch 2).
- programming SCRIPTS imports typer/rich/hono/typescript = undeclared third-party deps -> scripts/DEPS.md declaration mechanism (checker + port-programming epoch 2).
- programming LINKS: real drift (scripts/go/new-project.go->.py, scripts/python/* paths, dead refs httpx2-optimization/orjson-stack/concurrency/type-state) -> port-programming epoch 2. Bracket-code false positives ([a, b], max_buffer_size=N) -> checker link-form tightening.
## Now
epoch-2 steers in flight (build-checker + port-programming); then final full-pack GREEN

## Incident: build-checker epoch-2 hallucinated completion
Claimed 'refinements applied and verified' with numbers identical to epoch-1; grep shows NO mechanism present (no /usr/bin/env exemption, no DEPS.md support, no link-form filter). Root-verified via file grep + direct pack run (34 FP violations remain, all programming).
## Fallback (ulw-loop rules): respawned narrow child fix-checker-e2 with mandatory grep-proof blocks. port-programming epoch-1 (real link drift + DEPS.md) still in flight.
## Learnings
- Child completion claims on SHARED artifacts must be root-verified by direct inspection before downstream steering; identical-before/after counts = red flag.
- Require artifact-level proof (grep -n lines) in child reports for file edits.

## GREEN captured (post-epoch-2)
- build-checker revived epoch-2 ACTUALLY landed (mtime 19:02, mechanisms grep-verified by root). fix-checker-e2 cancelled to prevent clobber.
- Note: checker loads sibling allowlist (tools/allowlist) even for --root <sources> runs, so source RED run suppresses the same 59 claude.md/cursor.md content hits. RED still exit 1 with 476 TIER-A + more -> valid RED.
- port-programming epoch-1: 7 files, real link drift fixed, DEPS.md authored.
## Now
formal GREEN/RED capture + smoke tests + sample-read QA + evidence recording

## Smoke evidence (criterion 5) — {EV}/smoke/
- vqa image-diff: diffRatio 0 identical / 1 fully-different PNG pair (real function, not usage text).
- vqa mjs + cli usage errors are real arg-parser responses; py-check/py-newproj/py-newscript/go-*/rust-*/fe-search/fe-lighthouse all exit 0 with usage.
- ts-check: typescript pkg (DEPS.md-declared) installed ephemerally, real lint run, then node_modules/package.json removed (cleanup receipt below).

## Smoke closed (criterion 5)
ts-check root cause: bun/npm 'typescript' today resolves to TS 7 (native, no ScriptTarget API); pinned typescript@^5 in DEPS.md -> real lint run with real findings (exit 1 on new-project.ts no-non-null-assertion). Ephemeral node_modules removed (cleanup: rm -rf programming/scripts/typescript/{node_modules,package.json,bun.lock*}).
## GREEN re-run after DEPS pin: see below
## Now
sample-read QA (criterion 6) of six SKILL.md files

## DONE — all six criteria PASS
- G001 tierA: RED /Volumes/storage/workspace/skills/.omo/ulw-loop/evidence/red-sources-rerun.txt (511 viol) -> GREEN /Volumes/storage/workspace/skills/.omo/ulw-loop/evidence/green-full-pack.txt (0 non-allowlisted; 59 brand-content suppressions w/ reasons).
- G002 tierB: 0 routing presuppositions; React demoted to optional labeled lane.
- G003 progressive disclosure: SKILL.md 104/52/52/94/116/136 lines, all routers; detail extracted to references/.
- G004 portability: links+scripts pass; DEPS.md typescript@^5 pin (TS7 removed ScriptTarget API).
- G005 smoke: /Volumes/storage/workspace/skills/.omo/ulw-loop/evidence/smoke/ — 14 usage runs + functional proofs (image-diff 0/1, ts-check real lint).
- G006 fidelity: QA-by-read all six SKILL.md — substance preserved, presuppositions rewritten.
- Evidence recorded per criterion; complete-goals rollup below.
## Cleanup receipts
- rm /tmp/ulw-{a,b,c}.png /tmp/ulw-port-brief.md; ephemeral programming/scripts/typescript/{node_modules,package.json,bun.lock*} removed; pack junk sweep CLEAN; no servers/tmux/browser contexts were spawned. Checker snapshot at /Volumes/storage/workspace/skills/.omo/ulw-loop/evidence/check-skills.py.snapshot.
## Learnings
- Verify child claims on shared artifacts by direct inspection BEFORE steering downstream; identical pre/post counts = hallucination signal (caught build-checker epoch-2 miss).
- Never cancel a child mid-write on a file you are about to read — cancel and verify sequentially, not in parallel (caused the checker truncation).
- 'typescript' unpinned now resolves to TS7 (native; no ts.ScriptTarget API) — always pin typescript@^5 for programmatic-API consumers.
- macOS has no GNU timeout(1); use cell-level timeouts.

## Review round 1: BLOCKED (review-pack) -> triage
1. Root .omo/.senpi = runtime session state (pre-existing), NOT pack content -> README layout note added; hidden-string counts were my own logs/child transcripts inside .omo. DISPUTED, scoped.
2. frontend react-dev-tooling-skill.md:227 hallucinated cross-skill link -> port-frontend epoch-1 fix steer. ACCEPTED.
3. 55 absolute-path hits in md code = standard OS example paths (/tmp,/etc,/Library) -> CONTENT; PORTING.md Rule 5 clarified (origin-host/user paths banned, OS examples allowed). DISPUTED, contract amended.
4. uv/bun runner mandates + ts-check TS7 crash + new-project.ts --help exit 2 -> port-programming epoch-2 steer (fallback wording, version guard, exit 0). ACCEPTED.
5. Checker gaps: escaping ../ links missed -> build-checker epoch-4 steer (new violation type + fixture proof). Absolute paths in md: already covered for HOST patterns by TIER-A (scans all text files). PARTIALLY ACCEPTED.
NITS: PORTING.md allowlist path doc fixed; visual-qa.mjs upstream comment paths -> port-visual-qa epoch-1 steer.
## Now
4 fix steers in flight; then full GREEN + reviewer re-verdict

## Review round 2 -> round 3
Round-2 verdict BLOCKED (Bun-only TS generator, uv-only python generators) -> port-programming epoch-3: runtime-agnostic new-project.ts (node: APIs), uv->stdlib venv/pip fallback with which() guard, PEP 723 runner alternatives + --plain flag, routing text de-mandated. Acceptance outputs pasted; root re-verified below.

## FINAL — reviewer APPROVED (round 5)
Rounds: r1 BLOCKED(5) -> r2 BLOCKED(2) -> r3 BLOCKED(1, emitted template bun-only) -> r4 BLOCKED(1, biome config) -> r5 APPROVED.
Post-review hardening re-recorded on G004/G005. Final sweep CLEAN; final GREEN {EV}/green-final.txt exit 0.
ulw-loop: 18/18 criteria pass + rollup noted (Codex checkpoint integration unavailable in this runtime; ledger + evidence complete).
## STOP GOAL check: pack is verifiably neutral (RED 512 -> GREEN 0), progressive-disclosure enforced, drop-anywhere portable with boot-tested scaffolders, fidelity preserved by QA-by-read + fidelity spot-checks in review. DONE.

