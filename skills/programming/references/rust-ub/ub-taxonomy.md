# Rust Undefined Behavior Taxonomy

> Read this when classifying a suspected Rust undefined-behavior finding before fixing it.

Every category of UB that the Rust compiler, Miri, and the language specification recognize. The agent must know the full surface to hunt systematically. Each entry names the UB class, its root cause, canonical trigger, Miri detection status, and the canonical fix.

## 1. Aliasing Violations (Stacked Borrows / Tree Borrows)

**Root cause:** Two pointers access the same memory in ways that violate Rust's borrowing model — even through raw pointers inside `unsafe`.

**Canonical triggers:**
- Creating a `&mut T` while another `&T` or `&mut T` to the same location exists.
- Dereferencing a raw pointer derived from a reference after that reference was invalidated (e.g., `&mut` was retaken).
- Calling `slice::from_raw_parts_mut` on overlapping regions.
- Interior mutability through `UnsafeCell` without going through the `UnsafeCell` API.
- Casting `&T` to `*mut T` and writing through it (even via FFI).

**Miri detection:** YES — Stacked Borrows is the default model. Tree Borrows (`-Zmiri-tree-borrows`) is the newer, more permissive model. Run both. The models disagree in both directions: Stacked Borrows rejects most reborrow patterns Tree Borrows accepts, and Tree Borrows rejects some code Stacked Borrows accepts. Treat a failure under either model as UB and fix the code until both pass.

**Fix pattern:** Use `UnsafeCell` for all interior mutability, or restructure so no raw pointer is created or used across a `&mut` borrow. Never cast `&T` to `*mut T`. Derive mutable pointers from `*mut T` obtained via `UnsafeCell::get()` or `addr_of_mut!()`.

---

## 2. Data Races

**Root cause:** Two threads access the same non-atomic memory location, at least one is a write, and there is no happens-before ordering between them.

**Canonical triggers:**
- `unsafe impl Send for T` on a type containing `*mut U` without synchronization.
- `unsafe impl Sync for T` on a type containing `Cell<T>` or `UnsafeCell<T>` without a lock.
- Using `std::ptr::write` from multiple threads to the same allocation.
- Shared `&T` where `T` has interior mutability but no atomic/lock guard.

**Miri detection:** YES — Miri's data-race detector is on by default. It detects races on non-atomic accesses. Preemptive scheduling stress is a flag (see the preemption-rate section of [miri-sanitizers-loom.md](miri-sanitizers-loom.md)).

**Complementary tools:** `loom` for exhaustive interleaving exploration on lock-free algorithms. ThreadSanitizer (TSAN) for integration tests Miri cannot run (I/O, FFI).

**Fix pattern:** Wrap in `Mutex`/`RwLock`/`AtomicXxx`. Never `unsafe impl Sync` unless you can name the synchronization primitive guarding every mutable field.

---

## 3. Use After Free / Dangling Pointers

**Root cause:** A pointer or reference outlives the allocation it points to.

**Canonical triggers:**
- Returning a reference to a local variable (compiler catches most, but raw pointers escape).
- `Box::into_raw` → manual `Box::from_raw` with wrong lifetime.
- `Vec` reallocation invalidating raw pointers obtained from `as_ptr()` / `as_mut_ptr()`.
- `Pin<Box<T>>` unpinned and moved after self-referential pointers were set up.

**Miri detection:** YES — allocation tracking catches use-after-free on the exact operation.

**Fix pattern:** Borrow checker for references. For raw pointers: tie pointer validity to an explicit lifetime via a `PhantomData<&'a T>` in the wrapper, or use arena allocation (`bumpalo`) so all pointers share one lifetime.

---

## 4. Uninitialized Memory

**Root cause:** Reading a value from memory that was never written to.

**Canonical triggers:**
- `MaybeUninit::assume_init()` before all bytes are written.
- `mem::uninitialized()` (deprecated, still compiles).
- `alloc::alloc(layout)` returns uninitialized memory — reading it before writing is UB.
- Padding bytes in structs read via `transmute` or raw pointer casts.
- `read_unaligned` on uninitialized memory.

**Miri detection:** YES — tracks initialization state per byte. Catches partial-init structs, padding reads, and premature `assume_init`.

**Fix pattern:** Replace `mem::uninitialized()` with `MaybeUninit::uninit()` + `write()` + `assume_init()`. Use `MaybeUninit::zeroed()` when zero-init is acceptable. Write every field before calling `assume_init()`. Use `MaybeUninit::write()` instead of raw pointer writes. Never `transmute` structs with padding unless you zeroed the padding.

---

## 5. Invalid Values (Type Invariant Violations)

**Root cause:** Producing a value that violates the type's validity invariant.

**Canonical triggers:**
- `bool` not 0 or 1.
- `char` outside Unicode scalar range.
- Enum discriminant not matching any variant.
- `NonZeroU32` containing 0.
- `&T` or `&mut T` that is null or dangling.
- `str` containing non-UTF-8 bytes.
- `fn` pointer that is null.

**Miri detection:** YES — validity checks are on by default.

**Fix pattern:** Validate before transmuting. Use `TryFrom` at boundaries. Never `transmute` to enum types — use a checked conversion function.

---

## 6. Misaligned Pointer Access

**Root cause:** Dereferencing a pointer that is not aligned to the type's required alignment.

**Canonical triggers:**
- Casting `*const u8` to `*const u64` and dereferencing (alignment goes from 1 to 8).
- References to fields of a `#[repr(packed)]` struct (the compiler warns, but raw pointers bypass the warning).
- Network buffer parsing where offsets are arbitrary.

**Miri detection:** YES — immediate trap on misaligned read/write.

**Fix pattern:** Use `read_unaligned` / `write_unaligned` for packed data. Use `bytemuck` or `zerocopy` for safe reinterpretation with alignment checks.

---

## 7. Violating `Pin` Invariants

**Root cause:** Moving a value that was pinned and relied on its address stability (self-referential types, intrusive linked lists).

**Canonical triggers:**
- `mem::swap` on a `Pin<&mut T>` after `unsafe` deref.
- Implementing `Unpin` for a type that contains self-referential pointers.
- Manually calling `Pin::new_unchecked` on a movable allocation.

**Miri detection:** PARTIAL — Miri detects the resulting aliasing/use-after-free if the self-referential pointer is actually used. It does not detect "Pin contract violated but pointer was never dereferenced."

**Fix pattern:** Never `impl Unpin` for self-referential types. Use `pin_project` or `pin_project_lite` for safe pin projections. Review every `Pin::new_unchecked` call.

---

## 8. FFI Boundary UB

**Root cause:** Mismatch between Rust's ABI expectations and the foreign code's actual behavior.

**Canonical triggers:**
- C function returning uninitialized memory into a Rust `&T`.
- Wrong `#[repr(C)]` layout (padding differs between platforms).
- Passing a Rust `enum` to C without `#[repr(C)]` or `#[repr(i32)]`.
- Null pointer passed where C expects non-null (and Rust wraps it in `&T`).
- C code writing to Rust-owned memory through a pointer Rust considers immutable.
- Declaring a foreign function as `safe fn` inside `unsafe extern` when it has caller preconditions (null, length, lifetime), so safe code can violate them.

**Miri detection:** LIMITED — Miri cannot execute foreign code. It detects UB in the Rust-side handling of FFI return values.

**Complementary tools:** AddressSanitizer (ASAN), MemorySanitizer (MSAN) for detecting actual FFI-side corruption. Valgrind as a last resort.

**Fix pattern:** Validate every FFI return at the boundary. Use `Option<NonNull<T>>` for nullable pointers (`NonNull::new(raw).ok_or(Error::NullFromFfi)?`). Use `CStr`/`CString` for strings. Add `cbindgen` to CI to verify layout agreement. Wrap every FFI call in a safe Rust function that checks preconditions.

---

## 9. Incorrect `Send` / `Sync` Implementations

**Root cause:** Manually implementing `Send` or `Sync` for a type that does not actually uphold the required invariant.

**Canonical triggers:**
- `unsafe impl Send for Wrapper(*mut T)` when `T` is not `Send`.
- `unsafe impl Sync for Wrapper(UnsafeCell<T>)` without a lock, atomic, or other synchronization.
- Types containing `Rc<T>` with a manual `Send` impl (Rc is not `Send`: the auto trait is derived as negative).

**Miri detection:** YES for the *resulting* data race if exercised. Miri's data-race detector will fire when two threads access the same location unsynchronized.

**Fix pattern:** Never manually implement `Send`/`Sync` unless you can write a SAFETY proof naming the synchronization mechanism (for example, the `Mutex` guarding the only non-`Send` field). Use `PhantomData<*const ()>` to opt-out of auto-`Send`/`Sync` when in doubt.

---

## 10. Out-of-Bounds Memory Access

**Root cause:** Pointer arithmetic or indexing that escapes the allocation.

**Canonical triggers:**
- `ptr.offset(n)` where `n` exceeds the allocation size.
- `slice::from_raw_parts(ptr, len)` where `len` is too large.
- Off-by-one in manual buffer management.
- Integer overflow in size calculations leading to undersized allocation.

**Miri detection:** YES — allocation-precise bounds checking.

**Fix pattern:** Use checked arithmetic (`checked_add`, `checked_mul`) for size calculations. Use `slice::from_raw_parts` only with validated lengths. Prefer safe indexing (`get()`, iterators) over raw pointer arithmetic.

---

## 11. Provenance Violations

**Root cause:** Using a pointer whose provenance does not grant access to the target memory, even if the address is numerically correct.

**Canonical triggers:**
- Casting an integer to a pointer and dereferencing it (`addr as *const T`).
- Roundtripping a pointer through `usize` and back (`ptr as usize as *const T`) — the provenance is lost.
- Using `ptr::with_exposed_provenance` on an address that was never exposed with `ptr.expose_provenance()`.

**Miri detection:** YES with strict provenance.

**Fix pattern:** Use `ptr::with_exposed_provenance` / `ptr.expose_provenance()` for legitimate int-to-ptr roundtrips. Avoid `as usize as *const T` entirely. These APIs are stable since Rust 1.84; the `sptr` crate provides them on older toolchains.

---

## 12. Double Free / Invalid Free

**Root cause:** Freeing the same allocation twice, or freeing memory not obtained from the allocator.

**Canonical triggers:**
- `Box::from_raw` called twice on the same pointer.
- Manual `dealloc` on a pointer already freed.
- `ManuallyDrop` dropped explicitly then the outer type also drops it.

**Miri detection:** YES — immediate trap.

**Fix pattern:** Enforce single ownership via RAII. Use `ManuallyDrop` with extreme care — document who is responsible for the drop. Never clone a raw pointer and `Box::from_raw` both copies.

---

## 13. Library / Unsafe Contract Violations

**Root cause:** Violating the documented safety invariant of a safe or unsafe API, where the library author relied on the invariant for soundness.

**Canonical triggers:**
- `Vec::set_len(n)` where the first `n` elements are not initialized.
- `String::from_utf8_unchecked` on non-UTF-8 bytes.
- `HashMap` key mutated after insertion (breaks the hash invariant: a logic error on its own, UB once `unsafe` code relies on the invariant, and Miri may detect the downstream effects).
- `BTreeMap` key with broken `Ord` impl (the standard library assumes a total order).

**Miri detection:** PARTIAL — Miri catches the downstream UB (e.g., reading uninitialized bytes from a `Vec` with inflated len). It does not catch "you violated the documented contract" if no memory-level UB results.

**Fix pattern:** Read the `# Safety` section of every `unsafe fn` you call. Document the invariant in your SAFETY comment. When in doubt, use the safe API and pay the cost.

---

## 14. Unwinding Across `extern "C"` Boundaries

**Root cause:** A Rust panic unwinding through a frame that uses the C calling convention.

**Canonical triggers:**
- `panic!()` inside a `#[unsafe(no_mangle)] extern "C" fn` callback passed to C code.
- `unwrap()` inside FFI callbacks.
- Foreign code unwinding (C++ exceptions, `longjmp`) through a Rust frame declared `extern "C"`.

Since Rust 1.81 a Rust panic that reaches an `extern "C"` boundary aborts the process instead of unwinding into foreign frames: no longer UB, but still a crash.

**Miri detection:** PARTIAL — Miri does not model foreign unwinding, but it can detect the immediate UB if the panic reaches the FFI boundary.

**Fix pattern:** Use `std::panic::catch_unwind` at every FFI entry point and return an error code. Declare the ABI `extern "C-unwind"` (stable since 1.71) only when both sides are built to let unwinding cross.

