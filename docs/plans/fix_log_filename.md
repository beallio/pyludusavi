# Plan - Fix Log Filename

Correct the Ludusavi log filename from `ludusavi.log` to `ludusavi_rCURRENT.log`.

## Problem Definition
The current implementation of `Ludusavi.log_show()` looks for a file named `ludusavi.log`. However, the correct filename is `ludusavi_rCURRENT.log`.

## Architecture Overview
- Modify `Ludusavi.log_show()` in `src/pyludusavi/main.py`.
- Update docstrings and comments.

## Core Data Structures
N/A

## Public Interfaces
- `Ludusavi.log_show()` behavior remains the same (returns file content or empty string), but looks at a different file.

## Dependency Requirements
None.

## Testing Strategy
- Create a new test case in `tests/test_log.py` that specifically verifies the filename being opened.
- Run all tests to ensure no regressions.
