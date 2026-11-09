"""OMP-NAME rule: an omp-native skill may name only what omp has.

A skill opts in by shipping references/omp-names.md. Its `## Agents`, `## Tools`
and `## Eval helpers` tables list what omp provides (first backticked token of
each row). Every line of the skill fails when it names an agent or tool in a
dispatch-shaped phrase that the matching table does not list.
"""
from __future__ import annotations
import re
from pathlib import Path

TABLE_FILE = Path("references") / "omp-names.md"
NAMESPACES = {"agents": "agent", "tools": "tool", "eval helpers": "helper"}
ROW = re.compile(r"^\|\s*`([^`]+)`")
QUOTE = "[\"'`]"
DISPATCH = (
    ("agent", re.compile(rf"{QUOTE}?\bagent{QUOTE}?\s*[:=]\s*{QUOTE}([\w-]+){QUOTE}")),
    ("agent", re.compile(rf"\bworkpool\s*\(\s*{QUOTE}([\w-]+){QUOTE}")),
    ("agent", re.compile(r"`([\w-]+)`\s+agents?\b", re.IGNORECASE)),
    ("agent", re.compile(r"\bagent\s+`([\w-]+)`", re.IGNORECASE)),
    ("tool", re.compile(r"`([\w-]+)`\s+tools?\b", re.IGNORECASE)),
    ("tool", re.compile(r"\btool\s+`([\w-]+)`", re.IGNORECASE)),
)

def read_table(text: str) -> dict[str, set[str]]:
    allowed: dict[str, set[str]] = {kind: set() for kind in NAMESPACES.values()}
    section = ""
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        found = ROW.match(line)
        if found and section in NAMESPACES:
            allowed[NAMESPACES[section]].add(found.group(1).strip().removesuffix("()"))
    return allowed

def check(skill: Path, texts: dict[Path, str]) -> list[tuple[Path, int, str, str]]:
    table = skill / TABLE_FILE
    if table not in texts:
        return []
    allowed = read_table(texts[table])
    if not all(allowed.values()):
        return [(table, 1, "omp-names.md needs Agents, Tools and Eval helpers rows", "")]
    failures: list[tuple[Path, int, str, str]] = []
    for path, text in texts.items():
        lines = text.splitlines()
        for kind, dispatch in DISPATCH:
            for found in dispatch.finditer(text):
                if found.group(1) not in allowed[kind]:
                    number = text.count("\n", 0, found.start(1)) + 1
                    failures.append((path, number, f"`{found.group(1)}` is not an omp {kind} listed in references/omp-names.md", lines[number - 1]))
    return failures
