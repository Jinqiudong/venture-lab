import importlib.util
import unittest
from unittest import mock
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / ".github/actions/run-agent/run_claude.py"
spec = importlib.util.spec_from_file_location("run_claude", SCRIPT)
run_claude = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_claude)


class RunClaudeCommandTests(unittest.TestCase):
    def test_read_only_profile_allows_only_inspection_tools(self):
        cmd = run_claude.build_command("p", ":read-only", "", "")
        self.assertIn("--allowedTools", cmd)
        self.assertNotIn("bypassPermissions", cmd)
        for tool in ("Edit", "Write", "Bash"):
            self.assertNotIn(tool, cmd)

    def test_workspace_profile_can_edit_but_never_publish(self):
        cmd = run_claude.build_command("p", ":workspace", "", "medium")
        self.assertIn("bypassPermissions", cmd)
        self.assertIn("Bash(git push:*)", cmd)
        self.assertEqual(cmd[cmd.index("--effort") + 1], "medium")

    def test_research_profile_adds_web_tools_but_no_edits(self):
        cmd = run_claude.build_command("p", ":research", "", "")
        self.assertIn("WebSearch", cmd)
        self.assertIn("WebFetch", cmd)
        self.assertNotIn("bypassPermissions", cmd)
        for tool in ("Edit", "Write"):
            self.assertNotIn(tool, cmd)

    def test_schema_requests_structured_output(self):
        cmd = run_claude.build_command("p", ":read-only", '{"type":"object"}', "")
        self.assertEqual(cmd[cmd.index("--json-schema") + 1], '{"type":"object"}')

    def test_unknown_profile_is_rejected(self):
        with self.assertRaises(SystemExit):
            run_claude.build_command("p", ":danger", "", "")


class NormalizeSecretTests(unittest.TestCase):
    def test_line_breaks_and_spaces_are_removed(self):
        with mock.patch.dict(run_claude.os.environ, {"TOKEN": "sk-ant-oat01-abc\n def \r\n"}):
            run_claude.normalize_secret("TOKEN")
            self.assertEqual(run_claude.os.environ["TOKEN"], "sk-ant-oat01-abcdef")

    def test_blank_secret_is_unset(self):
        with mock.patch.dict(run_claude.os.environ, {"TOKEN": " \n"}):
            run_claude.normalize_secret("TOKEN")
            self.assertNotIn("TOKEN", run_claude.os.environ)


if __name__ == "__main__":
    unittest.main()
