# Design Debate

Read this when a design direction is genuinely contested — competing options are argued with real trade-offs, an accessibility check is applied, and the user decides.

Back-link: [Lane A — Direction & Discovery](../lane-a-direction.md)

Good design decisions come from tension, not consensus. When agents converge too quickly, they optimise for agreement instead of the best answer. This skill creates productive conflict — agents argue for competing directions with real trade-offs, and the user decides.

## When to Use

- When a planning pass identifies multiple viable directions
- When a visual direction is proposed and real alternatives exist
- When the user says "I'm not sure which way to go" or "what are my options?"
- When critique recommends "rethink" — a debate can surface the better path
- When a decision has significant downstream consequences (navigation pattern, layout model, interaction paradigm)
- When the user explicitly asks for a debate: "debate this", "argue both sides", "what are the trade-offs?"

## Do Not Use When

- The decision is trivial (icon choice, exact padding value)
- Accessibility requirements dictate the answer — there is nothing to debate
- The user has already made up their mind — respect their direction
- The brief clearly specifies the approach — follow it

## Process

### Step 1: Frame the Question

Define the design question precisely. A debate without a clear question produces noise.

Format:
```
DESIGN QUESTION: [Specific, answerable question]
CONTEXT: [Brief context from the project design record, when one exists]
CONSTRAINTS: [Non-negotiable requirements from brief, accessibility, taste profile]
STAKES: [Why this decision matters — what it affects downstream]
```

**Example:**
```
DESIGN QUESTION: Should the onboarding flow use a multi-step wizard or a single scrollable page?
CONTEXT: App for first-time pet owners, ages 25-45. Primary persona has mild anxiety about "doing it right."
CONSTRAINTS: Must be completable in under 3 minutes. Must work on mobile. Must not require account creation upfront.
STAKES: Sets the interaction pattern for all future multi-step flows in the app.
```

### Step 2: Assign Advocates

Select 2-3 perspectives to argue for different directions. Each argues FOR its assigned position — an advocate, not a neutral analyst.

| Role | What They Argue |
|------|----------------|
| **Advocate A** | The case for Direction A — strengths, evidence, personas it serves best |
| **Advocate B** | The case for Direction B — strengths, evidence, personas it serves best |
| **Advocate C** (optional) | A third direction, a hybrid, or a "neither — here's why" position |

Assign agents based on their expertise:

| Perspective | Best suited to advocate for |
|-------------|---------------------------|
| UX strategy | Patterns, information architecture, user-flow approaches |
| Visual direction | Layout models, composition, component architecture |
| Content strategy | Tone directions, naming conventions, copy structure |
| Interaction | Interaction paradigms, feedback models, transition approaches |
| Accessibility | The most inclusive option and its cognitive-load implications |
| Research evidence | Evidence-backed positions from competitive research |

### Step 3: Run the Debate

Each advocate delivers their argument in this format:

```markdown
## [Perspective] argues for: [Direction]

### The Case
[2-3 paragraphs making the strongest possible argument for this direction.
Be specific — reference the brief, personas, principles, and evidence.]

### Who This Serves Best
[Which personas benefit most and why]

### Who This Serves Least
[Which personas might struggle and why — be honest]

### Trade-Offs
[What you give up by choosing this direction]

### Evidence
[Research, patterns, competitive examples, or design principles that support this]
```

Rules for advocates:
1. **Argue to win** — make the strongest case you can. Do not hedge
2. **Be honest about weaknesses** — a strong argument acknowledges its trade-offs
3. **Reference the brief** — ground arguments in the project's actual goals
4. **Reference personas** — every argument must address who it helps and who it doesn't
5. **No straw men** — do not weaken the opposing position to make yours look better

### Step 4: Cross-Examination

After all advocates present, each gets one round of rebuttal:

```markdown
### [Perspective] responds to [Other perspective]:
[1-2 paragraphs directly addressing the strongest point of the opposing argument.
Concede what is true. Challenge what is weak.]
```

This prevents echo-chamber advocacy — each agent must engage with the other side's best arguments.

### Step 5: Accessibility Check

Before presenting to the user, apply an accessibility check to all proposed directions:

```markdown
## Accessibility Assessment

| Direction | Accessibility Impact | Concern Level |
|-----------|---------------------|---------------|
| Direction A | [Assessment] | Low / Medium / High |
| Direction B | [Assessment] | Low / Medium / High |

[If any direction creates accessibility barriers, flag it clearly.
This is not an argument for a direction — it is a constraint check.]
```

If a direction has High accessibility concern, it should be flagged prominently in the presentation to the user. The user can still choose it, but they should know the cost.

### Step 6: Present to User

Show the debate to the user in a structured format:

| Direction | Argued by | The case | Best for | Trade-off |
|-----------|-----------|----------|----------|-----------|
| A: [name] | [perspective] | [2-3 sentence summary] | [personas] | [key trade-off] |
| B: [name] | [perspective] | [2-3 sentence summary] | [personas] | [key trade-off] |
| C: [name] (optional) | [perspective] | [hybrid or "neither — here's why"] | [personas] | [key trade-off] |

**Accessibility:** [one-line summary of any concerns].

**Your call:** which direction do you want to take? Ask for more detail on any direction, or propose a hybrid.


### Step 7: Record the Decision

After the user decides:

1. Record the chosen direction, with rationale, in the project design record when one exists
2. Record the rejected directions and why — this is valuable context for future debates
3. If the decision reveals a taste preference, record it as a descriptive taste signal
4. Hand the chosen direction to the workflow that owns the next step

## Debate Depth

Not every debate needs the full process. Scale the depth to the stakes:

| Stakes | Debate Format |
|--------|--------------|
| **High** (sets architectural pattern) | Full debate: 2-3 advocates, cross-examination, accessibility review |
| **Medium** (affects multiple screens) | Quick debate: 2 advocates, no cross-examination, accessibility flag |
| **Low** (affects one component) | Micro debate: 2 options presented as a simple comparison table, user picks |

## Integration

- **Triggered by:** planning when several directions are viable, critique when it recommends a rethink, or the user asking for the trade-offs
- **Updates:** the project design record when one exists, with the decision and the rejected alternatives
- **Informs:** taste signals recorded from the user's choice
- **Pairs with:** `taste-feedback`, [design-review.md](../review/design-review.md)

## Anti-Patterns

| Pattern | Why It Fails |
|---------|-------------|
| Debating after the user has decided | Wastes time. If the user has a direction, execute it |
| Debating trivial decisions | 8px vs 12px padding is not a debate — it's a design system decision |
| Agents being polite instead of advocating | "Both options are great!" is not a debate. Agents must argue to win |
| Presenting a debate without accessibility review | Every direction must be evaluated for inclusion before the user chooses |
| More than 3 directions | Too many options cause decision paralysis. If there are more than 3, narrow down first |
