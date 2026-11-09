"""OMP-NAME rule: an omp-native skill may name only what omp has.

A skill opts in by shipping references/omp-names.md. Its `## Agents`, `## Tools`
and `## Eval helpers` tables list what omp provides (first backticked token of
each row). Its `## Not on omp` table lists names from other hosts; a row whose
third cell is `quoted` is an ordinary word and fails only inside backticks or
quotes, any other row fails wherever it appears. Every line of the skill except
those table rows fails when it names a refused name, or names an agent or tool
in a dispatch-shaped phrase that the matching allowed table does not list.
"""
from __future__ import annotations
import re
from pathlib import Path

TABLE_FILE = Path("references") / "omp-names.md"
NAMESPACES = {"agents": "agent", "tools": "tool", "eval helpers": "helper"}
DENIED_SECTION = "not on omp"
ROW = re.compile(r"^\|\s*`([^`]+)`(.*)$")
QUOTE = "[\"'`]"
DISPATCH = (
    ("agent", re.compile(rf"{QUOTE}?\bagent{QUOTE}?\s*[:=]\s*{QUOTE}([\w-]+){QUOTE}")),
    ("agent", re.compile(rf"\bworkpool\(\s*{QUOTE}([\w-]+){QUOTE}")),
    ("agent", re.compile(r"`([\w-]+)`\s+agents?\b", re.IGNORECASE)),
    ("agent", re.compile(r"\bagent\s+`([\w-]+)`", re.IGNORECASE)),
    ("tool", re.compile(r"`([\w-]+)`\s+tools?\b", re.IGNORECASE)),
    ("tool", re.compile(r"\btool\s+`([\w-]+)`", re.IGNORECASE)),
)

def read_table(text: str) -> tuple[dict[str, set[str]], list[tuple[str, bool]], set[int]]:
    allowed: dict[str, set[str]] = {kind: set() for kind in NAMESPACES.values()}
    denied: list[tuple[str, bool]] = []
    row_lines: set[int] = set()
    section = ""
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        found = ROW.match(line)
        if not found:
            continue
        name = found.group(1).strip()
        if section in NAMESPACES:
            allowed[NAMESPACES[section]].add(name.removesuffix("()"))
            row_lines.add(number)
        elif section == DENIED_SECTION:
            cells = [cell.strip() for cell in found.group(2).split("|")]
            denied.append((name, len(cells) > 2 and cells[2] == "`quoted`"))
            row_lines.add(number)
    return allowed, denied, row_lines

def denied_pattern(name: str, quoted_only: bool) -> re.Pattern[str]:
    if name.endswith("()"):
        return re.compile(rf"(?<![\w.]){re.escape(name[:-2])}\(")
    body = "[-_]".join(re.escape(part) for part in name.split("-"))
    if quoted_only:
        return re.compile(rf"{QUOTE}{body}{QUOTE}", re.IGNORECASE)
    return re.compile(rf"(?<![\w-]){body}(?![\w-])", re.IGNORECASE)

def check(skill: Path, texts: dict[Path, str]) -> list[tuple[Path, int, str, str]]:
    table = skill / TABLE_FILE
    if table not in texts:
        return []
    allowed, denied, row_lines = read_table(texts[table])
    if not all(allowed.values()) or not denied:
        return [(table, 1, "omp-names.md needs Agents, Tools, Eval helpers and Not on omp rows", "")]
    patterns = [(name, denied_pattern(name, quoted)) for name, quoted in denied]
    failures: list[tuple[Path, int, str, str]] = []
    for path, text in texts.items():
        for number, line in enumerate(text.splitlines(), 1):
            if path == table and number in row_lines:
                continue
            for name, pattern in patterns:
                if pattern.search(line):
                    failures.append((path, number, f"`{name}` is not on omp (see references/omp-names.md)", line))
            for kind, dispatch in DISPATCH:
                for found in dispatch.finditer(line):
                    if found.group(1) not in allowed[kind]:
                        failures.append((path, number, f"`{found.group(1)}` is not an omp {kind} listed in references/omp-names.md", line))
    return failures
