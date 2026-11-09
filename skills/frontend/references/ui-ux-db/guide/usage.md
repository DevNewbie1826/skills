# Usage Guide

Read this when running the bundled search CLI: prerequisites, the step-by-step workflow, domain/stack tables, an example workflow, output formats, and query tips.

Part of [UI/UX Pro Max - Design Intelligence](../README.md)

## How to Use

Search specific domains using the CLI tool below.

---

## Prerequisites

Check if Python is installed:

```bash
python3 --version || python --version
```

If Python is not installed, install it for your OS (e.g., `brew install python3` on macOS).

---

## How to Use This Skill

Use this skill when the user requests any of the following:

| Scenario | Start From |
|----------|------------|
| **New project / page** | Step 1 → Step 2 (design system) |
| **New component** | Step 3 (domain search: style, ux) |
| **Choose style / color / font** | Step 2 (design system) |
| **Review existing UI** | [Quick Reference](quick-reference.md#quick-reference) |
| **Fix a UI bug** | [Quick Reference](quick-reference.md#quick-reference) → relevant section |
| **Improve / optimize** | Step 3 (domain search: ux, react) |
| **Implement dark mode** | Step 3 (domain: style "dark mode") |
| **Add charts / data viz** | Step 3 (domain: chart) |
| **Stack best practices** | Step 4 (stack search) |

Follow this workflow:

### Step 1: Analyze User Requirements

Extract key information from user request:
- **Product type**: Entertainment (social, video, music, gaming), Tool (scanner, editor, converter), Productivity (task manager, notes, calendar), or hybrid
- **Target audience**: C-end consumer users; consider age group, usage context (commute, leisure, work)
- **Style keywords**: playful, vibrant, minimal, dark mode, content-first, immersive, etc.
- **Stack**: the project's actual stack; choose the matching option from the available stack list

### Step 2: Generate Design System

Use `--design-system` when you need a comprehensive recommendation with reasoning:

```bash
python3 $SKILL_DIR/references/ui-ux-db/scripts/search.py "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

This command:
1. Searches domains in parallel (product, style, color, landing, typography)
2. Applies reasoning rules from `ui-reasoning.csv` to select best matches
3. Returns complete design system: pattern, style, colors, typography, effects
4. Includes anti-patterns to avoid

**Example:**
```bash
python3 $SKILL_DIR/references/ui-ux-db/scripts/search.py "beauty spa wellness service" --design-system -p "Serenity Spa"
```

### Step 2b: Persist Design System (Master + Overrides Pattern)

To save the design system for **hierarchical retrieval across sessions**, add `--persist`:

```bash
python3 $SKILL_DIR/references/ui-ux-db/scripts/search.py "<query>" --design-system --persist -p "Project Name"
```

This creates:
- `design-system/<project-slug>/MASTER.md` — Global Source of Truth with all design rules
- `design-system/<project-slug>/pages/` — Folder for page-specific overrides

**With page-specific override:**
```bash
python3 $SKILL_DIR/references/ui-ux-db/scripts/search.py "<query>" --design-system --persist -p "Project Name" --page "dashboard"
```

This also creates:
- `design-system/<project-slug>/pages/dashboard.md` — Page-specific deviations from Master

**How hierarchical retrieval works:**
1. When building a specific page (e.g., "Checkout"), first check `design-system/<project-slug>/pages/checkout.md`
2. If the page file exists, its rules **override** the Master file
3. If not, use `design-system/<project-slug>/MASTER.md` exclusively

**Context-aware retrieval prompt:**
```
I am building the [Page Name] page. Please read design-system/<project-slug>/MASTER.md.
Also check if design-system/<project-slug>/pages/[page-name].md exists.
If the page file exists, prioritize its rules.
If not, use the Master rules exclusively.
Now, generate the code...
```

### Step 3: Supplement with Detailed Searches (as needed)

After getting the design system, use domain searches to get additional details:

```bash
python3 $SKILL_DIR/references/ui-ux-db/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

### Step 4: Stack Guidelines

Get implementation-specific best practices for the project's stack:

```bash
python3 $SKILL_DIR/references/ui-ux-db/scripts/search.py "<keyword>" --stack <stack>
```

---

## Search Reference

### Available Domains

| Domain | Use For | Example Keywords |
|--------|---------|------------------|
| `product` | Product type recommendations | SaaS, e-commerce, portfolio, healthcare, beauty, service |
| `style` | UI styles, colors, effects | glassmorphism, minimalism, dark mode, brutalism |
| `typography` | Font pairings and implementation details | elegant, playful, professional, modern |
| `icons` | Icon libraries and usage guidance | button, navigation, status, alert |
| `color` | Color palettes by product type | saas, ecommerce, healthcare, beauty, fintech, service |
| `landing` | Page structure and CTA strategies | hero, testimonial, pricing, social-proof |
| `chart` | Chart types and library recommendations | trend, comparison, timeline, funnel, pie |
| `ux` | Best practices and anti-patterns | animation, accessibility, z-index, loading |
| `react` | React performance guidance | waterfall, bundle, suspense, memo, rerender, cache |
| `web` | App interface guidance | accessibility, touch targets, safe areas, dynamic type |

### Available Stacks

| Stack | Focus |
|-------|-------|
| `react` | React UI implementation guidelines |
| `nextjs` | Next.js UI implementation guidelines |
| `vue` | Vue UI implementation guidelines |
| `svelte` | Svelte UI implementation guidelines |
| `astro` | Astro UI implementation guidelines |
| `swiftui` | SwiftUI implementation guidelines |
| `react-native` | React Native UI implementation guidelines |
| `flutter` | Flutter UI implementation guidelines |
| `nuxtjs` | Nuxt framework UI implementation guidelines |
| `nuxt-ui` | Nuxt UI component guidelines |
| `html-tailwind` | HTML and Tailwind UI implementation guidelines |
| `shadcn` | shadcn/ui component guidelines |
| `jetpack-compose` | Jetpack Compose UI implementation guidelines |

---

## Output Formats

The `--design-system` flag supports two output formats:

```bash
# ASCII box (default) - best for terminal display
python3 $SKILL_DIR/references/ui-ux-db/scripts/search.py "fintech crypto" --design-system

# Markdown - best for documentation
python3 $SKILL_DIR/references/ui-ux-db/scripts/search.py "fintech crypto" --design-system -f markdown
```

---

## Tips for Better Results

### Query Strategy

- Use **multi-dimensional keywords** — combine product + industry + tone + density: `"entertainment social vibrant content-dense"` not just `"app"`
- Try different keywords for the same need: `"playful neon"` → `"vibrant dark"` → `"content-first minimal"`
- Use `--design-system` first for full recommendations, then `--domain` to deep-dive any dimension you're unsure about
- Add `--stack <stack>` for implementation-specific guidance

### Common Sticking Points

| Problem | What to Do |
|---------|------------|
| Can't decide on style/color | Re-run `--design-system` with different keywords |
| Dark mode contrast issues | [Quick Reference §6](quick-reference.md#6-typography--color-medium): `color-dark-mode` + `color-accessible-pairs` |
| Animations feel unnatural | [Quick Reference §7](quick-reference.md#7-animation-medium): `spring-physics` + `easing` + `exit-faster-than-enter` |
| Form UX is poor | [Quick Reference §8](quick-reference.md#8-forms--feedback-medium): `inline-validation` + `error-clarity` + `focus-management` |
| Navigation feels confusing | [Quick Reference §9](quick-reference.md#9-navigation-patterns-high): `nav-hierarchy` + `bottom-nav-limit` + `back-behavior` |
| Layout breaks on small screens | [Quick Reference §5](quick-reference.md#5-layout--responsive-high): `mobile-first` + `breakpoint-consistency` |
| Performance / jank | [Quick Reference §3](quick-reference.md#3-performance-high): `virtualize-lists` + `main-thread-budget` + `debounce-throttle` |

---

## Common Rules for Professional UI
