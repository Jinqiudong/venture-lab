import unittest
from unittest import mock

from orchestrator.state import classify_stage
from scripts import generate_dashboard as dashboard


class DraftStageTests(unittest.TestCase):
    def test_draft_is_owner_held_not_ai_work(self):
        self.assertEqual(classify_stage("draft"), "needs_you")

    def test_draft_item_is_not_reset_to_ready_by_dependency_resolution(self):
        items = [
            {"issue": 8, "issue_state": "closed", "workflow_stage": "done"},
            {"issue": 9, "issue_state": "open", "workflow_stage": "draft", "blocked_by": [8]},
        ]
        resolved = dashboard.resolve_dependencies(items)
        self.assertEqual(resolved[1]["workflow_stage"], "draft")

    def test_open_draft_pr_maps_to_draft_stage(self):
        issue = {"title": "t", "html_url": "u", "state": "open"}
        pr = {"number": 34, "html_url": "p", "state": "open", "draft": True}
        with mock.patch.object(dashboard, "request_json", return_value=issue), \
                mock.patch.object(dashboard, "linked_pr", return_value=pr):
            item = dashboard.workflow_item("o/r", {"issue": 9, "status": "blocked"})
        self.assertEqual(item["workflow_stage"], "draft")
        self.assertTrue(item["needs_human"])

    def test_open_ready_pr_still_maps_to_review(self):
        issue = {"title": "t", "html_url": "u", "state": "open"}
        pr = {"number": 37, "html_url": "p", "state": "open", "draft": False}
        with mock.patch.object(dashboard, "request_json", return_value=issue), \
                mock.patch.object(dashboard, "linked_pr", return_value=pr):
            item = dashboard.workflow_item("o/r", {"issue": 38, "status": "ready"})
        self.assertEqual(item["workflow_stage"], "review")


if __name__ == "__main__":
    unittest.main()
