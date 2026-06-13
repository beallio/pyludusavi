from pathlib import Path

import pyludusavi


def test_version_attribute():
    assert hasattr(pyludusavi, "__version__")


def test_py_typed_marker_present():
    marker = Path(pyludusavi.__file__).parent / "py.typed"
    assert marker.exists()


def test_timeout_error_exported():
    assert hasattr(pyludusavi, "LudusaviTimeoutError")
    assert issubclass(pyludusavi.LudusaviTimeoutError, pyludusavi.LudusaviError)
