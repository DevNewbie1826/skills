Read this when you judge captures or brief a reviewer: the platform-baseline checklist, items A1-J2, each PASS, FAIL, or N/A and proven by a named capture.

# Visual QA checklist

This is the baseline distilled from platform design guidelines and the visually checkable rules of the `frontend` skill. Run it yourself on the capture matrix before dispatching reviewers and fix what you can; then both review passes run it again independently (Pass B owns A-F, Pass A owns G-J, see [Independent review passes](independent-review.md)). An item the surface has no instance of is N/A, never PASS. Every FAIL cites the capture or clip that proves it. `(mac)` marks macOS desktop items, `(phone)` marks items judged on the 390 px captures; unmarked items apply everywhere. A terminal or printed surface answers the items that have an instance there and marks the rest N/A.

A machine pre-check shortens the review: on a web surface read computed values from the rendered page (`getComputedStyle`: contrast against the painted background, font sizes per heading step, spacing above and below headings and groups, `overflow` per element) and overflow at 320-1440 px under an unbroken stress string. If your project already ships a page-audit tool, run it on every enumerated page first. A measured miss is a FAIL on the matching item (E2, B8, A9, A13, F8, F9, C4) before either reviewer looks; fix it and rerun. Keep the output beside the captures and hand it to both reviewers.

## A. Layout and alignment

- A1 Content is anchored by intent, centred or on the layout grid; nothing sits in the top-left of an otherwise empty canvas.
- A2 Backgrounds and scrolling layouts run full-bleed to the display edges; no stray inset margin.
- A3 Margins are symmetric; prose sits in a 65-75 character measure on desktop and at least 45 on a phone.
- A4 (phone) Safe areas respected: bars and content inset for the home indicator, notch, and status bar.
- A5 (phone) Scrollbars are overlay; no reserved right-hand gutter.
- A6 One scroll owner per region, no nested same-direction scrolling; a sticky or floating bar stays legible over whatever scrolls under it.
- A7 Elements align to shared edges; gaps come from the spacing scale.
- A8 Related items are visibly grouped; controls have clear space around them and between each other.
- A9 One readable column at 390 with no horizontal scroll of primary content; nothing clips or overlaps at 1440/1920 or under empty, long-label, and unbroken-string content.
- A10 Content that continues out of view shows a cue (partial item, fade, chevron).
- A11 (mac) Nothing important lives only at the window's bottom edge; the minimum window size keeps toolbar and content legible; the sidebar collapses when the window narrows.
- A12 (web and app screens; N/A for a TUI, a printed page, or a figure) Layout contract: every changed screen or region has a layout line naming its pattern, owner scroller, and anti-patterns (in `DESIGN.md`, or in the change description when the project has none). The capture shows that pattern's structure; the logged owner is the region's main scroller in the probe output below, and every other scroller listed is nested inside it for its own content (a code block, a dropdown, a composer) or is named in the line too; none of the line's anti-patterns appear. A missing line, a different main scroller, an unexplained sibling scroller, or a present anti-pattern is a FAIL; a logged skip still owes the scroll-owner check.
- A13 Spacing rhythm, read from computed values: the space above a section heading is at least 1.5x the space below it, and the gap between groups is at least 2x the gap inside a group, unless the brief's chosen style sets its own rhythm and records the deviation in the brief or `DESIGN.md`, in which case that value is the check.

Scroll-owner probe for A12: run it at each viewport and attach the output to the captures.

```js
await page.evaluate(() => [...document.querySelectorAll("*")]
  .filter((el) => /auto|scroll/.test(getComputedStyle(el).overflowY) && el.scrollHeight > el.clientHeight)
  .map((el) => el.id ? "#" + el.id : el.tagName.toLowerCase() + (el.getAttribute("class") ? "." + el.getAttribute("class").trim().split(/\s+/).join(".") : ""))
  .concat(document.scrollingElement.scrollHeight > innerHeight ? ["document"] : []))
```

## B. Hierarchy

- B1 One primary action per view, in the prominent style (accent on its background, not its glyph); peers differ by style, never by size.
- B2 Destructive actions carry the destructive style and are never the default (Enter) action; Cancel is never the default either.
- B3 Every screen or window has a plain title that says what it is, not the app name; a toolbar title stays around 15 characters.
- B4 The most important content sits top/leading in reading order; secondary detail does not crowd it.
- B5 One or two accents per screen; toolbars and tab bars stay monochrome over colourful content; nothing decorative carries accent.
- B6 Type hierarchy comes from weight, size, and colour, holds in both themes, and uses at most two typefaces.
- B7 (web and app screens; N/A for a TUI, a printed page, or a figure) The screen matches its brief (the `frontend` skill's design brief: named primary action, priorities, and what is left out on purpose): the named primary action is the single prominent control, priorities 1-3 appear in that order in reading order on the first viewport, and nothing listed under "left out on purpose" is on the screen. A screen built or changed in this session with no brief is a FAIL; a pre-existing screen under audit with no brief is N/A.
- B8 Type scale floor, read from computed values: each heading step in use (display to h3, and the smallest heading to body) differs by at least 1.25x in size, and body-family roles (lead, body, small, caption, label) that sit closer also differ by weight, colour, or case; a display heading stays at or under 6rem and letter spacing never goes below -0.04em, unless the brief's chosen style sets its own display scale or tracking (then that value is the check).

## C. Text and copy

- C1 Body text is at least 17 pt-equivalent at 390 (15 pt for secondary text) and 14 px on desktop; no thin weights at small sizes.
- C2 No raw machine text where a sentence belongs: ISO timestamps, internal ids, enum or engine strings; times are relative and local.
- C3 Action labels are outcome verbs, tab and segment labels are nouns, one capitalization style throughout; "OK" is never the default on a question; (mac) actions that need more input end with an ellipsis.
- C4 Truncation and wrapping are designed: ellipsis or wrap, never clipped glyphs or descenders, no overlap at large text sizes or 200% zoom; no heading wraps to four lines.
- C5 CJK text breaks naturally: no orphaned particle or ending, no clause split from its predicate, no broken citation string (the Pass B charter carries the examples).
- C6 Empty states and errors say what happened and what to do next, next to the point of failure, without blame.
- C7 Every text field has a visible label; the placeholder shows the expected format and is never the only label.
- C8 Useful label text (ids, errors, addresses, paths) is selectable.

## D. Touch and pointer targets

- D1 Touch targets are at least 44x44 pt (44 CSS px on the web) with 8-12 pt between neighbours; pointer targets are padded about 10 px beyond the glyph.
- D2 (phone) Tab bar: about 49 pt plus the safe area, icon above a one-word label, every tab visible, the active tab matches the route, no tab disabled or hidden.
- D3 Toolbar: at most three groups, standard back and close glyphs, one prominent primary action at the trailing end, text-labelled actions kept apart from glyph actions.
- D4 Adjacent bar buttons have continuous hit areas.

## E. Contrast, colour, and themes

- E1 Light and dark both render correctly, captured as a pair; no light-only asset glows in dark; icons legible in both.
- E2 WCAG AA in both themes: 4.5:1 for body text, 3:1 for large text, icons, and control edges, including placeholder and disabled states.
- E3 Nothing is carried by colour alone: status colour pairs with a glyph, label, or shape; focus is not colour-only.
- E4 One colour never means two things; status colours are consistent across the surface.
- E5 Translucent surfaces keep text legible over any scrolled content: blur or vibrancy, not a plain alpha fill.
- E6 The theme follows the system; an in-app theme control also offers "system".
- E7 Secondary text on a tinted or coloured surface is a shade of that hue or the foreground at reduced alpha, never neutral gray; a shadow carries a y-offset and a soft blur, never a zero-offset coloured glow unless the brief asked for glowing-border cards.

## F. Consistency and brand

- F1 One icon set with one stroke, weight, and size; icon weight matches adjacent text; no emoji used as an icon.
- F2 Spacing and radii come from the token scales; nested corners are concentric.
- F3 A shared component looks the same on every surface that uses it; the fix is verified on every sibling route or app that shares it.
- F4 The owner's brand elements (logo, wordmark, stage badge) are present and untouched; nothing else carries branding: no persistent logo in content space, no branding-only launch screen.
- F5 Selected or active state is a wash plus a glyph; focus is a focus-visible ring on fields and a row highlight in lists; no coloured accent side-border marks state.
- F6 Standard glyphs for standard actions (share, close, back, search, more) in their standard places.
- F7 Windows, sheets, and popovers use system shapes; one sheet or popover at a time; a popover's arrow points at its source; only an alert may appear over a popover.
- F8 Browser surfaces carry the palette in both themes: text selection, caret, visible scrollbars, focus ring, link underline offset, and tabular numerals in changing or aligned numbers; none shows the browser default (select text and focus a field in the capture to prove it).
- F9 None of the generated scaffolds: a kicker label above a heading, an icon tile stacked over a heading in a grid of same-size cards, a hero metric with no decision behind it, a card nested in a card, monospace used as a "technical" costume (the `frontend` skill's deslop taxonomy lists them). One the brief asked for, recorded as such, passes.

## G. Motion and feedback

- G1 Every animation has a cause: an interaction, a state change, an arrival; no motion on non-interactive elements, no hover that changes nothing, no permanent loop. A background the brief asked for may loop on its decorative layer only while in view: it starts from an IntersectionObserver, stops off-screen and on visibilitychange, and paints one static frame under reduced motion.
- G2 Transitions keep identity: a surface that resizes or moves animates from its old geometry to the new; exit mirrors entry; nothing reflows under the pointer.
- G3 Motion is interruptible and never gates input: mid-animation input retargets smoothly and never snaps; nobody waits for an animation to act.
- G4 Under `prefers-reduced-motion`, positional, scale, and depth motion becomes a cross-fade; fades, progress, and gesture tracking stay; blur never animates.
- G5 A press is acknowledged in the same frame; a spinner appears only past about one second; progress moves at an even pace, never swaps spinner for bar, never front-loads to 90%.
- G6 No layout shift after load; the first paint is the real first screen, not a branded splash.
- G7 No flashing or strobing; no slow (~0.2 Hz) oscillation on viewport-filling motion; motion never blocks reading.

## H. States

- H1 Every view has empty, loading, error, and offline states; the empty state offers the next action.
- H2 Loading shows something at once (placeholder or skeleton); a spinner only for waits past about one second, with a short specific description; an indicator that stops moving is a FAIL.
- H3 Failure is reported next to the object with its cause; success is shown by the changed state; a toast only for outcomes not visible in place; no alert for routine or undoable actions and none at launch.
- H4 Alerts: the title states the situation, the message is at most two short sentences, buttons are outcome verbs (not "OK"), Cancel is present whenever a destructive option exists, the destructive option is styled so, and the alert never scrolls.
- H5 Every control shows hover (pointer), pressed, focused, and disabled states; disabled is dimmed but legible; a toggle's on and off differ by more than colour.
- H6 Sheets and modals: one at a time; always a visible way out (Cancel or Back beside Done); a grabber on resizable sheets; unsaved changes are confirmed before dismissal.
- H7 Long operations are cancellable when safe; a cancel with consequences warns first.
- H8 Permission and consent requests appear in context, not at launch unless core; a pre-prompt screen has one button that opens the system prompt and no exit that dodges it; the purpose text says what the data is for.
- H9 Sign-in is deferred until needed and its benefit stated; the auth method is named ("Sign in with <provider>", not "Sign in"); no license text in onboarding; password fields are masked and never pre-filled.
- H10 Search, when present: one search location, scope visible in the placeholder or a scope bar, recents or suggestions offered.
- H11 Settings, when present: labels say what ON does; system-wide settings are not duplicated; (mac) the settings window title names the visible pane.

## I. Keyboard and accessibility

- I1 A visible focus ring on every interactive element; focus order equals reading order; focus never moves without user action and never lands on a destructive or approve action by default.
- I2 Escape closes the topmost modal, popover, or menu; Enter triggers the non-destructive default; standard shortcuts are not overridden (Cmd-, opens settings, Cmd-Z undoes).
- I3 Accessibility tree: inputs are named, icon-only controls have a name and a tooltip, meaningful images are described, landmarks exist.
- I4 Every gesture has a control alternative: a swipe-dismissed sheet also has a close control, swipe actions also live in a menu.
- I5 Autoplaying media shows pause and stop controls; no auto-play audio.

## J. Platform specifics

- J1 (mac) System window chrome; every toolbar action also exists in the menu bar; Cmd-, opens settings titled by pane; 1 pt split-view dividers; sortable column headers where values exist; hover-revealed controls appear after hover intent and leave with the pointer.
- J2 (phone) No popover in compact width (a sheet instead); a large title collapses on scroll when used; `inputmode` matches the data (numeric, email, URL).
