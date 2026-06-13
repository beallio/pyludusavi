import unittest
from unittest.mock import patch
import json
from pathlib import Path
from pyludusavi.main import Ludusavi
from pyludusavi.core import LudusaviResponse


class TestAlias(unittest.TestCase):
    def setUp(self):
        # Mock discovery to avoid searching for real ludusavi
        self.patcher = patch("pyludusavi.main.find_ludusavi")
        self.mock_find = self.patcher.start()
        self.mock_find.return_value = ["ludusavi"]
        self.ludusavi = Ludusavi()

    def tearDown(self):
        self.patcher.stop()

    @patch("pyludusavi.main.Ludusavi.config_path")
    @patch("pyludusavi.main.Ludusavi.config_show")
    @patch.object(Path, "replace")
    @patch.object(Path, "write_text")
    def test_add_game_alias(self, mock_write, mock_replace, mock_show, mock_path):
        # Setup
        mock_path.return_value = "/path/to/config.yaml"
        mock_show.return_value = LudusaviResponse(
            data={"customGames": []}, raw={"customGames": []}, warnings="", command=[]
        )

        # Execute
        self.ludusavi.add_game_alias("My Game", "Official Game")

        # Verify: atomic write goes to a temp file, then replaces the real config.
        mock_write.assert_called_once()
        written_data = mock_write.call_args[0][0]
        parsed_data = json.loads(written_data)

        self.assertEqual(len(parsed_data["customGames"]), 1)
        self.assertEqual(parsed_data["customGames"][0]["name"], "My Game")
        self.assertEqual(parsed_data["customGames"][0]["alias"], "Official Game")

        # The replace target is the real config path.
        mock_replace.assert_called_once_with(Path("/path/to/config.yaml"))

    @patch("pyludusavi.main.Ludusavi.config_path")
    @patch("pyludusavi.main.Ludusavi.config_show")
    @patch.object(Path, "replace")
    @patch.object(Path, "write_text")
    def test_add_game_alias_idempotent_when_unchanged(
        self, mock_write, mock_replace, mock_show, mock_path
    ):
        # An identical entry already exists -> no write should occur.
        mock_path.return_value = "/path/to/config.yaml"
        existing = {"customGames": [{"name": "My Game", "alias": "Official Game"}]}
        mock_show.return_value = LudusaviResponse(
            data=existing, raw=existing, warnings="", command=[]
        )

        self.ludusavi.add_game_alias("My Game", "Official Game")

        mock_write.assert_not_called()
        mock_replace.assert_not_called()

    @patch("pyludusavi.main.Ludusavi.config_path")
    @patch("pyludusavi.main.Ludusavi.config_show")
    @patch.object(Path, "replace")
    @patch.object(Path, "write_text")
    def test_add_game_alias_updates_conflicting_alias(
        self, mock_write, mock_replace, mock_show, mock_path
    ):
        # An entry with the same name but a different alias -> update in place.
        mock_path.return_value = "/path/to/config.yaml"
        existing = {"customGames": [{"name": "My Game", "alias": "Old Target"}]}
        mock_show.return_value = LudusaviResponse(
            data=existing, raw=existing, warnings="", command=[]
        )

        self.ludusavi.add_game_alias("My Game", "New Target")

        mock_write.assert_called_once()
        parsed_data = json.loads(mock_write.call_args[0][0])
        self.assertEqual(len(parsed_data["customGames"]), 1)
        self.assertEqual(parsed_data["customGames"][0]["alias"], "New Target")
        mock_replace.assert_called_once_with(Path("/path/to/config.yaml"))

    @patch("pyludusavi.main.Ludusavi.config_show")
    def test_get_game_alias_found(self, mock_show):
        mock_show.return_value = LudusaviResponse(
            data={"customGames": [{"name": "My Custom Name", "alias": "The Witcher 3"}]},
            raw={},
            warnings="",
            command=[],
        )
        alias = self.ludusavi.get_game_alias("My Custom Name")
        self.assertEqual(alias, "The Witcher 3")

    @patch("pyludusavi.main.Ludusavi.config_show")
    def test_get_game_alias_not_found(self, mock_show):
        mock_show.return_value = LudusaviResponse(
            data={"customGames": []},
            raw={},
            warnings="",
            command=[],
        )
        alias = self.ludusavi.get_game_alias("Nonexistent")
        self.assertIsNone(alias)
