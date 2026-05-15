import unittest
import os
from unittest.mock import patch, MagicMock
from pyludusavi.core import LudusaviExecutor, LudusaviExecutionError, LudusaviContractError


class TestExecutor(unittest.TestCase):
    def setUp(self):
        self.prefix = ["ludusavi"]
        self.executor = LudusaviExecutor(self.prefix)

    @patch("subprocess.run")
    def test_execute_json_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='{"status": "ok"}', stderr="")
        response = self.executor.execute(["backup"], mode="JSON")
        self.assertEqual(response.data, {"status": "ok"})
        self.assertEqual(response.warnings, "")
        self.assertEqual(response.raw, {"status": "ok"})

    @patch("subprocess.run")
    def test_execute_json_with_stderr_warnings(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout='{"status": "ok"}', stderr="Warning: low disk space"
        )
        response = self.executor.execute(["backup"], mode="JSON")
        self.assertEqual(response.data, {"status": "ok"})
        self.assertEqual(response.warnings, "Warning: low disk space")

    @patch("subprocess.run")
    def test_execute_json_failure_exit_code(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1, stdout='{"status": "error"}', stderr="Critical error"
        )
        with self.assertRaises(LudusaviExecutionError) as cm:
            self.executor.execute(["backup"], mode="JSON")
        self.assertEqual(cm.exception.returncode, 1)
        self.assertEqual(cm.exception.stderr, "Critical error")

    @patch("subprocess.run")
    def test_execute_json_contract_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="Invalid JSON output", stderr="")
        with self.assertRaises(LudusaviContractError):
            self.executor.execute(["backup"], mode="JSON")

    @patch("subprocess.run")
    def test_execute_text_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="ludusavi 0.31.0", stderr="")
        response = self.executor.execute(["--version"], mode="TEXT")
        self.assertEqual(response.data, "ludusavi 0.31.0")

    @patch.dict(os.environ, {"PATH": "/ambient/bin", "KEEP": "yes"}, clear=True)
    @patch("subprocess.run")
    def test_executor_merges_instance_env_for_run(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="ludusavi 0.31.0", stderr="")
        executor = LudusaviExecutor(self.prefix, env={"PATH": "/custom/bin", "EXTRA": "1"})

        executor.execute(["--version"], mode="TEXT")

        self.assertEqual(
            mock_run.call_args.kwargs["env"],
            {"PATH": "/custom/bin", "KEEP": "yes", "EXTRA": "1"},
        )

    @patch("subprocess.Popen")
    def test_execute_spawn_success(self, mock_popen):
        # Spawn mode should not wait for the process
        self.executor.execute(["gui"], mode="SPAWN")
        mock_popen.assert_called()

    @patch.dict(os.environ, {"PATH": "/ambient/bin"}, clear=True)
    @patch("subprocess.Popen")
    def test_executor_merges_instance_env_for_spawn(self, mock_popen):
        executor = LudusaviExecutor(self.prefix, env={"PATH": "/custom/bin"})

        executor.execute(["gui"], mode="SPAWN")

        self.assertEqual(mock_popen.call_args.kwargs["env"], {"PATH": "/custom/bin"})

    @patch("subprocess.run")
    def test_execute_stdin_json_serializes_empty_dict(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='{"status": "ok"}', stderr="")
        self.executor.execute(["api"], mode="STDIN_JSON", input_data={}, auto_api=False)
        self.assertEqual(mock_run.call_args.kwargs["input"], "{}")

    @patch("subprocess.run")
    def test_execute_stdin_json_serializes_empty_list(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='{"status": "ok"}', stderr="")
        self.executor.execute(["api"], mode="STDIN_JSON", input_data=[], auto_api=False)
        self.assertEqual(mock_run.call_args.kwargs["input"], "[]")

    @patch("subprocess.run")
    def test_execute_stdin_json_none_omits_payload(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='{"status": "ok"}', stderr="")
        self.executor.execute(["api"], mode="STDIN_JSON", input_data=None, auto_api=False)
        self.assertIsNone(mock_run.call_args.kwargs["input"])
