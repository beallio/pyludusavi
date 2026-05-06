# Plan: Ludusavi Python Wrapper (Final Contract)

This plan defines the implementation of a robust, Linux-only Python wrapper for Ludusavi (Targeting v0.31.0+).

## Phase 0: Environment & Discovery Contract

- **Task 0.1: Discovery & Base Command**
    - Implement `find_ludusavi()` returning a `list[str]` (the "Command Prefix").
    - Precedence: `Explicit Path` -> `PATH Lookup` -> `Flatpak ID`.
    - Example Output: `["/usr/bin/ludusavi"]` or `["flatpak", "run", "com.github.mtkennerly.ludusavi"]`.
    - Validation: Confirm existence via `prefix + ["--version"]`.
- **Task 0.2: Enforcement Tooling**
    - Implement `.pre-commit-config.yaml` running `ruff` and `pytest`.
    - Update `scripts/check_tdd.sh` to fail if a new method is added to `src/` without a corresponding `test_` file/case.

## Phase 1: Execution Surface Mapping

- **Task 1.1: Command Descriptor Table**
    | Method | CLI Subcommand | Execution Mode | Output Type |
    | :--- | :--- | :--- | :--- |
    | `manifest_update()` | `manifest update` | `JSON` | `dict` |
    | `backup()` | `backup` | `JSON` | `dict` |
    | `restore()` | `restore` | `JSON` | `dict` |
    | `find()` | `find` | `JSON` | `dict` |
    | `bulk_api()` | `api` | `STDIN_JSON` | `dict` |
    | `schema()` | `schema` | `TEXT` | `str/dict` |
    | `complete()` | `complete` | `TEXT` | `str` |
    | `version()` | `--version` | `TEXT` | `str` |
    | `open_gui()` | `gui` | `SPAWN` | `None` |

## Phase 2: The Execution Engine (`_execute`)

- **Task 2.1: Multi-Mode Executor**
    - Create a unified `_execute(args, mode, timeout, env)` method.
    - **Modes**:
        - `JSON`: Captures stdout, parses JSON, handles `LudusaviContractError` on malformed output.
        - `TEXT`: Returns raw `stdout` string.
        - `STDIN_JSON`: Streams `input_data` to `stdin`.
        - `SPAWN`: Uses `subprocess.Popen` for non-blocking GUI launch.
- **Task 2.2: Public Subprocess Contract**
    - Every public method will accept an optional `timeout: float | None` and `env: dict | None`.
    - Default timeout: 30s (Metadata) / `None` (Operations).
    - `stderr` handling: Captured into `LudusaviResponse.warnings` unless `returncode != 0`.

## Phase 3: Typed Models (Hybrid Policy)

- **Task 3.1: Stable Envelope vs. Volatile Payload**
    - **Stable Models**: (e.g., `ResponseEnvelope`) will be strict (all top-level fields required).
    - **Volatile Payloads**: (e.g., `GameResult`) will use `total=False` to handle upstream drift.
    - Implementation: Use `typing.TypedDict` and `typing.Annotated`.

## Phase 4: Implementation & Verification

- **Task 4.1: Implementation of Core API**
    - Build out the `Ludusavi` class using the engine from Phase 2.
- **Task 4.2: Argument Builder Engine**
    - Logic for repeated flags (`--game`), mutually exclusive flags, and positional args (`--`).
- **Task 4.3: QA & TDD**
    - **Discovery**: Verify `argv` construction for both Binary and Flatpak.
    - **Error Mapping**: Test `LudusaviExecutionError` (exit code) vs `LudusaviContractError` (parse failure).
    - **Timeouts**: Verify cancellation signals for long-running backup jobs.

## Phase 5: Documentation & Finalization

- **Task 5.1: Manual README & Examples**.
- **Task 5.2: Agent Session Log**.
