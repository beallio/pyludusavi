from unittest.mock import patch, MagicMock
from pyludusavi.main import Ludusavi


def test_main_import():
    assert Ludusavi


@patch("pyludusavi.main.find_ludusavi")
@patch("pyludusavi.main.LudusaviExecutor")
def test_backup_flags(mock_executor_cls, mock_find):
    mock_find.return_value = ["ludusavi"]
    mock_executor = MagicMock()
    mock_executor_cls.return_value = mock_executor

    lud = Ludusavi()
    lud.backup(no_force_cloud_conflict=True)

    args, kwargs = mock_executor.execute.call_args
    assert "--no-force-cloud-conflict" in args[0]


@patch("pyludusavi.main.find_ludusavi")
@patch("pyludusavi.main.LudusaviExecutor")
def test_restore_flags(mock_executor_cls, mock_find):
    mock_find.return_value = ["ludusavi"]
    mock_executor = MagicMock()
    mock_executor_cls.return_value = mock_executor

    lud = Ludusavi()
    lud.restore(no_force_cloud_conflict=True)

    args, kwargs = mock_executor.execute.call_args
    assert "--no-force-cloud-conflict" in args[0]


@patch("pyludusavi.main.find_ludusavi")
@patch("pyludusavi.main.LudusaviExecutor")
def test_config_show_flags(mock_executor_cls, mock_find):
    mock_find.return_value = ["ludusavi"]
    mock_executor = MagicMock()
    mock_executor_cls.return_value = mock_executor

    lud = Ludusavi()
    lud.config_show(default=True)

    args, kwargs = mock_executor.execute.call_args
    assert "--default" in args[0]
