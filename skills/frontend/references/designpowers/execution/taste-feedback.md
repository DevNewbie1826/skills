# Live Taste Feedback

Read this when a build involves subjective aesthetic decisions and the user should see intermediate visual output at 2–4 strategic checkpoints, with specific taste questions, before the build completes.

Back-link: [Lane B — Design Execution Guidance](../lane-b-execution.md)

The standard Designpowers pipeline catches taste mismatches at critique — after the full build is done. That's expensive. A wrong color palette discovered after 8 components are built means rebuilding all 8. This skill interrupts the build at strategic moments to show intermediate output and ask: "Is this heading in the right direction?"

## When to Use

- During implementation, at natural visual checkpoints
- When the build involves subjective aesthetic decisions (color, typography, spacing, tone)
- When the project's taste direction is ambiguous on the decision at hand
- When the project is new and there's little explicit direction yet for this decision
- When the current direction was based on interpretation, not explicit user instruction

## Do Not Use When

- The user has asked not to be interrupted for taste checks
- The build is purely structural (data models, API integration, routing)
- The project's taste direction already settles this decision clearly
- The user has explicitly said "just build it, I'll review at the end"

## Process

### Step 1: Identify Checkpoints

Before the build begins, identify 2-4 moments where taste feedback is most valuable. More than 4 interruptions becomes annoying. Choose wisely.

**High-value checkpoints:**

| Checkpoint | Why It Matters | When to Show |
|------------|---------------|-------------|
| **Color and typography applied** | The foundational visual layer — everything else builds on this | After the first component is styled |
| **Layout structure visible** | Spatial relationships, density, whitespace | After the primary screen scaffold is built |
| **First interaction implemented** | How the interface moves and responds | After the first stateful component works |
| **Content integrated** | How real words look in the design | After the real copy is in place |

**Low-value checkpoints (avoid):**

| Checkpoint | Why It's Low Value |
|------------|-------------------|
| Unstyled HTML structure | Nothing to react to aesthetically |
| Individual component in isolation | Context-free judgement is unreliable |
| After every small change | Interruption fatigue kills the creative flow |

### Step 2: Prepare the Checkpoint

At each checkpoint, capture the current state:

1. **Take a screenshot** of the running output (or describe the visual state precisely if screenshots aren't available)
2. **Identify the taste-sensitive decisions** visible in the current output
3. **Prepare specific questions** — do not ask "does this look good?" (too vague)

Good taste questions are specific and answerable:

| Bad Question | Good Question |
|-------------|--------------|
| "Does this look good?" | "The heading is set in 32px Inter Medium — is that weight right, or do you want bolder/lighter?" |
| "Any feedback?" | "The cards have 16px padding and 8px radius. Does this density feel right, or do you want more breathing room?" |
| "Is this the right direction?" | "I went warm grey (#F5F3F0) for the background instead of pure white. Does this warmth match what you had in mind?" |

### Step 3: Present the Checkpoint

Show the user the intermediate state with targeted questions:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TASTE CHECK  [1 of 3]
  Phase: [e.g., "Color & Typography"]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [Screenshot or detailed visual description]

  DECISIONS VISIBLE:
  • [Decision 1 — e.g., "Sage green (#8FAE8B) as primary"]
  • [Decision 2 — e.g., "Space Grotesk for headings, Inter for body"]
  • [Decision 3 — e.g., "Generous padding, low density"]

  TASTE QUESTIONS:
  1. [Specific question about a visible decision]
  2. [Specific question about a visible decision]

  Quick responses welcome:
  • "Looks right" → continue building
  • "Warmer/cooler/bolder/quieter" → adjust and continue
  • "Stop — wrong direction" → pause build, discuss
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 4: Process the Response

The user's response determines what happens next:

| Response | Action | Taste Signal |
|----------|--------|-------------|
| "Looks right" / "Yes" / "Continue" | Resume building. No changes needed | Moderate positive — record as a confirmed direction |
| Specific adjustment ("make it warmer") | Apply the adjustment, show confirmation, then continue | Strong — record the adjustment and the direction they moved from/to |
| "Wrong direction" / "Stop" | Pause the build. Ask what feels off. This is the most valuable taste data | Very strong negative — record what was rejected and why |
| Detailed feedback ("I like the type but the color feels too muted") | Apply partial changes. Acknowledge what works, adjust what doesn't | Mixed signal — record both the positive and negative separately |
| "Skip these checks" | Disable further taste checks for this build. Respect the preference | Meta-preference — they want to review at the end instead |

### Step 5: Adjust and Confirm

When the user requests a change:

1. Make the adjustment
2. Show the updated state briefly — do not re-present the full checkpoint
3. Confirm: "Updated [what changed]. Continuing the build."
4. Do not ask for re-approval unless the change was ambiguous

If the change cascades (e.g., new color palette affects multiple components already built):

1. Flag the cascade: "This color change will affect the 3 components already built. I'll update them all."
2. Update everything before continuing
3. Optionally show the cascaded result at the next checkpoint

### Step 6: Record Taste Data

After each checkpoint interaction, update taste signals:

1. Record confirmed decisions as positive taste signals
2. Record adjustments with before/after — these are the richest taste data
3. Record rejections as anti-pattern candidates
4. Note the *direction* of adjustments — "wanted warmer", "wanted more contrast", "wanted tighter spacing" — these directional signals generalize across projects

## Integration

- **Used during:** implementation, at visual checkpoints chosen in Step 1
- **Reads from:** the taste profile (known preferences) and the project design record when one exists
- **Pairs with:** [design-review.md](../review/design-review.md) for the critique that follows the build

## Anti-Patterns

| Pattern | Why It Fails |
|---------|-------------|
| Asking "does this look good?" | Too vague. The user can't give actionable feedback without specific questions |
| Checking after every change | Interruption fatigue. 2-4 checkpoints per build, maximum |
| Showing unstyled output | There's nothing to react to. Wait until visual decisions are visible |
| Ignoring "skip" signals | If the user wants to review at the end, respect that. Don't force mid-flight checks |
| Not recording feedback | Every checkpoint interaction is taste data. If you don't record it, you'll ask the same questions next project |
| Asking about non-visual decisions | "Is this the right React component pattern?" is not a taste question. Keep checks visual and aesthetic |
