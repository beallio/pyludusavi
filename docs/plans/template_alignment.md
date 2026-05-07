# Plan: Template Alignment

## Problem Definition

`pyludusavi` has drifted from `/home/beallio/Dropbox/Scripts/project_template`.
The repository already has the generated project structure and cache-isolated
Python tooling, but its local agent protocol, protocol tests, TDD script,
pre-commit hook, and contributor documentation still reflect older conventions.

## Architecture Overview

Align the repository with the current generated-project contract while keeping
project-specific package code, Ludusavi wrapper tests, and existing specs intact.
The alignment should update only repository workflow, documentation, and protocol
surface unless tests expose behavior that needs a code fix.

## Core Data Structures

- `.protocol`: project-local protocol metadata with `PROTOCOL_VERSION=2` and
  `CACHE_ROOT=/tmp/pyludusavi`.
- `AGENTS.md`: canonical agent instruction file for generated projects.
- `.git/hooks/pre-commit`: local commit-time quality gate.
- `scripts/check_tdd.sh`: staged-source-file test presence check.
- `tests/test_protocol.py`: executable assertions for protocol structure.
- `README.md`: user and contributor-facing setup and validation guidance.

## Public Interfaces

- Project commands continue to run through `./run.sh`.
- Contributor validation commands are:
  - `./run.sh uv run ruff check . --fix`
  - `./run.sh uv run ruff format .`
  - `./run.sh uv run ty check src/`
  - `./run.sh uv run pytest`
- `AGENTS.md` remains the only canonical project agent instruction file.

## Dependency Requirements

- No new runtime dependencies.
- No new development dependencies.
- Existing `uv`, `ruff`, `pytest`, `pytest-cov`, and `ty` tooling remains
  cache-isolated under `/tmp/pyludusavi`.

## Testing Strategy

Follow Red-Green-Refactor:

1. Add protocol tests that assert template-aligned agent instructions,
   pre-commit command wrapping, no Gemini-specific canonical files, and required
   project documentation directories.
2. Run focused protocol tests and confirm failure.
3. Update workflow and documentation files to satisfy those tests.
4. Run focused tests, then the full validation suite through `./run.sh`.

## Tasks

- [x] Add failing protocol tests for template alignment.
- [x] Update `AGENTS.md` to the current generated-project protocol.
- [x] Update `.git/hooks/pre-commit` to run tooling through `./run.sh`.
- [x] Replace `scripts/check_tdd.sh` with the staged source-file check.
- [x] Remove Gemini-specific project instruction files from the canonical
      project surface.
- [x] Update `.gitignore` and remove repo-local generated cache artifacts.
- [x] Refresh README setup and validation guidance.
- [x] Record an agent session summary.
