#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
#
# How to run:
#   uv run --script check-no-excuse-rules.py src/lib.rs src/main.rs
#   uv run --script check-no-excuse-rules.py src/           # recursively finds .rs files
#   uv run --script check-no-excuse-rules.py .              # entire tree
#
# No-excuse rule checker for Rust files — Python rewrite of check-no-excuse-rules.sh.
# Only rules enforceable via pure text matching live here.
# Everything semantic is on clippy + miri + nextest.
#
# Rules:
#   unwrap            .unwrap() outside tests without a #[expect(clippy::unwrap_used, reason = "...")]
#   expect            .expect() outside tests without a #[expect(clippy::expect_used, reason = "...")]
#   placeholder-macro todo!/unimplemented!/unreachable!/unreachable_unchecked! in committed code
#   box-dyn-error     Box<dyn Error> in non-test code
#   lib-panic         panic!() in library code
#   discarded-result  `let _ = call(...)` without a #[expect(clippy::let_underscore_must_use, reason = "...")]
#   blocking-in-async blocking calls (thread::sleep / std::fs / reqwest::blocking / .blocking_*()) in async code
#   unsafe-no-safety  unsafe { without // SAFETY: in preceding 5 lines
#   allow-attribute   #[allow(...)] - silence lints with #[expect(lint, reason)]
#   expect-without-reason  #[expect(...)] with no `reason = "..."`
#   narrowing-as-cast possible narrowing 'as' cast
#
# Opt-out: a proven invariant is expressed with the attribute the compiler also sees,
# on the statement or the line above it:
#   #[expect(clippy::unwrap_used, reason = "...")]
#   #[expect(clippy::expect_used, reason = "...")]
#   #[expect(clippy::let_underscore_must_use, reason = "...")]
#   // SAFETY: <reason>          (for unsafe blocks, within 5 lines above)
#
# Test paths (exempt from unwrap/expect/placeholder/box-dyn-error/lib-panic):
#   tests/, benches/, examples/, build.rs, *_test.rs, #[cfg(test)] regions

from __future__ import annotations

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Patterns (compiled once)
# ---------------------------------------------------------------------------

RE_UNWRAP = re.compile(r"\.unwrap\(\)")
RE_EXPECT = re.compile(r"\.expect\(")
RE_UNWRAP_OPT_OUT = re.compile(r"#\[expect\(clippy::unwrap_used,.*reason")
RE_EXPECT_OPT_OUT = re.compile(r"#\[expect\(clippy::expect_used,.*reason")
RE_DISCARDED_RESULT = re.compile(r"let\s+_\s*=\s*[^;]*\(")
RE_DISCARDED_OPT_OUT = re.compile(r"#\[expect\(clippy::let_underscore_must_use,.*reason")
RE_PLACEHOLDER = re.compile(r"\b(todo!|unimplemented!|unreachable!|unreachable_unchecked!)")
RE_BOX_DYN_ERROR = re.compile(r"Box<dyn\s+Error")
RE_PANIC = re.compile(r"\bpanic!\(")
RE_BLOCKING_CALL = re.compile(
    r"(thread::sleep\(|std::fs::|reqwest::blocking::|\.blocking_(recv|send|lock|read|write)\()"
)
RE_ASYNC_REGION = re.compile(
    r"(^|[^A-Za-z0-9_])async(\s+(move\s*)?\{|\s+(unsafe\s+)?fn\s)"
)
RE_UNSAFE_BLOCK = re.compile(r"\bunsafe\s*\{")
RE_SAFETY = re.compile(r"//\s*SAFETY:")
RE_ALLOW_ATTRIBUTE = re.compile(r"#!?\[allow\(")
RE_EXPECT_ATTRIBUTE = re.compile(r"#!?\[expect\(")
RE_REASON = re.compile(r"reason\s*=")
RE_CFG_TEST = re.compile(r"#\[cfg\(test\)\]")

# Narrowing cast: (wider) as (narrower). No leading \b - must match e.g.
# `999u64 as u32` where a digit precedes the type.
_WIDER = r"(?:u16|u32|u64|u128|usize|i16|i32|i64|i128|isize)"
_NARROWER = r"(?:u8|u16|u32|i8|i16|i32)"
RE_NARROWING_CAST = re.compile(
    rf"{_WIDER}\s+as\s+{_NARROWER}(?:[^A-Za-z0-9_]|$)"
)

# Test-path fragments.
_TEST_PATH_PARTS = {"tests", "benches", "examples"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

violations = 0


def report(file: str, line: int, rule: str, detail: str) -> None:
    """Emit a GitHub-Actions-compatible error annotation to stderr."""
    global violations
    print(f"::error file={file},line={line}::[{rule}] {detail}", file=sys.stderr)
    violations += 1


def is_test_path(path: Path) -> bool:
    """Return True if *path* is in a test/bench/example directory or is a test file."""
    parts = path.parts
    for part in parts:
        if part in _TEST_PATH_PARTS:
            return True
    if path.name == "build.rs":
        return True
    if path.name.endswith("_test.rs"):
        return True
    return False


def is_lib_path(file: Path) -> bool:
    """Heuristic: is this file library code (not main.rs, not src/bin/*)."""
    parts = list(file.parts)
    # Must live under src/
    if "src" not in parts:
        return False
    if file.name == "main.rs":
        return False
    # src/bin/* is binary code
    src_idx = parts.index("src")
    if src_idx + 1 < len(parts) and parts[src_idx + 1] == "bin":
        return False
    return True


def strip_line_comment(line: str) -> str:
    """Return the portion of *line* before any ``//`` line comment.

    This is a crude heuristic — it does not handle ``//`` inside string
    literals, but matches the behaviour of the bash version.
    """
    idx = line.find("//")
    if idx == -1:
        return line
    return line[:idx]


def collect_rs_files(args: list[str]) -> list[Path]:
    """Expand CLI arguments: files are kept as-is, directories are walked."""
    result: list[Path] = []
    for arg in args:
        p = Path(arg)
        if p.is_file():
            if p.suffix == ".rs":
                result.append(p)
        elif p.is_dir():
            result.extend(sorted(p.rglob("*.rs")))
        # Ignore non-existent / non-.rs
    return result


# ---------------------------------------------------------------------------
# Main checker
# ---------------------------------------------------------------------------

def check_file(file: Path) -> None:
    in_test_file = is_test_path(file)
    in_cfg_test = False
    cfg_test_brace_depth = 0
    in_async = False
    async_brace_depth = 0
    async_opened = False

    try:
        lines = file.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        print(f"warning: cannot read {file}: {exc}", file=sys.stderr)
        return

    for line_no_0, raw_line in enumerate(lines):
        line_no = line_no_0 + 1  # 1-indexed
        code_only = strip_line_comment(raw_line)
        opens = code_only.count("{")
        closes = code_only.count("}")

        # --- #[cfg(test)] region tracker ---
        if RE_CFG_TEST.search(raw_line):
            in_cfg_test = True
            cfg_test_brace_depth = 0

        if in_cfg_test:
            cfg_test_brace_depth += opens - closes
            if cfg_test_brace_depth <= 0 and not RE_CFG_TEST.search(raw_line):
                in_cfg_test = False

        # --- async region tracker (async fn / async block) ---
        if not in_async and RE_ASYNC_REGION.search(code_only):
            in_async = True
            async_brace_depth = 0
            async_opened = False
        async_line = in_async
        if in_async:
            async_brace_depth += opens - closes
            if opens > 0:
                async_opened = True
            if async_opened and async_brace_depth <= 0:
                in_async = False

        exempt = in_test_file or in_cfg_test
        prev = lines[line_no_0 - 1] if line_no_0 > 0 else ""

        if not exempt:
            # .unwrap() — a proven invariant uses .expect() behind #[expect(clippy::expect_used, ...)]
            if RE_UNWRAP.search(code_only) and not RE_UNWRAP_OPT_OUT.search(prev):
                report(
                    str(file), line_no, "unwrap",
                    ".unwrap() outside tests - use ? / ok_or / let-else, or for a "
                    "proven invariant use .expect() behind "
                    '#[expect(clippy::expect_used, reason = "...")]',
                )

            # .expect("...") — allowed only for a proven invariant
            if RE_EXPECT.search(code_only) and not RE_EXPECT_OPT_OUT.search(prev):
                report(
                    str(file), line_no, "expect",
                    ".expect() outside tests - use ?, or for a proven invariant "
                    "annotate the previous line with "
                    '#[expect(clippy::expect_used, reason = "...")]',
                )

            # todo!/unimplemented!/unreachable!/unreachable_unchecked!
            if RE_PLACEHOLDER.search(code_only):
                report(
                    str(file), line_no, "placeholder-macro",
                    "todo!/unimplemented!/unreachable! in committed code",
                )

            # Box<dyn Error>
            if RE_BOX_DYN_ERROR.search(code_only):
                report(
                    str(file), line_no, "box-dyn-error",
                    "Box<dyn Error> in non-test code - use anyhow::Error (apps) "
                    "or thiserror enum (libs)",
                )

            # panic!() in library code
            if is_lib_path(file) and RE_PANIC.search(code_only):
                report(
                    str(file), line_no, "lib-panic",
                    "panic!() in library code - return Result",
                )

            # let _ = call(...) drops the error
            if RE_DISCARDED_RESULT.search(code_only) and not RE_DISCARDED_OPT_OUT.search(prev):
                report(
                    str(file), line_no, "discarded-result",
                    "let _ = call() drops its result - propagate or handle the "
                    "error; log it on a best-effort path",
                )

            # Blocking calls inside async code
            if async_line and RE_BLOCKING_CALL.search(code_only):
                report(
                    str(file), line_no, "blocking-in-async",
                    "blocking call inside async code - use tokio::time::sleep / "
                    "tokio::fs / the async client, or move it into spawn_blocking",
                )

        # unsafe { without // SAFETY: — always enforced, even in tests
        if RE_UNSAFE_BLOCK.search(code_only):
            start = max(0, line_no_0 - 5)
            window = "\n".join(lines[start : line_no_0 + 1])
            if not RE_SAFETY.search(window):
                report(
                    str(file), line_no, "unsafe-no-safety-comment",
                    "unsafe block without // SAFETY: comment in preceding 5 lines",
                )

        # #[allow(...)] — silence lints with #[expect(lint, reason)] instead
        if RE_ALLOW_ATTRIBUTE.search(code_only):
            report(
                str(file), line_no, "allow-attribute",
                '#[allow(...)] - use #[expect(lint, reason = "...")] so the '
                "exception fails once the lint stops firing",
            )

        # #[expect(...)] without `reason = "..."` on the attribute
        if RE_EXPECT_ATTRIBUTE.search(code_only):
            attr = "\n".join(lines[line_no_0 : line_no_0 + 4])
            if not RE_REASON.search(attr):
                report(
                    str(file), line_no, "expect-without-reason",
                    '#[expect(...)] needs reason = "..." naming why the lint does '
                    "not apply",
                )

        # Narrowing numeric `as` casts
        if RE_NARROWING_CAST.search(code_only):
            report(
                str(file), line_no, "narrowing-as-cast",
                "possible narrowing 'as' cast - use TryFrom / try_into() for "
                "fallible conversion",
            )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    global violations

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <file.rs|dir> [file.rs|dir ...]", file=sys.stderr)
        sys.exit(2)

    files = collect_rs_files(sys.argv[1:])
    if not files:
        print("warning: no .rs files found in the given arguments", file=sys.stderr)
        sys.exit(0)

    for f in files:
        check_file(f)

    if violations > 0:
        print("", file=sys.stderr)
        print(
            f"rust-programmer: {violations} violation(s). Fix before declaring work done.",
            file=sys.stderr,
        )
        print("", file=sys.stderr)
        print("Then run the full toolchain gate:", file=sys.stderr)
        print("  cargo +stable fmt --all -- --check", file=sys.stderr)
        print(
            "  cargo +stable clippy --all-targets --all-features -- -D warnings",
            file=sys.stderr,
        )
        print(
            "  cargo nextest run --all-targets --all-features && cargo test --doc",
            file=sys.stderr,
        )
        print(
            "  cargo +nightly miri nextest run --all-features    # if unsafe touched",
            file=sys.stderr,
        )
        print("  cargo machete", file=sys.stderr)
        print("  cargo deny check", file=sys.stderr)
        sys.exit(1)

    print(f"rust-programmer: no-excuse rules passed for {len(files)} file(s).")


if __name__ == "__main__":
    main()
