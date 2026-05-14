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
    @patch.object(Path, "write_text")
    def test_add_game_alias(self, mock_write, mock_show, mock_path):
        # Setup
        mock_path.return_value = "/path/to/config.yaml"
        mock_show.return_value = LudusaviResponse(
            data={"customGames": []}, raw={"customGames": []}, warnings="", command=[]
        )

        # Execute
        self.ludusavi.add_game_alias("My Game", "Official Game")

        # Verify
        # Path.write_text is called on the Path object created from mock_path.return_value
        mock_write.assert_called_once()
        written_data = mock_write.call_args[0][0]
        parsed_data = json.loads(written_data)

        self.assertEqual(len(parsed_data["customGames"]), 1)
        self.assertEqual(parsed_data["customGames"][0]["name"], "My Game")
        self.assertEqual(parsed_data["customGames"][0]["alias"], "Official Game")

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
