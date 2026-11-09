"""OMP-NAME rule: an omp-native skill may name only what omp has.

A skill opts in by shipping references/omp-names.md. Its `## Agents`, `## Tools`
and `## Eval helpers` tables list the names omp provides (first backticked token
of each row); its `## Not on omp` table lists names from other hosts. Every other
text file in the skill fails when it names a `## Not on omp` entry, or names an
agent or tool, in a dispatch-shaped phrase, that the allowed tables do not list.
"""
from __future__ import annotations
import re
from pathlib import Path

TABLE_FILE = Path("references") / "omp-names.md"
ALLOWED_SECTIONS = ("agents", "tools", "eval helpers")
DENIED_SECTION = "not on omp"
ROW_NAME = re.compile(r"^\|\s*`([^`]+)`")
DISPATCH = (
    re.compile(r"\bagent\s*[:=]\s*[\"']([\w-]+)[\"']"),
    re.compile(r"`([\w-]+)`\s+(?:agent|tool)s?\b", re.IGNORECASE),
    re.compile(r"\b(?:agent|tool)\s+`([\w-]+)`", re.IGNORECASE),
)

def read_table(text: str) -> tuple[set[str], list[str]]:
    allowed: set[str] = set()
    denied: list[str] = []
    section = ""
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        found = ROW_NAME.match(line)
        if not found:
            continue
        name = found.group(1).strip()
        if section in ALLOWED_SECTIONS:
            allowed.add(name.removesuffix("()"))
        elif section == DENIED_SECTION:
            denied.append(name)
    return allowed, denied

def denied_pattern(name: str) -> re.Pattern[str]:
    if name.endswith("()"):
        return re.compile(rf"(?<![\w.]){re.escape(name[:-2])}\(")
    body = r"[-\s]?".join(re.escape(part) for part in name.split("-"))
    return re.compile(rf"(?<![\w-]){body}(?![\w-])", re.IGNORECASE)

def check(skill: Path, texts: dict[Path, str]) -> list[tuple[Path, int, str, str]]:
    table = skill / TABLE_FILE
    if table not in texts:
        return []
    allowed, denied = read_table(texts[table])
    if not allowed or not denied:
        return [(table, 1, "omp-names.md needs Agents/Tools/Eval helpers rows and a Not on omp table", "")]
    patterns = [(name, denied_pattern(name)) for name in denied]
    failures: list[tuple[Path, int, str, str]] = []
    for path, text in texts.items():
        if path == table:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            for name, pattern in patterns:
                if pattern.search(line):
                    failures.append((path, number, f"`{name}` is not on omp (see references/omp-names.md)", line))
            for dispatch in DISPATCH:
                for found in dispatch.finditer(line):
                    if found.group(1) not in allowed:
                        failures.append((path, number, f"`{found.group(1)}` is not an omp agent or tool listed in references/omp-names.md", line))
    return failures
