# Bound Discovery Verification Review - Round 2

**Verdict: CHANGES REQUIRED**

**Reviewed branch:** `fix/bound-discovery-verification`
**Reviewed HEAD:** `15c676d69234af55073caf86ca044ad620bc4800`
**Review basis:** `docs/plans/2026-06-13_bound_discovery_verification.md`

## Required Finding

### F1 - The prohibited `uv.lock` delta is still present

Round 1 was not actually resolved. The current branch still adds:

```toml
[options]
exclude-newer = "0001-01-01T00:00:00Z"
exclude-newer-span = "P7D"
```

The objective evidence is:

```text
git diff dev...HEAD --numstat -- uv.lock
4       0       uv.lock
```

Commit `54358bd661e90062e2b2142f922bd5335ca5e5a7` is an empty commit. It contains no
lockfile correction. The round 1 resolution statement claiming that the branch diff was
empty is therefore inaccurate.

The cause is the repository pre-commit hook. After `uv.lock` is restored, the hook runs
several `uv run` commands. This machine has the following global uv policy:

```toml
exclude-newer = "7 days"
```

Those commands regenerate the four lockfile lines, and the hook's `git add -u` stages
them again. The resulting index matches the pre-correction commit, producing the empty
commit observed in round 1.

## Required Remediation

Use frozen uv behavior for the corrective commit so the hook validates the existing
lockfile without rewriting it:

```bash
git switch fix/bound-discovery-verification
git restore --source=dev -- uv.lock
git add uv.lock
UV_FROZEN=1 git commit -m "chore(lock): remove unrelated lockfile churn"
```

Do not use `--no-verify`. The hook must run and pass. `UV_FROZEN=1` is required only to
prevent the machine-level uv policy from rewriting a lockfile that this feature must not
change.

Immediately after the commit, run all of these checks:

```bash
git status --short
git diff --quiet dev...HEAD -- uv.lock
test "$(git show --format= --numstat HEAD -- uv.lock | awk '{print $1 \":\" $2}')" = "0:4"
```

Expected results:

- `git status --short` is empty.
- `git diff --quiet dev...HEAD -- uv.lock` exits zero.
- The new correction commit removes four lines from `uv.lock`; it must not be empty.

Run the quality gates without permitting uv to rewrite the lockfile:

```bash
UV_FROZEN=1 ./run.sh uv run ruff check .
UV_FROZEN=1 ./run.sh uv run ruff format --check .
UV_FROZEN=1 ./run.sh uv run ty check src/
UV_FROZEN=1 ./run.sh uv run pytest
git diff --check dev...HEAD
git status --short
```

Update the inaccurate round 1 resolution by appending a correction stating that the
first attempt produced an empty commit because the hook regenerated the global
`exclude-newer` options, and identify the effective correction commit SHA.

Append a `## Round 2 Resolution` section to this file containing:

- The effective correction commit SHA.
- The output of `git diff --quiet dev...HEAD -- uv.lock`.
- Confirmation that the correction commit is non-empty and removes four lines.
- The final quality-gate results.

Commit the updated round 1 note and this round 2 note as:

```text
docs(review): record discovery timeout review round 2
```

Use `UV_FROZEN=1 git commit ...` for the review-note commit as well, so its hook does not
reintroduce the lockfile options.

Finally, rewrite the same empty marker:

```bash
: > /tmp/pyludusavi/2026-06-13_bound_discovery_verification_finished
```

Then wait for:

```text
docs/review/2026-06-13_bound_discovery_verification_review_round_3.md
```

## Verified As Passing

The discovery implementation itself remains correct. At reviewed HEAD:

```text
ruff check                  PASS
ruff format --check         PASS
ty check src/               PASS
pytest                      PASS - 93 tests, 91% total coverage
git diff --check            PASS
```

## Round 2 Resolution

- Addressed F1 using `UV_FROZEN=1` to prevent hook-induced lockfile drift.
- Effective correction commit SHA: `c34a3a80991064434cf9d706780d2287d0fe241d`.
- `git diff --quiet dev...HEAD -- uv.lock` exited with 0 (empty output).
- Confirmed the commit is non-empty and removes four lines.
- Quality gates with `UV_FROZEN=1` pass cleanly.
