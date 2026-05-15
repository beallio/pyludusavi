import unittest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from pyludusavi.discovery import find_ludusavi, LudusaviNotFoundError


class TestDiscovery(unittest.TestCase):
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_find_by_explicit_path(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        path = "/custom/ludusavi"
        result = find_ludusavi(explicit_path=path)
        self.assertEqual(result, [path])
        mock_run.assert_called_with(
            [path, "--version"], capture_output=True, text=True, check=False
        )

    @patch.dict(os.environ, {"PATH": "/ambient/bin", "KEEP": "yes"}, clear=True)
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_find_uses_merged_env_for_explicit_path_verification(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        path = "/custom/ludusavi"

        result = find_ludusavi(explicit_path=path, env={"PATH": "/custom/bin", "EXTRA": "1"})

        self.assertEqual(result, [path])
        mock_run.assert_called_with(
            [path, "--version"],
            capture_output=True,
            text=True,
            check=False,
            env={"PATH": "/custom/bin", "KEEP": "yes", "EXTRA": "1"},
        )

    @patch.dict(os.environ, {"PATH": "/ambient/bin"}, clear=True)
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_find_uses_merged_env_path_for_path_lookup(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        mock_which.return_value = "/custom/bin/ludusavi"

        result = find_ludusavi(env={"PATH": "/custom/bin"})

        self.assertEqual(result, ["/custom/bin/ludusavi"])
        mock_which.assert_called_with("ludusavi", path="/custom/bin")

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_find_by_explicit_path_object(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        path = Path("/custom/ludusavi")
        result = find_ludusavi(explicit_path=path)
        self.assertEqual(result, [str(path)])
        mock_run.assert_called_with(
            [str(path), "--version"], capture_output=True, text=True, check=False
        )

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_find_by_path_lookup(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0)
        mock_which.return_value = "/usr/bin/ludusavi"
        result = find_ludusavi()
        self.assertEqual(result, ["/usr/bin/ludusavi"])

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_find_by_flatpak(self, mock_run, mock_which):
        # 1. PATH lookup fails (shutil.which returns None)
        # 2. Flatpak lookup succeeds (shutil.which returns path, _verify returns True)
        mock_which.side_effect = [None, "/usr/bin/flatpak"]
        mock_run.return_value = MagicMock(returncode=0)

        result = find_ludusavi()
        self.assertEqual(result, ["flatpak", "run", "com.github.mtkennerly.ludusavi"])
        # Verify that it tried to verify the flatpak command
        mock_run.assert_called_with(
            ["flatpak", "run", "com.github.mtkennerly.ludusavi", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_find_by_explicit_flatpak_id(self, mock_run, mock_which):
        mock_which.return_value = "/usr/bin/flatpak"
        mock_run.return_value = MagicMock(returncode=0)

        result = find_ludusavi(explicit_flatpak_id="com.github.mtkennerly.ludusavi")

        self.assertEqual(result, ["flatpak", "run", "com.github.mtkennerly.ludusavi"])
        mock_which.assert_called_once_with("flatpak")
        mock_run.assert_called_with(
            ["flatpak", "run", "com.github.mtkennerly.ludusavi", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_explicit_flatpak_id_not_found_raises_error(self, mock_run, mock_which):
        mock_which.return_value = "/usr/bin/flatpak"
        mock_run.return_value = MagicMock(returncode=1)

        with self.assertRaises(LudusaviNotFoundError):
            find_ludusavi(explicit_flatpak_id="com.github.mtkennerly.ludusavi")

    @patch("shutil.which")
    def test_not_found_raises_error(self, mock_which):
        mock_which.return_value = None
        with self.assertRaises(LudusaviNotFoundError):
            find_ludusavi()
