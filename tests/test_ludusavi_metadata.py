import unittest
import os
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

    def test_init_accepts_flatpak_id(self):
        self.patcher.stop()
        with patch("pyludusavi.main.find_ludusavi") as mock_find:
            mock_find.return_value = ["flatpak", "run", "com.github.mtkennerly.ludusavi"]
            Ludusavi(flatpak_id="com.github.mtkennerly.ludusavi")
            mock_find.assert_called_once_with(
                explicit_path=None,
                explicit_flatpak_id="com.github.mtkennerly.ludusavi",
                env=None,
            )
        self.patcher = patch("pyludusavi.main.find_ludusavi")
        self.mock_find = self.patcher.start()
        self.mock_find.return_value = ["ludusavi"]

    @patch.dict(os.environ, {"PATH": "/ambient/bin", "KEEP": "yes"}, clear=True)
    def test_init_accepts_env(self):
        self.patcher.stop()
        with (
            patch("pyludusavi.main.find_ludusavi") as mock_find,
            patch("pyludusavi.main.LudusaviExecutor") as mock_executor,
        ):
            mock_find.return_value = ["ludusavi"]
            Ludusavi(env={"PATH": "/custom/bin", "EXTRA": "1"})
            resolved_env = {"PATH": "/custom/bin", "KEEP": "yes", "EXTRA": "1"}
            mock_find.assert_called_once_with(
                explicit_path=None,
                explicit_flatpak_id=None,
                env=resolved_env,
            )
            mock_executor.assert_called_once_with(["ludusavi"], env=resolved_env)
        self.patcher = patch("pyludusavi.main.find_ludusavi")
        self.mock_find = self.patcher.start()
        self.mock_find.return_value = ["ludusavi"]

    @patch("pyludusavi.core.LudusaviExecutor.execute")
    def test_config_path(self, mock_execute):
        mock_execute.return_value = LudusaviResponse(
            data="/path/to/config.yaml",
            raw="/path/to/config.yaml",
            warnings="",
            command=["ludusavi", "config", "path"],
        )
        result = self.ludusavi.config_path()
        self.assertEqual(result, "/path/to/config.yaml")
        mock_execute.assert_called_with(["config", "path"], mode="TEXT")

    @patch("pyludusavi.core.LudusaviExecutor.execute")
    def test_schema(self, mock_execute):
        mock_execute.return_value = LudusaviResponse(
            data={"schema": "ok"},
            raw={"schema": "ok"},
            warnings="",
            command=["ludusavi", "schema", "--format", "json", "api-output"],
        )
        result = self.ludusavi.schema("api-output")
        self.assertEqual(result, {"schema": "ok"})
        mock_execute.assert_called_with(
            ["schema", "--format", "json", "api-output"], mode="JSON", auto_api=False
        )

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
