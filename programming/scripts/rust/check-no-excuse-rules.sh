#!/usr/bin/env bash
# No-excuse rule checker for Rust files.
# Mirrors the philosophy of python-programmer / typescript-programmer scripts:
# only rules that can be enforced via pure text matching live here.
# Everything semantic is on clippy + miri + nextest.
#
# Rules:
#   unwrap / expect         outside tests, unless the previous line carries
#                           #[expect(clippy::unwrap_used|expect_used, reason = "...")]
#   placeholder-macro       todo!/unimplemented!/unreachable! in committed code
#   box-dyn-error           Box<dyn Error> in non-test code
#   lib-panic               panic!() in library code
#   discarded-result        `let _ = call(...)`, unless the previous line carries
#                           #[expect(clippy::let_underscore_must_use, reason = "...")]
#   blocking-in-async       std::thread::sleep / std::fs / reqwest::blocking /
#                           .blocking_*() inside an async fn or async block
#   unsafe-no-safety        unsafe { without // SAFETY: in the preceding 5 lines
#   allow-attribute         #[allow(...)] - silence lints with #[expect(lint, reason)]
#   expect-without-reason   #[expect(...)] with no `reason = "..."`
#   narrowing-as-cast       possible narrowing numeric `as` cast

set -euo pipefail

if [ $# -eq 0 ]; then
    echo "Usage: $0 <file.rs> [file.rs ...]" >&2
    exit 2
fi

violations=0
report() {
    local file="$1"
    local line="$2"
    local rule="$3"
    local detail="$4"
    echo "::error file=${file},line=${line}::[${rule}] ${detail}" >&2
    violations=$((violations + 1))
}

is_test_path() {
    local path="$1"
    case "$path" in
        */tests/*|*/benches/*|*/examples/*|*/build.rs|*_test.rs|tests/*|benches/*|examples/*) return 0 ;;
    esac
    # In-file #[cfg(test)] modules are handled per-line below.
    return 1
}

count_char() {
    local only="${1//[^$2]/}"
    echo "${#only}"
}

for file in "$@"; do
    [ -f "$file" ] || continue
    case "$file" in
        *.rs) ;;
        *) continue ;;
    esac

    if is_test_path "$file"; then
        # Test files are exempt from unwrap/expect/todo rules.
        # Still enforce unsafe-comment, allow-comment, panic-in-lib rules below
        # by setting a marker - keeping the loop unified.
        in_test_file=1
    else
        in_test_file=0
    fi

    # Track #[cfg(test)] and async regions per line; a region starts at its
    # marker line and ends once the braces it opened are closed again.
    in_cfg_test=0
    cfg_test_brace_depth=0
    in_async=0
    async_brace_depth=0
    async_opened=0
    line_no=0

    while IFS= read -r raw_line || [ -n "$raw_line" ]; do
        line_no=$((line_no + 1))
        line="$raw_line"

        # Strip line comments before pattern checks - so doc comments and
        # explanatory prose do not trip the regexes.
        code_only="${line%%//*}"
        opens=$(count_char "$code_only" "{")
        closes=$(count_char "$code_only" "}")

        # Crude #[cfg(test)] region tracker: when we see #[cfg(test)] on a
        # line followed by a mod with `{`, count braces until depth returns
        # to zero. This is approximate but matches typical formatting.
        if [[ "$line" =~ \#\[cfg\(test\)\] ]]; then
            in_cfg_test=1
            cfg_test_brace_depth=0
        fi
        if [ "$in_cfg_test" -eq 1 ]; then
            cfg_test_brace_depth=$((cfg_test_brace_depth + opens - closes))
            if [ "$cfg_test_brace_depth" -le 0 ] && [[ ! "$line" =~ \#\[cfg\(test\)\] ]]; then
                in_cfg_test=0
            fi
        fi

        # Same brace tracking for `async fn` / `async {` blocks, so blocking
        # calls are only flagged inside async code.
        if [ "$in_async" -eq 0 ] && [[ "$code_only" =~ (^|[^[:alnum:]_])async([[:space:]]+(move[[:space:]]*)?\{|[[:space:]]+(unsafe[[:space:]]+)?fn[[:space:]]) ]]; then
            in_async=1
            async_brace_depth=0
            async_opened=0
        fi
        async_line=$in_async
        if [ "$in_async" -eq 1 ]; then
            async_brace_depth=$((async_brace_depth + opens - closes))
            [ "$opens" -gt 0 ] && async_opened=1
            if [ "$async_opened" -eq 1 ] && [ "$async_brace_depth" -le 0 ]; then in_async=0; fi
        fi

        exempt=0
        [ "$in_test_file" -eq 1 ] && exempt=1
        [ "$in_cfg_test" -eq 1 ] && exempt=1

        # The line above this one, where the #[expect(...)] opt-outs live.
        prev_line=""
        [ "$line_no" -gt 1 ] && prev_line=$(sed -n "$((line_no - 1))p" "$file" 2>/dev/null || true)

        if [ "$exempt" -eq 0 ]; then
            # .unwrap() - a proven invariant uses .expect() behind #[expect(clippy::expect_used, ...)]
            if [[ "$code_only" =~ \.unwrap\(\) ]] && [[ ! "$prev_line" =~ \#\[expect\(clippy::unwrap_used,.*reason ]]; then
                report "$file" "$line_no" "unwrap" ".unwrap() outside tests - use ? / ok_or / let-else, or for a proven invariant use .expect() behind #[expect(clippy::expect_used, reason = \"...\")]"
            fi

            # .expect("...") - allowed only for a proven invariant
            if [[ "$code_only" =~ \.expect\( ]] && [[ ! "$prev_line" =~ \#\[expect\(clippy::expect_used,.*reason ]]; then
                report "$file" "$line_no" "expect" ".expect() outside tests - use ?, or for a proven invariant annotate the previous line with #[expect(clippy::expect_used, reason = \"...\")]"
            fi

            # todo!() / unimplemented!() / unreachable!()
            if [[ "$code_only" =~ (todo!|unimplemented!|unreachable!|unreachable_unchecked!) ]]; then
                report "$file" "$line_no" "placeholder-macro" "todo!/unimplemented!/unreachable! in committed code"
            fi

            # Box<dyn Error
            if [[ "$code_only" =~ Box\<dyn[[:space:]]+Error ]]; then
                report "$file" "$line_no" "box-dyn-error" "Box<dyn Error> in non-test code - use anyhow::Error (apps) or thiserror enum (libs)"
            fi

            # panic!( in lib
            if [[ "$file" == */src/lib.rs || "$file" == */src/*/mod.rs || ( "$file" == */src/*.rs && "$file" != */src/main.rs && "$file" != */src/bin/* ) ]]; then
                if [[ "$code_only" =~ panic!\( ]]; then
                    report "$file" "$line_no" "lib-panic" "panic!() in library code - return Result"
                fi
            fi

            # let _ = call(...) drops the error
            if [[ "$code_only" =~ let[[:space:]]+_[[:space:]]*=[[:space:]]*[^\;]*\( ]] && [[ ! "$prev_line" =~ \#\[expect\(clippy::let_underscore_must_use,.*reason ]]; then
                report "$file" "$line_no" "discarded-result" "let _ = call() drops its result - propagate or handle the error; log it on a best-effort path"
            fi

            # Blocking calls inside async code
            if [ "$async_line" -eq 1 ] && [[ "$code_only" =~ (thread::sleep\(|std::fs::|reqwest::blocking::|\.blocking_(recv|send|lock|read|write)\() ]]; then
                report "$file" "$line_no" "blocking-in-async" "blocking call inside async code - use tokio::time::sleep / tokio::fs / the async client, or move it into spawn_blocking"
            fi
        fi

        # unsafe { without preceding // SAFETY: in the last 5 lines (always enforced)
        if [[ "$code_only" =~ unsafe[[:space:]]*\{ ]]; then
            start=$((line_no > 5 ? line_no - 5 : 1))
            window=$(sed -n "${start},${line_no}p" "$file" 2>/dev/null || true)
            if [[ ! "$window" =~ //[[:space:]]*SAFETY: ]]; then
                report "$file" "$line_no" "unsafe-no-safety-comment" "unsafe block without // SAFETY: comment in preceding 5 lines"
            fi
        fi

        # #[allow(...)] - silence lints with #[expect(lint, reason)] instead
        if [[ "$code_only" =~ \#!?\[allow\( ]]; then
            report "$file" "$line_no" "allow-attribute" "#[allow(...)] - use #[expect(lint, reason = \"...\")] so the exception fails once the lint stops firing"
        fi

        # #[expect(...)] without `reason = "..."` on the attribute
        if [[ "$code_only" =~ \#!?\[expect\( ]]; then
            attr=$(sed -n "${line_no},$((line_no + 3))p" "$file" 2>/dev/null || true)
            if [[ ! "$attr" =~ reason[[:space:]]*= ]]; then
                report "$file" "$line_no" "expect-without-reason" "#[expect(...)] needs reason = \"...\" naming why the lint does not apply"
            fi
        fi

        # Narrowing numeric `as` casts - heuristic flag for human review.
        # Catches the common shapes; precise type analysis belongs to clippy::cast_possible_truncation.
        if [[ "$code_only" =~ (u16|u32|u64|u128|usize|i16|i32|i64|i128|isize)[[:space:]]+as[[:space:]]+(u8|u16|u32|i8|i16|i32)([^[:alnum:]_]|$) ]]; then
            report "$file" "$line_no" "narrowing-as-cast" "possible narrowing 'as' cast - use TryFrom / try_into() for fallible conversion"
        fi
    done < "$file"
done

if [ "$violations" -gt 0 ]; then
    echo "" >&2
    echo "rust-programmer: ${violations} violation(s). Fix before declaring work done." >&2
    echo "" >&2
    echo "Then run the full toolchain gate:" >&2
    echo "  cargo +stable fmt --all -- --check" >&2
    echo "  cargo +stable clippy --all-targets --all-features -- -D warnings" >&2
    echo "  cargo nextest run --all-targets --all-features && cargo test --doc" >&2
    echo "  cargo +nightly miri nextest run --all-features    # if unsafe touched" >&2
    echo "  cargo machete" >&2
    echo "  cargo deny check" >&2
    exit 1
fi

echo "rust-programmer: no-excuse rules passed for $# file(s)."
