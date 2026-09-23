#!/usr/bin/env python3
"""Synchronize the portable StyleGallery documentation snapshot."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import cast
from urllib.parse import unquote

REPO = Path(__file__).resolve().parent.parent
SOURCE = "https://github.com/changeroa/StyleGallery"
DOMAINS = (
    "patterns", "recipes", "guides", "motion", "design-engineering",
    "game-ui", "platform-guides", "design-terminology", "layout",
)
EXCLUDED = ("design-engineering/reference-profiles/", "game-ui/unity/data/")
ROOT_FILES = ("index.md", "CATALOG.md", "GUIDE.md", "LICENSE-DOCS", "NOTICE")


class Arguments(argparse.Namespace):
    def __init__(self) -> None:
        super().__init__()
        self.upstream: Path = Path(".")
        self.dest: Path = Path("frontend/references/stylegallery")
        self.check: bool = False


LINK = re.compile(r"\]\(([^)\n]+)\)")
DEFINITION = re.compile(r"^(\s{0,3}\[[^\]\n]+\]:\s*)(<[^>\n]+>|\S+)", re.MULTILINE)
CODE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
MAINTENANCE = re.compile(
    r"^(?:<!-- Generated from `scripts/.*?-->|Generated from `scripts/.*)$"
)


def selected(upstream: Path) -> list[Path]:
    """Return the source paths of the documented portable subset."""
    files = [Path(name) for name in ROOT_FILES]
    for domain in DOMAINS:
        files.extend(
            path.relative_to(upstream)
            for path in (upstream / domain).rglob("*.md")
            if not path.relative_to(upstream).as_posix().startswith(EXCLUDED)
        )
    return sorted(files)


def linked_url(raw: str, source: Path, upstream: Path, included: set[Path], revision: str) -> str:
    """Pin links to excluded upstream content while preserving anchors and titles."""
    token = raw.split(maxsplit=1)[0]
    bracketed = token.startswith("<") and token.endswith(">")
    target = token[1:-1] if bracketed else token
    if not target or target.startswith(("#", "/", "//")) or re.match(r"^[a-z][\w+.-]*:", target, re.I):
        return raw
    path_part, sep, fragment = target.partition("#")
    path_part = unquote(path_part.split("?", 1)[0])
    resolved = (upstream / source.parent / path_part).resolve()
    if not resolved.is_relative_to(upstream.resolve()):
        return raw
    relative = resolved.relative_to(upstream.resolve())
    present = relative in included or (resolved.is_dir() and any(relative in p.parents for p in included))
    if present:
        return raw
    url = f"{SOURCE}/{'tree' if resolved.is_dir() or target.endswith('/') else 'blob'}/{revision}/{relative.as_posix()}"
    if sep:
        url += f"#{fragment}"
    return raw.replace(token, f"<{url}>" if bracketed else url, 1)


def transform(text: str, source: Path, upstream: Path, included: set[Path],
              revision: str, cues: dict[str, str]) -> str:
    """Apply local routing and replace references to content outside the snapshot."""
    lines = [line for line in text.splitlines(keepends=True) if not MAINTENANCE.match(line.strip())]
    text = "".join(lines)

    def code_link(match: re.Match[str]) -> str:
        span = match.group(1)
        token = span.strip().split(maxsplit=1)[0].strip("'\"").rstrip(".,;:")
        path = token.split("#", 1)[0].split("?", 1)[0]
        parts = path.split("/")
        candidate = path.startswith(("scripts/", "references/")) or (
            ".." in parts and (Path(path).suffix or any(p in {"scripts", "references"} for p in parts))
        )
        if not candidate or any(character in span for character in "<>*=,"):
            return match.group(0)
        base = Path(".") if path.startswith(("scripts/", "references/")) else source.parent
        result = linked_url(token, base / "index.md", upstream, included, revision)
        return f"[{span}]({result})" if result != token else match.group(0)

    text = CODE.sub(code_link, text)
    text = LINK.sub(
        lambda match: f"]({linked_url(match.group(1), source, upstream, included, revision)})", text
    )
    text = DEFINITION.sub(
        lambda match: match.group(1) + linked_url(match.group(2), source, upstream, included, revision),
        text,
    )

    rows = text.splitlines(keepends=True)
    front_end = next((i for i in range(1, len(rows)) if rows[i].strip() == "---"), 0) if rows and rows[0].strip() == "---" else 0
    cued = (
        front_end > 0 and any(re.match(r"^description:\s*\S", line) for line in rows[1:front_end])
    ) or any(
        line.startswith(("Primary role:", "Read this when"))
        for line in rows[front_end + 1 if front_end else 0:(front_end + 1 if front_end else 0) + 15]
    )
    if not cued:
        cue = cues.get(source.as_posix())
        if not cue:
            raise ValueError(f"uncued file without overlay entry: {source}")
        heading = next((i for i, line in enumerate(rows) if line.startswith("# ")), None)
        if heading is None:
            raise ValueError(f"uncued file has no H1: {source}")
        rows.insert(heading + 1, cue + "\n")
    return "".join(rows)


def render(upstream: Path, target: Path, cues: dict[str, str], revision: str, date: str) -> None:
    """Create a complete expected tree, without modifying the live destination."""
    files = selected(upstream)
    included = set(files)
    used: set[str] = set()
    for relative in files:
        destination = target / relative
        _ = destination.parent.mkdir(parents=True, exist_ok=True)
        if relative.suffix == ".md":
            original = (upstream / relative).read_text(encoding="utf-8")
            result = transform(original, relative, upstream, included, revision, cues)
            if relative.as_posix() in cues and result != original and (
                "Read this when" in result and not "Read this when" in original
            ):
                used.add(relative.as_posix())
            _ = destination.write_text(result, encoding="utf-8")
        else:
            _ = shutil.copyfile(upstream / relative, destination)
    for entry in sorted(cues.keys() - used):
        print(f"warning: unused cue overlay: {entry}", file=sys.stderr)
    _ = (target / "UPSTREAM.md").write_text("\n".join([
        "---",
        "description: Read this when you need the synced upstream revision or resync procedure.",
        "---",
        "",
        "# StyleGallery upstream snapshot",
        "",
        f"- Repository: {SOURCE}",
        f"- Revision: {revision}",
        f"- Sync date (upstream commit): {date}",
        "- Included: Markdown under patterns/, recipes/, guides/, motion/, design-engineering/, game-ui/, platform-guides/, design-terminology/, layout/; root index.md, CATALOG.md, GUIDE.md; LICENSE-DOCS and NOTICE.",
        "- Excluded: design-engineering/reference-profiles/, game-ui/unity/data/, and all other upstream material.",
        "- Transforms: remove generated maintenance lines; pin excluded relative links, reference definitions and path-like code spans to this revision; add routing cues from the cue overlay where needed; preserve source frontmatter.",
        "",
        "## Resync",
        "",
        "Check out the desired upstream revision, then from the pack root run `python3 tools/sync-stylegallery.py --upstream PATH` followed by `python3 tools/sync-stylegallery.py --upstream PATH --check` and `python3 tools/check-skills.py --skills frontend`. Review the diff and attribution before updating references elsewhere in the pack.",
        "",
    ]), encoding="utf-8")


def drift(expected: Path, actual: Path) -> list[str]:
    """Compare paths and bytes, including unexpected destination files."""
    left = {p.relative_to(expected) for p in expected.rglob("*") if p.is_file()}
    right: set[Path] = {p.relative_to(actual) for p in actual.rglob("*") if p.is_file()} if actual.exists() else set()
    return [
        *(f"missing: {p}" for p in sorted(left - right)),
        *(f"extra: {p}" for p in sorted(right - left)),
        *(f"changed: {p}" for p in sorted(left & right) if (expected / p).read_bytes() != (actual / p).read_bytes()),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument("--upstream", type=Path, required=True, help="upstream git checkout")
    _ = parser.add_argument("--dest", type=Path, default=Path("frontend/references/stylegallery"),
                            help="destination (relative paths use the pack root)")
    _ = parser.add_argument("--check", action="store_true", help="report byte-level drift without writing destination")
    args = parser.parse_args(namespace=Arguments())
    upstream = args.upstream.resolve()
    dest = args.dest if args.dest.is_absolute() else REPO / args.dest
    revision = subprocess.check_output(["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True).strip()
    timestamp = subprocess.check_output(["git", "-C", str(upstream), "show", "-s", "--format=%cI", "HEAD"], text=True).strip()
    date = datetime.fromisoformat(timestamp).date().isoformat()
    cues = cast(dict[str, str], json.loads((REPO / "tools/stylegallery-cues.json").read_text(encoding="utf-8")))
    with tempfile.TemporaryDirectory(prefix="stylegallery-sync-") as directory:
        expected = Path(directory) / "stylegallery"
        _ = expected.mkdir()
        try:
            render(upstream, expected, cues, revision, date)
        except ValueError as error:
            print(error, file=sys.stderr)
            return 1
        if args.check:
            changes = drift(expected, dest)
            for change in changes:
                print(change)
            print(f"StyleGallery drift: {len(changes)} files" if changes else "StyleGallery is up to date")
            return 1 if changes else 0
        if dest.exists():
            shutil.rmtree(dest)
        _ = shutil.copytree(expected, dest)
        print(f"Synced {len(selected(upstream))} upstream files to {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
