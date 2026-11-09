#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Persist generated design systems using the Master + Overrides pattern."""

from pathlib import Path

from rendering_master import format_master_md
from rendering_pages import format_page_override_md


def persist_design_system(design_system: dict, page: str = None, output_dir: str = None, page_query: str = None) -> dict:
    """
    Persist design system to design-system/<project>/ folder using Master + Overrides pattern.

    Args:
        design_system: The generated design system dictionary
        page: Optional page name for page-specific override file
        output_dir: Optional output directory (defaults to current working directory)
        page_query: Optional query string for intelligent page override generation

    Returns:
        dict with created file paths and status
    """
    base_dir = Path(output_dir) if output_dir else Path.cwd()

    # Use project name for project-specific folder
    project_name = design_system.get("project_name", "default")
    project_slug = project_name.lower().replace(' ', '-')

    design_system_dir = base_dir / "design-system" / project_slug
    pages_dir = design_system_dir / "pages"

    created_files = []

    design_system_dir.mkdir(parents=True, exist_ok=True)
    pages_dir.mkdir(parents=True, exist_ok=True)

    master_file = design_system_dir / "MASTER.md"

    master_content = format_master_md(design_system)
    with open(master_file, 'w', encoding='utf-8') as f:
        f.write(master_content)
    created_files.append(str(master_file))

    if page:
        page_file = pages_dir / f"{page.lower().replace(' ', '-')}.md"
        page_content = format_page_override_md(design_system, page, page_query)
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(page_content)
        created_files.append(str(page_file))

    return {
        "status": "success",
        "design_system_dir": str(design_system_dir),
        "created_files": created_files
    }
