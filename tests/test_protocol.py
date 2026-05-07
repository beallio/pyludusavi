from pathlib import Path


def test_plans_directory():
    assert Path("docs/plans").exists()


def test_agents_file():
    assert Path("AGENTS.md").exists()


def test_protocol_docs_match_project_template_contract():
    protocol = Path("AGENTS.md").read_text()

    assert "Protocol Version: 2" in protocol
    assert "Command Wrapper: ./run.sh" in protocol
    assert "Execution Mode: (Script | Project)" in protocol
    assert "Monorepo" not in protocol
    assert "mypy" not in protocol.lower()
    assert "./run.sh uv run ty check src/" in protocol
    assert "Conventional Commits" in protocol
    assert "docs/review/" in protocol
    assert "Gemini-specific" in protocol


def test_repository_uses_canonical_agent_instruction_file():
    assert Path("AGENTS.md").exists()
    assert not Path("GEMINI.md").exists()
    assert not Path(".geminiignore").exists()


def test_pre_commit_runs_through_project_wrapper():
    hook_path = Path(".git/hooks/pre-commit")
    if not hook_path.exists():
        return

    hook = hook_path.read_text()

    assert "./run.sh uv run ruff check . --fix" in hook
    assert "./run.sh uv run ruff format ." in hook
    assert "./run.sh uv run ty check src/" in hook
    assert "./run.sh uv run pytest" in hook
    assert "\nruff check . --fix" not in hook
    assert "\nuv run pytest" not in hook


def test_template_documentation_directories_exist():
    assert Path("docs/specs").exists()
    assert Path("docs/review").exists()
    assert Path("docs/agent_conversations").exists()
