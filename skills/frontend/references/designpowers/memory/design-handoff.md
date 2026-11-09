# Design Handoff

Read this when completed design work must be communicated to engineering — component specifications, rationale, trade-offs, and accessibility requirements an implementer can follow directly.

Back-link: [Lane D — Design Record, Debt & Handoff](../lane-d-memory.md)

Handoff is where design intent meets engineering reality. A poor handoff produces a poor implementation, regardless of how good the design was. This skill ensures every decision is documented clearly enough that an engineer who was not in the room can implement it faithfully.

## When to Use

- Design critique is complete and issues are resolved
- Design work is ready for engineering implementation
- Engineering team needs specifications for components, layouts, or interactions

## Process

### Step 1: Assemble the Handoff Package

Gather all artefacts from the design process:
- Design brief (context and intent)
- Personas (who this serves)
- Design principles (what guides decisions)
- Visual specifications (layouts, colors, typography)
- Interaction specifications (states, transitions, feedback)
- Accessibility requirements (per component)
- Design system references (tokens, components used)

### Step 2: Write Component Specifications

For each component or screen, provide:

```markdown
## [Component/Screen Name]

### Purpose
[What this element does and why it exists]

### Visual Specification
- Layout: [positioning, spacing, alignment — reference tokens]
- Typography: [font, size, weight, line-height — reference tokens]
- Color: [foreground, background, borders — reference tokens]
- Responsive behaviour: [how this adapts at each breakpoint]

### Interaction Specification
- States: [default, hover, focus, active, disabled, error, loading]
- Transitions: [what animates, duration, easing, reduced-motion alternative]
- Feedback: [what the user perceives at each state change]

### Accessibility Requirements
- Semantic element: [which HTML element to use]
- ARIA: [roles, labels, states — only if semantic HTML is insufficient]
- Keyboard: [tab order, interaction keys, focus management]
- Screen reader: [what is announced in each state]
- Contrast: [specific ratios for text and UI elements]
- Touch: [target sizes]
- Motion: [prefers-reduced-motion behaviour]

### Content
- Labels: [exact text for labels, buttons, headings]
- Error messages: [exact text for each error state]
- Help text: [exact text for instructions or hints]
- Alt text: [exact text for images]

### Design Rationale
[Why this component looks and behaves this way — reference design principles and persona needs]
```

### Step 3: Document Decisions and Trade-offs

For decisions that might seem arbitrary or surprising to an engineer, explain:
- **The decision:** what was chosen
- **The alternatives considered:** what was not chosen
- **The reason:** why this option serves users better
- **The accessibility driver:** which inclusive design requirement influenced this

### Step 4: Name the Accessibility Requirements

Specify each component's requirements in Step 2 and let the WCAG gate own the evidence: run [perfection/wcag-gate.md](../../perfection/wcag-gate.md) and record its PASS/FAIL table with the handoff. Do not carry a second checklist here.

### Step 5: User Review

Present the handoff package to the user before sharing with engineering. Confirm:
- Is the rationale clear?
- Are there any design decisions that need more context?
- Are the accessibility requirements complete?

## Integration

- **Follows:** critique that passed its findings
- **Pairs with:** [design-review.md](../review/design-review.md) and final verification before declaring work complete
