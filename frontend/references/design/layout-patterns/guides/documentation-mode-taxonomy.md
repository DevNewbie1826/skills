---
type: Documentation Guide
title: Documentation Mode Taxonomy
description: Primary documentation modes, hybrid decisions, and task routing for layout documentation.
---

# Documentation Mode Taxonomy

Use this guide when adding, moving, or reviewing documentation. Each page should have one primary documentation mode so readers know whether to learn, follow steps, look up a contract, understand a rationale, or apply a policy gate.

## Modes

| Mode | Reader posture | Page should contain |
| --- | --- | --- |
| Tutorial | Learn by completing a first small task. | Ordered path, concrete starting state, completion marker. |
| How-to | Follow steps to finish a known task. | Action sequence, decision points, expected handoff. |
| Reference | Look up stable facts or contracts. | Names, fields, sections, indexes, boundaries. |
| Explanation | Understand principles and rationale. | Why the documentation works this way, scope, tradeoffs. |
| Policy/procedure | Decide whether work is admissible. | Required contract, evidence, blocking conditions, boundary. |

Do not use `mixed` as a mode. If a page has more than one reading posture, keep one primary mode and record the secondary mode plus the reason.

## Page-Mode Matrix

| Page or family | Primary mode | Secondary mode | Routing note |
| --- | --- | --- | --- |
| [Layout Planning Guide](../planning-guide.md) | How-to | Explanation | Start here before the layout problem is obvious. |
| [Layout Pattern Catalog](../CATALOG.md) | Reference | None | Use when the pattern name or spatial problem is already known. |
| [Decision Tree](decision-tree.md) | How-to | Reference | Route from constraints to pattern families and recipes. |
| [Layout Brief](layout-brief.md) | How-to | Reference | Fill before selecting a pattern stack. |
| [Controlled Vocabulary](vocabulary.md) | Reference | Policy/procedure | Look up canonical terms, aliases, deprecated terms, and scannability rules. |
| [Webpage Generation Workflow](webpage-generation-workflow.md) | How-to | Policy/procedure | Convert raw content into a webpage handoff while preserving evaluation order. |
| This taxonomy | Reference | Policy/procedure | Audit documentation modes and routing. |
| [Recipe index](../../layout-recipes/index.md) | Reference | How-to | Look up screen-level recipes. |
| [Primitive-to-recipe matrix](../../layout-recipes/primitive-to-recipe-matrix.md) | Reference | How-to | Compare recipe pattern slots, substitution risks, and structural responsibilities. |
| Recipe pages | How-to | Reference | Compose a screen while preserving pattern stacks, constraints, and scroll ownership. |
| [Pattern category index](../index.md) | Reference | None | Browse pattern families. |
| Pattern category pages | Reference | None | Browse the patterns in one category. |
| Pattern pages | Reference | None | Consult a stable layout contract for one spatial problem. |

The family rows are intentional. Pattern pages share one stable reference contract, and category indexes share one stable reference posture.

## Hybrid Decisions

| Page or family | Decision | Reason |
| --- | --- | --- |
| Layout Planning Guide | Keep and label | The guide is a how-to entry point, but it needs explanation to separate before-problem and after-problem use. |
| Layout Pattern Catalog | Keep and label | The catalog is a reference index, with enough routing to choose the next pattern. |
| Decision Tree | Keep and label | The page is navigational how-to; reference links are necessary outputs, not a competing mode. |
| Layout Brief | Keep and label | The page is a fill-in how-to whose prompts also act as a stable brief reference. |
| Controlled Vocabulary | Keep and label | The page is a term reference with policy rules for canonical and deprecated language. |
| Webpage Generation Workflow | Keep and label | The page is a how-to workflow with evaluation checkpoints around image reference and handoff order. |
| This taxonomy | Keep and label | The page is a reference matrix with policy rules for avoiding unlabeled mixed modes. |
| Recipe index | Keep and label | The page is a recipe lookup index, with enough how-to routing to choose the next recipe. |
| Primitive-to-recipe matrix | Keep and label | The page is a reference matrix that supports how-to substitution decisions. |
| Recipe pages | Intentional hybrid | Recipes teach composition steps while preserving reusable reference contracts for pattern stacks, constraints, and scroll ownership. |
| Pattern category indexes | Keep as reference | Category indexes route readers to pattern contracts. |
| Pattern pages | Keep as reference | Pattern pages define stable spatial contracts with examples, constraints, and boundaries. |

## Task Routing

| User task | Read first | Then read |
| --- | --- | --- |
| Choose a layout when the pattern name is unknown. | [Layout Planning Guide](../planning-guide.md) | [Decision Tree](decision-tree.md) |
| Turn raw content into a homepage or webpage. | [Webpage Generation Workflow](webpage-generation-workflow.md) | [Homepage recipe](../../layout-recipes/homepage.md), then evaluate content-layout fit |
| Look up a known layout primitive. | [Layout Pattern Catalog](../CATALOG.md) | The relevant pattern page |
| Compose a screen from reusable patterns. | [Recipe index](../../layout-recipes/index.md) | The matching recipe page and linked pattern contracts |
| Review a layout handoff. | [Layout Brief](layout-brief.md) | The relevant recipe and pattern contracts |

## First-Run Tutorial Outline

The webpage-generation path needs a tutorial only when a reader has raw content and has not yet produced a layout handoff before. Keep the full workflow in [Webpage Generation Workflow](webpage-generation-workflow.md); add a separate tutorial only if repeated users need a smaller first success path.

Suggested tutorial outline:

1. Start with one short homepage brief and supplied content blocks.
2. Name the use case and primary task.
3. Map content blocks to section jobs.
4. Choose [Homepage](../../layout-recipes/homepage.md) or reject it with one reason.
5. Run the harmony evaluation checklist.
6. Produce the implementation handoff.

Completion marker:

```txt
First-run complete when the reader has a use case, section-job map, selected recipe, harmony-evaluation decision, and implementation handoff.
```

Do not treat generated imagery, screenshots, or decorative choices as the tutorial completion marker. The first success is a handoff that can be implemented without weakening semantic order, scroll ownership, or verification boundaries.
