---
type: Domain Guide
title: Interface Craft Decisions
description: Repository-bounded method for purpose, implementation, review, and evidence decisions at the product layer.
domain: design-engineering
lifecycle: experimental
source_repository: https://github.com/emilkowalski/skills
source_path: skills/emil-design-eng/SKILL.md
source_revision: 220e8607c90b17337d210125777b7b695f26c221
---

# Interface Craft Decisions

Primary role: design-engineering decision guide.

## Repository Boundary

This page helps connect product intent, implementation detail, and verification. It does not create a second StyleGallery principle set, rank visual taste as objective quality, or override Layout, accessibility, source-order, and shared evidence contracts.

## Reusable Method

### Establish The Job

Before tuning the interface, name:

- the user task and state change;
- why the behavior or treatment is necessary;
- how frequently it appears;
- which constraints and inputs it must survive;
- the observable that will decide whether it works.

If those answers are absent, implementation detail is premature.

### Build A Verifiable Representation

Use semantic structure and the owning domain's smallest robust contract first. Prototype the uncertain interaction or visual relationship at the lowest fidelity that exposes its failure modes. A prototype is evidence of one implementation state, not proof of general usability.

### Review Observable Failures

Inspect real content, empty states, long labels, constrained containers, repeated interaction, focus order, alternative input, relevant preferences, and target browsers/devices. When timing or continuity matters, review recordings slowly or frame by frame.

### Record The Decision

Use the shared high-impact claim shape:

```text
Principle:
Claim:
Context:
Use case:
Warrant:
Evidence family:
Verification protocol:
Implementation handoff:
Consumer reference: not_applicable
Consumer reference reason: This blank craft-decision template declares no consumer-specific reference record.
Boundary or limitation:
Debt or escalation:
Decision:
```

This makes the result reviewable without turning the practitioner's preference into authority.

## Decision Questions

| Question | Evidence that can help | What it cannot prove alone |
| --- | --- | --- |
| Does the detail serve the primary task? | Task model, prototype, user evidence | Universal preference |
| Is the default understandable without instruction? | Task completion, terminology test, comparative prototype | Long-term adoption |
| Does repetition make the behavior costly? | Frequency estimate, interaction timing, user evidence | One universal threshold |
| Does the interface preserve continuity? | Rendered sequence, source/focus inspection | Human orientation for every user |
| Does the implementation survive real constraints? | Content/container/input/browser matrix | Brand or aesthetic quality |
| Is the final polish coherent with declared intent? | Named comparative criteria and representative review | Objective beauty |

## Opinionated Guidance

Small details can compound, strong defaults can lower adoption effort, and fresh-eye review can expose defects familiarity hides. These are practitioner heuristics. “Beautiful,” “delightful,” “premium,” “obvious,” and “feels right” require an operational definition and suitable human evidence when used as claims.

## Platform-Specific Guidance

CSS entry features, clipping techniques, Motion/Framer Motion, React effects, component-library variables, pointer capture, and browser-specific performance behavior belong in bounded implementation notes. Verify current official documentation and the actual product surface before recommending them.

## Unsupported Absolutes

- Beauty is not repository leverage or a sufficient acceptance criterion.
- A fixed duration, easing, scale, velocity, or frequency threshold is not universal.
- CSS does not categorically outperform JavaScript.
- A property or API name does not prove hardware acceleration.
- Product popularity does not prove a reusable implementation pattern.
- A promotional or enthusiastic posture is not part of the review contract.

## Verification Contract

Every high-impact recommendation maps `principle -> claim -> context -> warrant -> evidence -> protocol -> boundary/debt`. Visual and interaction claims require rendered evidence; accessibility claims use the accessibility gate; human-quality claims need corresponding user or HCI evidence. A passing implementation keeps the owning domain's constraints visible in the handoff.

## Source, License, And Attribution

- Upstream inspiration: [emil-design-eng/SKILL.md](https://github.com/emilkowalski/skills/blob/220e8607c90b17337d210125777b7b695f26c221/skills/emil-design-eng/SKILL.md)
- Snapshot: `220e8607c90b17337d210125777b7b695f26c221`
- Upstream license: MIT, Copyright (c) 2026 Emil Kowalski.
- Reuse form: independent method rewrite; upstream prose, tables, code, examples, distinctive ordering, and the quotation attributed to Paul Graham were not retained.
- Evidence boundary: this practitioner source suggests review questions; it does not establish local quality, accessibility, performance, or adoption outcomes.

## IA Navigation

Parent: [Design Engineering](index.md).
Next: [Platform Guides](../platform-guides/index.md).
