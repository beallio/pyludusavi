from unittest.mock import patch, mock_open
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
            with patch("builtins.open", mock_open(read_data=log_content)):
                with patch("os.path.exists", return_value=True):
                    assert lud.log_show() == log_content


def test_log_show_not_found():
    with patch("pyludusavi.main.find_ludusavi", return_value=["ludusavi"]):
        lud = Ludusavi()
        with patch.object(Ludusavi, "log_dir", return_value="/path/to/logs"):
            with patch("os.path.exists", return_value=False):
                assert lud.log_show() == ""


def test_log_show_filename():
    with patch("pyludusavi.main.find_ludusavi", return_value=["ludusavi"]):
        lud = Ludusavi()
        with patch.object(Ludusavi, "log_dir", return_value="/path/to/logs"):
            with patch("os.path.exists", return_value=True):
                with patch("builtins.open", mock_open()) as mocked_open:
                    lud.log_show()
                    mocked_open.assert_called_once_with(
                        "/path/to/logs/ludusavi_rCURRENT.log", "r", encoding="utf-8"
                    )
