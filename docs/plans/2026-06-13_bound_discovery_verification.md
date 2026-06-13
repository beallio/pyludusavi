# Bound Ludusavi Discovery Verification

## Summary

Implement the SDH-Ludusavi discovery timeout upstream in `pyludusavi`. Every `--version`
verification probe will have a private 15-second timeout, and timeout expiration will
reject that candidate instead of hanging indefinitely.

- Plan name: `2026-06-13_bound_discovery_verification`
- Plan file: `docs/plans/2026-06-13_bound_discovery_verification.md`
- Working branch: `fix/bound-discovery-verification`, created from current `dev`
- Release: stable `v0.2.6` from `dev`
- Required skill: read and follow the `implementer` skill before beginning
- No public API, dependency, model, or executor changes

## Preparation And Git

1. Read `AGENTS.md`, `.protocol`, `run.sh`, this plan, and the complete `implementer`
   skill.
2. Perform the required protocol handshake and verify:
   - Repository root is `/home/beallio/Dropbox/Scripts/pyludusavi`.
   - Project commands use `./run.sh`.
   - Caches remain under `/tmp/pyludusavi`.
   - `ty` is the type checker.
3. Require a clean working tree. Do not stash, discard, or overwrite unrelated work.
4. Synchronize and branch:

   ```bash
   git switch dev
   git fetch pyludusavi
   git pull --ff-only pyludusavi dev
   git switch -c fix/bound-discovery-verification
   ```

5. Materialize this plan at its declared path and commit it as:

   ```text
   docs(plan): add bounded discovery verification plan
   ```

6. Establish a green baseline:

   ```bash
   ./run.sh uv sync
   ./run.sh uv run ruff check .
   ./run.sh uv run ruff format --check .
   ./run.sh uv run ty check src/
   ./run.sh uv run pytest
   ```

7. If baseline validation fails, capture output under `/tmp/pyludusavi/`, diagnose it,
   and do not implement on top of an unexplained failure.

## Implementation

1. Follow strict red-green-refactor. Tests must be changed before production code.
2. In `tests/test_discovery.py`, specify all required behavior:
   - Verification without an explicit environment passes `timeout=15.0`.
   - Verification with a resolved custom environment passes both `env=...` and the
     timeout.
   - A successful probe still returns the candidate.
   - A non-zero return code still rejects the candidate.
   - Any `OSError` still rejects the candidate.
   - `subprocess.TimeoutExpired` rejects the candidate without escaping.
   - Explicit-path timeout ultimately raises `LudusaviNotFoundError`.
   - Automatic PATH-candidate timeout permits fallback to Flatpak.
3. Update existing `mock_run.assert_called_with(...)` expectations to include the
   timeout.
4. Run the tests before implementation and record the expected failure:

   ```bash
   set -o pipefail
   ./run.sh uv run pytest tests/test_discovery.py -q 2>&1 \
     | tee /tmp/pyludusavi/2026-06-13_bound_discovery_verification_red.log
   ```

5. In `src/pyludusavi/discovery.py`:
   - Add `_DISCOVERY_VERIFY_TIMEOUT_SECONDS = 15.0`.
   - Pass that constant as `timeout=` in both `_verify()` subprocess branches.
   - Catch `(OSError, subprocess.TimeoutExpired)` and return `False`.
   - Do not change `find_ludusavi()` or `_verify()` parameters.
   - Do not expose a configurable timeout or import executor machinery.
6. Preserve discovery precedence and semantics:
   - Explicit path and explicit Flatpak failures raise `LudusaviNotFoundError`.
   - Automatic PATH failure continues to Flatpak discovery.
   - Automatic discovery raises `LudusaviNotFoundError` only after candidates fail.
7. Run the focused tests until green, then refactor only if behavior remains unchanged.
8. Update documentation:
   - README timeout documentation must distinguish the fixed 15-second discovery probe
     from command execution timeouts.
   - `docs/specs/compatibility_policy.md` must record bounded discovery verification as
     an execution-safety guarantee.
   - Record the session in
     `docs/agent_conversations/2026-06-13_bound_discovery_verification.json`.
9. Do not modify `pyproject.toml`, `uv.lock`, public exports, `Ludusavi.__init__`, or
   operational timeout defaults.
10. Commit passing implementation and tests as:

    ```text
    fix(discovery): bound verification subprocess
    ```

    Commit documentation/session records separately using Conventional Commits.

## Validation And Completion Signal

Run all gates before declaring implementation complete:

```bash
./run.sh uv run ruff check . --fix
./run.sh uv run ruff format .
./run.sh uv run ty check src/
./run.sh uv run pytest
git diff --check
git status --short
```

Confirm the branch contains only intended files and every commit passes the repository
hook. Then write the exact empty completion marker:

```bash
mkdir -p /tmp/pyludusavi
: > /tmp/pyludusavi/2026-06-13_bound_discovery_verification_finished
```

The marker must be an empty regular file. Its absolute path is:

```text
/tmp/pyludusavi/2026-06-13_bound_discovery_verification_finished
```

## Mandatory Review Loop

After creating the marker, remain active and poll every 60 seconds for the next review
file:

```text
/home/beallio/Dropbox/Scripts/pyludusavi/docs/review/2026-06-13_bound_discovery_verification_review_round_<N>.md
```

Review notes must be written inside the project's `docs/review/` directory, never only
under `/tmp`. File appearance means that review round is complete and triggers renewed
agent work.

1. Start with round 1 and process rounds sequentially.
2. Each note must state `Verdict: PASSED` or `Verdict: CHANGES REQUIRED`.
3. For required changes:
   - Address every finding on the working branch with red-green-refactor.
   - Run focused tests and all quality gates.
   - Create atomic Conventional Commits.
   - Append a resolution section to the review note.
   - Commit the review note as
     `docs(review): record discovery timeout review round <N>` if it is not already
     committed.
   - Rewrite the same empty completion marker to update its timestamp.
   - Resume polling for round `<N+1>`.
4. For a passing review:
   - Commit the passing review note if it is untracked or modified.
   - Do not invent additional implementation work.
   - Proceed to integration and release.

## Integration, Cleanup, And Release

1. Require a clean working tree and passing gates on the feature branch.
2. Update `dev` without rewriting history:

   ```bash
   git switch dev
   git pull --ff-only pyludusavi dev
   git merge --no-ff fix/bound-discovery-verification \
     -m "merge: bound discovery verification"
   ```

3. Run the complete validation suite again on merged `dev`.
4. Delete the merged local working branch with `git branch -d`. If it was pushed, delete
   only that remote feature branch without force pushing.
5. Push and verify `dev`:

   ```bash
   git push pyludusavi dev
   ```

   Confirm local `dev` and `pyludusavi/dev` resolve to the same SHA and wait for the
   corresponding GitHub CI run to pass.
6. Verify `v0.2.6` does not already exist locally or remotely. Never move or replace an
   existing tag.
7. Create the annotated tag locally:

   ```bash
   git tag -a v0.2.6 -m "v0.2.6: bound discovery verification"
   ```

8. Build before publishing and confirm wheel/sdist names contain `0.2.6`:

   ```bash
   ./run.sh uv build --out-dir /tmp/pyludusavi/v0.2.6-build
   ```

9. Push the tag:

   ```bash
   git push pyludusavi v0.2.6
   ```

10. Watch `.github/workflows/workflow.yml` to successful completion. Verify:
    - The test, PyPI publish, and GitHub release jobs passed.
    - `gh release view v0.2.6` reports a non-draft, non-prerelease release.
    - PyPI serves `pyludusavi==0.2.6`.
    - The tag resolves to the pushed `dev` SHA.
11. After all verification succeeds, write the final empty signal:

    ```bash
    : > /tmp/pyludusavi/2026-06-13_bound_discovery_verification_release_finished
    ```

## Acceptance Criteria

- Discovery probes cannot run longer than 15 seconds each.
- Timeout expiration behaves as candidate verification failure.
- Existing discovery order, exceptions, environment merging, and public signatures
  remain compatible.
- Tests cover timeout behavior and fallback behavior.
- README, compatibility specification, session log, and review notes are committed.
- All quality gates pass on both the feature branch and merged `dev`.
- The feature branch is merged and cleaned up without force pushing.
- `dev` is synchronized with GitHub.
- Stable release `v0.2.6` is published successfully to GitHub and PyPI.
- Both required completion files exist under `/tmp/pyludusavi/`.
