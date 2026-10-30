import importlib.util
import unittest
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

    def test_schema_requests_structured_output(self):
        cmd = run_claude.build_command("p", ":read-only", '{"type":"object"}', "")
        self.assertEqual(cmd[cmd.index("--json-schema") + 1], '{"type":"object"}')

    def test_unknown_profile_is_rejected(self):
        with self.assertRaises(SystemExit):
            run_claude.build_command("p", ":danger", "", "")


if __name__ == "__main__":
    unittest.main()
