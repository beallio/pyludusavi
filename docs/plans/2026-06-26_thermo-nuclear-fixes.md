# Plan: Thermo-Nuclear Review Fixes (thermo-nuclear-fixes)

## Context

The review in `docs/review/thermo_nuclear_review.md` raised four findings. After
verification against the code, three are worth acting on; the headline "BLOCKING"
finding (#1) was judged overblown and is **explicitly out of scope**.

Owner decisions already made (do not re-litigate):

- **Finding #2 (config write):** `add_game_alias` rewrites the user's `config.yaml`
  using `json.dumps()` of Ludusavi's *merged* API output — clobbering YAML
  comments/formatting and baking in default values. A correct fix would need a YAML
  library, but this project is deliberately **zero-runtime-dependency**
  (`dependencies = []`). Decision: **remove `add_game_alias` entirely**; keep the
  read-only `get_game_alias`. Ludusavi's GUI owns writing custom games; this library
  only reads them. **Do not add any runtime dependency.**
- **Finding #1 (`_build_args` refactor):** **Out of scope.** Leave `main.py`'s explicit
  per-flag argument building exactly as-is.
- **Finding #3 (`discovery.py` redundant branches):** In scope — collapse two
  behavior-identical branches in `_verify` and `_which`.
- **Finding #4 (`models.py` typing):** In scope, minimal — standardize `ApiErrorDetails`
  to the `NotRequired[Optional[...]]` pattern already used by `LudusaviApiOutput` in the
  same file. Do **not** introduce typed models for `roots`/`customGames`/etc.; the
  `Dict[str, Any]` pass-through boundary stays.

Intended outcome: the destructive config writer is gone, two dead branches are removed,
and the error-details TypedDict is internally consistent — with the zero-dependency
stance and the public read API (`get_game_alias`) preserved.

Relevant files: `src/pyludusavi/main.py`, `src/pyludusavi/discovery.py`,
`src/pyludusavi/models.py`, `tests/test_alias.py`, `tests/test_discovery.py`,
`tests/test_models.py`, `README.md`.

Project protocol (`AGENTS.md` / `.protocol`): run all commands through `./run.sh`;
caches stay under `/tmp/pyludusavi`; TDD is mandatory (Red→Green→Refactor); Conventional
Commits; record a session log under `docs/agent_conversations/`.

**Slug used throughout this plan:** `thermo-nuclear-fixes`

---

## Orchestration Contract

**Slug:** `thermo-nuclear-fixes`

**Plan file:**

```text
docs/plans/2026-06-26_thermo-nuclear-fixes.md
```

**Implementation branch:**

```text
feat/thermo-nuclear-fixes
```

**Round-complete marker:**

```text
/tmp/pyludusavi/thermo-nuclear-fixes_finished
```

**Finalized marker:**

```text
/tmp/pyludusavi/thermo-nuclear-fixes_finalized
```

**Review notes:**

```text
docs/review/thermo-nuclear-fixes-review-*.md
```

Each review note ends with exactly one status trailer:

```text
STATUS: CHANGES_REQUESTED
```

or:

```text
STATUS: APPROVED
```

---

## Required Agent Protocol

1. Use the **implementer** skill.
2. Work from the repository root.
3. Branch from `main`.
4. Commit this plan as the first commit on the implementation branch.
5. Follow TDD where behavior changes are testable.
6. Run quality gates before marking any round complete.
7. Do not write your own review.
8. Do not create files under `docs/review/`.
9. Do not delete files under `docs/review/`.
10. Review notes are durable audit records and must be committed.
11. Resolving a review note means:
    - implement the requested changes;
    - run quality gates;
    - commit the code/docs changes;
    - commit the review note itself if it is not already committed;
    - recreate the round-complete marker.
12. After finalization, stop polling and exit cleanly.

---

## Setup

Start from `main`:

```bash
git checkout main
# Local-only: the git remote here is named `pyludusavi` (not `origin`) and
# push/release is deferred, so do NOT pull from a remote. Work from local main.
git checkout -b feat/thermo-nuclear-fixes
```

Commit this plan first:

```bash
git add docs/plans/2026-06-26_thermo-nuclear-fixes.md
git commit -m "docs(plan): add thermo-nuclear-fixes implementation plan"
```

---

## Implementation Tasks

Do all three findings on this one branch, as **three atomic commits** (disjoint files,
independently revertible). Combine into one review round.

| Commit | Finding | Files |
|--------|---------|-------|
| 1 | #2 remove `add_game_alias` | `src/pyludusavi/main.py`, `tests/test_alias.py`, `README.md` |
| 2 | #3 discovery branch cleanup | `src/pyludusavi/discovery.py`, `tests/test_discovery.py` |
| 3 | #4 `ApiErrorDetails` typing | `src/pyludusavi/models.py`, `tests/test_models.py` |

### Task 1 — Finding #2: Remove `add_game_alias` (commit 1)

**Tests first (`tests/test_alias.py`):**
- Delete the three `add_game_alias` tests: `test_add_game_alias`,
  `test_add_game_alias_idempotent_when_unchanged`,
  `test_add_game_alias_updates_conflicting_alias`.
- Keep `test_get_game_alias_found` and `test_get_game_alias_not_found`.
- Add a guard test (RED before removal, GREEN after):
  ```python
  def test_add_game_alias_removed(self):
      assert not hasattr(Ludusavi, "add_game_alias")
  ```
- Remove now-unused imports in this file: `import json` and `from pathlib import Path`
  (only the deleted tests used them). Grep to confirm nothing else references them.
- Run `./run.sh uv run pytest tests/test_alias.py` and confirm the guard test FAILS
  before the next step.

**Implementation (`src/pyludusavi/main.py`):**
- Delete the entire `add_game_alias` method (`def add_game_alias` through its final
  `tmp.replace(path)` line). Keep `get_game_alias` directly below it unchanged.
- Remove `import json` from the top of the file — after deletion it is unused (the other
  `json` occurrences are string literals / `Literal` values, not the module). Verify with
  `grep -n "json\." src/pyludusavi/main.py` returning nothing.
- Do **not** touch `src/pyludusavi/__init__.py` (it never exported the method).

**Docs (`README.md`):**
- Rewrite the **"Game Aliases"** section: remove all `add_game_alias` prose and the
  `lud.add_game_alias(...)` example. Replace with a read-only description, e.g.:
  > `get_game_alias(name)` returns the manifest title a custom name is aliased to (or
  > `None`). Custom games / aliases are created in the Ludusavi GUI or config file; this
  > library reads them but does not write them.
  ```python
  lud.get_game_alias("My Game")  # -> "The Witcher 3" or None
  ```
- Leave `docs/plans/add_game_alias.md` in place (durable historical record).

Commit: `refactor(alias): remove destructive add_game_alias writer`

### Task 2 — Finding #3: Collapse redundant branches in `discovery.py` (commit 2)

Both branches are provably behavior-identical: `subprocess.run(..., env=None)` already
inherits the parent env; `shutil.which(cmd, path=None)` already falls back to
`os.environ["PATH"]`.

**Guard tests first (`tests/test_discovery.py`):** confirm coverage exists for BOTH paths
of each helper — `_verify` with `env=None` **and** with an explicit `env` dict; `_which`
with `path=None` **and** with an explicit `path`. If a `None` case is missing, add a small
characterization test for it and confirm green before editing.

**Implementation (`src/pyludusavi/discovery.py`):**
- `_which` becomes:
  ```python
  def _which(command: str, path: Optional[str]) -> Optional[str]:
      return shutil.which(command, path=path)
  ```
- `_verify`: drop the `if env is None / else` split; keep one call that always passes
  `env=env`:
  ```python
  def _verify(prefix: list[str], env: Optional[dict[str, str]] = None) -> bool:
      """Verify that the command prefix correctly calls Ludusavi."""
      try:
          result = subprocess.run(
              prefix + ["--version"],
              capture_output=True,
              text=True,
              check=False,
              env=env,
              timeout=_DISCOVERY_VERIFY_TIMEOUT_SECONDS,
          )
          return result.returncode == 0
      except (OSError, subprocess.TimeoutExpired):
          return False
  ```
- Preserve `_DISCOVERY_VERIFY_TIMEOUT_SECONDS` and the exception handling exactly.

Commit: `refactor(discovery): drop redundant env/path branches`

### Task 3 — Finding #4: Standardize `ApiErrorDetails` typing (commit 3)

Make `ApiErrorDetails` consistent with the sibling envelope `LudusaviApiOutput`, which
already uses `NotRequired[Optional[...]]`.

**Test first (`tests/test_models.py`)** — mirror `test_api_output_optional_top_level_fields`:
```python
def test_api_error_details_keys_optional():
    from pyludusavi.models import ApiErrorDetails
    for key in ("cloudConflict", "cloudSyncFailed", "someGamesFailed", "unknownGames"):
        assert key in ApiErrorDetails.__optional_keys__
        assert key not in ApiErrorDetails.__required_keys__
```
This passes today (via `total=False`) and must keep passing after the change.

**Implementation (`src/pyludusavi/models.py`):** replace
```python
class ApiErrorDetails(TypedDict, total=False):
    cloudConflict: Optional[Dict]
    cloudSyncFailed: Optional[Dict]
    someGamesFailed: Optional[bool]
    unknownGames: Optional[List[str]]
```
with (drop `total=False`; `NotRequired` is already imported):
```python
class ApiErrorDetails(TypedDict):
    cloudConflict: NotRequired[Optional[Dict]]
    cloudSyncFailed: NotRequired[Optional[Dict]]
    someGamesFailed: NotRequired[Optional[bool]]
    unknownGames: NotRequired[Optional[List[str]]]
```
Do not change any other TypedDict; the `Dict[str, Any]` boundary in `ApiConfig` stays.

Commit: `refactor(models): use NotRequired for ApiErrorDetails keys`

### Session log

Create `docs/agent_conversations/2026-06-26_thermo-nuclear-fixes.md` (or `.json`) with:
date, objective, files modified, tests added/removed, design decisions (the
zero-dependency choice to remove rather than fix `add_game_alias`; #1 out of scope), and
results. Commit it with the round.

### Known risks / watch-outs

- **Breaking API change:** removing `add_game_alias` is breaking for callers — acceptable
  for a 0.x beta; reflect it in the README. Do not bump versions or tag releases.
- **Unused imports** are the most likely gate failure: removing the method orphans
  `import json` in both `main.py` and `tests/test_alias.py`, plus `from pathlib import
  Path` in the test. Remove them explicitly (do not rely solely on ruff).
- **Don't over-reach #4:** do not type `roots`/`customGames`; that boundary is intentional.
- **Don't touch `get_game_alias`:** it stays and its tests must keep passing.
- **No new dependencies:** `pyproject.toml` `dependencies` must remain `[]`. Confirm with
  `git diff pyproject.toml uv.lock` (no dependency changes).

---

## Quality Gates

Run before marking any round complete:

```bash
scripts/orchestration/run-quality-gates
scripts/orchestration/check-review-notes-not-deleted
git status --short
```

The round is not complete unless:

1. all requested implementation work is done;
2. all relevant tests pass;
3. build/typecheck gates pass;
4. review notes have not been deleted;
5. the working tree is clean;
6. all code/docs changes are committed.

---

## Verification

Run end-to-end from the repo root:

1. `grep -rn "add_game_alias" src tests README.md` → only matches are the removed-method
   guard test (and optionally the session log); **no** method definition or call site.
2. `grep -n "import json" src/pyludusavi/main.py` → nothing.
3. `./run.sh uv run ruff check .` → clean.
4. `./run.sh uv run ruff format --check .` → clean.
5. `./run.sh uv run ty check src/` → clean.
6. `./run.sh uv run pytest` → all green, including the new tests
   `test_add_game_alias_removed`, `test_api_error_details_keys_optional`, and any added
   discovery characterization test; existing `test_regression.py` / `test_main.py` still pass.
7. `git diff pyproject.toml uv.lock` → no dependency changes (`dependencies = []` intact).

Deferred verification: none required beyond the automated suite. There is no on-device or
manual UAT step for this change; release/publish is deferred and opt-in.

---

## Mark Round Complete

When the implementation round is complete and the working tree is clean, run:

```bash
scripts/orchestration/mark-finished thermo-nuclear-fixes
```

This writes:

```text
/tmp/pyludusavi/thermo-nuclear-fixes_finished
```

Then exit cleanly. If this process exits, the orchestrator will resume you through
`scripts/orchestration/continue-implementer thermo-nuclear-fixes`.

---

## Review Polling Loop

After marking the round complete, check existing review notes first, then poll for new review notes if you remain active:

```text
docs/review/thermo-nuclear-fixes-review-*.md
```

When a review note exists or a new review note appears:

1. Read the full review note.
2. If the note ends with:

   ```text
   STATUS: CHANGES_REQUESTED
   ```

   then resume work.

3. Clear the round-complete marker:

   ```bash
   scripts/orchestration/clear-finished thermo-nuclear-fixes
   ```

4. Address every requested change.
5. Run quality gates:

   ```bash
   scripts/orchestration/run-quality-gates
   scripts/orchestration/check-review-notes-not-deleted
   ```

6. Commit code/docs fixes.
7. Commit the review-note file itself if it is not already committed:

   ```bash
   git add docs/review/thermo-nuclear-fixes-review-*.md
   git commit -m "docs(review): record thermo-nuclear-fixes review notes"
   ```

8. Recreate the round-complete marker:

   ```bash
   scripts/orchestration/mark-finished thermo-nuclear-fixes
   ```

9. Either continue polling or exit cleanly. If you exit, the orchestrator will resume you with `scripts/orchestration/continue-implementer thermo-nuclear-fixes` after the next review note is created.

---

## Approval Handling

If the latest review note ends with:

```text
STATUS: APPROVED
```

then:

1. Confirm every previous review item has been addressed.
2. Confirm all review notes are committed:

   ```bash
   scripts/orchestration/check-review-notes-committed thermo-nuclear-fixes
   ```

3. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

4. Finalize:

   ```bash
   scripts/orchestration/finalize thermo-nuclear-fixes
   ```

5. Confirm the finalized marker exists:

   ```text
   /tmp/pyludusavi/thermo-nuclear-fixes_finalized
   ```

6. Stop polling and exit cleanly.

---

## Review Rules

Do not write your own review.

Do not create files under:

```text
docs/review/
```

Do not delete files under:

```text
docs/review/
```

Only the orchestrator writes review notes. Your job is to read them, resolve them, commit them as audit records, and continue the loop.

---

## Finalization Rules

Only finalize after a review note with:

```text
STATUS: APPROVED
```

Finalization is performed with:

```bash
scripts/orchestration/finalize thermo-nuclear-fixes
```

Do not manually merge into `main` unless the finalize script fails and the user/orchestrator explicitly instructs you to recover manually.

Leave both markers in place after finalization:

```text
/tmp/pyludusavi/thermo-nuclear-fixes_finished
/tmp/pyludusavi/thermo-nuclear-fixes_finalized
```

Any project-specific release step runs from the project's
`scripts/orchestration-hooks/finalize-release` hook, invoked by finalize.
