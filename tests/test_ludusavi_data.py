import unittest
from unittest.mock import patch
from pyludusavi.core import LudusaviResponse
from pyludusavi.main import Ludusavi


class TestLudusaviData(unittest.TestCase):
    def setUp(self):
        self.patcher = patch("pyludusavi.main.find_ludusavi")
        self.mock_find = self.patcher.start()
        self.mock_find.return_value = ["ludusavi"]
        self.ludusavi = Ludusavi()

    def tearDown(self):
        self.patcher.stop()

    @patch("pyludusavi.core.LudusaviExecutor.execute")
    def test_backup_all(self, mock_execute):
        mock_execute.return_value = LudusaviResponse(data={}, raw={}, warnings="", command=[])
        self.ludusavi.backup()
        mock_execute.assert_called_with(["backup"], mode="JSON", timeout=None)

    @patch("pyludusavi.core.LudusaviExecutor.execute")
    def test_backup_specific_games_and_preview(self, mock_execute):
        mock_execute.return_value = LudusaviResponse(data={}, raw={}, warnings="", command=[])
        self.ludusavi.backup(games=["Witcher 3", "Cyberpunk"], preview=True)
        # Verify that games are passed as positional arguments
        mock_execute.assert_called_with(
            ["backup", "--preview", "Witcher 3", "Cyberpunk"], mode="JSON", timeout=None
        )

    @patch("pyludusavi.core.LudusaviExecutor.execute")
    def test_backups_list(self, mock_execute):
        mock_execute.return_value = LudusaviResponse(data={}, raw={}, warnings="", command=[])
        self.ludusavi.backups_list(path="/custom/path")
        mock_execute.assert_called_with(["backups", "--path", "/custom/path"], mode="JSON")
