import unittest
from unittest.mock import patch
from pyludusavi.core import LudusaviResponse
from pyludusavi.main import Ludusavi


class TestLudusaviIntegration(unittest.TestCase):
    def setUp(self):
        self.patcher = patch("pyludusavi.main.find_ludusavi")
        self.mock_find = self.patcher.start()
        self.mock_find.return_value = ["ludusavi"]
        self.ludusavi = Ludusavi()

    def tearDown(self):
        self.patcher.stop()

    @patch("pyludusavi.core.LudusaviExecutor.execute")
    def test_find_with_options(self, mock_execute):
        mock_execute.return_value = LudusaviResponse(data={}, raw={}, warnings="", command=[])
        self.ludusavi.find(games=["Witcher"], steam_id="123", fuzzy=True)
        mock_execute.assert_called_with(
            ["find", "--steam-id", "123", "--fuzzy", "Witcher"], mode="JSON"
        )

    @patch("pyludusavi.core.LudusaviExecutor.execute")
    def test_bulk_api(self, mock_execute):
        mock_execute.return_value = LudusaviResponse(data={}, raw={}, warnings="", command=[])
        payload = {"requests": []}
        self.ludusavi.bulk_api(payload)
        mock_execute.assert_called_with(["api"], mode="STDIN_JSON", input_data=payload)

    @patch("pyludusavi.core.LudusaviExecutor.execute")
    def test_wrap(self, mock_execute):
        mock_execute.return_value = LudusaviResponse(data={}, raw={}, warnings="", command=[])
        self.ludusavi.wrap(["./game.exe", "--arg"])
        mock_execute.assert_called_with(["wrap", "--", "./game.exe", "--arg"], mode="JSON")
