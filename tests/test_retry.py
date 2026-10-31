import unittest
from unittest import mock

from orchestrator import retry
from scripts import generate_dashboard as dashboard
from scripts import orchestrate

OWNER = {"login": "o"}


def comment(body, created, issue=2, user=OWNER):
    return {"body": body, "created_at": created, "user": user, "issue_url": f"https://api.github.com/repos/o/r/issues/{issue}"}


FAILED_1 = comment("<!-- venture-checkpoint:agent-failed:1 -->", "2026-10-31T01:00:00Z")
FAILED_2 = comment("<!-- venture-checkpoint:agent-failed:2 -->", "2026-10-31T02:00:00Z")
STOP = comment("<!-- venture-auto-stop -->\n### 🛑 Auto-stop", "2026-10-31T02:01:00Z")


class RetryTests(unittest.TestCase):
    def test_only_plain_owner_comments_retry(self):
        self.assertTrue(retry.is_retry(comment("/retry", "t"), "o"))
        self.assertTrue(retry.is_retry(comment("token fixed, 重试", "t"), "o"))
        self.assertFalse(retry.is_retry(comment("/retry", "t", user={"login": "x"}), "o"))
        self.assertFalse(retry.is_retry(comment("<!-- venture-x --> /retry", "t"), "o"))
        self.assertFalse(retry.is_retry(comment("comment `/retry` to resume", "t"), "o"))

    def test_failure_gate_ignores_failures_before_retry(self):
        comments = [FAILED_1, FAILED_2, STOP]
        with mock.patch.object(orchestrate, "request_json", return_value=comments):
            self.assertEqual(orchestrate.failure_gate("o/r", 2), (True, 2, True))
        with mock.patch.object(orchestrate, "request_json", return_value=comments + [comment("/retry", "2026-10-31T03:00:00Z")]):
            self.assertEqual(orchestrate.failure_gate("o/r", 2), (False, 0, False))

    def test_dashboard_stops_clear_after_retry(self):
        responses = {"comments": [STOP]}

        def fake(path):
            if "/issues/comments" in path:
                return responses["comments"]
            return []

        with mock.patch.object(dashboard, "request_json", side_effect=fake):
            self.assertEqual(dashboard.repo_index("o/r")["stops"], {2})
            responses["comments"] = [STOP, comment("/retry", "2026-10-31T03:00:00Z")]
            self.assertEqual(dashboard.repo_index("o/r")["stops"], set())


if __name__ == "__main__":
    unittest.main()
