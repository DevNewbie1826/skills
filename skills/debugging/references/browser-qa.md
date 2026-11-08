> Read this when a browser-served UI bug needs reproduction in a real browser, with evidence strong enough to trust.

# Reproducing UI Bugs in a Real Browser

An HTTP client proves what the server sent. It cannot prove what the user saw. This reference covers the reproduction loop, the console and network record, the screenshots, and the flake discipline that make a browser reproduction trustworthy. Examples below use placeholder names and capability descriptions; substitute whatever scriptable driver the environment provides.

## Reproduce the bug in a real browser

A reproduction is trustworthy when a second person can replay it and land on the same visible wrong state. Get that before forming a theory about the cause.

### Why an HTTP client is not enough

A page is rendered, not merely transferred. A raw request misses:

- Layout and paint: overlap, clipping, wrong stacking, overflow, missing styles at a width.
- Client-side state: router state, in-memory store, hydration mismatch, focus ownership.
- Cookies and client-side storage: session scope, stale values, per-profile state.
- Service-worker caches: an old shell served from cache while the server is already fixed.
- Script-triggered navigation and submit handling that never appears in a server log.
- Input semantics: pointer versus touch, hover, keyboard, scroll position, zoom.

So a non-browser probe can explain a server response, but it cannot confirm or dismiss a UI symptom. Do not substitute one for the other.

### The reproduction loop

1. Start from the exact user-visible symptom. Write it as a sentence a user would say: "the total stays at zero after applying a valid code", not "the apply handler throws".
2. Write the minimal ordered action list. Include the starting URL, preconditions (account role, seeded data, prior navigation), and every click, type, key press, and scroll in order. Include the expected visible result after each step, so a replay can show where the path diverges.
3. Keep the reported footprint. Use the same viewport width and height, device scale, zoom, locale, input mode, and signed-in role. A layout bug reproduced at a different width is a different bug.
4. Replay the list with the driver. Capture console, network, and screenshots as described below.
5. Confirm the failure is the SAME failure. Same visible wrong state, same region, same text or missing value. A crash or a console error somewhere else is a different defect; do not relabel it as the reported one.
6. Replay from a clean profile once. That distinguishes stored state from code. Note whether the failure survived.
7. Reduce the action list only after the failure is stable. Drop steps one at a time and re-run; keep the journal entry for the reduced list.

### When the driver cannot reach the state

Some states need a real hand: a hardware token, a captcha, an installed extension, a native file dialog, a login only the user can complete. Drive the browser manually, follow the same ordered list, and capture the same console, network, and screenshots by hand. Record the limitation in the journal: which step needed a human, why the driver could not perform it, and what evidence the manual run produced. A manually driven real browser is acceptable evidence. A non-browser probe standing in for it is not.

## Capture console output

Subscribe before navigating, not after the failure. Errors raised during load, hydration, or the first paint are the ones most often lost.

- Record each message with its level, text, source location, and timestamp.
- Keep uncaught exceptions separate from logged errors and failed assertions. They have different causes and different fixes.
- Note warnings that precede the failure even when they are not errors. A key warning or a rejected state update is often the first visible clue.
- Treat an absence of output as data. State what you expected to see and did not: a missing request log, a missing error, a silent handler.
- Include a trimmed excerpt in the journal with timestamps, plus a one-line note on anything filtered out.
- If the page has its own in-app error surface, capture that too. A caught error shown in the UI may never reach the console.

## Capture network activity

Record every request and response the page makes during the replay. For each entry keep the method, URL, status, duration, and the moment it started relative to the failing action.

- Capture the failing request's status, response body, and response headers. The body is usually the explanation.
- Capture requests that never completed: still pending, canceled by the page, blocked, refused, or timed out. Say which, since "no response" and "500" lead in different directions.
- Capture request bodies only where the payload matters, and say why.
- Redact credentials and tokens before anything reaches the journal. Replace authorization headers, cookie values, and query tokens with a marker such as `<redacted>`; never paste the real values into a journal, a screenshot, or a commit message.
- Correlate the network entry with the UI moment. The request that failed just before the wrong state is the candidate; one that failed during unrelated background polling probably is not.

A minimal record shape:

```text
time  method  url                      status  duration
0.41  GET     /api/cart                200     38ms
0.52  POST    /api/discount            422     61ms   response: {"error":"code expired"}
0.53  GET     /api/recommendations     pending         canceled when the view changed
```

Attach the actual failing response body beneath the table, redacted where needed.

## Screenshot discipline

Screenshots are evidence only if a reader can tell what they show and when.

- Capture the full page and the specific element or region that shows the bug. The full page gives context; the region makes the defect legible. Where the driver captures only the viewport, resize the viewport to the document height and capture again, and say which method produced the image.
- Capture before and after the failing action. The pair shows what changed and rules out a pre-existing state.
- Capture at the reported viewport plus the nearest breakpoint on each side. If the layout shifts at 768 and 1024, a 900-wide report gets 768 and 1024, not an arbitrary phone width.
- Wait for a stable visual state before capturing: fonts loaded, images loaded, spinner stopped, no in-flight transition. Wait on the condition with a bounded timeout; do not capture mid-animation and call the frame the bug.
- Capture again after any change to the page, the script, or the viewport. A stale image is worse than no image because it looks like proof.
- Name files so the scenario and step are readable, for example `/tmp/debug-checkout-total-1024-before.png` and `/tmp/debug-checkout-total-1024-after.png`.
- Never screenshot a scrolled-away or redacted state and present it as the bug. Scroll the failing region into view, keep it unredacted where it is not sensitive, and note any unavoidable redaction.

## Evidence to capture

A trustworthy browser reproduction leaves a journal entry that another person can replay. It contains:

- The ordered reproduction steps, including preconditions and expected result per step.
- The exact driver invocation: script path, command line, and environment variables that affect behavior.
- The console excerpt, with levels, timestamps, and a note on filtered lines.
- The network excerpt, with the failing entry and its redacted body.
- The screenshot paths, each labeled full page or region, before or after, and at which viewport.
- The viewport and device settings: width, height, pixel density, zoom, locale, input mode.
- The build or commit under test, so the evidence is tied to one revision.
- The observed-versus-expected statement in one or two sentences.
- A limitations list naming every piece above that could not be captured, and why.

A missing piece is a limitation to state, never an omission to hide. If the console record is unavailable, say so; do not imply the console was clean.

## Handle flaky reproduction

A reproduction that succeeds once and fails later is not yet evidence. Classify the flake before blaming or crediting any fix.

- Does it fail on every replay, only under machine load, only at one viewport, only from a fresh profile, or only with a warm cache? Each points at a different cause.
- Record the pass/fail sequence, not a single run: for example, "4 failures in 6 replays, all at 375 wide; 0 in 5 at 1280". A ratio plus conditions is a finding.
- Wait for a state or an event with a bounded timeout instead of sleeping for a guessed duration. Wait for the element, the response, or the settled layout that proves the action finished.
- Isolate from concurrent work: use a clean browser profile and an isolated driver endpoint per run so another replay cannot share storage, cache, or a listening socket.
- Keep the same seed data and account between replays. A different fixture explains many "flakes" without any race at all.
- If it stays intermittent, report the observed ratio and the distinguishing conditions. Do not declare the bug fixed on a lucky run.
- Never raise a timeout to cover a race, and never retry until green. Both hide the defect and destroy the value of the evidence.

When the flake has a stable signature, continue with [intermittent-failure triage](methodology/03-flaky-triage.md).
