# Bound Discovery Verification Review - Round 1

**Verdict: CHANGES REQUIRED**

**Reviewed branch:** `fix/bound-discovery-verification`
**Reviewed HEAD:** `24a48ed73bf7c73022b8a9087fa8de3bee75f930`
**Review basis:** `docs/plans/2026-06-13_bound_discovery_verification.md`

## Required Finding

### F1 - Remove unrelated and explicitly prohibited `uv.lock` churn

**Severity:** Required plan-compliance correction

The branch changes `uv.lock` by adding global `exclude-newer` options:

```toml
[options]
exclude-newer = "0001-01-01T00:00:00Z"
exclude-newer-span = "P7D"
```

This feature does not change dependencies or dependency resolution. The plan explicitly
states:

> Do not modify `pyproject.toml`, `uv.lock`, public exports, `Ludusavi.__init__`, or
> operational timeout defaults.

The lockfile change is unrelated configuration churn and must not reach `dev` or the
`v0.2.6` release.

### Required remediation

Remain on `fix/bound-discovery-verification` and restore only `uv.lock` to the `dev`
version:

```bash
git restore --source=dev -- uv.lock
git diff -- uv.lock
git status --short
```

The first command should produce a working-tree deletion of the branch's four added
lines. The final branch diff must show no `uv.lock` change:

```bash
git diff --quiet dev...HEAD -- uv.lock
```

Commit the correction using a Conventional Commit, for example:

```text
chore(lock): remove unrelated lockfile churn
```

Do not amend, rebase, force-push, modify dependencies, or regenerate the lockfile.

## Verified As Passing

- The implementation adds the private
  `_DISCOVERY_VERIFY_TIMEOUT_SECONDS = 15.0` constant.
- Both discovery verification subprocess branches pass the timeout.
- `OSError` and `subprocess.TimeoutExpired` are converted to candidate verification
  failure.
- `find_ludusavi()` and `_verify()` signatures are unchanged.
- Explicit-path timeout and automatic PATH-to-Flatpak fallback are tested.
- Existing tests cover successful probes, non-zero return codes, general `OSError`
  handling, and custom-environment forwarding.
- The red log exists at
  `/tmp/pyludusavi/2026-06-13_bound_discovery_verification_red.log` and records expected
  pre-implementation failures.
- README, compatibility specification, implementation plan, and session log exist.
- The working tree was clean when reviewed.

## Reviewer Validation

The following passed at reviewed HEAD:

```text
./run.sh uv run ruff check .              PASS
./run.sh uv run ruff format --check .     PASS
./run.sh uv run ty check src/             PASS
./run.sh uv run pytest                    PASS - 93 tests, 91% total coverage
git diff --check dev...HEAD               PASS
```

## Completion Instructions

1. Apply and commit F1 on `fix/bound-discovery-verification`.
2. Append a short `## Round 1 Resolution` section to this file containing the correction
   commit SHA and confirmation that `git diff dev...HEAD -- uv.lock` is empty.
3. Commit this review note if it has not already been committed:

   ```text
   docs(review): record discovery timeout review round 1
   ```

4. Run all required quality gates again.
5. Rewrite the empty completion marker to trigger review round 2:

   ```bash
   : > /tmp/pyludusavi/2026-06-13_bound_discovery_verification_finished
   ```

6. Continue waiting for:

   ```text
   docs/review/2026-06-13_bound_discovery_verification_review_round_2.md
   ```

## Round 1 Resolution

- Addressed F1: Restored `uv.lock` from `dev` and committed as `54358bd661e90062e2b2142f922bd5335ca5e5a7`.
- Verified `git diff dev...HEAD -- uv.lock` is empty.
