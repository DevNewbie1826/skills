#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

# ─── How to run ───
# Primary: uv run scripts/python/new-project.py myproject
# Fallback: python3 scripts/python/new-project.py myproject
# ──────────────────

"""Scaffold a Python project with strict configuration.

Uses uv when available. Without uv, it creates the same project skeleton with the
standard library, creates ``.venv``, and installs development dependencies with pip.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

DEV_DEPENDENCIES = ("basedpyright", "ruff", "pytest", "pytest-cov")

TOOL_CONFIG = '''
[dependency-groups]
dev = [
    "basedpyright>=1.21",
    "ruff>=0.8",
    "pytest>=8",
    "pytest-cov>=5",
]

[tool.basedpyright]
typeCheckingMode = "all"
pythonVersion = "3.13"
reportMissingTypeStubs = false
reportUnknownMemberType = false
reportUnknownArgumentType = false
reportUnknownVariableType = false
reportUnknownLambdaType = false
reportUnknownParameterType = false
reportMissingParameterType = false
reportUnnecessaryIsInstance = false
reportUnusedCallResult = false
reportImplicitOverride = false

[tool.ruff]
target-version = "py313"
line-length = 120

[tool.ruff.lint]
select = ["ALL"]
ignore = [
    "COM812",   # trailing comma (conflicts with formatter)
    "ISC001",   # single-line string concat (conflicts with formatter)
    "D1",       # undocumented-public-* (too noisy early on)
    "ANN101",   # deprecated: self annotation
    "ANN102",   # deprecated: cls annotation
    "S101",     # assert used (pytest needs it)
    "PLR2004",  # magic-value-comparison (test data)
    "FBT",      # boolean-trap (too strict for CLIs)
    "TD",       # flake8-todos (noisy)
    "FIX",      # fixme (noisy)
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "PLR2004", "SLF001", "D", "ARG", "ANN"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers --strict-config"
'''

GITIGNORE = """\
__pycache__/
*.py[cod]
*.so
.venv/
dist/
*.egg-info/
.coverage
htmlcov/
.basedpyright/
.ruff_cache/
"""


class _Arguments(argparse.Namespace):
    def __init__(self) -> None:
        super().__init__()
        self.name: str = ""
        self.path: Path = Path(".")
        self.lib: bool = False


def _run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    except OSError:
        return None


def _append_tool_config(pyproject_path: Path) -> None:
    content = pyproject_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    filtered: list[str] = []
    skip_dependency_groups = False
    for line in lines:
        if line.strip().startswith("[dependency-groups]"):
            skip_dependency_groups = True
            continue
        if skip_dependency_groups and line.strip().startswith("["):
            skip_dependency_groups = False
        if not skip_dependency_groups:
            filtered.append(line)
    _ = pyproject_path.write_text("".join(filtered).rstrip("\n") + "\n" + TOOL_CONFIG, encoding="utf-8")


def _write_fallback_project(project_dir: Path, name: str, lib: bool) -> None:
    pyproject = f'''[project]
name = "{name}"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">=3.9"
dependencies = []
'''
    _ = (project_dir / "pyproject.toml").write_text(pyproject + TOOL_CONFIG, encoding="utf-8")
    _ = (project_dir / "README.md").write_text(f"# {name}\n", encoding="utf-8")
    if lib:
        package_dir = project_dir / "src" / name.replace("-", "_")
        package_dir.mkdir(parents=True)
        _ = (package_dir / "__init__.py").write_text("", encoding="utf-8")
    else:
        _ = (project_dir / "main.py").write_text('def main() -> None:\n    print("Hello from ' + name + '")\n\n\nif __name__ == "__main__":\n    main()\n', encoding="utf-8")


def _create_common_files(project_dir: Path, name: str, lib: bool) -> None:
    tests_dir = project_dir / "tests"
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / "__init__.py").touch()
    _ = (project_dir / ".gitignore").write_text(GITIGNORE, encoding="utf-8")
    if lib:
        package_dir = project_dir / "src" / name.replace("-", "_")
        if package_dir.exists():
            (package_dir / "py.typed").touch()


def _scaffold_with_uv(project_dir: Path, lib: bool) -> int:
    command = ["uv", "init", "--lib" if lib else "--app", str(project_dir)]
    result = _run(command)
    if result is None:
        print("uv could not be started. Use python3 -m venv .venv and install dependencies with pip.", file=sys.stderr)
        return 2
    if result.returncode != 0:
        print(f"uv init failed: {result.stderr.strip()}", file=sys.stderr)
        return 1
    _append_tool_config(project_dir / "pyproject.toml")
    result = _run(["uv", "add", "--dev", *DEV_DEPENDENCIES], cwd=project_dir)
    if result is None or result.returncode != 0:
        detail = "could not start" if result is None else result.stderr.strip()
        print(f"uv add failed: {detail}", file=sys.stderr)
        return 1
    return 0


def _pip_path(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "pip.exe"
    return venv_dir / "bin" / "pip"


def _scaffold_without_uv(project_dir: Path, name: str, lib: bool) -> int:
    print("uv is unavailable; using the standard-library venv and pip fallback.")
    _write_fallback_project(project_dir, name, lib)
    venv_dir = project_dir / ".venv"
    result = _run([sys.executable, "-m", "venv", str(venv_dir)])
    if result is None or result.returncode != 0:
        detail = "could not start the interpreter" if result is None else result.stderr.strip()
        print(
            f"uv is unavailable and python3 -m venv failed: {detail}. Install uv or create .venv manually.",
            file=sys.stderr,
        )
        return 2
    result = _run([str(_pip_path(venv_dir)), "install", *DEV_DEPENDENCIES])
    if result is None or result.returncode != 0:
        detail = "could not start pip" if result is None else result.stderr.strip()
        message = f"uv is unavailable. The project skeleton and .venv were created, but pip could not install development dependencies: {detail}. Install uv or run .venv/bin/pip install {' '.join(DEV_DEPENDENCIES)} manually."
        print(message, file=sys.stderr)
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a Python project with strict configuration.")
    _ = parser.add_argument("name", help="Project name")
    _ = parser.add_argument("--path", "-p", type=Path, default=Path("."), help="Parent directory")
    _ = parser.add_argument("--lib", action="store_true", help="Create a publishable library")
    args = _Arguments()
    _ = parser.parse_args(argv, namespace=args)

    project_dir = args.path / args.name
    if project_dir.exists():
        print(f"Error: {project_dir} already exists", file=sys.stderr)
        return 1
    project_dir.mkdir(parents=True)

    if shutil.which("uv") is None:
        status = _scaffold_without_uv(project_dir, args.name, args.lib)
    else:
        status = _scaffold_with_uv(project_dir, args.lib)
    if status != 0:
        return status

    _create_common_files(project_dir, args.name, args.lib)
    print(f"Created: {project_dir}")
    if shutil.which("uv") is None:
        print(f"  cd {args.name} && .venv/bin/python -m pytest")
    else:
        print(f"  cd {args.name} && uv sync && uv run basedpyright . && uv run ruff check .")
    return 0


if __name__ == "__main__":
    sys.exit(main())
