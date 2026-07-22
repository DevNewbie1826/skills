# Bundled Script Dependencies

This file declares the non-standard-library packages imported by bundled scripts. Install only the dependencies for the script you intend to run. Shell scripts and standard-library-only Python scripts need no package installation.

## `scripts/go/check-no-excuse-rules.sh`

**Third-party packages:** none. Run with a POSIX-compatible Bash environment; the checker inspects Go source text and does not import a package.

## `scripts/go/new-project.py`

**Third-party packages:** `typer`, `rich`.

**Install:** `python3 -m pip install typer rich` or `uv add typer rich`.

## `scripts/python/check-no-excuse-rules.py`

**Third-party packages:** none. It requires Python 3.9+ and the standard library only.

## `scripts/python/new-project.py`

**Third-party packages:** none. The script uses the standard library, prefers `uv` when available, and otherwise creates `.venv` and invokes pip directly.

**Install:** none for the script itself; install `uv` for the primary path or use its built-in Python and pip fallback.

## `scripts/python/new-script.py`

**Third-party packages:** none. The generator uses the standard library and can run with `python3` or `uv`.

**Generated-script runners:** the default header names `uv` and other PEP 723 runners such as `pipx run`; `--plain` emits a `python3` shebang for manually managed dependencies.

## `scripts/rust/check-no-excuse-rules.py`

**Third-party packages:** none. It uses the Python standard library only.

## `scripts/rust/check-no-excuse-rules.sh`

**Third-party packages:** none. Run it with Bash against Rust source files.

## `scripts/rust/new-project.py`

**Third-party packages:** `typer`, `rich`.

**Install:** `python3 -m pip install typer rich` or `uv add typer rich`.

## `scripts/typescript/check-no-excuse-rules.ts`

**Third-party packages:** `typescript`.

**Install:** `npm install typescript@^5` or `bun add typescript@^5` — TypeScript 7+ removed the programmatic API (`ts.createSourceFile`, `ts.ScriptTarget`) this script uses; the 5.x line of `typescript` is required.

**Run:** invoke with Bun or another TypeScript runner that resolves the installed package.

## `scripts/typescript/new-project.ts`

**Third-party packages:** none for the generator itself. The generated Bun template uses `hono`; the generated Node template also uses `@hono/node-server`, `tsx`, and `@types/node`.

**Install:** run `bun install` for the default Bun template or `npm install` for `--runtime node`; generated `package.json` declares the required packages.

**Run:** invoke the generator with Node 22+, Bun, or tsx; it uses only Node-compatible runtime APIs. `--runtime bun` is the default and `--runtime node` emits npm and Node scripts.
