# Designpowers Bundling Evidence

Read this when verifying that the bundled designpowers reference corpus is present and neutralized for this skill pack.

The `vendor/` directory contains role and skill reference material used only as design-process input. The portability pass intentionally adapts metadata and wording, so byte-for-byte upstream comparisons are not a valid integrity check here.

## Portable checks

Run from `references/designpowers/`:

```sh
find vendor/skills -mindepth 1 -maxdepth 1 -type d | wc -l
find vendor/skills -name reference.md | wc -l
find vendor/agents -maxdepth 1 -type f -name '*.md' | wc -l
```

The bundled corpus should contain 27 skill reference files and 10 role-reference files.

## Integration-boundary checks

The material is reference-only. Verify that no hooks, scripts, hidden state directories, or runtime-specific configuration are bundled:

```sh
find vendor \( -path '*/hooks/*' -o -path '*/scripts/*' -o -path '*/.github/*' \) -print
```

The command should produce no paths.

## Content checks

- Role files are prompt perspectives, not runtime declarations.
- Skill references do not create schedulers, bridge tooling, or automatic execution paths.
- Materialized references remain subordinate to `frontend`, project rules, and user instructions.
- License notices in `vendor/LICENSE` remain available with the bundled material.
