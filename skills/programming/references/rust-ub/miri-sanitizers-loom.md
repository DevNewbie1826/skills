# Miri, Sanitizers, Loom, and Fuzzing — The UB Detection Arsenal

> Read this when selecting evidence for a Rust undefined-behavior, concurrency, or parser audit.

Miri is the **primary weapon**. Everything else is supplementary for the gaps Miri cannot reach.

---

## Miri — The First and Last Line of Defense

### What Miri Is

Miri is an interpreter for Rust's MIR (Mid-level IR). It executes your test suite inside a virtual machine that tracks every byte of memory for validity, provenance, alignment, initialization, and aliasing. It is **deterministic** for a given seed and flag set (a nonzero preemption rate makes scheduling depend on the seed), and it can find UB that no amount of testing on real hardware will ever trigger.

Miri detects 10 of the 14 categories in [ub-taxonomy.md](ub-taxonomy.md) with high confidence (1-6 and 9-12); categories 7, 8, 13, and 14 are only partly covered and need the tools below.

### Installation

```bash
rustup install nightly
rustup component add miri rust-src --toolchain nightly
```

Verify:
```bash
cargo +nightly miri --version
```

### Running Miri

**Default run (Stacked Borrows, standard checks):**
```bash
cargo +nightly miri test
```

**With nextest (recommended for projects already using nextest):**
```bash
cargo +nightly miri nextest run
```

**Specific test:**
```bash
cargo +nightly miri test -- test_name
```

**Run a binary:**
```bash
cargo +nightly miri run
```

### MIRIFLAGS — The Dial-Up Knobs

These flags are set via the `MIRIFLAGS` environment variable. The agent should use ALL of the strictness flags during a UB audit.

#### Aliasing Model

```bash
# Default: Stacked Borrows (strict)
cargo +nightly miri test

# Tree Borrows (newer, more permissive — use as a second pass)
MIRIFLAGS="-Zmiri-tree-borrows" cargo +nightly miri test
```

**Protocol:** Run Stacked Borrows first. If it fails, fix it. Then run Tree Borrows as a separate pass. The models are not nested: Stacked Borrows is stricter about most reborrow patterns, but Tree Borrows rejects some code Stacked Borrows accepts. Ship only when both are clean.

#### Strict Provenance

```bash
MIRIFLAGS="-Zmiri-strict-provenance" cargo +nightly miri test
```

Catches `ptr as usize as *const T` roundtrips where provenance is lost. **Should be ON for every audit.**

#### Symbolic Alignment Checks

```bash
MIRIFLAGS="-Zmiri-symbolic-alignment-check" cargo +nightly miri test
```

Catches alignment UB that happens to be aligned on your machine but is not guaranteed by the type system.

#### Data Race Detection Tuning

```bash
# Targeted stress on one suspected race (the audit sweep uses 0.1 to keep full-suite runs fast)
MIRIFLAGS="-Zmiri-preemption-rate=0.5" cargo +nightly miri test

# Disable preemption (sequential scheduling — fewer races found but deterministic)
MIRIFLAGS="-Zmiri-preemption-rate=0" cargo +nightly miri test
```

#### The Full Paranoia Sweep (Use This for Audits)

Level 3:
```bash
MIRIFLAGS="\
  -Zmiri-strict-provenance \
  -Zmiri-symbolic-alignment-check \
  -Zmiri-preemption-rate=0.1 \
  -Zmiri-backtrace=full" \
cargo +nightly miri test
```

Level 4, a second pass with Tree Borrows:
```bash
MIRIFLAGS="\
  -Zmiri-tree-borrows \
  -Zmiri-strict-provenance \
  -Zmiri-symbolic-alignment-check \
  -Zmiri-preemption-rate=0.1 \
  -Zmiri-backtrace=full" \
cargo +nightly miri test
```

Add `-Zmiri-disable-isolation` only for the tests that need I/O (see below).

#### Isolation and I/O

Miri runs in isolation by default — no file I/O, no network, no system calls. If your tests need the filesystem:
```bash
MIRIFLAGS="-Zmiri-disable-isolation" cargo +nightly miri test
```

Use sparingly — isolation is a feature, not a limitation. Tests that need I/O should have a separate `#[cfg(not(miri))]` path.

### UB Audit Workflow

**Phase 1: Reconnaissance.** Find the hunting ground:

```bash
rg 'unsafe\s*(fn|impl|\{)' --type rust -n
rg 'unsafe\s+impl\s+(Send|Sync)' --type rust -n
rg '(transmute|transmute_copy|from_raw|into_raw|as_ptr|as_mut_ptr|offset|add|sub|read|write|copy|ptr::null)' --type rust -n
rg 'extern\s+"C"' --type rust -n
```

Catalog each hit: file, line, `unsafe` category, initial risk (high/medium/low based on the UB taxonomy).

**Phase 2: Miri sweep.** Run every level; **do not skip any**:

1. Level 1: the default run (Stacked Borrows).
2. Level 2: `-Zmiri-strict-provenance -Zmiri-symbolic-alignment-check -Zmiri-backtrace=full`.
3. Level 3: the full paranoia sweep above (the audit standard).
4. Level 4: the Tree Borrows pass above (second model confirmation).

A failure at Level 1 is definite UB; a failure first seen at Level 2 is provenance or alignment UB; a failure only at Level 4 means the aliasing models disagree, and [ub-taxonomy.md](ub-taxonomy.md) category 1 states the policy for that case. Passing all four makes the code Miri-clean.

**Phase 3: Supplementary scans.** For code Miri cannot fully cover, run loom for custom atomics, ASAN for FFI-heavy code, and cargo-fuzz for untrusted input parsing (commands in the sections below).

**Phase 4: Fix-and-prove loop.** For each UB finding:

1. **Classify** against the 14-category taxonomy.
2. **Write the SAFETY comment** stating the invariant the fix establishes ([../rust/unsafe-discipline.md](../rust/unsafe-discipline.md), "SAFETY Comment Grammar").
3. **Apply the minimal fix.** Do not refactor — fix the UB and nothing else.
4. **Run Miri (Level 3 minimum) on the specific test that triggered the UB.**
5. **Run Miri (Level 3) on the full test suite** to check for regressions.
6. **Document the bead:**
   ```
   BEAD: [Category #] [Short description]
   FILE: [path:line]
   ROOT CAUSE: [one sentence]
   FIX: [one sentence]
   PROOF: Miri Level [N] pass — [command used]
   ```

**Phase 5: Hardening.** After all beads are resolved, add Miri to CI (config below; it runs Level 2 under both aliasing models), add a `#[cfg(miri)]` regression test for each bead, and review the SAFETY comment on every remaining `unsafe` block. Head the audit report with its scope, the `cargo +nightly miri --version` output, and the date.

During any Rust task, not just audits: when the changeset touches `unsafe`, run Levels 1 and 2 before proceeding and stop to classify, fix, and prove on any failure. **Every `unsafe` block passes Miri Levels 3 and 4 before it ships.**

### Miri Limitations

| Cannot do | Workaround |
|-----------|-----------|
| Execute FFI / C code | ASAN, MSAN, Valgrind |
| Run I/O-heavy tests (default) | `-Zmiri-disable-isolation` or `#[cfg(not(miri))]` |
| Exhaustive interleaving exploration | loom |
| Find performance bugs | criterion, flamegraph |
| Run inline assembly | skip with `#[cfg(not(miri))]` |
| Test OS-specific behavior | real hardware + sanitizers |

### Miri in CI

```yaml
# GitHub Actions example
miri:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: dtolnay/rust-toolchain@nightly
      with:
        components: miri, rust-src
    - name: Miri test (Stacked Borrows + strict provenance)
      run: |
        MIRIFLAGS="-Zmiri-strict-provenance -Zmiri-symbolic-alignment-check -Zmiri-backtrace=full" \
        cargo +nightly miri test
    - name: Miri test (Tree Borrows)
      run: |
        MIRIFLAGS="-Zmiri-tree-borrows -Zmiri-strict-provenance -Zmiri-symbolic-alignment-check -Zmiri-backtrace=full" \
        cargo +nightly miri test
```

### Miri-Incompatible Test Gating

```rust
#[test]
#[cfg_attr(miri, ignore)]  // Miri cannot run this (FFI, I/O, inline asm)
fn test_requires_real_hardware() {
    // ...
}

// Or conditionally compile the test body:
#[test]
fn test_with_miri_fallback() {
    #[cfg(miri)]
    {
        // Simplified version that avoids FFI
    }
    #[cfg(not(miri))]
    {
        // Full version with FFI
    }
}
```

---

## Sanitizers — Where Miri Cannot Reach

Sanitizers are compiler instrumentation passes. They run your actual binary on real hardware with extra checks injected. Use them for FFI, I/O-heavy code, and integration tests.

### AddressSanitizer (ASAN)

Detects: use-after-free, buffer overflow, stack-use-after-return, double-free, memory leaks.

```bash
RUSTFLAGS="-Zsanitizer=address" cargo +nightly test -Zbuild-std --target x86_64-unknown-linux-gnu
```

On macOS:
```bash
RUSTFLAGS="-Zsanitizer=address" cargo +nightly test -Zbuild-std --target aarch64-apple-darwin
```

### ThreadSanitizer (TSAN)

Detects: data races on non-atomic accesses across threads.

```bash
RUSTFLAGS="-Zsanitizer=thread" cargo +nightly test -Zbuild-std --target x86_64-unknown-linux-gnu
```

**When to use over Miri:** Integration tests involving real threads + real I/O + FFI. Miri's data-race detector is superior for pure-Rust code.

### MemorySanitizer (MSAN)

Detects: reads of uninitialized memory.

```bash
RUSTFLAGS="-Zsanitizer=memory -Zsanitizer-memory-track-origins" cargo +nightly test -Zbuild-std --target x86_64-unknown-linux-gnu
```

**When to use over Miri:** FFI code where C/C++ may return uninitialized memory into Rust.

### UndefinedBehaviorSanitizer (UBSAN)

Detects: integer overflow, misaligned access, null dereference, and other C/C++-style UB at the LLVM level.

```bash
RUSTFLAGS="-Zsanitizer=undefined" cargo +nightly test -Zbuild-std --target x86_64-unknown-linux-gnu
```

### Sanitizer Limitations

- Require nightly + `-Zbuild-std` (rebuilds the standard library with instrumentation).
- MSAN requires ALL dependencies (including C libs) to be instrumented — practically hard.
- Cannot catch aliasing violations (that is Miri's domain).
- Significant runtime overhead (2-15x slower).
- Linux has the best support; macOS works for ASAN; Windows support is minimal.

---

## Loom — Exhaustive Concurrency Testing

Loom explores all possible thread interleavings of a bounded concurrent program. It is mandatory for lock-free and wait-free primitives.

### When to Use Loom

- Any `unsafe` code involving atomics with ordering weaker than `SeqCst`.
- Custom lock implementations.
- Lock-free queues, stacks, or other concurrent data structures.
- Any code where you chose `Relaxed`, `Acquire`, or `Release` ordering.

### When NOT to Use Loom

- Code using only `Mutex`/`RwLock` from std or `parking_lot` — the locks are sound, your usage is the question, and Miri + TSAN cover that.
- Async code (loom does not model async runtimes — use `tokio::test` + Miri instead).

### Setup

```toml
[dev-dependencies]
loom = "0.7"
```

### Loom Test Pattern

```rust
#[cfg(loom)]
mod loom_tests {
    use loom::sync::atomic::{AtomicUsize, Ordering};
    use loom::sync::Arc;
    use loom::thread;

    #[test]
    fn concurrent_increment_is_sound() {
        loom::model(|| {
            let counter = Arc::new(AtomicUsize::new(0));

            let threads: Vec<_> = (0..2).map(|_| {
                let c = counter.clone();
                thread::spawn(move || {
                    c.fetch_add(1, Ordering::SeqCst);
                })
            }).collect();

            for t in threads {
                t.join().unwrap();
            }

            assert_eq!(counter.load(Ordering::SeqCst), 2);
        });
    }
}
```

### Conditional Compilation for Loom

```rust
#[cfg(loom)]
use loom::sync::atomic::{AtomicUsize, Ordering};
#[cfg(not(loom))]
use std::sync::atomic::{AtomicUsize, Ordering};
```

### Running Loom Tests

```bash
# Loom tests only (use cfg flag)
RUSTFLAGS="--cfg loom" cargo test --lib -- loom_tests

# With release optimizations (loom is slow)
RUSTFLAGS="--cfg loom" cargo test --lib --release -- loom_tests
```

### Loom + Miri Interaction

Loom and Miri solve different problems:
- **Miri** checks a single execution for UB (aliasing, validity, provenance).
- **Loom** checks all interleavings for correctness (ordering, atomicity).

Run BOTH on lock-free code:
```bash
# Step 1: loom for interleaving correctness
RUSTFLAGS="--cfg loom" cargo test --lib --release -- loom_tests

# Step 2: Miri for UB in each path
cargo +nightly miri test -- concurrent_tests
```

---

## Cargo-Fuzz — Property-Based UB Hunting

Fuzzing generates random inputs to maximize code coverage and find crashes, panics, and UB.

### Setup

```bash
cargo install cargo-fuzz
cargo fuzz init
```

### Fuzz Target

```rust
// fuzz/fuzz_targets/parse_input.rs
#![no_main]
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &[u8]| {
    // Your parsing/deserialization/processing code here.
    // If it panics or triggers UB, the fuzzer catches it.
    let _ = my_crate::parse(data);
});
```

### Running

```bash
# Run until interrupted
cargo +nightly fuzz run parse_input

# Cap memory (cargo fuzz builds with ASAN by default, which catches memory bugs in unsafe code)
cargo +nightly fuzz run parse_input -- -rss_limit_mb=4096

# Minimize a crashing input
cargo +nightly fuzz tmin parse_input artifacts/parse_input/crash-xxxxx
```

### Fuzz + Miri Pipeline

When the fuzzer finds a crashing input:
1. Minimize it with `cargo fuzz tmin`.
2. Add it as a regression test.
3. Run the regression test under Miri to classify whether it is a panic (safe) or UB (must fix).

```bash
# After adding the input as a test case:
cargo +nightly miri test -- test_fuzz_regression_001
```

---

Tool selection by code type lives in [README.md](README.md) under "Tool Selection".

## The One Rule

> **When in doubt, run Miri.** If Miri cannot run it, write a version it can run, and test that under Miri. Then test the real version under sanitizers. Never ship `unsafe` code that has not passed Miri.
