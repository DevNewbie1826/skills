# Strict `.golangci.yml` (golangci-lint v2)

> Read this when configuring or interpreting strict Go linting.

The single source of truth for "is this Go code acceptable". Drop this in unmodified. **Every linter below is enabled deliberately — read the rationale before disabling one.**

`golangci-lint` v2 changed config schema (top-level `version: "2"`). All v1 configs are incompatible. The block below is v2.

## `.golangci.yml`

```yaml
version: "2"

run:
  timeout: 5m
  tests: true
  modules-download-mode: readonly

linters:
  default: none
  enable:
    # ── Correctness — bug catchers ───────────────────────────────
    - govet              # stdlib vet, includes shadow, fieldalignment, nilness
    - staticcheck        # SA1*-SA9* — the de facto Go correctness linter
    - errcheck           # unhandled errors. ZERO tolerance.
    - errorlint          # %w wrapping, errors.As vs type-assertion, errors.Is vs ==
    - nilerr             # `return nil` after `err != nil` — classic bug
    - nilnil             # returning `(nil, nil)` from a (*T, error) function
    - bodyclose          # http.Response.Body not closed
    - rowserrcheck       # sql.Rows.Err() not checked
    - sqlclosecheck      # sql.Rows / sql.Stmt not closed
    - contextcheck       # functions taking context.Context don't get context.Background()
    - fatcontext         # context.WithValue() in a loop — leaks
    - copyloopvar        # Go 1.22 loop-var capture — should now use the new semantics
    - intrange           # use `for i := range N` (Go 1.22+) instead of `for i := 0; i < N; i++`
    - usetesting         # use t.TempDir/t.Setenv over os.* in tests
    - testifylint        # require vs assert correctness, ObjectsAreEqual misuse

    # ── Style / readability — kept narrow to avoid bikeshedding ─
    - gofumpt            # stricter gofmt
    - goimports          # import grouping + local prefix
    - whitespace         # leading/trailing whitespace
    - misspell           # typos in comments and strings
    - unconvert          # redundant type conversions
    - unparam            # unused function parameters
    - ineffassign        # ineffective assignments
    - dupword            # duplicate words ("the the")

    # ── Architecture — file size, complexity, dead code ─────────
    - gocognit           # cognitive complexity per function (threshold 25)
    - gocyclo            # cyclomatic complexity per function (threshold 15)
    - funlen             # function length (90 lines, 60 statements)
    - lll                # line length 120
    - nestif             # excessive nesting depth (>4)
    - dupl               # duplicate code blocks
    - revive             # extensible replacement for golint; selected rules below
    - unused             # unused vars/funcs/types

    # ── Exhaustiveness — Go's weakest spot ──────────────────────
    - exhaustive         # type switch and enum-like const groups completeness

    # ── Security ────────────────────────────────────────────────
    - gosec              # CWE-aware security scanner

    # ── Logging ─────────────────────────────────────────────────
    - sloglint           # slog attr-only style, no mixed args; enforce structured logs

    # ── Performance ─────────────────────────────────────────────
    - perfsprint         # fmt.Sprintf where strconv suffices
    - prealloc           # slice prealloc when length is known
    - makezero           # make([]T, n) with non-zero n then append (the classic bug)

linters-settings:
  errcheck:
    check-type-assertions: true
    check-blank: true     # `_ = err` is a violation

  govet:
    enable-all: true
    settings:
      shadow:
        strict: true
      fieldalignment:
        # On by default; this catches struct layouts wasting memory.
        # Disable per-file with //nolint:fieldalignment ONLY for boundary types
        # whose JSON tag order matters for OpenAPI doc stability.

  errorlint:
    errorf: true          # %w mandatory for wrapping
    asserts: true         # errors.As over type-assertion on `error`
    comparison: true      # errors.Is over ==

  gocognit:
    min-complexity: 25

  gocyclo:
    min-complexity: 15

  funlen:
    lines: 90
    statements: 60
    ignore-comments: true

  lll:
    line-length: 120
    tab-width: 4

  nestif:
    min-complexity: 4

  exhaustive:
    default-signifies-exhaustive: false
    check:
      - switch
      - map

  gosec:
    excludes:
      - G104        # handled by errcheck/errorlint
      - G304        # file path provided as input — too noisy for CLIs

  sloglint:
    no-mixed-args: true       # all attr or all key-value, never mixed
    kv-only: false
    attr-only: true           # force slog.String(...) form
    no-global: all            # disallow slog.Info; force a logger receiver
    context: scope            # require *Context variants where ctx is in scope
    static-msg: true          # msg must be a string literal (not fmt.Sprintf)
    no-raw-keys: true         # use slog.String("key", ...) not raw "key", "val"
    key-naming-case: snake

  testifylint:
    enable-all: true
    disable:
      - require-error          # We DO use assert.Error in table-driven loops

  revive:
    severity: warning
    rules:
      - name: var-naming
      - name: package-comments
      - name: exported
      - name: error-return
      - name: error-naming
      - name: errorf            # use fmt.Errorf instead of errors.New(fmt.Sprintf)
      - name: if-return
      - name: indent-error-flow
      - name: range-val-in-closure
      - name: redefines-builtin-id
      - name: superfluous-else
      - name: unhandled-error
        arguments:
          - "fmt.Print.*"
          - "fmt.Fprint.*"

  perfsprint:
    integer-format: true
    error-format: true
    bool-format: true
    string-format: true

  goimports:
    local-prefixes:
      - github.com/your-org

issues:
  max-issues-per-linter: 0
  max-same-issues: 0
  exclude-rules:
    # Tests get a longer leash on funlen + lll
    - path: _test\.go
      linters:
        - funlen
        - lll
        - dupl
        - gosec
    # Generated code never lints
    - path: \.pb\.go$
      linters: [all]
    - path: \.connect\.go$
      linters: [all]
    - path: ^.*sqlc/.*\.sql\.go$
      linters: [all]

formatters:
  enable:
    - gofumpt
    - goimports
```

## Rationale for the less obvious linters

The config comments explain each linter. Two need more:

| Linter | What it catches | Why no compromise |
|---|---|---|
| `govet/fieldalignment` | Struct field order wasting memory | Cheap correctness signal. Disable per-file when JSON tag order matters for OpenAPI. |
| `gocognit` / `gocyclo` / `funlen` | Functions exceeding cognitive thresholds | Direct architectural signal — same purpose as the 250 LOC ceiling, at function granularity. |

## `nolint` policy

`//nolint:linter1,linter2 // <reason>` is permitted with **two hard rules**:

1. **One linter at a time per directive.** No `//nolint:all`. No omitting the linter name.
2. **A reason after `//` is mandatory.** "Generated code", "false positive — protobuf imports", "OpenAPI field order" are acceptable. "Ignore" is not.

The skill auto-rejects `//nolint` without a reason. So does `revive` if you enable its `nolint` rule.

## Toolchain policy

| Category | Use | Never |
|---|---|---|
| Go version | **1.23+** (range-over-func, iter package, slog stable) | <1.23 |
| Module | `go modules` + `go work` for monorepos | dep, GOPATH layouts |
| Format | **`gofumpt`** (stricter gofmt) + `goimports -local <module>` | bare `gofmt` |
| Linter | **`golangci-lint v2`** with the strict bundle in `golangci-strict.md` | bare `go vet` |
| Nil checker | **`nilaway`** (Uber, stable since 2024) in CI | hope |
| Vet bundle | `go vet` + `fieldalignment` + `shadow` | "tests cover it" |
| Tests | `go test -race -shuffle=on -count=1` | `-count` cache, no race |
| Goroutine leaks | `go.uber.org/goleak` in `TestMain` | "looks fine" |
| Mock | `go.uber.org/mock` (gomock successor) | hand-written stubs |
| DB | `sqlc` + `jackc/pgx/v5` | `database/sql` + `gorm` |
| HTTP framework lane | Choose `gin-gonic/gin` for its full framework ecosystem, `go-chi/chi` for minimal `net/http` composition, or `connectrpc/connect-go` for RPC; see `libraries.md` for trade-offs | Picking by habit instead of service constraints |
| RPC | **`connectrpc/connect-go`** (gRPC-compatible, HTTP/1.1-friendly, browser-friendly) | hand-rolled `grpc-go` unless you specifically need bidi streaming features Connect lacks |
| Validation | `go-playground/validator/v10` for HTTP boundary + `bufbuild/protovalidate-go` for proto + smart constructors for domain | ad-hoc `if len(s) == 0` chains |
| Config | `caarlos0/env/v11` (struct-tag env) | `viper` unless you actually need file+env+flag merging |
| Logging | **`log/slog`** (stdlib, Go 1.21+) | logrus, zap, zerolog (all superseded) |
| CLI | `spf13/cobra` | hand-rolled `os.Args` parsing past 2 flags |
| TUI | `charm.land/bubbletea/v2` + `bubbles/v2` + `lipgloss/v2` — see `bubbletea-v2.md` for CJK/IME | bubbletea v1 for CJK input |

## CI gate

This is the single gate; [`bootstrap.md`](bootstrap.md) wires it into CI.

```bash
gofumpt -l . | (! grep .)                          # format
golangci-lint run --timeout 5m ./...                # everything above
go vet -vettool=$(which fieldalignment) ./...       # extra check (also in govet)
nilaway ./...                                       # nil-deref static analysis
go test -race -shuffle=on -count=1 ./...            # races + ordering
```

Any non-zero exit = the change does not ship.

## Sources

- golangci-lint v2 docs: https://golangci-lint.run/docs/configuration/
- staticcheck rules: https://staticcheck.dev/docs/checks
- sloglint: https://github.com/go-simpler/sloglint
- exhaustive: https://github.com/nishanths/exhaustive
- nilaway: https://github.com/uber-go/nilaway
