from unittest.mock import patch
from pathlib import Path
from pyludusavi import Ludusavi


def test_log_dir():
    with patch("pyludusavi.main.find_ludusavi", return_value=["ludusavi"]):
        lud = Ludusavi()
        with patch.object(
            Ludusavi, "config_path", return_value="/home/user/.config/ludusavi/config.yaml"
        ):
            assert lud.log_dir() == "/home/user/.config/ludusavi"


def test_log_show_success():
    with patch("pyludusavi.main.find_ludusavi", return_value=["ludusavi"]):
        lud = Ludusavi()
        log_content = "some log data"
        with patch.object(Ludusavi, "log_dir", return_value="/path/to/logs"):
            with patch.object(Path, "exists", return_value=True):
                with patch.object(Path, "read_text", return_value=log_content):
                    assert lud.log_show() == log_content


def test_log_show_not_found():
    with patch("pyludusavi.main.find_ludusavi", return_value=["ludusavi"]):
        lud = Ludusavi()
        with patch.object(Ludusavi, "log_dir", return_value="/path/to/logs"):
            with patch.object(Path, "exists", return_value=False):
                assert lud.log_show() == ""


def test_log_show_logic():
    with patch("pyludusavi.main.find_ludusavi", return_value=["ludusavi"]):
        lud = Ludusavi()
        with patch.object(Ludusavi, "log_dir", return_value="/path/to/logs"):
            with patch.object(Path, "exists", return_value=True):
                with patch.object(Path, "read_text", return_value="content") as mocked_read:
                    lud.log_show()
                    # Verify that read_text was called with the correct encoding
                    mocked_read.assert_called_once_with(encoding="utf-8")
