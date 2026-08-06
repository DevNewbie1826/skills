#!/usr/bin/env python3
"""Check that a skill pack is portable, neutral, and self-contained."""
from __future__ import annotations
import argparse
import ast
import fnmatch
import json
import re
import sys
from collections import Counter, defaultdict
from importlib.util import find_spec
from pathlib import Path
from sysconfig import get_path
from typing import TypedDict, cast
from urllib.parse import unquote

class Violation(TypedDict):
    path: str
    line: int
    rule: str
    message: str
    excerpt: str

class AllowlistEntry(TypedDict):
    path_glob: str
    token: str
    reason: str

class Results(TypedDict):
    root: str
    skills: list[str]
    violations: list[Violation]
    suppressed: int
    summary: dict[str, int]
    ok: bool

DEFAULT_SKILLS = ("frontend", "debugging", "remove-ai-slops", "visual-qa", "programming", "git-master", "lore")
TEXT_SUFFIXES = {".md", ".py", ".ts", ".mjs", ".json", ".csv", ".txt"}
SCRIPT_SUFFIXES = {".py", ".ts", ".mjs"}

def bounded(pattern: str, trailing_boundary: bool = True, case_sensitive: bool = False) -> re.Pattern[str]:
    end = r"(?![A-Za-z0-9_])" if trailing_boundary else ""
    return re.compile(rf"(?<![A-Za-z0-9_])(?:{pattern}){end}", 0 if case_sensitive else re.IGNORECASE)

def banned(name: str, pattern: str, aliases: tuple[str, ...] = (), trailing_boundary: bool = True, case_sensitive: bool = False) -> tuple[str, re.Pattern[str], tuple[str, ...]]:
    return name, bounded(pattern, trailing_boundary, case_sensitive), aliases

WORD_TOKENS = (
    "senpi", "sisyphus", "opencode", "codex", "omo", "codegraph", "ulw-loop", "ultrawork",
    "ulw-plan", "ulw-research", "start-work", "review-work", "hyperplan", "prometheus", "boulder",
    "subagent_type", "fork_context", "wait_agent", "followup_task", "interrupt_agent", "list_agents",
    "load_skills", "team_create", "team_wait", "script/qa", "claude", "gemini", "kimi", "qwen",
    "deepseek", "opus", "sonnet", "haiku", "imagen", "stitch", "midjourney", "anthropic", "openai",
    "open-design", "agent-browser",
)
BANNED: list[tuple[str, re.Pattern[str], tuple[str, ...]]] = [
    banned(token, re.escape(token)) for token in WORD_TOKENS
] + [
    banned("claude-code", r"claude[ -]code", ("claude code", "claude[ -]code")),
    banned(".omo/", r"\.omo/", (".omo",), False),
    banned("/Volumes/", r"/Volumes/", trailing_boundary=False, case_sensitive=True),
    banned("/Users/", r"/Users/", trailing_boundary=False, case_sensitive=True),
    banned("/home/", r"/home/", trailing_boundary=False, case_sensitive=True),
    banned("gpt-*", r"gpt[- ]?[0-9]", ("gpt", "gpt[- ]?[0-9]")),
    banned("dall-e", r"dall-?e", ("dalle", "dall-?e")),
    banned("oracle-persona", r"(?:spawn\s+(?:an?\s+)?oracle|oracle\s+(?:sub)?agents?|" +
           r"(?:sub)?agents?\s+oracle|dual[-\s]+oracle|" +
           r"(?:ask|consult|delegate(?:\s+\w+){0,3}\s+to)\s+(?:an?\s+)?oracle)", ("oracle",)),
]
MANDATE = re.compile(
    r"(?<![A-Za-z0-9_])(?:installed\s+by\s+default|must\s+use|always\s+use|" +
    r"default:?\s+|required:)", re.IGNORECASE
)
CONDITIONAL = re.compile(
    r"(?:if\s+your|when\s+using|for\b.*\bprojects\b|equivalent\s+for\s+your\s+stack)", re.IGNORECASE
)
HAZARD_SPAWN = re.compile(r"(?<![.:])\bspawn\b(?!\s*\()", re.IGNORECASE)
HAZARD_SPAWN_VARIANT = re.compile(
    r"(?<![.:])\bspawn(?:s|ed|ing)\b(?!\s*\()(?=(?:\s+\w+){0,3}\s+(?:subagents?|agents?|workers?|reviewers?)\b)", re.IGNORECASE
)
HAZARD_SUBAGENT = re.compile(r"\bsubagents?\b", re.IGNORECASE)
HAZARD_FAN_OUT = re.compile(r"\bfan.?out\b", re.IGNORECASE)
HAZARD_DELEGATE = re.compile(r"\bdelegate\b", re.IGNORECASE)
HAZARD_PARALLEL = re.compile(r"\bparallel\s+\w*(?:subagent|worker|agent|reviewer)s?\b", re.IGNORECASE)
HAZARD_TECHNICAL_SPAWN = re.compile(
    r"\b(?:threads?|goroutines?|tokio|process(?:es)?|vitest|node|embedded\s+code|tasks?)\b", re.IGNORECASE
)
HAZARD_TECHNICAL_FAN_OUT = re.compile(
    r"\b(?:channels?|queues?|goroutines?|tokio|connections?|concurrency|streams?|http|pools?|services?|producers?|consumers?|mpsc)\b", re.IGNORECASE
)
HAZARD_AGENT_ROLE = re.compile(r"\b(?:subagents?|agents?|reviewers?)\b", re.IGNORECASE)
HAZARD_DELEGATION_ACTION = re.compile(
    r"\b(?:use|run|dispatch|start|launch|assign|send|give|create|spawn(?:s|ed|ing)?|fan.?out|delegate|parallel|must|should|need)\b", re.IGNORECASE
)
HAZARD_FAN_OUT_CONTEXT = re.compile(
    r"\b(?:subagents?|agents?|reviewers?)\b|\b(?:review|investigat|delegat|dispatch|assign|launch|start)\w*\b", re.IGNORECASE
)
HAZARD_SUBAGENT_REFERENCE = re.compile(r"\bsubagents?\s+(?:handoffs?|tool|type|field|identifier)\b", re.IGNORECASE)
HAZARD_CODE_DELEGATE = re.compile(r"\bdelegate\s+to\s+`[^`]+`", re.IGNORECASE)
HAZARD_BOUND = re.compile(
    r"\bper\s+(?:\w+\s+){0,2}(?:file|batch|angle|lane|screen)\b|" +
    r"\bone\s+worker\b|\bat\s+most\b|\bbatches\s+of\b|<=|" +
    r"\bno\s+more\s+than\b|\bexactly\b|\bnever\s+spawn\b|" +
    r"\b(?:two|three|four)\b|\b(?:one|two|three|four)\s+(?:\w+\s+){0,3}per\s+\w+\b", re.IGNORECASE
)
HAZARD_PER_ITEM = re.compile(r"\bper\s+(?:finding|question|item)\b", re.IGNORECASE)
HAZARD_NEGATION = re.compile(r"\b(?:never|do\s+not|don't|avoid)\b[^.!?]{0,40}$", re.IGNORECASE)
FRAMEWORK_RE = [(name, bounded(pattern)) for name, pattern in (
    ("react", r"react"), ("vue", r"vue"), ("svelte", r"svelte"), ("angular", r"angular"),
    ("next.js", r"next\.?js"), ("solid", r"solid"), ("qwik", r"qwik"), ("astro", r"astro"),
    ("django", r"django"), ("rails", r"rails"), ("laravel", r"laravel"), ("tailwind", r"tailwind"),
)]
LANGUAGE_RE = [(name, bounded(pattern)) for name, pattern in (
    ("python", r"python"), ("rust", r"rust"), ("go", r"go(?:lang)?"), ("typescript", r"typescript"),
    ("javascript", r"javascript"), ("ruby", r"ruby"), ("java", r"java"), ("kotlin", r"kotlin"), ("swift", r"swift"),
)]
MARKDOWN_LINK = re.compile(r"\]\(([^)\n]+)\)")
INLINE_PATH = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
REFERENCE_DEF = re.compile(r"^\s{0,3}\[([^\]\n]+)\]:\s*(?:<([^>\n]+)>|(\S+))")
REFERENCE_USE = re.compile(r"(?<![!\\])\[([^\]\n]+)\](?:\[\])?(?!\s*(?:\[|:|\())")
DEPS_TOKEN = re.compile(r"`([^`]+)`")
JS_IMPORT = re.compile(
    r"\b(?:import|export)\s+(?:type\s+)?(?:[^'\"]*?\bfrom\s+)?[\"']([^\"']+)[\"']" +
    r"|\b(?:require|import)\s*\(\s*[\"']([^\"']+)[\"']"
)
ABSOLUTE_PATH = re.compile(
    r"(?<![:/A-Za-z0-9_])/(?:[A-Za-z0-9_.~+-]+/)+[A-Za-z0-9_.~+-]+" +
    r"|[\"'`]/(?:Volumes|Users|home|tmp|var|usr|opt|private|etc|Library)(?:/|[\"'`])" +
    r"|(?<![A-Za-z0-9_])[A-Za-z]:[\\/]"
)
NODE_BUILTINS = {
    "assert", "buffer", "child_process", "cluster", "console", "constants", "crypto", "dgram",
    "diagnostics_channel", "dns", "domain", "events", "fs", "http", "http2", "https", "module",
    "net", "os", "path", "perf_hooks", "process", "punycode", "querystring", "readline", "repl",
    "stream", "string_decoder", "sys", "timers", "tls", "trace_events", "tty", "url", "util", "v8",
    "vm", "wasi", "worker_threads", "zlib",
}
PY_STDLIB = set(getattr(sys, "stdlib_module_names", ())) | set(sys.builtin_module_names) | {"__future__", "builtins"}
STDLIB_ROOT = Path(get_path("stdlib")).resolve()
def display_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()
def excerpt(line: str) -> str:
    value = line.strip().replace("\t", "    ")
    return value if len(value) <= 220 else value[:217] + "..."
def add_failure(results: Results, root: Path, path: Path, line: int, rule: str, message: str, text: str = "") -> None:
    results["violations"].append({"path": display_path(root, path), "line": line, "rule": rule,
                                   "message": message, "excerpt": excerpt(text)})
def is_inside(path: Path, directory: Path) -> bool:
    try:
        _ = path.resolve().relative_to(directory.resolve())
        return True
    except ValueError:
        return False
def is_python_stdlib(module: str) -> bool:
    base = module.split(".", 1)[0]
    if base in PY_STDLIB:
        return True
    try:
        spec = find_spec(base)
    except (AttributeError, ImportError, ValueError):
        return False
    if spec is None or spec.origin is None:
        return False
    origin = Path(spec.origin)
    return spec.origin in {"built-in", "frozen"} or (is_inside(origin, STDLIB_ROOT) and not {"site-packages", "dist-packages"}.intersection(origin.parts))
def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")
def text_files(directory: Path, suffixes: set[str]) -> list[Path]:
    return sorted((path for path in directory.rglob("*") if path.is_file() and path.suffix.lower() in suffixes),
                  key=lambda path: path.as_posix())
def allowlist_paths(root: Path) -> list[Path]:
    locations = [root / "tools" / "allowlist", Path(__file__).resolve().parent / "allowlist"]
    result: list[Path] = []
    seen: set[Path] = set()
    for location in locations:
        resolved = location.resolve()
        if location.is_dir() and resolved not in seen:
            result.extend(sorted(location.glob("*.json")))
            seen.add(resolved)
    return result
def load_allowlists(root: Path, results: Results) -> list[AllowlistEntry]:
    entries: list[AllowlistEntry] = []
    for path in allowlist_paths(root):
        try:
            data = cast(object, json.loads(read_text(path)))
        except (OSError, json.JSONDecodeError) as error:
            add_failure(results, root, path, 0, "ALLOWLIST", f"invalid JSON: {error}")
            continue
        if not isinstance(data, list):
            add_failure(results, root, path, 0, "ALLOWLIST", "allowlist must be a JSON list")
            continue
        for index, raw in enumerate(cast(list[object], data), start=1):
            if not isinstance(raw, dict):
                add_failure(results, root, path, index, "ALLOWLIST", "entries need path_glob, token, and reason")
                continue
            entry = cast(dict[object, object], raw)
            glob, token, reason = entry.get("path_glob"), entry.get("token"), entry.get("reason")
            if not isinstance(glob, str) or not glob or not isinstance(token, str) or not token or not isinstance(reason, str) or not reason:
                add_failure(results, root, path, index, "ALLOWLIST", "entries need path_glob, token, and reason")
                continue
            entries.append({"path_glob": glob, "token": token, "reason": reason})
    return entries
def allowlisted(entries: list[AllowlistEntry], relative_path: str, token: str, matched: str, aliases: tuple[str, ...]) -> bool:
    names = {token.casefold(), matched.casefold(), *(alias.casefold() for alias in aliases)}
    for entry in entries:
        glob = entry["path_glob"].replace("\\", "/").removeprefix("./")
        matches_path = fnmatch.fnmatchcase(relative_path, glob) or (glob.startswith("**/") and fnmatch.fnmatchcase(relative_path, glob[3:]))
        if matches_path and entry["token"].casefold() in names:
            return True
    return False
def scan_tier_a(root: Path, path: Path, text: str, allowlists: list[AllowlistEntry], results: Results) -> None:
    relative_path = display_path(root, path)
    for line_number, line in enumerate(text.splitlines(), start=1):
        matches: list[tuple[int, int, int, str, str, tuple[str, ...]]] = []
        for order, (token, pattern, aliases) in enumerate(BANNED):
            matches.extend((match.start(), match.end(), order, token, match.group(), aliases) for match in pattern.finditer(line))
        occupied: list[tuple[int, int]] = []
        for start, end, order, token, matched, aliases in sorted(matches, key=lambda item: (item[0], -(item[1] - item[0]), item[2])):
            if any(start < used_end and end > used_start for used_start, used_end in occupied):
                continue
            occupied.append((start, end))
            if allowlisted(allowlists, relative_path, token, matched, aliases):
                results["suppressed"] += 1
            else:
                add_failure(results, root, path, line_number, "TIER-A", f'banned token "{token}"', line)
def frontmatter(lines: list[str]) -> tuple[list[str], int] | None:
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index], index
    return None
def yaml_field(front: list[str], name: str) -> tuple[str, int] | None:
    matcher = re.compile(rf"^{re.escape(name)}\s*:\s*(.*)$")
    for index, line in enumerate(front):
        found = matcher.match(line)
        if not found:
            continue
        value = found.group(1).strip()
        if value.startswith(("|", ">")):
            value = next((later.strip() for later in front[index + 1:] if later.startswith((" ", "\t")) and later.strip()), "")
        elif len(value) >= 2 and value[0] in "\"'" and value[-1] == value[0]:
            value = value[1:-1]
        else:
            value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
        return value, index + 2
    return None
def check_structure(root: Path, skill: Path, skill_name: str, text: str, results: Results) -> None:
    path, lines = skill / "SKILL.md", text.splitlines()
    parsed = frontmatter(lines)
    if parsed is None:
        add_failure(results, root, path, 1, "STRUCTURE", "SKILL.md needs YAML frontmatter", lines[0] if lines else "")
        return
    front, closing = parsed
    name, description = yaml_field(front, "name"), yaml_field(front, "description")
    if name is None:
        add_failure(results, root, path, 1, "STRUCTURE", "frontmatter is missing name")
    elif name[0] != skill_name:
        add_failure(results, root, path, name[1], "STRUCTURE", f'name must be "{skill_name}"', lines[name[1] - 1])
    if description is None or not description[0].strip():
        line = description[1] if description else 1
        add_failure(results, root, path, line, "STRUCTURE", "frontmatter needs a non-empty description", lines[line - 1] if lines else "")
    if len(lines[closing + 1:]) > 200:
        line = closing + 202
        add_failure(results, root, path, line, "STRUCTURE", "SKILL.md body exceeds 200 lines", lines[line - 1])
def names_on_line(line: str, choices: list[tuple[str, re.Pattern[str]]]) -> list[str]:
    return [name for name, pattern in choices if pattern.search(line)]
def check_tier_b(root: Path, path: Path, text: str, results: Results) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not MANDATE.search(line) or CONDITIONAL.search(line):
            continue
        frameworks, languages = names_on_line(line, FRAMEWORK_RE), names_on_line(line, LANGUAGE_RE)
        selected: list[str] = []
        if len(frameworks) == 1:
            selected.append(f"framework {frameworks[0]}")
        if len(languages) == 1:
            selected.append(f"language {languages[0]}")
        if selected:
            add_failure(results, root, path, line_number, "TIER-B", "single-stack mandate: " + ", ".join(selected), line)
def hazard_matches(text: str) -> list[re.Match[str]]:
    matches: list[re.Match[str]] = []
    if not HAZARD_TECHNICAL_SPAWN.search(text) or HAZARD_AGENT_ROLE.search(text):
        matches.extend(HAZARD_SPAWN.finditer(text))
        matches.extend(HAZARD_SPAWN_VARIANT.finditer(text))
    if HAZARD_DELEGATION_ACTION.search(text):
        matches.extend(match for match in HAZARD_SUBAGENT.finditer(text)
                       if not HAZARD_SUBAGENT_REFERENCE.match(text, match.start()))
    if HAZARD_FAN_OUT_CONTEXT.search(text) or not HAZARD_TECHNICAL_FAN_OUT.search(text):
        matches.extend(HAZARD_FAN_OUT.finditer(text))
    matches.extend(match for match in HAZARD_DELEGATE.finditer(text)
                   if not HAZARD_CODE_DELEGATE.match(text, match.start()))
    matches.extend(HAZARD_PARALLEL.finditer(text))
    return matches

def hazards_per_item(text: str, matches: list[re.Match[str]]) -> bool:
    for match in matches:
        for unit in HAZARD_PER_ITEM.finditer(text):
            gap = max(match.start(), unit.start()) - min(match.end(), unit.end())
            if gap > 80:
                continue
            preceding = text[max(0, match.start() - 48):match.start()]
            if not HAZARD_NEGATION.search(preceding):
                return True
    return False

def check_hazards(root: Path, path: Path, text: str, results: Results) -> None:
    lines, start = text.splitlines(), 0
    for index, line in enumerate([*lines, ""], start=1):
        if line.strip():
            if not start:
                start = index
            continue
        if not start:
            continue
        paragraph = "\n".join(lines[start - 1:index - 1])
        matches = hazard_matches(paragraph)
        if matches and (hazards_per_item(paragraph, matches) or not HAZARD_BOUND.search(paragraph)):
            add_failure(results, root, path, start, "HAZARDS", "unitless delegation wording", lines[start - 1])
        start = 0

def markdown_target(value: str) -> str:
    value = value.strip()
    value = value[1:value.index(">")] if value.startswith("<") and ">" in value else (value.split(maxsplit=1)[0] if value else "")
    return unquote(value.split("#", 1)[0].split("?", 1)[0])
def relative_target(value: str) -> bool:
    return bool(value) and not value.startswith(("#", "/", "\\", "//")) and not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value)
def target_exists(base: Path, target: str, skill: Path) -> tuple[bool, str]:
    candidate = (base / target).resolve()
    if not is_inside(candidate, skill):
        return False, "target escapes the skill directory"
    return (True, "") if candidate.exists() else (False, "target does not exist")

def reference_label(value: str) -> str:
    return " ".join(value.split()).casefold()

def check_relative_link(root: Path, path: Path, skill: Path, base: Path, target: str, line_number: int, line: str, kind: str, results: Results) -> None:
    if not relative_target(target):
        return
    valid, reason = target_exists(base, target, skill)
    if not valid:
        add_failure(results, root, path, line_number, "LINKS", f'{kind} "{target}": {reason}', line)

def check_links(root: Path, skill: Path, texts: dict[Path, str], results: Results) -> None:
    for path, text in texts.items():
        if path.suffix.lower() != ".md":
            continue
        lines = text.splitlines()
        definitions = {reference_label(match.group(1)): markdown_target(match.group(2) or match.group(3) or "") for source_line in lines for match in REFERENCE_DEF.finditer(source_line)}
        for line_number, line in enumerate(lines, start=1):
            for match in MARKDOWN_LINK.finditer(line):
                raw, target = match.group(1).strip(), markdown_target(match.group(1))
                if "/" in target or Path(target).suffix or raw.startswith("#"):
                    check_relative_link(root, path, skill, path.parent, target, line_number, line, "markdown link", results)
            for match in REFERENCE_USE.finditer(line):
                target = definitions.get(reference_label(match.group(1)))
                if target:
                    check_relative_link(root, path, skill, path.parent, target, line_number, line, "reference link", results)
            for match in INLINE_PATH.finditer(line):
                span = match.group(1)
                target = span.strip().split(maxsplit=1)[0].strip("'\"").rstrip(".,;:").split("#", 1)[0].split("?", 1)[0]
                if (target.startswith(("references/", "scripts/")) or (".." in target.split("/") and (Path(target).suffix or any(part in {"references", "scripts"} for part in target.split("/"))))) and not any(character in span for character in "<>*=,"):
                    check_relative_link(root, path, skill, skill if target.startswith(("references/", "scripts/")) else path.parent, target, line_number, line, "inline path", results)

def local_module_exists(skill: Path, base: Path, module: str, extensions: tuple[str, ...]) -> bool:
    target = base.joinpath(*module.split(".")) if module else base
    candidates = [target, *(target.with_suffix(extension) for extension in extensions), target / "__init__.py"]
    return any(is_inside(candidate, skill) and candidate.exists() for candidate in candidates)

def python_import_resolves(skill: Path, path: Path, module: str, level: int, dependencies: set[str]) -> bool:
    if level:
        base = path.parent
        for _ in range(level - 1):
            base = base.parent
        return local_module_exists(skill, base, module, (".py",))
    base = module.split(".", 1)[0]
    if base in dependencies or is_python_stdlib(module):
        return True
    return any(local_module_exists(skill, base, module, (".py",)) for base in (path.parent, skill))

def js_import_resolves(skill: Path, path: Path, specifier: str, dependencies: set[str]) -> bool:
    specifier = specifier.split("#", 1)[0].split("?", 1)[0]
    package = "/".join(specifier.split("/")[:2]) if specifier.startswith("@") else specifier.split("/", 1)[0]
    if specifier.startswith("node:") or package in NODE_BUILTINS or package in dependencies:
        return True
    if not specifier.startswith((".", "/")):
        return False
    candidate = (path.parent / specifier).resolve()
    if not is_inside(candidate, skill):
        return False
    candidates = [candidate]
    if not candidate.suffix:
        candidates.extend(candidate.with_suffix(ext) for ext in (".ts", ".mjs", ".js", ".json"))
        candidates.extend(candidate / f"index{ext}" for ext in (".ts", ".mjs", ".js"))
    elif candidate.suffix in {".js", ".mjs", ".cjs"}:
        candidates.extend(candidate.with_suffix(ext) for ext in (".ts", ".mts", ".cts"))
    return any(item.exists() and is_inside(item, skill) for item in candidates)

def check_python_imports(root: Path, skill: Path, path: Path, text: str, dependencies: set[str], results: Results) -> None:
    lines = text.splitlines()
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as error:
        line = error.lineno or 1
        add_failure(results, root, path, line, "SCRIPTS", f"invalid Python: {error.msg}", lines[line - 1] if line <= len(lines) else "")
        return
    imports: list[tuple[int, str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend((node.lineno, alias.name, 0) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                imports.append((node.lineno, node.module, node.level))
            else:
                imports.extend((node.lineno, alias.name, node.level) for alias in node.names if alias.name != "*")
    for line, module, level in sorted(imports):
        if not python_import_resolves(skill, path, module, level, dependencies):
            add_failure(results, root, path, line, "SCRIPTS", f'import "{"." * level}{module}" does not resolve inside the skill', lines[line - 1])

def check_js_imports(root: Path, skill: Path, path: Path, text: str, dependencies: set[str], results: Results) -> None:
    seen: set[tuple[int, str]] = set()
    lines = text.splitlines()
    for match in JS_IMPORT.finditer(text):
        specifier = match.group(1) or match.group(2)
        line = text.count("\n", 0, match.start()) + 1
        if (line, specifier) in seen:
            continue
        seen.add((line, specifier))
        if not js_import_resolves(skill, path, specifier, dependencies):
            add_failure(results, root, path, line, "SCRIPTS", f'import "{specifier}" does not resolve inside the skill', lines[line - 1])

def check_scripts(root: Path, skill: Path, texts: dict[Path, str], results: Results) -> None:
    scripts = skill / "scripts"
    if not scripts.is_dir():
        return
    dependencies = set(DEPS_TOKEN.findall(texts.get(scripts / "DEPS.md", "")))
    for path in text_files(scripts, SCRIPT_SUFFIXES):
        try:
            text = texts[path] if path in texts else read_text(path)
        except OSError as error:
            add_failure(results, root, path, 0, "SCRIPTS", f"could not read script: {error}")
            continue
        lines = text.splitlines()
        for line_number, line in enumerate(lines, start=1):
            if ABSOLUTE_PATH.search(line) and not (line.startswith("#!") or "/usr/bin/env" in line):
                add_failure(results, root, path, line_number, "SCRIPTS", "absolute path in script", line)
        if path.suffix.lower() == ".py":
            check_python_imports(root, skill, path, text, dependencies, results)
        else:
            check_js_imports(root, skill, path, text, dependencies, results)

def is_omp_native(skill_text: str | None) -> bool:
    # OMP-native skills (PORTING.md Rule 8) are exempt from the Tier-A/Tier-B neutrality
    # checks. They mark themselves with `omp-native: true` in SKILL.md frontmatter.
    if skill_text is None:
        return False
    parsed = frontmatter(skill_text.splitlines())
    if parsed is None:
        return False
    field = yaml_field(parsed[0], "omp-native")
    return field is not None and field[0].strip().lower() in ("true", "yes", "1")

def check_skill(root: Path, skill_name: str, allowlists: list[AllowlistEntry], results: Results) -> None:
    skill, skill_file = root / skill_name, root / skill_name / "SKILL.md"
    if not skill.is_dir():
        add_failure(results, root, skill, 0, "STRUCTURE", "missing skill directory")
        return
    texts: dict[Path, str] = {}
    for path in text_files(skill, TEXT_SUFFIXES):
        try:
            texts[path] = read_text(path)
        except OSError as error:
            add_failure(results, root, path, 0, "TIER-A", f"could not read text file: {error}")
            continue
    omp_native = is_omp_native(texts.get(skill_file))
    for path, text in texts.items():
        if not omp_native:
            scan_tier_a(root, path, text, allowlists, results)
            if path.suffix.lower() == ".md":
                check_hazards(root, path, text, results)
    if skill_file not in texts:
        add_failure(results, root, skill_file, 0, "STRUCTURE", "could not read SKILL.md" if skill_file.exists() else "missing SKILL.md")
    else:
        check_structure(root, skill, skill_name, texts[skill_file], results)
        if not omp_native:
            check_tier_b(root, skill_file, texts[skill_file], results)
    check_links(root, skill, texts, results)
    check_scripts(root, skill, texts, results)

def run(root: Path, skills: list[str]) -> Results:
    results: Results = {"root": str(root), "skills": skills, "violations": [], "suppressed": 0, "summary": {}, "ok": False}
    allowlists = load_allowlists(root, results)
    for skill in skills:
        check_skill(root, skill, allowlists, results)
    results["violations"].sort(key=lambda item: (item["rule"], item["path"], item["line"], item["message"]))
    results["summary"] = dict(sorted(Counter(item["rule"] for item in results["violations"]).items()))
    results["ok"] = not results["violations"]
    return results

def print_human(results: Results) -> None:
    violations = results["violations"]
    if not violations:
        print(f"PASS: {len(results['skills'])} skill(s) checked")
    else:
        print(f"FAIL: {len(violations)} violation(s)")
        grouped: defaultdict[str, list[Violation]] = defaultdict(list)
        for violation in violations:
            grouped[violation["rule"]].append(violation)
        for rule in sorted(grouped):
            print(f"\n{rule} ({len(grouped[rule])})")
            for violation in grouped[rule]:
                print(f"  {violation['path']}:{violation['line']}: {rule}: {violation['message']}")
                if violation["excerpt"]:
                    print(f"    {violation['excerpt']}")
    print(f"SUPPRESSED: {results['suppressed']}")

def main() -> int:
    parser = argparse.ArgumentParser(description="Check a portable skill pack.")
    _ = parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    _ = parser.add_argument("--skills", default=",".join(DEFAULT_SKILLS), help="comma-separated skill directories")
    _ = parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    root, raw_skills, as_json = cast(Path, args.root), cast(str, args.skills), cast(bool, args.json)
    skills = list(dict.fromkeys(part.strip() for part in raw_skills.split(",") if part.strip()))
    if not skills:
        parser.error("--skills must name at least one skill")
    results = run(root.expanduser().resolve(), skills)
    if as_json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        print_human(results)
    return 0 if results["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
