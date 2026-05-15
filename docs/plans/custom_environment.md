# Custom Environment Cascade

## Problem Definition

`Ludusavi` does not expose an instance-level environment. Callers cannot pass custom
environment variables for discovery or normal command execution without dropping to the
lower-level executor API.

## Architecture Overview

- Add `env` to `Ludusavi(...)` and `find_ludusavi(...)`.
- Merge provided values over a copy of `os.environ`.
- Use the resolved environment for discovery verification and all instance subprocess calls.
- Keep the environment instance-scoped instead of adding per-method overrides.

## Core Data Structures

- `Mapping[str, str]` for caller-provided overrides.
- `dict[str, str]` for the resolved subprocess environment.

## Public Interfaces

- `Ludusavi(env: Optional[Mapping[str, str]] = None)`
- `find_ludusavi(env: Optional[Mapping[str, str]] = None)`

## Dependency Requirements

No new dependencies are required.

## Testing Strategy

- Add red tests for discovery verification receiving the merged environment.
- Add red tests for custom `PATH` lookup using the merged environment.
- Add red tests for `Ludusavi(env=...)` forwarding the resolved environment to discovery and executor.
- Add red tests for executor `run` and `Popen` subprocess calls using the instance environment.
- Validate with Ruff, ty, pytest, and the local pre-commit hook.
