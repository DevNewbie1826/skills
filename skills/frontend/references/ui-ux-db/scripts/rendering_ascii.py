#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ASCII box renderer for generated design systems."""

import os
from datetime import datetime

BOX_WIDTH = 90  # Wider box for more content

COLOR_ENTRIES = (
    ("Primary",      "primary",      "--color-primary"),
    ("On Primary",   "on_primary",   "--color-on-primary"),
    ("Secondary",    "secondary",    "--color-secondary"),
    ("Accent/CTA",   "accent",       "--color-accent"),
    ("Background",   "background",   "--color-background"),
    ("Foreground",   "foreground",   "--color-foreground"),
    ("Muted",        "muted",        "--color-muted"),
    ("Border",       "border",       "--color-border"),
    ("Destructive",  "destructive",  "--color-destructive"),
    ("Ring",         "ring",         "--color-ring"),
)

CHECKLIST_ITEMS = (
    "No emojis as icons (use SVG: Heroicons/Lucide)",
    "cursor-pointer on all clickable elements",
    "Hover states with smooth transitions (150-300ms)",
    "Light mode: text contrast 4.5:1 minimum",
    "Focus states visible for keyboard nav",
    "prefers-reduced-motion respected",
    "Responsive: 375px, 768px, 1024px, 1440px",
)

def color_rows(colors: dict):
    """Yield (label, hex, css_var) for each populated palette role."""
    for label, key, css_var in COLOR_ENTRIES:
        hex_val = colors.get(key, "")
        if hex_val:
            yield label, hex_val, css_var


def hex_to_ansi(hex_color: str) -> str:
    """Convert hex color to ANSI True Color swatch (██) with fallback."""
    if not hex_color or not hex_color.startswith('#'):
        return ""
    colorterm = os.environ.get('COLORTERM', '')
    if colorterm not in ('truecolor', '24bit'):
        return ""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return ""
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"\033[38;2;{r};{g};{b}m██\033[0m "


def ansi_ljust(s: str, width: int) -> str:
    """Like str.ljust but accounts for zero-width ANSI escape sequences."""
    import re
    visible_len = len(re.sub(r'\033\[[0-9;]*m', '', s))
    pad = width - visible_len
    return s + (" " * max(0, pad))


def section_header(name: str, width: int) -> str:
    """Create a Unicode section separator: ├─── NAME ───...┤"""
    label = f"─── {name} "
    fill = "─" * (width - len(label) - 1)
    return f"├{label}{fill}┤"


def wrap_text(text: str, prefix: str, width: int) -> list:
    """Wrap long text into multiple lines."""
    if not text:
        return []
    words = text.split()
    lines = []
    current_line = prefix
    for word in words:
        if len(current_line) + len(word) + 1 <= width - 2:
            current_line += (" " if current_line != prefix else "") + word
        else:
            if current_line != prefix:
                lines.append(current_line)
            current_line = prefix + word
    if current_line != prefix:
        lines.append(current_line)
    return lines

def format_ascii_box(design_system: dict) -> str:
    """Format design system as Unicode box with ANSI color swatches."""
    project = design_system.get("project_name", "PROJECT")
    pattern = design_system.get("pattern", {})
    style = design_system.get("style", {})
    colors = design_system.get("colors", {})
    typography = design_system.get("typography", {})
    effects = design_system.get("key_effects", "")
    anti_patterns = design_system.get("anti_patterns", "")

    sections = pattern.get("sections", "").split(">")
    sections = [s.strip() for s in sections if s.strip()]

    lines = []
    w = BOX_WIDTH - 1

    lines.append("╔" + "═" * w + "╗")
    lines.append(ansi_ljust(f"║  TARGET: {project} - RECOMMENDED DESIGN SYSTEM", BOX_WIDTH) + "║")
    lines.append("╚" + "═" * w + "╝")
    lines.append("┌" + "─" * w + "┐")

    lines.append(section_header("PATTERN", BOX_WIDTH + 1))
    lines.append(f"│  Name: {pattern.get('name', '')}".ljust(BOX_WIDTH) + "│")
    if pattern.get('conversion'):
        lines.append(f"│     Conversion: {pattern.get('conversion', '')}".ljust(BOX_WIDTH) + "│")
    if pattern.get('cta_placement'):
        lines.append(f"│     CTA: {pattern.get('cta_placement', '')}".ljust(BOX_WIDTH) + "│")
    lines.append("│     Sections:".ljust(BOX_WIDTH) + "│")
    for i, section in enumerate(sections, 1):
        lines.append(f"│       {i}. {section}".ljust(BOX_WIDTH) + "│")

    lines.append(section_header("STYLE", BOX_WIDTH + 1))
    lines.append(f"│  Name: {style.get('name', '')}".ljust(BOX_WIDTH) + "│")
    light = style.get("light_mode", "")
    dark = style.get("dark_mode", "")
    if light or dark:
        lines.append(f"│     Mode Support: Light {light}  Dark {dark}".ljust(BOX_WIDTH) + "│")
    if style.get("keywords"):
        for line in wrap_text(f"Keywords: {style.get('keywords', '')}", "│     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "│")
    if style.get("best_for"):
        for line in wrap_text(f"Best For: {style.get('best_for', '')}", "│     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "│")
    if style.get("performance") or style.get("accessibility"):
        perf_a11y = f"Performance: {style.get('performance', '')} | Accessibility: {style.get('accessibility', '')}"
        lines.append(f"│     {perf_a11y}".ljust(BOX_WIDTH) + "│")

    lines.append(section_header("COLORS", BOX_WIDTH + 1))
    for label, hex_val, css_var in color_rows(colors):
        swatch = hex_to_ansi(hex_val)
        content = f"│     {swatch}{label + ':':14s} {hex_val:10s} ({css_var})"
        lines.append(ansi_ljust(content, BOX_WIDTH) + "│")
    if colors.get("notes"):
        for line in wrap_text(f"Notes: {colors.get('notes', '')}", "│     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "│")

    lines.append(section_header("TYPOGRAPHY", BOX_WIDTH + 1))
    lines.append(f"│  {typography.get('heading', '')} / {typography.get('body', '')}".ljust(BOX_WIDTH) + "│")
    if typography.get("mood"):
        for line in wrap_text(f"Mood: {typography.get('mood', '')}", "│     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "│")
    if typography.get("best_for"):
        for line in wrap_text(f"Best For: {typography.get('best_for', '')}", "│     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "│")
    if typography.get("google_fonts_url"):
        lines.append(f"│     Google Fonts: {typography.get('google_fonts_url', '')}".ljust(BOX_WIDTH) + "│")
    if typography.get("css_import"):
        lines.append(f"│     CSS Import: {typography.get('css_import', '')[:70]}...".ljust(BOX_WIDTH) + "│")

    if effects:
        lines.append(section_header("KEY EFFECTS", BOX_WIDTH + 1))
        for line in wrap_text(effects, "│     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "│")

    if anti_patterns:
        lines.append(section_header("AVOID", BOX_WIDTH + 1))
        for line in wrap_text(anti_patterns, "│     ", BOX_WIDTH):
            lines.append(line.ljust(BOX_WIDTH) + "│")

    lines.append(section_header("PRE-DELIVERY CHECKLIST", BOX_WIDTH + 1))
    for item in CHECKLIST_ITEMS:
        lines.append(f"│     [ ] {item}".ljust(BOX_WIDTH) + "│")

    lines.append("└" + "─" * w + "┘")

    return "\n".join(lines)
