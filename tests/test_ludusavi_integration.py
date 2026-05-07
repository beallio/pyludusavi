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
        mock_execute.assert_called_with(
            ["api"], mode="STDIN_JSON", input_data=payload, auto_api=False
        )

    @patch("pyludusavi.core.LudusaviExecutor.execute")
    def test_cloud_upload_with_options(self, mock_execute):
        mock_execute.return_value = LudusaviResponse(data={}, raw={}, warnings="", command=[])
        self.ludusavi.cloud_upload(
            games=["Witcher 3"],
            local="/local/backups",
            cloud="/cloud/backups",
            force=True,
            preview=True,
            gui=True,
        )
        mock_execute.assert_called_with(
            [
                "cloud",
                "upload",
                "--local",
                "/local/backups",
                "--cloud",
                "/cloud/backups",
                "--force",
                "--preview",
                "--gui",
                "Witcher 3",
            ],
            mode="JSON",
        )

    @patch("pyludusavi.core.LudusaviExecutor.execute")
    def test_cloud_download_with_options(self, mock_execute):
        mock_execute.return_value = LudusaviResponse(data={}, raw={}, warnings="", command=[])
        self.ludusavi.cloud_download(
            games=["Witcher 3"],
            local="/local/backups",
            cloud="/cloud/backups",
            force=True,
            preview=True,
            gui=True,
        )
        mock_execute.assert_called_with(
            [
                "cloud",
                "download",
                "--local",
                "/local/backups",
                "--cloud",
                "/cloud/backups",
                "--force",
                "--preview",
                "--gui",
                "Witcher 3",
            ],
            mode="JSON",
        )

    @patch("pyludusavi.core.LudusaviExecutor.execute")
    def test_wrap_with_name(self, mock_execute):
        mock_execute.return_value = LudusaviResponse(data={}, raw={}, warnings="", command=[])
        self.ludusavi.wrap(["./game.exe", "--arg"], name="Witcher 3")
        mock_execute.assert_called_with(
            ["wrap", "--name", "Witcher 3", "--", "./game.exe", "--arg"],
            mode="TEXT",
        )

    @patch("pyludusavi.core.LudusaviExecutor.execute")
    def test_wrap_with_infer_and_options(self, mock_execute):
        mock_execute.return_value = LudusaviResponse(data={}, raw={}, warnings="", command=[])
        self.ludusavi.wrap(
            ["steam", "-applaunch", "292030"],
            infer="steam",
            force=True,
            force_backup=True,
            force_restore=True,
            no_backup=True,
            no_restore=True,
            no_force_cloud_conflict=True,
            gui=True,
            path="/backups",
            format="zip",
            compression="zstd",
            compression_level=10,
            full_limit=3,
            differential_limit=2,
            cloud_sync=True,
            ask_downgrade=True,
        )
        mock_execute.assert_called_with(
            [
                "wrap",
                "--infer",
                "steam",
                "--force",
                "--force-backup",
                "--force-restore",
                "--no-backup",
                "--no-restore",
                "--no-force-cloud-conflict",
                "--gui",
                "--path",
                "/backups",
                "--format",
                "zip",
                "--compression",
                "zstd",
                "--compression-level",
                "10",
                "--full-limit",
                "3",
                "--differential-limit",
                "2",
                "--cloud-sync",
                "--ask-downgrade",
                "--",
                "steam",
                "-applaunch",
                "292030",
            ],
            mode="TEXT",
        )

    def test_wrap_requires_name_or_infer(self):
        with self.assertRaises(ValueError):
            self.ludusavi.wrap(["./game.exe"])

    def test_wrap_rejects_name_and_infer(self):
        with self.assertRaises(ValueError):
            self.ludusavi.wrap(["./game.exe"], name="Witcher 3", infer="steam")

    def test_wrap_rejects_cloud_sync_conflict(self):
        with self.assertRaises(ValueError):
            self.ludusavi.wrap(
                ["./game.exe"], name="Witcher 3", cloud_sync=True, no_cloud_sync=True
            )
