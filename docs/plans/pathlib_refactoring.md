# Refactor Path Management to Pathlib

Refactor legacy `os.path` and string/list-based path management to use `pathlib.Path` for improved readability, maintainability, and type safety.

## Objective
- Migrate `src/pyludusavi/discovery.py` to support `pathlib.Path` in its public API.
- Refactor `src/pyludusavi/main.py` to use `pathlib.Path` for all filesystem operations (logs, config).
- Ensure consistent use of `pathlib` across the core library.

## Key Files & Context
- `src/pyludusavi/discovery.py`: Entry point for locating the Ludusavi executable.
- `src/pyludusavi/main.py`: Primary CLI wrapper class handling config and logs.
- `tests/test_discovery.py`: Unit tests for discovery logic.
- `tests/test_log.py`: Unit tests for log access.

## Implementation Steps

### Phase 1: Discovery Refactoring
1.  **Modify `src/pyludusavi/discovery.py`**:
    - Import `Path` from `pathlib`.
    - Update `find_ludusavi` signature: `explicit_path: Optional[Union[str, Path]] = None`.
    - Ensure internal verification handles `Path` objects correctly (though `subprocess` handles them natively in modern Python).

### Phase 2: Main Wrapper Refactoring
1.  **Modify `src/pyludusavi/main.py`**:
    - Import `Path` from `pathlib`.
    - Refactor `log_dir()` to use `Path(self.config_path()).parent`.
    - Refactor `log_show()` to use `/` operator for path joining and `Path.exists()`.
    - Update `add_game_alias` to use `Path` for writing the config file.

### Phase 3: Test Updates
1.  **Update `tests/test_discovery.py`**:
    - Add a test case for passing a `Path` object to `find_ludusavi`.
2.  **Update `tests/test_log.py`**:
    - Update mocks to handle `pathlib.Path` methods instead of `os.path`.

## Verification & Testing
- Run existing test suite: `./run.sh uv run pytest`
- Verify type safety: `./run.sh uv run ty check src/`
- Run linting: `./run.sh uv run ruff check .`
