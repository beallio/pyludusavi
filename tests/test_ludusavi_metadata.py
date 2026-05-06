import unittest
from unittest.mock import patch
from pyludusavi.core import LudusaviResponse
from pyludusavi.main import Ludusavi


class TestLudusaviMetadata(unittest.TestCase):
    def setUp(self):
        # Mock the discovery so it doesn't try to find real ludusavi
        self.patcher = patch("pyludusavi.main.find_ludusavi")
        self.mock_find = self.patcher.start()
        self.mock_find.return_value = ["ludusavi"]
        self.ludusavi = Ludusavi()

    def tearDown(self):
        self.patcher.stop()

    @patch("pyludusavi.core.LudusaviExecutor.execute")
    def test_version(self, mock_execute):
        mock_execute.return_value = LudusaviResponse(
            data="ludusavi 0.31.0",
            raw="ludusavi 0.31.0",
            warnings="",
            command=["ludusavi", "--version"],
        )
        version = self.ludusavi.version()
        self.assertEqual(version, "ludusavi 0.31.0")
        mock_execute.assert_called_with(["--version"], mode="TEXT")

    @patch("pyludusavi.core.LudusaviExecutor.execute")
    def test_config_path(self, mock_execute):
        mock_execute.return_value = LudusaviResponse(
            data="/path/to/config.yaml",
            raw="/path/to/config.yaml",
            warnings="",
            command=["ludusavi", "config", "path"],
        )
        result = self.ludusavi.config_path()
        self.assertEqual(result.data, "/path/to/config.yaml")
        mock_execute.assert_called_with(["config", "path"], mode="TEXT")

    @patch("pyludusavi.core.LudusaviExecutor.execute")
    def test_manifest_show(self, mock_execute):
        mock_execute.return_value = LudusaviResponse(
            data={"game": {}},
            raw={"game": {}},
            warnings="",
            command=["ludusavi", "manifest", "show", "--api"],
        )
        result = self.ludusavi.manifest_show()
        self.assertEqual(result.data, {"game": {}})
        mock_execute.assert_called_with(["manifest", "show"], mode="JSON")
