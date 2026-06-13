# Project Review Remediation — `project_review_2026_06_12`

## Problem Definition

A full review of pyludusavi found one critical bug and several functional, typing,
packaging, test-coverage, CI, and documentation issues:

- **Critical**: `wrap()` and other long-running operations (`cloud_upload`,
  `cloud_download`, `manifest_update`, `bulk_api`) inherit the executor's 30-second
  default timeout. A game wrapped via `wrap()` is killed after 30 seconds.
- No dedicated timeout exception — callers cannot distinguish a timeout from a generic
  `LudusaviError`.
- `backup()`/`restore()` do not expose the CLI's `--gui` flag.
- `backups_edit(comment="")` drops an intentional empty comment.
- `add_game_alias()` rewrites `config.yaml` on no-op calls, ignores conflicting aliases,
  and writes non-atomically (crash mid-write corrupts user config).
- No `py.typed` marker, so the "type-safe" claim is invisible to consumers.
- `LudusaviApiOutput` is `total=True` but real CLI output omits `errors`/`overall`/`cloud`.
- 15 `assert response is not None` lines exist only because `execute()` returns
  `Optional` for SPAWN mode.
- `Ludusavi.__init__` rejects `pathlib.Path` even though `find_ludusavi` accepts it.
- `_verify` catches only `FileNotFoundError`/`PermissionError`, missing other `OSError`s.
- Test gaps: timeout behavior, auto-`--api`, `manifest_update`, `cloud_set`, `complete`,
  `open_gui`; fixture loading is CWD-dependent.
- CI never runs on `dev` (only `main`).
- README omits logs, `get_game_alias`, timeouts, and the new error.

## Architecture Overview

Single-package src layout (`src/pyludusavi/`):
- `core.py` — `LudusaviExecutor` (subprocess engine), exceptions, `LudusaviResponse`.
- `main.py` — `Ludusavi` public API (one method per CLI subcommand).
- `discovery.py` — locates the binary/Flatpak.
- `_environment.py` — env override merging.
- `models.py` — `TypedDict` output models.

No new modules. Changes are localized to existing files plus a new `py.typed` marker.

## Public Interface Changes

- New exception `LudusaviTimeoutError(LudusaviError)` (exported).
- New `timeout: Optional[float] = None` kwarg on `wrap`, `cloud_upload`, `cloud_download`,
  `manifest_update`, `bulk_api`.
- New `gui: bool = False` kwarg on `backup`, `restore`.
- `Ludusavi.__init__` accepts `Union[str, Path]` for `explicit_path`, `config_dir`.
- `LudusaviApiOutput`: `errors`/`overall`/`cloud` become `NotRequired`.
- `add_game_alias` becomes idempotent and atomic (behavioral, signature unchanged).

## Testing Strategy

Strict TDD per `AGENTS.md` §9 — failing test before each change, run via
`./run.sh uv run pytest`. New/updated tests in the matching `tests/test_<module>.py`.
The `ty check src/` gate validates the typing-only changes (Tasks 7, 8). Full gate
(`ruff check`, `ruff format`, `ty check src/`, `pytest`) before every commit.

## Phases

1. Infrastructure/exceptions: Task 1.
2. Core logic fixes: Tasks 2–5, 10.
3. Typing/packaging: Tasks 6–9.
4. Tests: Task 11.
5. CI + docs: Tasks 12–14.
6. Verification + release: final gate, merge to `dev`, tag `v0.2.5`.

See the approved plan for per-task detail and the reviewer communication protocol.
