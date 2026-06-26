# Review — thermo-nuclear-fixes (round 01)

Branch: `feat/thermo-nuclear-fixes`
Commit reviewed: `11c4d0269ba3f96fc093df664125166a6da33145`
Reviewed against: `docs/plans/2026-06-26_thermo-nuclear-fixes.md`

## Verdict

**APPROVED.** All three in-scope findings are implemented exactly as specified, with the
out-of-scope items (Finding #1 and the #4 typed-model expansion) correctly left untouched.
Commits are atomic and plan-first; the audit trail is complete.

## Gate status

Independently re-ran `scripts/orchestration/run-quality-gates` on the feature branch:

- `ruff check .` — clean
- `ruff format --check .` — clean
- `ty check src/` — clean
- `pytest` — 92 passed (was 93; net -1 after removing 3 `add_game_alias` tests and adding
  2 guard tests). `discovery.py` and `models.py` at 100% coverage.
- review-note integrity — no deleted notes.

Working tree clean.

## Findings resolution

- **#2 (config write) — RESOLVED.** `add_game_alias` removed in full from `main.py`; the
  orphaned `import json` removed (`from pathlib import Path` correctly retained — still used
  by the log methods). Read-only `get_game_alias` preserved. `tests/test_alias.py` drops the
  three writer tests, adds `test_add_game_alias_removed`, and removes its now-unused `json`
  and `Path` imports. README "Game Aliases" section rewritten to read-only framing. No
  runtime dependency added (`git diff pyproject.toml uv.lock` empty; `dependencies = []`).
- **#3 (discovery branches) — RESOLVED.** `_which` and `_verify` collapsed to single calls;
  timeout constant and exception handling preserved. `tests/test_discovery.py` assertions
  correctly updated to expect `env=None` / `path=None` pass-through — a necessary and
  faithful consequence of the collapse, not a weakening.
- **#4 (typing) — RESOLVED.** `ApiErrorDetails` now uses `NotRequired[Optional[...]]`,
  matching the sibling `LudusaviApiOutput`. Other `Dict[str, Any]` boundaries left intact as
  instructed. `test_api_error_details_keys_optional` added to pin the contract.
- **#1 (`_build_args`) — correctly OUT OF SCOPE.** No changes to `main.py`'s per-flag arg
  building.

## Audit trail

Commit sequence is correct: plan committed first
(`docs(plan): add thermo-nuclear-fixes implementation plan`), then three atomic refactor
commits (alias / discovery / models), then the session log under
`docs/agent_conversations/2026-06-26_thermo-nuclear-fixes.md`. Nothing created or deleted
under `docs/review/`.

## Required changes

None.

## Finalization instructions

This note authorizes finalization. Confirm review notes are committed, confirm a clean tree,
then run `scripts/orchestration/finalize thermo-nuclear-fixes`. Finalize is
**local-by-default** here (merge `feat/thermo-nuclear-fixes` into `main` locally, delete the
branch; the `finalize-release` hook is a no-op). Do not push or release — that is deferred
and opt-in. Leave both markers in place afterward and exit cleanly.

STATUS: APPROVED
