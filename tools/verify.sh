#!/usr/bin/env bash
# Full regression gate for this skill pack. Run with: bash tools/verify.sh
# --fast is the pre-commit subset: the contract checker and SKILL.md line cap.
set -euo pipefail

SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"

usage() {
    cat <<'USAGE'
Usage: bash tools/verify.sh [--fast]

Run the full regression gate. --fast runs only the portable-skill contract checker
and the SKILL.md line cap; it is intended for the installed pre-commit hook.
USAGE
}

fast=0
case "${1-}" in
    "")
        ;;
    --fast)
        fast=1
        ;;
    -h|--help)
        usage
        exit 0
        ;;
    *)
        usage >&2
        exit 2
        ;;
esac

if (( $# > 1 )); then
    usage >&2
    exit 2
fi

TEMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/skills-verify.XXXXXX")"
current_section=''

cleanup() {
    local status=$?
    rm -rf -- "$TEMP_ROOT" || true
    if (( status != 0 )); then
        if [[ -n "$current_section" ]]; then
            printf '\nFAIL: %s\n' "$current_section" >&2
        fi
        printf 'FAIL: verification gate\n' >&2
    fi
    trap - EXIT
    exit "$status"
}
trap cleanup EXIT

cd "$REPO_ROOT"

smoke_index=0

run_section() {
    local label=$1
    shift

    current_section=$label
    printf '\n==> %s\n' "$label"
    "$@"
    printf 'PASS: %s\n' "$label"
    current_section=''
}

require_command() {
    local command=$1
    if ! command -v "$command" >/dev/null 2>&1; then
        printf 'Required command is unavailable: %s\n' "$command" >&2
        return 127
    fi
}

smoke_help() {
    local label=$1
    local output
    local status=0
    shift

    smoke_index=$((smoke_index + 1))
    output="$TEMP_ROOT/smoke-$smoke_index.log"
    printf '  smoke: %s\n' "$label"
    if "$@" >"$output" 2>&1; then
        return 0
    else
        status=$?
        printf '  --help failed for %s:\n' "$label" >&2
        cat "$output" >&2
        return "$status"
    fi
}

smoke_usage_error() {
    local label=$1
    local expected_pattern=$2
    local output
    shift 2

    smoke_index=$((smoke_index + 1))
    output="$TEMP_ROOT/smoke-$smoke_index.log"
    printf '  smoke: %s (usage error)\n' "$label"
    if "$@" >"$output" 2>&1; then
        printf '  expected a documented usage error, but %s exited 0:\n' "$label" >&2
        cat "$output" >&2
        return 1
    fi
    if grep -Eq "$expected_pattern" "$output"; then
        return 0
    fi

    printf '  %s did not emit its documented usage text:\n' "$label" >&2
    cat "$output" >&2
    return 1
}

check_skill_contract() {
    require_command python3
    python3 tools/check-skills.py
}

check_entrypoint_smoke() {
    local script
    local checker_count=0
    local typescript_count=0
    local typescript_root="$TEMP_ROOT/typescript"
    local node_path

    require_command python3
    require_command uv
    require_command bun
    require_command npm

    smoke_help "Lighthouse audit" python3 frontend/scripts/perfection/lighthouse-audit.py --help
    smoke_help "UI/UX database search" python3 frontend/references/ui-ux-db/scripts/search.py --help
    smoke_help "Python project scaffolder" python3 programming/scripts/python/new-project.py --help
    smoke_help "Go project scaffolder" uv run --with typer --with rich programming/scripts/go/new-project.py --help
    smoke_help "Rust project scaffolder" uv run --with typer --with rich programming/scripts/rust/new-project.py --help
    smoke_help "Python script generator" python3 programming/scripts/python/new-script.py --help
    smoke_help "Python no-excuse checker" python3 programming/scripts/python/check-no-excuse-rules.py --help

    for script in programming/scripts/{go,rust}/check-no-excuse-rules.{sh,py}; do
        [[ -f "$script" ]] || continue
        checker_count=$((checker_count + 1))
        case "$script" in
            *.sh)
                smoke_usage_error "$script" '^Usage: .+' bash "$script"
                ;;
            *.py)
                smoke_usage_error "$script" '^Usage: .+' python3 "$script"
                ;;
        esac
    done
    if (( checker_count == 0 )); then
        printf 'No Go or Rust no-excuse checker entrypoints were found.\n' >&2
        return 1
    fi

    printf '  installing temporary typescript@^5 dependency\n'
    npm install --prefix "$typescript_root" --no-save --no-package-lock --ignore-scripts --no-audit --no-fund 'typescript@^5'
    node_path="$typescript_root/node_modules"
    if [[ -n "${NODE_PATH-}" ]]; then
        node_path="$node_path:$NODE_PATH"
    fi

    for script in programming/scripts/typescript/*.ts; do
        [[ -f "$script" ]] || continue
        typescript_count=$((typescript_count + 1))
        case "$(basename "$script")" in
            check-no-excuse-rules.ts)
                smoke_usage_error "$script" '^usage: check-no-excuse-rules\.ts <file-or-dir>\.\.\.$' \
                    env NODE_PATH="$node_path" bun "$script"
                ;;
            *)
                smoke_help "$script" bun "$script" --help
                ;;
        esac
    done
    rm -rf -- "$typescript_root"

    if (( typescript_count == 0 )); then
        printf 'No TypeScript entrypoints were found.\n' >&2
        return 1
    fi

    smoke_usage_error "visual-qa image-diff" \
        '^visual-qa error: usage: image-diff <reference\.png> <actual\.png>$' \
        bun visual-qa/scripts/cli.ts image-diff
    smoke_usage_error "visual-qa tui-check" \
        '^visual-qa error: usage: tui-check <capture\.txt> \[--cols N\]$' \
        bun visual-qa/scripts/cli.ts tui-check
}

check_ui_ux_db_matrix() {
    local ruleset_dir="frontend/references/ui-ux-db/scripts"
    local config
    local kind
    local name
    local output
    local count=0

    if ! config="$(cd "$ruleset_dir" && python3 - <<'PY'
from core import AVAILABLE_DOMAINS, AVAILABLE_STACKS

for domain in AVAILABLE_DOMAINS:
    print(f"domain\t{domain}")
for stack in AVAILABLE_STACKS:
    print(f"stack\t{stack}")
PY
)"; then
        printf 'Could not load the UI/UX database domain and stack configuration.\n' >&2
        return 1
    fi

    while IFS=$'\t' read -r kind name; do
        [[ -n "$kind" ]] || continue
        count=$((count + 1))
        output="$TEMP_ROOT/ui-ux-$count.log"
        case "$kind" in
            domain)
                if ! (cd "$ruleset_dir" && python3 search.py "button" --domain "$name" >"$output" 2>&1); then
                    printf 'UI/UX domain search failed for %s:\n' "$name" >&2
                    cat "$output" >&2
                    return 1
                fi
                ;;
            stack)
                if ! (cd "$ruleset_dir" && python3 search.py "button" --stack "$name" >"$output" 2>&1); then
                    printf 'UI/UX stack search failed for %s:\n' "$name" >&2
                    cat "$output" >&2
                    return 1
                fi
                ;;
            *)
                printf 'Unknown UI/UX configuration kind: %s\n' "$kind" >&2
                return 1
                ;;
        esac
    done <<< "$config"

    if (( count == 0 )); then
        printf 'The UI/UX database configuration did not expose any domains or stacks.\n' >&2
        return 1
    fi
    printf '  exercised %d configured domains/stacks\n' "$count"
}

check_visual_qa_functional() {
    local image_dir="$TEMP_ROOT/visual-qa"
    local identical_output="$image_dir/identical.json"
    local different_output="$image_dir/different.json"

    mkdir -p "$image_dir"
    python3 - "$image_dir/reference.png" "$image_dir/identical.png" "$image_dir/different.png" <<'PY'
import struct
import sys
import zlib
from pathlib import Path


def chunk(kind: bytes, data: bytes) -> bytes:
    checksum = zlib.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", checksum)


def write_png(path: str, rgba: tuple[int, int, int, int]) -> None:
    header = struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)
    pixels = b"\x00" + bytes(rgba)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b"")
    Path(path).write_bytes(png)


write_png(sys.argv[1], (255, 0, 0, 255))
write_png(sys.argv[2], (255, 0, 0, 255))
write_png(sys.argv[3], (0, 0, 255, 255))
PY

    if ! bun visual-qa/scripts/cli.ts image-diff "$image_dir/reference.png" "$image_dir/identical.png" >"$identical_output" 2>&1; then
        printf 'visual-qa identical-image diff failed:\n' >&2
        cat "$identical_output" >&2
        return 1
    fi
    if ! bun visual-qa/scripts/cli.ts image-diff "$image_dir/reference.png" "$image_dir/different.png" >"$different_output" 2>&1; then
        printf 'visual-qa different-image diff failed:\n' >&2
        cat "$different_output" >&2
        return 1
    fi

    python3 - "$identical_output" "$different_output" <<'PY'
import json
import sys

identical = json.load(open(sys.argv[1], encoding="utf-8"))
different = json.load(open(sys.argv[2], encoding="utf-8"))

if identical.get("diffRatio") != 0:
    raise SystemExit(f"identical images produced diffRatio={identical.get('diffRatio')!r}, expected 0")
if not isinstance(different.get("diffRatio"), (int, float)) or different["diffRatio"] <= 0:
    raise SystemExit(f"different images produced diffRatio={different.get('diffRatio')!r}, expected > 0")
PY

    printf '  image-diff returned diffRatio 0 for identical images and >0 for different images\n'
}

check_skill_line_cap() {
    local manifest="$TEMP_ROOT/skill-files"
    local skill
    local line_count
    local found=0
    local too_long=0

    if ! find "$REPO_ROOT" -type f -name SKILL.md -print0 >"$manifest"; then
        printf 'Could not enumerate SKILL.md files.\n' >&2
        return 1
    fi

    while IFS= read -r -d '' skill; do
        found=$((found + 1))
        line_count=$(wc -l < "$skill")
        if (( line_count > 200 )); then
            printf '%s has %d lines (maximum: 200).\n' "${skill#"$REPO_ROOT"/}" "$line_count" >&2
            too_long=1
        fi
    done < "$manifest"

    if (( found == 0 )); then
        printf 'No SKILL.md files were found.\n' >&2
        return 1
    fi
    if (( too_long != 0 )); then
        return 1
    fi
    printf '  %d SKILL.md file(s) are within the 200-line cap\n' "$found"
}

check_wf_goal_regression() {
    require_command bun
    bun tools/wf-goal.test.ts
}

if (( fast )); then
    printf 'Running fast pre-commit subset (contract checker and SKILL.md cap).\n'
    run_section 'A. portable skill contract' check_skill_contract
    run_section 'E. SKILL.md line cap' check_skill_line_cap
else
    run_section 'A. portable skill contract' check_skill_contract
    run_section 'B. bundled entrypoint smoke' check_entrypoint_smoke
    run_section 'C. UI/UX database matrix' check_ui_ux_db_matrix
    run_section 'D. visual-qa functional check' check_visual_qa_functional
    run_section 'E. SKILL.md line cap' check_skill_line_cap
    run_section 'F. wf-goal extension regression' check_wf_goal_regression
fi

printf '\nPASS: verification gate\n'
