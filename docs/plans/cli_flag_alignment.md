# Plan: CLI Flag Alignment

## Objective
Add missing CLI flags to the `Ludusavi` class to match the latest Ludusavi CLI capabilities (v0.31.0+).

## Changes

### 1. `Ludusavi.backup()`
- Add `no_force_cloud_conflict: bool = False` to arguments.
- Pass `--no-force-cloud-conflict` to the executor if enabled.

### 2. `Ludusavi.restore()`
- Add `no_force_cloud_conflict: bool = False` to arguments.
- Pass `--no-force-cloud-conflict` to the executor if enabled.

### 3. `Ludusavi.config_show()`
- Add `default: bool = False` to arguments.
- Pass `--default` to the executor if enabled.

## Verification
- Add test cases to `tests/test_main.py` (or existing integration tests) to verify these flags result in the correct command arguments.
- Run `ruff` and `ty` check.
