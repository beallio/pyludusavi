import os
from unittest.mock import patch

from pyludusavi._environment import resolve_environment


def test_resolve_environment_returns_none_without_overrides():
    assert resolve_environment(None) is None


def test_resolve_environment_merges_overrides_without_mutating_input():
    overrides = {"PATH": "/custom/bin", "EXTRA": "1"}

    with patch.dict(os.environ, {"PATH": "/ambient/bin", "KEEP": "yes"}, clear=True):
        resolved = resolve_environment(overrides)

    assert resolved == {"PATH": "/custom/bin", "KEEP": "yes", "EXTRA": "1"}
    assert overrides == {"PATH": "/custom/bin", "EXTRA": "1"}
