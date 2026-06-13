import pyludusavi


def test_version_attribute():
    assert hasattr(pyludusavi, "__version__")


def test_timeout_error_exported():
    assert hasattr(pyludusavi, "LudusaviTimeoutError")
    assert issubclass(pyludusavi.LudusaviTimeoutError, pyludusavi.LudusaviError)
