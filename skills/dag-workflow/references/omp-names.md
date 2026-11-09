---
description: "The agent, tool and eval-helper names omp 18.18.1 provides, read from its package source, and the names from other hosts that this skill must not use. tools/check-skills.py reads this file (rule OMP-NAME)."
---

# omp names

> Read this when you name an agent, tool or eval helper in this skill or in a node prompt. Paths are relative to the `@oh-my-pi/pi-coding-agent` package.

The pack checker treats the first backticked name of each row below as the list: `## Agents`, `## Tools` and `## Eval helpers` are allowed, `## Not on omp` is refused anywhere else in this skill.

## Agents

omp has bundled agents and no categories: the `task` tool and `agent()` pick one of these by name (`src/task/agents.ts`, `EMBEDDED_AGENT_DEFS`).

| name | use it for | source |
| --- | --- | --- |
| `task` | the default worker: a change and its proof, a fix, a commit node | `src/task/agents.ts` |
| `sonic` | strictly mechanical edits or data collection on the small model | `src/task/agents.ts` |
| `scout` | read-only investigation: collection, research angles, the small-work analysis node | `src/prompts/agents/scout.md` |
| `reviewer` | the review node of every DAG and the PR review rounds | `src/prompts/agents/reviewer.md` |
| `security-reviewer` | review of anything touching security | `src/prompts/agents/security-reviewer.md` |
| `seance` | questions to an earlier session's transcript | `src/prompts/agents/seance.md` |

## Tools

Always-on builtins are in `src/tools/builtin-names.ts` (`BUILTIN_TOOL_NAMES`, hidden ones in `HIDDEN_TOOL_NAMES`); `browser` and `computer` are registered when enabled.

| name | kind |
| --- | --- |
| `read` | builtin |
| `bash` | builtin |
| `edit` | builtin |
| `write` | builtin |
| `glob` | builtin |
| `grep` | builtin |
| `find` | builtin |
| `ast_grep` | builtin |
| `ast_edit` | builtin |
| `lsp` | builtin |
| `eval` | builtin |
| `task` | builtin |
| `wait` | builtin |
| `todo` | builtin |
| `ask` | builtin |
| `debug` | builtin |
| `ida` | builtin |
| `github` | builtin |
| `web_search` | builtin |
| `security_scan` | builtin |
| `checkpoint` | builtin: a context checkpoint, rewound with `rewind`; not a run journal |
| `rewind` | builtin |
| `context_notes` | builtin |
| `new_context` | builtin |
| `memory_edit` | builtin |
| `retain` | builtin |
| `recall` | builtin |
| `reflect` | builtin |
| `learn` | builtin |
| `manage_skill` | builtin |
| `goal` | hidden: create, get, resume, complete, drop; one goal at a time |
| `yield` | hidden |
| `think` | hidden |
| `browser` | conditional |
| `computer` | conditional |

## Eval helpers

Inside the `eval` tool (`src/prompts/tools/eval-agents.md`, `src/prompts/tools/eval-helpers.md`).

| name | what it does |
| --- | --- |
| `agent()` | starts one background node and returns a handle: `.wait()`, `.send()`, `.cancel()`, `.status()`, `.output()` |
| `workpool()` | a keep-alive pool for a batch of independent items; the first full drain closes it |
| `wait()` | the kernel barrier over a list of handles; `raiseErrors: false` keeps a failure in its slot |
| `tool()` | defines a tool a node can call back into the kernel |

## Not on omp

Names from other hosts. Each row says what to use instead. `anywhere` names fail wherever they appear; `quoted` names are ordinary words and fail only inside backticks or quotes.

| name | use instead | match |
| --- | --- | --- |
| `ultrabrain` | `reviewer` | anywhere |
| `oracle` | `reviewer` | `quoted` |
| `explore` | `scout` | `quoted` |
| `librarian` | `scout` | `quoted` |
| `deep-low` | `task` | anywhere |
| `deep-high` | `task` | anywhere |
| `unspecified-low` | `task` | anywhere |
| `unspecified-high` | `task` | anywhere |
| `visual-engineering` | `task` with the `frontend` skill | anywhere |
| `artistry` | `task` | `quoted` |
| `plan-reviewer` | `reviewer` | anywhere |
| `omo-native-gate-reviewer` | `reviewer` | anywhere |
| `mass-ulw` | a DAG of `agent()` nodes in `eval` (`references/graph-runs.md`) | anywhere |
| `ulw-loop` | the one `goal` plus `todo` phases (`references/graph-runs.md`) | anywhere |
| `ulw-plan` | a `reviewer` node on the plan | anywhere |
| `ulw-research` | `scout` nodes plus a review node | anywhere |
| `hyperplan` | a `reviewer` node on the plan | anywhere |
| `review-work` | `reviewer` | anywhere |
| `subagent_type` | the `agent` option of `agent()` or of a `task` item | anywhere |
| `load_skills` | name the skill in the node prompt | anywhere |
| `team_create` | one DAG; steer a node with `.send()` | anywhere |
| `parallel()` | `agent()` handles plus `wait()` | anywhere |
| `pipeline()` | waves of `agent()` handles, one `wait()` per wave | anywhere |
