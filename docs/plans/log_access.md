# Plan: Add Log Access Functions

Add two new functions to the `Ludusavi` class to provide access to Ludusavi's internal logs.

## Problem Definition
Users need a programmatic way to locate Ludusavi's log directory and read the current log file's contents for debugging or monitoring purposes.

## Architecture Overview
The functions will be added to the `Ludusavi` class in `src/pyludusavi/main.py`. Since Ludusavi stores its logs in the same directory as its configuration file (`config.yaml`), we can leverage the existing `config_path()` method to determine the base directory.

## Core Data Structures
- `log_dir()`: Returns a `str` path.
- `log_show()`: Returns the `str` content of the current log file.

## Public Interfaces
### `Ludusavi.log_dir()`
- **Returns**: `str` - The absolute path to the directory containing Ludusavi logs.
- **Implementation**: Uses `self.config_path()` and `os.path.dirname()` to find the directory.

### `Ludusavi.log_show()`
- **Returns**: `str` - The contents of the `ludusavi.log` file.
- **Implementation**: Reads the file located at `os.path.join(self.log_dir(), "ludusavi.log")`.

## Dependency Requirements
- `os`: Standard library for path manipulation.

## Implementation Steps
1. **Research**: Confirm log file names and rotation patterns (e.g., `ludusavi.log`).
2. **Implementation**:
    - Update `src/pyludusavi/main.py` to add `log_dir()`.
    - Update `src/pyludusavi/main.py` to add `log_show()`.
3. **Verification**:
    - Add unit tests in `tests/test_main.py` mocking the filesystem and `config_path()`.

## Testing Strategy
- **Unit Tests**: Mock `open()` and `os.path.exists()` to verify that `log_show()` correctly reads the file and `log_dir()` correctly parses the config path.
- **Error Handling**: Handle cases where the log file does not exist (return empty string or raise specific error).
