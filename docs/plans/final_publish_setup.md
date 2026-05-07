# Plan: Final Release Configuration & Publishing

## Objective
Finalize the project setup for automated publishing to PyPI via GitHub Actions, as per the provided metadata.

## Metadata
- **Project Name:** `pyludusavi`
- **Owner:** `beallio`
- **Workflow Name:** `workflow.yml`
- **Environment Name:** `pypi`
- **Remote Name:** `pyludusavi`
- **Repository:** `https://github.com/beallio/pyludusavi.git`

## Implementation Steps

### 1. Update Workflow
- Rename `.github/workflows/ci.yml` to `.github/workflows/workflow.yml`.
- Add a `publish` job that:
    - Depends on the `test` job.
    - Runs only on version tags (e.g., `v*`).
    - Uses the `pypi` environment.
    - Requests `id-token: write` permissions for Trusted Publishing.
    - Executes `uv build` and `uv publish`.

### 2. Configure Git Remote
- Add a new remote named `pyludusavi` pointing to `https://github.com/beallio/pyludusavi.git`.

### 3. Commit & Push
- Commit the workflow rename and update.
- Push the `main` branch to the `pyludusavi` remote.
- Push the `v0.1.0` tag to the `pyludusavi` remote to trigger the first publish.

## Verification
- Verify the workflow file syntax.
- Confirm the remote is correctly added.
- Monitor the GitHub Action for successful testing and publishing.
