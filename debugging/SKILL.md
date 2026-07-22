---
name: debugging
description: "MUST USE for real runtime debugging across any language or binary: crashes, silent failures, wrong responses, stuck processes, memory leaks, async misbehavior, unexplained timing, or reverse engineering. Runs a hypothesis-driven loop: form at least three hypotheses, investigate independent evidence paths, after two failed rounds use independent adversarial review passes from orthogonal angles (parallel subagents if your runtime supports delegation, otherwise fresh-eyes self-review passes), confirm root cause, lock it with a failing test, fix minimally, QA by using the system, and scrub artifacts. The HOW lives in `references/`. Triggers: 'debug this', 'why is X not working', 'hanging', 'attach a debugger', 'reverse engineer', 'pwndbg', 'gdb', 'lldb', 'node inspect', 'tsx debug', 'pdb', 'dlv', 'delve', 'rust-gdb', 'set a breakpoint', 'why is the response empty', 'trace this bug', 'reproduce and fix', 'silent failure', 'HTTP 200 but empty', 'inspect the binary', or 'playwright'."
---

# Debugging

You are a hypothesis-driven debugger. Two disciplines apply regardless of language, runtime, or source availability:

1. **Runtime truth beats code reading.** Every claim about why the bug happens comes from observed state, never a plausible story from reading code.
2. **Leave no trace.** Journal and remove every debugging artifact before calling the task done.

This file is a map. The expertise is in `references/`; open every reference whose scenario applies before using its commands.

---

## Runtime setup - read before attaching

The methodology is language-agnostic. Launch, attach, breakpoint, and inspection commands are not.

| Runtime | Read first | Why |
|---|---|---|
| Python (CPython, pytest, asyncio, Django, FastAPI) | [references/runtimes/python.md](references/runtimes/python.md) | Attach semantics, async breakpoints, and launcher wrappers differ. |
| Node.js / tsx / ts-node / Bun / Deno source | [references/runtimes/node.md](references/runtimes/node.md) | Source maps and inspector behavior can make apparent breakpoints ineffective. |
| Rust (cargo, tokio, panics) | [references/runtimes/rust.md](references/runtimes/rust.md) | Symbols, async task inspection, and lightweight diagnostics differ. |
| Go (goroutines, dlv, pprof, race) | [references/runtimes/go.md](references/runtimes/go.md) | Goroutine leaks, recovered panics, and race detection need runtime-specific evidence. |
| Native binary / stripped C/C++ / no source | [references/runtimes/native-binary.md](references/runtimes/native-binary.md) | Triage, dynamic tracing, static analysis, and scripted repro have a different order. |
| Bundled-app binary (Bun SEA, Node SEA, Deno compile, pkg, nexe, Electron, Tauri, PyInstaller) | [references/runtimes/bundled-js-binary.md](references/runtimes/bundled-js-binary.md) | Recover high-level source before spending time decompiling the bundled runtime. |
| Runtime not listed | Apply the phase loop with your runtime's analogous tools (debugger, tracer, logger); name the missing reference and proceed from [00-setup.md](references/methodology/00-setup.md). | The phase loop's evidence standard still applies without a runtime-specific reference. |

Before Phase 0, open the matching runtime reference when one is listed. Otherwise, name the missing reference in the journal and use the fallback row's analogous tools.

> **Native versus bundled binary:** `file ./target` calls both Mach-O or ELF. Check size and runtime markers: `du -h ./target` plus `strings -n 12 ./target | rg -iE 'bun|node_modules|webpack|esbuild|deno|pkg/lib|electron|pyinstaller|nexe|NODE_SEA_FUSE|tauri'`. Hits mean read `bundled-js-binary.md`; a clean result means read `native-binary.md`.

---

## Specialist tools - use the applicable capability

Read the matching tool reference before use. If a named tool is unavailable, use the stated fallback, preserve the evidence standard, and say what could not be captured.

| Capability | Use when | Reference and fallback |
|---|---|---|
| Browser-driving automation | A browser UI flow, viewport, or browser state may cause the bug. | [Playwright CLI](references/tools/playwright-cli.md), if available; otherwise another browser-driving capability or a manually driven real browser with captured evidence. Never substitute an HTTP client for browser behavior. |
| Native decompilation | A binary lacks trustworthy source. | [Ghidra](references/tools/ghidra.md), if available; otherwise an installed decompiler or disassembler and an explicit limitation. |
| Interactive native debugging | You need registers, stack, heap, or disassembly while a native binary runs. | [pwndbg](references/tools/pwndbg.md), if available; otherwise standard GDB or lldb with the equivalent inspection commands. |
| Scripted binary or network interaction | You need a reproducible crafted payload, fuzz harness, or binary repro. | [pwntools](references/tools/pwntools.md), if available; otherwise a deterministic script using available subprocess or socket facilities. |

---

## The phase loop - read the reference as you enter each phase

| # | Phase | Reference |
|---|---|---|
| 0 | **Environment assessment** - identify runtime, ports, symbols, environment, and watchers. | [00-setup.md](references/methodology/00-setup.md) |
| 1 | **Journal setup** - record every artifact before creation. | [00-setup.md](references/methodology/00-setup.md) |
| 2 | **Hypothesis formation** - at least three orthogonal hypotheses with distinguishing evidence. | [02-investigate.md](references/methodology/02-investigate.md) |
| 3 | **Investigation** - parallel independent passes when delegation exists; otherwise fresh-eyes self-review passes. | [02-investigate.md](references/methodology/02-investigate.md) |
| 4 | **Independent review triple** - after two failed rounds, reframe from three orthogonal angles. | [04-independent-review-triple.md](references/methodology/04-independent-review-triple.md) |
| 5 | **User decision escalation** - only after evidence is exhausted and a policy choice remains. | [05-escalate.md](references/methodology/05-escalate.md) |
| 6 | **Root-cause confirmation** - confirm only when toggling the suspected cause toggles the bug. | [06-fix.md](references/methodology/06-fix.md) |
| 7 | **TDD fix** - red test first, smallest green change, no scope expansion. | [06-fix.md](references/methodology/06-fix.md) |
| 8 | **Manual QA** - use the real surface: a terminal multiplexer such as tmux if available (otherwise a regular terminal), browser automation or a real browser, real API request, or binary repro. | [08-qa.md](references/methodology/08-qa.md) |
| 9 | **Cleanup** - walk the journal and revert every artifact. | [09-cleanup.md](references/methodology/09-cleanup.md) |
| 10 | **Final verification** - show red-to-green, suite, manual QA, and artifact-cleanliness evidence. | [09-cleanup.md](references/methodology/09-cleanup.md) |

### Cross-cutting references

| Situation | Reference |
|---|---|
| You cannot run the real operation but still need runtime evidence. | [partial-runtime-evidence.md](references/methodology/partial-runtime-evidence.md) |
| You are about to declare an extraction, audit, or reverse-engineering artifact complete and need a skeptical pass. | [verification review pattern](references/methodology/partial-runtime-evidence.md#verification-review-pattern-for-non-debug-tasks) |

---

## Non-negotiable safety invariants

<safety>
1. **Runtime state is the only source of truth.** A hypothesis without an observed value is a guess. Do not fix guesses.
2. **Journal every debug artifact before creating it.** Journal, then modify.
3. **Do not ship a fix without a failing-first test.** Require a red-to-green transition or state why it is impossible.
4. **Do not declare done on type-check or compilation alone.** Run the actual user scenario.
5. **Do not ask a question that runtime evidence can answer.** Escalate only for genuine ambiguity.
6. **Do not silently swallow errors while debugging.** Make them loud temporarily, then remove temporary instrumentation at cleanup.
7. **Do not create a commit from this skill.** Leave commits to the user's approved workflow.
8. **Do not attach before reading the matching runtime reference, or, when none is listed, recording the missing reference and choosing analogous tools.**
</safety>

---

## Start here

1. Read the bug description and identify the runtime.
2. Open the matching runtime reference and every applicable tool reference; if no runtime reference is listed, name it as missing and choose analogous debugger, tracer, and logger tools.
3. Open [Phase 0](references/methodology/00-setup.md) and create the journal.
4. Follow the phase loop, opening each reference as you enter that phase.
