import unittest
import json
import os
from pyludusavi.core import LudusaviResponse


class TestRegression(unittest.TestCase):
    def load_fixture(self, name):
        path = os.path.join("docs", "specs", "fixtures", f"{name}.json")
        with open(path, "r") as f:
            return json.load(f)

    def test_parse_backup_preview(self):
        data = self.load_fixture("backup_preview")
        # Just verify we can load it into our logic (simulating _execute)
        response = LudusaviResponse(data=data, raw=data, warnings="", command=[])
        self.assertIn("games", response.data)
        self.assertIn("overall", response.data)

    def test_parse_manifest_show(self):
        data = self.load_fixture("manifest_show")
        response = LudusaviResponse(data=data, raw=data, warnings="", command=[])
        # Manifest is a large dict, verify a sample game if possible
        # Since it's a huge dict, just check type
        self.assertIsInstance(response.data, dict)
        self.assertTrue(len(response.data) > 0)

    def test_parse_find_success(self):
        data = self.load_fixture("find_success")
        response = LudusaviResponse(data=data, raw=data, warnings="", command=[])
        self.assertIn("games", response.data)
        game_name = list(response.data["games"].keys())[0]
        self.assertIn("score", response.data["games"][game_name])
