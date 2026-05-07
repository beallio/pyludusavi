# Plan: Fix Review Findings

This plan covers the issues found during the code review of the `pyludusavi`
wrapper and incorporates the mandatory workflow from `AGENTS.md`.

## Problem Definition

The wrapper has several places where the public Python API does not match
Ludusavi's CLI contract or the project's own documentation:

- `wrap()` emits an invalid command because Ludusavi requires either `--name`
  or `--infer`.
- `cloud_upload()` and `cloud_download()` omit documented CLI options.
- `STDIN_JSON` mode drops valid falsey JSON payloads such as `{}`.
- The README documents explicit Flatpak app ID usage, but discovery treats
  explicit values as executable paths only.
- Some docs/spec claims are stronger than the implementation, especially
  "100% CLI Coverage" and JSON-mode claims for commands that do not expose
  `--api`.
- `add_game_alias()` rewrites `config.yaml` as JSON, which is valid YAML but
  destroys comments and formatting.
- Argument validation currently delegates mutually exclusive flag combinations
  to Ludusavi instead of failing early in Python.

## Architecture Overview

Use a contract-first Red-Green-Refactor sequence:

1. Verify repository state, dependency state, cache isolation, and execution
   mode before implementation.
2. Add focused failing tests for each reviewed behavior.
3. Run the relevant tests through `./run.sh uv run pytest` and capture the
   expected failures.
4. Implement the minimal changes needed to pass the tests.
5. Refactor only after tests pass.
6. Validate through cache-isolated project commands.
7. Update documentation and record an agent session log.
8. Commit on a feature or fix branch only after validation passes.

The work is Project Mode because this repository has `pyproject.toml`,
package code in `src/pyludusavi`, and automated tests in `tests/`.

## Core Data Structures

- `LudusaviResponse`: existing response envelope for parsed data, raw output,
  warnings, and executed command.
- `LudusaviExecutor.command_prefix`: existing command prefix used for binary
  and Flatpak execution.
- `input_data`: JSON-serializable payload for `STDIN_JSON`; should accept any
  non-`None` JSON value that Ludusavi supports.
- `wrap` options: Python keyword arguments mapped to Ludusavi's documented
  `wrap` flags in stable order.
- Cloud sync options: Python keyword arguments mapped to `cloud upload` and
  `cloud download` flags in stable order.
- Config alias entries: dictionaries in the `customGames` list with `name`,
  `alias`, `files`, `registry`, `installDir`, and `winePrefix`.

## Public Interfaces

The intended public interface changes are:

```python
Ludusavi.wrap(
    command: list[str],
    *,
    name: str | None = None,
    infer: Literal["heroic", "lutris", "steam"] | None = None,
    force: bool = False,
    force_backup: bool = False,
    force_restore: bool = False,
    no_backup: bool = False,
    no_restore: bool = False,
    no_force_cloud_conflict: bool = False,
    gui: bool = False,
    path: str | None = None,
    format: Literal["simple", "zip"] | None = None,
    compression: Literal["none", "deflate", "bzip2", "zstd"] | None = None,
    compression_level: int | None = None,
    full_limit: int | None = None,
    differential_limit: int | None = None,
    cloud_sync: bool = False,
    no_cloud_sync: bool = False,
    ask_downgrade: bool = False,
) -> LudusaviResponse
```

`wrap()` must require exactly one of `name` or `infer`.

```python
Ludusavi.cloud_upload(
    games: list[str] | None = None,
    local: str | None = None,
    cloud: str | None = None,
    force: bool = False,
    preview: bool = False,
    gui: bool = False,
) -> LudusaviResponse

Ludusavi.cloud_download(
    games: list[str] | None = None,
    local: str | None = None,
    cloud: str | None = None,
    force: bool = False,
    preview: bool = False,
    gui: bool = False,
) -> LudusaviResponse
```

Discovery should either support explicit Flatpak IDs through the existing
`explicit_path` argument or introduce a clearer `flatpak_id` constructor
argument. The implementation choice must be reflected in README examples.

## Dependency Requirements

- Use `uv` only.
- Do not use `pip install` or `python -m venv`.
- Keep generated environments and caches under `/tmp/pyludusavi`.
- Use the existing `./run.sh` wrapper for project commands because it exports:
  - `UV_PROJECT_ENVIRONMENT=/tmp/pyludusavi/.venv`
  - `XDG_CACHE_HOME=/tmp/pyludusavi/.cache`
  - `PYTHONPYCACHEPREFIX=/tmp/pyludusavi/__pycache__`
  - `TMPDIR=/tmp/pyludusavi`
- Do not add a YAML dependency for alias config handling unless Task 6.1
  explicitly chooses that route.
- Commit-time validation is handled by `.git/hooks/pre-commit`. Keep
  commits atomic so hook failures map to one coherent change.

## Testing Strategy

Follow Red-Green-Refactor. Every implementation change must have a failing test
created earlier in the session.

Primary test command:

```bash
./run.sh uv run pytest
```

Focused test commands may be used during Red and Green, for example:

```bash
./run.sh uv run pytest tests/test_executor.py
./run.sh uv run pytest tests/test_discovery.py
./run.sh uv run pytest tests/test_ludusavi_integration.py
```

Validation commands:

```bash
./run.sh uv run pytest
./run.sh uv run ruff check
./run.sh uv run ty check
```

Before commit, stage an atomic change and let `.git/hooks/pre-commit` run as
the authoritative commit-time quality gate.

## Execution Lifecycle

### Phase 0: Analyze

- [x] **Task 0.1: Review existing implementation and tests**
  - Reviewed `src/pyludusavi/core.py`, `discovery.py`, `main.py`, and current
    tests.
  - Identified command-contract and documentation mismatches.

- [x] **Task 0.2: Review `AGENTS.md`**
  - Confirmed mandatory handshake, planning, TDD, cache isolation, validation,
    commit, and session logging requirements.

### Phase 1: Plan

- [x] **Task 1.1: Create durable plan**
  - Created `docs/plans/fix_review_findings.md`.

- [x] **Task 1.2: Update plan for `AGENTS.md`**
  - Added mandatory plan sections, lifecycle gates, cache commands, validation,
    and session logging.

### Phase 2: Verify State

- [x] **Task 2.1: Verify filesystem state**
  - Project root: `/home/beallio/Dropbox/Scripts/pyludusavi`.
  - Existing files include `pyproject.toml`, `run.sh`, `src/`, `tests/`, and
    `docs/`.

- [x] **Task 2.2: Verify dependency state**
  - Dependency state is represented by `pyproject.toml` and `uv.lock`.
  - Commands must use `./run.sh` to keep caches under `/tmp/pyludusavi`.

- [x] **Task 2.3: Verify branch state**
  - Confirm current branch.
  - Created and used `fix/pyludusavi-review-findings`.

- [x] **Task 2.4: Verify commit-time validation**
  - Confirm `.git/hooks/pre-commit` exists and is executable.
  - Plan atomic commits so each hook run validates one coherent change.

### Phase 3: Test (RED)

- [x] **Task 3.1: Add executor regression tests**
  - Verify `STDIN_JSON` serializes `{}`.
  - Verify `STDIN_JSON` serializes `[]` if accepted by the type signature.
  - Verify `None` still means no stdin payload.
  - Run focused tests and confirm failures before implementation.

- [x] **Task 3.2: Add discovery regression tests**
  - Verify an explicit filesystem executable still returns `[path]`.
  - Verify an explicit Flatpak app ID returns `["flatpak", "run", app_id]`.
  - Verify a bad explicit value still raises `LudusaviNotFoundError`.
  - Run focused tests and confirm failures before implementation.

- [x] **Task 3.3: Add wrap command tests**
  - Verify `wrap(command, name="Game")` emits:
    `["wrap", "--name", "Game", "--", *command]`.
  - Verify `wrap(command, infer="steam")` emits:
    `["wrap", "--infer", "steam", "--", *command]`.
  - Verify callers cannot set both `name` and `infer`.
  - Verify callers must set at least one of `name` or `infer`.
  - Verify documented flags are included in stable order.
  - Run focused tests and confirm failures before implementation.

- [x] **Task 3.4: Add cloud command tests**
  - Verify `cloud_upload()` and `cloud_download()` support `games`.
  - Verify both support `local`, `cloud`, `force`, `preview`, and `gui`.
  - Verify option order is deterministic and games are appended after options.
  - Run focused tests and confirm failures before implementation.

- [x] **Task 3.5: Add validation tests for conflicting flags**
  - Verify `backup(cloud_sync=True, no_cloud_sync=True)` raises before
    subprocess execution.
  - Verify `restore(cloud_sync=True, no_cloud_sync=True)` raises before
    subprocess execution.
  - Verify `backups_edit(lock=True, unlock=True)` raises before subprocess
    execution.
  - Run focused tests and confirm failures before implementation.

### Phase 4: Implement (GREEN)

- [x] **Task 4.1: Fix `STDIN_JSON` serialization**
  - Change the guard in `LudusaviExecutor.execute()` from truthiness to
    `input_data is not None`.
  - Broaden the `input_data` annotation if list payloads should be accepted.
  - Run the focused executor tests.

- [x] **Task 4.2: Support explicit Flatpak IDs**
  - Detect explicit values that are not filesystem paths but look like Flatpak
    IDs.
  - Verify `flatpak` exists before returning `["flatpak", "run", app_id]`.
  - Verify the Flatpak command with `--version`.
  - Run the focused discovery tests.

- [x] **Task 4.3: Redesign `wrap()`**
  - Require exactly one of `name` or `infer`.
  - Add supported options from `docs/specs/cli_help_audit.txt`: `force`,
    `force_backup`, `force_restore`, `no_backup`, `no_restore`,
    `no_force_cloud_conflict`, `gui`, `path`, `format`, `compression`,
    `compression_level`, `full_limit`, `differential_limit`, `cloud_sync`,
    `no_cloud_sync`, and `ask_downgrade`.
  - Emit `["wrap", ...options..., "--", *command]`.
  - Run focused wrap tests.

- [x] **Task 4.4: Expand cloud upload/download APIs**
  - Add parameters: `games`, `local`, `cloud`, `force`, `preview`, and `gui`.
  - Keep mode `JSON`, which lets the executor append `--api`.
  - Append games after options.
  - Run focused cloud command tests.

- [x] **Task 4.5: Add argument validation**
  - Raise `ValueError` for mutually exclusive flags instead of delegating
    invalid calls to Ludusavi.
  - Apply validation to cloud sync flags and backup edit lock flags.
  - Run focused validation tests.

### Phase 5: Refactor

- [x] **Task 5.1: Extract command-building helpers if duplication grows**
  - Prefer small private helpers only when they reduce real duplication.
  - Keep public behavior covered by tests.

- [x] **Task 5.2: Review type annotations**
  - Keep Python 3.12-compatible annotations.
  - Avoid broadening public types beyond Ludusavi's documented contract.

### Phase 6: Alias Config Decision

- [x] **Task 6.1: Decide alias-write policy**
  - Option A: Keep standard-library-only JSON rewriting and document that
    comments/formatting are not preserved.
  - Option B: Add a YAML dependency and preserve YAML structure as much as
    practical.
  - Option C: Remove or de-emphasize `add_game_alias()` until a safer
    config-editing path exists.

- [x] **Task 6.2: Document chosen policy**
  - Kept standard-library JSON rewriting.
  - Documented that comments and formatting are not preserved.

### Phase 7: Validate

- [x] **Task 7.1: Run full test suite**
  - `./run.sh uv run pytest`

- [x] **Task 7.2: Run lint**
  - `./run.sh uv run ruff check`

- [x] **Task 7.3: Run type checks if practical**
  - `./run.sh uv run ty check`

- [x] **Task 7.4: Prepare for pre-commit validation**
  - Stage changes as atomic commits.
  - Let `.git/hooks/pre-commit` run and pass at commit time.

### Phase 8: Commit

- [x] **Task 8.1: Use an appropriate branch**
  - Use a branch such as `fix/pyludusavi-review-findings`.

- [x] **Task 8.2: Commit only after validation**
  - Use imperative commit style, for example:
    `Fix pyludusavi CLI wrapper contracts`.
  - Keep commits atomic so pre-commit failures are isolated to one coherent
    change.

### Phase 9: Document

- [x] **Task 9.1: Update README**
  - Correct explicit Flatpak app ID examples.
  - Add examples for `wrap(name=...)` and `wrap(infer=...)`.
  - Adjust "100% CLI Coverage" unless all CLI flags are actually covered.

- [x] **Task 9.2: Update compatibility policy**
  - Correct mode claims for `backups_edit()` and `wrap()` if they remain TEXT
    commands.
  - Document which commands depend on executor `auto_api`.

- [x] **Task 9.3: Record session log**
  - Add `docs/agent_conversations/YYYY-MM-DD_fix_review_findings.json`.
  - Include date, task objective, files modified, tests added, design decisions,
    and results.

## Decisions

- Added a separate `flatpak_id` constructor argument and kept `explicit_path`
  path-only.
- Kept `wrap()` in TEXT mode because the CLI help audit does not expose
  `--api` for `wrap`.
- Kept `add_game_alias()` standard-library-only and documented that it rewrites
  config as JSON without preserving comments or formatting.
