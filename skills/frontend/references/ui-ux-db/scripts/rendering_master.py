#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MASTER.md renderer for the Master + Overrides persistence pattern."""

from datetime import datetime

from rendering_ascii import color_rows

MASTER_CHECKLIST_ITEMS = (
    "No emojis used as icons (use SVG instead)",
    "All icons from consistent icon set (Heroicons/Lucide)",
    "`cursor-pointer` on all clickable elements",
    "Hover states with smooth transitions (150-300ms)",
    "Light mode: text contrast 4.5:1 minimum",
    "Focus states visible for keyboard navigation",
    "`prefers-reduced-motion` respected",
    "Responsive: 375px, 768px, 1024px, 1440px",
    "No content hidden behind fixed navbars",
    "No horizontal scroll on mobile",
)

def format_master_md(design_system: dict) -> str:
    """Format design system as MASTER.md with hierarchical override logic."""
    project = design_system.get("project_name", "PROJECT")
    pattern = design_system.get("pattern", {})
    style = design_system.get("style", {})
    colors = design_system.get("colors", {})
    typography = design_system.get("typography", {})
    effects = design_system.get("key_effects", "")
    anti_patterns = design_system.get("anti_patterns", "")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []

    lines.append("# Design System Master File")
    lines.append("")
    lines.append("> **LOGIC:** When building a specific page, first check `design-system/pages/[page-name].md`.")
    lines.append("> If that file exists, its rules **override** this Master file.")
    lines.append("> If not, strictly follow the rules below.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"**Project:** {project}")
    lines.append(f"**Generated:** {timestamp}")
    lines.append(f"**Category:** {design_system.get('category', 'General')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Global Rules")
    lines.append("")

    lines.append("### Color Palette")
    lines.append("")
    lines.append("| Role | Hex | CSS Variable |")
    lines.append("|------|-----|--------------|")
    for label, hex_val, css_var in color_rows(colors):
        lines.append(f"| {label} | `{hex_val}` | `{css_var}` |")
    lines.append("")
    if colors.get("notes"):
        lines.append(f"**Color Notes:** {colors.get('notes', '')}")
        lines.append("")

    lines.append("### Typography")
    lines.append("")
    lines.append(f"- **Heading Font:** {typography.get('heading', 'Inter')}")
    lines.append(f"- **Body Font:** {typography.get('body', 'Inter')}")
    if typography.get("mood"):
        lines.append(f"- **Mood:** {typography.get('mood', '')}")
    if typography.get("google_fonts_url"):
        lines.append(f"- **Google Fonts:** [{typography.get('heading', '')} + {typography.get('body', '')}]({typography.get('google_fonts_url', '')})")
    lines.append("")
    if typography.get("css_import"):
        lines.append("**CSS Import:**")
        lines.append("```css")
        lines.append(typography.get("css_import", ""))
        lines.append("```")
        lines.append("")

    lines.append("### Spacing Variables")
    lines.append("")
    lines.append("| Token | Value | Usage |")
    lines.append("|-------|-------|-------|")
    lines.append("| `--space-xs` | `4px` / `0.25rem` | Tight gaps |")
    lines.append("| `--space-sm` | `8px` / `0.5rem` | Icon gaps, inline spacing |")
    lines.append("| `--space-md` | `16px` / `1rem` | Standard padding |")
    lines.append("| `--space-lg` | `24px` / `1.5rem` | Section padding |")
    lines.append("| `--space-xl` | `32px` / `2rem` | Large gaps |")
    lines.append("| `--space-2xl` | `48px` / `3rem` | Section margins |")
    lines.append("| `--space-3xl` | `64px` / `4rem` | Hero padding |")
    lines.append("")

    lines.append("### Shadow Depths")
    lines.append("")
    lines.append("| Level | Value | Usage |")
    lines.append("|-------|-------|-------|")
    lines.append("| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Subtle lift |")
    lines.append("| `--shadow-md` | `0 4px 6px rgba(0,0,0,0.1)` | Cards, buttons |")
    lines.append("| `--shadow-lg` | `0 10px 15px rgba(0,0,0,0.1)` | Modals, dropdowns |")
    lines.append("| `--shadow-xl` | `0 20px 25px rgba(0,0,0,0.15)` | Hero images, featured cards |")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Component Specs")
    lines.append("")

    lines.append("### Buttons")
    lines.append("")
    lines.append("```css")
    lines.append("/* Primary Button */")
    lines.append(".btn-primary {")
    lines.append(f"  background: {colors.get('cta', '#F97316')};")
    lines.append("  color: white;")
    lines.append("  padding: 12px 24px;")
    lines.append("  border-radius: 8px;")
    lines.append("  font-weight: 600;")
    lines.append("  transition: all 200ms ease;")
    lines.append("  cursor: pointer;")
    lines.append("}")
    lines.append("")
    lines.append(".btn-primary:hover {")
    lines.append("  opacity: 0.9;")
    lines.append("  transform: translateY(-1px);")
    lines.append("}")
    lines.append("")
    lines.append("/* Secondary Button */")
    lines.append(".btn-secondary {")
    lines.append(f"  background: transparent;")
    lines.append(f"  color: {colors.get('primary', '#2563EB')};")
    lines.append(f"  border: 2px solid {colors.get('primary', '#2563EB')};")
    lines.append("  padding: 12px 24px;")
    lines.append("  border-radius: 8px;")
    lines.append("  font-weight: 600;")
    lines.append("  transition: all 200ms ease;")
    lines.append("  cursor: pointer;")
    lines.append("}")
    lines.append("```")
    lines.append("")

    lines.append("### Cards")
    lines.append("")
    lines.append("```css")
    lines.append(".card {")
    lines.append(f"  background: {colors.get('background', '#FFFFFF')};")
    lines.append("  border-radius: 12px;")
    lines.append("  padding: 24px;")
    lines.append("  box-shadow: var(--shadow-md);")
    lines.append("  transition: all 200ms ease;")
    lines.append("  cursor: pointer;")
    lines.append("}")
    lines.append("")
    lines.append(".card:hover {")
    lines.append("  box-shadow: var(--shadow-lg);")
    lines.append("  transform: translateY(-2px);")
    lines.append("}")
    lines.append("```")
    lines.append("")

    lines.append("### Inputs")
    lines.append("")
    lines.append("```css")
    lines.append(".input {")
    lines.append("  padding: 12px 16px;")
    lines.append("  border: 1px solid #E2E8F0;")
    lines.append("  border-radius: 8px;")
    lines.append("  font-size: 16px;")
    lines.append("  transition: border-color 200ms ease;")
    lines.append("}")
    lines.append("")
    lines.append(".input:focus {")
    lines.append(f"  border-color: {colors.get('primary', '#2563EB')};")
    lines.append("  outline: none;")
    lines.append(f"  box-shadow: 0 0 0 3px {colors.get('primary', '#2563EB')}20;")
    lines.append("}")
    lines.append("```")
    lines.append("")

    lines.append("### Modals")
    lines.append("")
    lines.append("```css")
    lines.append(".modal-overlay {")
    lines.append("  background: rgba(0, 0, 0, 0.5);")
    lines.append("  backdrop-filter: blur(4px);")
    lines.append("}")
    lines.append("")
    lines.append(".modal {")
    lines.append("  background: white;")
    lines.append("  border-radius: 16px;")
    lines.append("  padding: 32px;")
    lines.append("  box-shadow: var(--shadow-xl);")
    lines.append("  max-width: 500px;")
    lines.append("  width: 90%;")
    lines.append("}")
    lines.append("```")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Style Guidelines")
    lines.append("")
    lines.append(f"**Style:** {style.get('name', 'Minimalism')}")
    lines.append("")
    if style.get("keywords"):
        lines.append(f"**Keywords:** {style.get('keywords', '')}")
        lines.append("")
    if style.get("best_for"):
        lines.append(f"**Best For:** {style.get('best_for', '')}")
        lines.append("")
    if effects:
        lines.append(f"**Key Effects:** {effects}")
        lines.append("")

    lines.append("### Page Pattern")
    lines.append("")
    lines.append(f"**Pattern Name:** {pattern.get('name', '')}")
    lines.append("")
    if pattern.get('conversion'):
        lines.append(f"- **Conversion Strategy:** {pattern.get('conversion', '')}")
    if pattern.get('cta_placement'):
        lines.append(f"- **CTA Placement:** {pattern.get('cta_placement', '')}")
    lines.append(f"- **Section Order:** {pattern.get('sections', '')}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Anti-Patterns (Do NOT Use)")
    lines.append("")
    if anti_patterns:
        anti_list = [a.strip() for a in anti_patterns.split("+")]
        for anti in anti_list:
            if anti:
                lines.append(f"- ❌ {anti}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Pre-Delivery Checklist")
    lines.append("")
    lines.append("Before delivering any UI code, verify:")
    lines.append("")
    for item in MASTER_CHECKLIST_ITEMS:
        lines.append(f"- [ ] {item}")
    lines.append("")

    return "\n".join(lines)
