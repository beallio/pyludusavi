import unittest
from unittest.mock import patch

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

    def test_add_game_alias_removed(self):
        assert not hasattr(Ludusavi, "add_game_alias")

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
