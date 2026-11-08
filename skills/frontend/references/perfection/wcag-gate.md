# WCAG 2.2 AA gate

Read this when finishing any UI or design-system deliverable: it states the accessibility result that goes into the hand-off.

Probe the built surface in a real browser and put a table in the deliverable (pull-request body, change description, or reply): one row per item below, PASS / FAIL / N/A, with its evidence. A FAIL is fixed, or recorded as accepted debt in `DESIGN.md` section 8 with the user's sign-off.

| Item | WCAG | Check |
|---|---|---|
| Contrast | 1.4.3, 1.4.11 | Text 4.5:1 (large text 3:1); icons and control edges 3:1; both themes; placeholder text included. |
| Focus | 2.4.7, 2.4.11 | Tab through every control and screenshot each ring; none missing, none entirely hidden by a sticky bar or overlay (the AA line; the target is none covered at all). |
| Target size | 2.5.8 | Every pointer target at least 24x24 CSS px, or an undersized one whose 24 px circle, centred on it, intersects no other target and no other undersized target's circle. Exempt: inline links in a sentence, targets the browser draws unstyled, a target with a same-function equivalent that passes, and a size the information requires. |
| Keyboard | 2.1.1, 2.1.2 | Every action works from the keyboard and focus never gets trapped. |
| Reflow and text spacing | 1.4.10, 1.4.12 | At 320 CSS px no content scrolls sideways, except content that needs two dimensions (a data table, a map, a diagram). With line-height 1.5, paragraph spacing 2em, letter spacing 0.12em, and word spacing 0.16em applied, nothing clips or overlaps. |
| Dragging, authentication, help, entry | 2.5.7, 3.3.8, 3.2.6, 3.3.7 | A single-pointer alternative for every drag; no cognitive test to sign in unless an alternative exists (paste and password managers work, or the test is object or personal-content recognition); help in the same place on every page; nothing asked twice in one flow. N/A only when the surface has none of these. |
| State-stable controls | build rule | Read each control's `getBoundingClientRect()` in every state (idle, hover, loading, success, disabled); width and height match across states. |
| System and surfaces | build rule | Colour roles exist in `DESIGN.md` before any component; each component names its source in the project's kit; a grep of the shipped styles finds no `backdrop-filter`, neumorphic double shadows, or mesh-gradient backgrounds unless the brief or a concrete reference supplies them. |

On the grounded path ([../design/grounding.md](../design/grounding.md)), close the gap ledger row by row: each fixed gap has its before/after pair and the check that proves it.
