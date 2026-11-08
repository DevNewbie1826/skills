#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

# ─── How to run ───
# Primary: uv run scripts/python/new-script.py my_tool
# Fallback: python3 scripts/python/new-script.py my_tool
# ──────────────────

"""Generate a PEP 723 Python script with runner guidance and strict boilerplate."""
from __future__ import annotations

import argparse
import stat
import sys
import tempfile
from pathlib import Path

TEMPLATE = '''\
{shebang}
# /// script
# requires-python = ">={python_version}"
# dependencies = [
{deps_block}# ]
# ///

# ─── How to run ───
# Runner options: run with uv, or any PEP 723 runner such as pipx run.
# 1. Run: {run_command}
# 2. Plain Python mode requires declared dependencies to be installed first.
# 3. Or make executable and run:
#      chmod +x {filename} && ./{filename}
# ──────────────────

from __future__ import annotations


def main() -> None:
    """TODO: implement."""


if __name__ == "__main__":
    main()
'''


class _Arguments(argparse.Namespace):
    def __init__(self) -> None:
        super().__init__()
        self.name: str = ""
        self.output: Path | None = None
        self.deps: list[str] = []
        self.py: str = "3.13"
        self.plain: bool = False


def _dependency_block(dependencies: list[str]) -> str:
    if dependencies:
        return "".join(f'#     "{dependency}",\n' for dependency in dependencies)
    return '#     # add deps here, e.g.: "httpx2[http2,brotli,zstd]"\n'


def _destination(name: str, output: Path | None) -> tuple[str, Path]:
    filename = f"{name}.py" if not name.endswith(".py") else name
    if output is not None:
        return filename, output
    temp_dir = Path(tempfile.gettempdir()) / "pep723-scripts"
    temp_dir.mkdir(exist_ok=True)
    return filename, temp_dir / filename


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a PEP 723 Python script.")
    _ = parser.add_argument("name", help="Script name, with or without .py")
    _ = parser.add_argument("--output", "-o", type=Path, help="Output path; defaults to the system temp directory")
    _ = parser.add_argument("--deps", "-d", action="append", default=[], help="Dependency to include; repeat for each dependency")
    _ = parser.add_argument("--py", default="3.13", help="Minimum Python version")
    _ = parser.add_argument("--plain", action="store_true", help="Emit a #!/usr/bin/env python3 shebang")
    args = _Arguments()
    _ = parser.parse_args(argv, namespace=args)

    filename, destination = _destination(args.name, args.output)
    shebang = "#!/usr/bin/env python3" if args.plain else "#!/usr/bin/env -S uv run --script"
    run_command = f"python3 {filename}" if args.plain else f"uv run {filename}"
    content = TEMPLATE.format(
        shebang=shebang,
        python_version=args.py,
        deps_block=_dependency_block(args.deps),
        filename=filename,
        run_command=run_command,
    )

    destination.parent.mkdir(parents=True, exist_ok=True)
    _ = destination.write_text(content, encoding="utf-8")
    if sys.platform != "win32":
        mode = destination.stat().st_mode
        destination.chmod(mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    command = f"python3 {destination}" if args.plain else f"uv run {destination}"
    print(f"Created: {destination}")
    print(f"  Run: {command}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
