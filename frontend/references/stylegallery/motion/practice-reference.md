---
type: Domain Guide
title: Motion Practice Reference
description: Bounded motion mechanics, heuristics, platform notes, and verification requirements.
domain: motion
lifecycle: experimental
source_repository: https://github.com/emilkowalski/skills
source_path: skills/review-animations/STANDARDS.md
source_revision: 220e8607c90b17337d210125777b7b695f26c221
---

# Motion Practice Reference

Primary role: motion evidence reference.

## Repository Boundary

This is a practice reference, not a standards document. Each item states what kind of claim it is and how to verify it before use.

## Reusable Method

For every proposed rule, record:

```text
Guidance:
Classification: reusable mechanic | opinionated heuristic | platform-specific | unsupported
Context:
Warrant:
Evidence:
Verification:
Boundary:
```

The classification controls authority. A reusable mechanic may explain a causal relationship; a heuristic proposes a starting question; a platform note is valid only for its named source/version; an unsupported claim cannot become a blocker.

## Practice Map

### Purpose And Frequency

Guidance: State why a transition exists and how often the user encounters it.

Classification: opinionated heuristic.

Verification: compare task completion and state comprehension with the behavior present, reduced, and removed.

Boundary: frequency alone does not dictate a universal duration or deletion rule.

### Spatial Continuity

Guidance: Preserve understandable relationships between trigger, moving representation, destination, and dismissal path.

Classification: reusable mechanic.

Verification: inspect before, intermediate, interrupted, and after states together with DOM and focus order.

Boundary: visual continuity cannot override semantic order or accessibility.

### Interruption

Guidance: A repeatedly triggered or directly manipulated transition should respond to new input without visible jumps or input lockout.

Classification: reusable mechanic.

Verification: reverse and retarget the interaction at multiple points while recording the presented state.

Boundary: no specific animation API is required.

### Timing, Easing, And Springs

Guidance: Treat timing curves and dynamic parameters as context-dependent starting hypotheses.

Classification: opinionated heuristic.

Verification: compare variants on the target device and task; record response latency, interruption, overshoot, and completion cues.

Boundary: fixed duration, easing, damping, bounce, or velocity values are not cross-product standards.

### Performance

Guidance: Prefer changes that avoid unnecessary repeated layout and paint work when measurements show they are material.

Classification: reusable mechanic.

Verification: use browser performance traces, frame evidence, target hardware, and representative concurrent work.

Boundary: `transform`, `opacity`, CSS, JavaScript, or Web Animations do not guarantee compositor/GPU execution or superior performance.

### Preferences And Input Capabilities

Guidance: Provide an equivalent state and feedback path for relevant user preferences and input capabilities.

Classification: reusable mechanic.

Verification: inspect the actual reduced-motion behavior, keyboard/pointer/touch flows, focus visibility, and state announcement.

Boundary: reduced motion may mean removal, substitution, or reduction; hover/pointer media features do not identify a universal device class.

### Product Cohesion

Guidance: Evaluate whether motion supports the product's declared task and tone.

Classification: opinionated heuristic.

Verification: use comparative review with named criteria and representative users when the claim concerns human perception.

Boundary: cohesion and delight are not mechanically provable from source code.

## Opinionated Guidance

Shorter, smaller, and less frequent motion is often a useful remediation direction for high-frequency interfaces, but it is not automatically correct. Source-anchored paths and asymmetry may improve comprehension when they correspond to real state relationships; they require rendered evidence.

## Platform-Specific Guidance

Browser compositor behavior, framework shorthands, native springs, pointer models, and operating-system preferences must be sourced and versioned independently. A native-platform value does not automatically translate to CSS or a JavaScript animation library.

## Unsupported Absolutes

- Only transform and opacity may be animated.
- Transform and opacity always run on the GPU.
- CSS animations categorically outperform JavaScript.
- Web Animations is universally hardware accelerated.
- Parent custom-property updates always cause unacceptable recalculation.
- A framework shorthand necessarily drops frames.
- Reduced motion always means crossfade rather than removal.
- Hover and pointer queries identify a touch-device class.
- All interface motion must remain under one fixed duration.

These statements may become scoped hypotheses only after the context, source, and verification protocol are named.

## Verification Contract

Use slow-motion or frame-by-frame inspection for discontinuity, browser traces for delivery claims, keyboard and assistive-technology checks for interaction/accessibility claims, and real-device or user evidence for perceptual quality. State what the selected evidence cannot prove.

## Source, License, And Attribution

- Upstream inspiration: [review-animations/STANDARDS.md](https://github.com/emilkowalski/skills/blob/220e8607c90b17337d210125777b7b695f26c221/skills/review-animations/STANDARDS.md)
- Snapshot: `220e8607c90b17337d210125777b7b695f26c221`
- Upstream license: MIT, Copyright (c) 2026 Emil Kowalski.
- Reuse form: independent method rewrite; upstream prose, tables, code, examples, and distinctive ordering were not retained.
- Evidence boundary: the upstream practice source can suggest questions but cannot prove local performance, accessibility, usability, or quality.

## IA Navigation

Parent: [Motion](index.md).
Next: [Design Engineering](../design-engineering/index.md).
