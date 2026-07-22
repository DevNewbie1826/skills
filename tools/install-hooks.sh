#!/usr/bin/env bash
# Install the local pre-commit gate without overwriting an unrelated hook.
set -euo pipefail

SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
MARKER='# skills-verify-hook'

if ! git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    printf 'Not inside a Git work tree: %s\n' "$REPO_ROOT" >&2
    exit 1
fi

configured_hooks_path="$(git -C "$REPO_ROOT" config --get core.hooksPath || true)"
if [[ -n "$configured_hooks_path" ]]; then
    case "$configured_hooks_path" in
        /*) hooks_dir="$configured_hooks_path" ;;
        *) hooks_dir="$REPO_ROOT/$configured_hooks_path" ;;
    esac
else
    hooks_dir="$(git -C "$REPO_ROOT" rev-parse --git-path hooks)"
    case "$hooks_dir" in
        /*) ;;
        *) hooks_dir="$REPO_ROOT/$hooks_dir" ;;
    esac
fi

mkdir -p "$hooks_dir"
hook_path="$hooks_dir/pre-commit"
if [[ -e "$hook_path" ]] && ! grep -Fqx "$MARKER" "$hook_path"; then
    printf 'Refusing to overwrite existing pre-commit hook: %s\n' "$hook_path" >&2
    printf 'Merge this gate into that hook manually, or replace the hook deliberately.\n' >&2
    exit 1
fi

temporary_hook="$(mktemp "$hooks_dir/pre-commit.XXXXXX")"
cleanup() {
    rm -f -- "$temporary_hook"
}
trap cleanup EXIT

cat > "$temporary_hook" <<'HOOK'
#!/usr/bin/env bash
# skills-verify-hook
# Fast local gate: sections A and E only. CI runs the full tools/verify.sh gate.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
exec bash "$repo_root/tools/verify.sh" --fast
HOOK
chmod 755 "$temporary_hook"
mv -f "$temporary_hook" "$hook_path"
trap - EXIT

printf 'Installed %s\n' "$hook_path"
printf 'Pre-commit runs the fast A+E subset; CI runs the complete verification gate.\n'
