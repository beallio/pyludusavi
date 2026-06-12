# Custom Environment Cascade

## Problem Definition

`Ludusavi` does not expose an instance-level environment. Callers cannot pass custom
environment variables for discovery or normal command execution without dropping to the
lower-level executor API.

The lower-level executor also accepts per-call overrides, but resolving those overrides
directly against `os.environ` discards configured instance values. Environment resolution
must cascade across all three levels.

## Architecture Overview

- Add `env` to `Ludusavi(...)` and `find_ludusavi(...)`.
- Merge provided values over a copy of `os.environ`.
- Use the resolved environment for discovery verification and all instance subprocess calls.
- Preserve the lower-level executor's per-call overrides with precedence:
  process environment, instance overrides, then call overrides.

## Core Data Structures

- `Mapping[str, str]` for caller-provided overrides.
- `dict[str, str]` for the resolved subprocess environment.

## Public Interfaces

- `Ludusavi(env: Optional[Mapping[str, str]] = None)`
- `find_ludusavi(env: Optional[Mapping[str, str]] = None)`
- `LudusaviExecutor.execute(..., env: Optional[Mapping[str, str]] = None)`

## Dependency Requirements

No new dependencies are required.

## Testing Strategy

- Add red tests for discovery verification receiving the merged environment.
- Add red tests for custom `PATH` lookup using the merged environment.
- Add red tests for `Ludusavi(env=...)` forwarding the resolved environment to discovery and executor.
- Add red tests for executor `run` and `Popen` subprocess calls using the instance environment.
- Add red tests proving call overrides retain instance values and take precedence on conflicts.
- Verify environment mappings are copied instead of mutated.
- Validate with Ruff, ty, pytest, and the local pre-commit hook.
