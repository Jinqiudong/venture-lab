import unittest
from unittest import mock

from orchestrator.state import classify_stage
from scripts import generate_dashboard as dashboard


class HoldStageTests(unittest.TestCase):
    def test_hold_is_owner_held_not_ai_work(self):
        self.assertEqual(classify_stage("hold"), "needs_you")

    def test_hold_item_is_not_reset_to_ready_by_dependency_resolution(self):
        items = [
            {"issue": 8, "issue_state": "closed", "workflow_stage": "done"},
            {"issue": 9, "issue_state": "open", "workflow_stage": "hold", "blocked_by": [8]},
        ]
        resolved = dashboard.resolve_dependencies(items)
        self.assertEqual(resolved[1]["workflow_stage"], "hold")

    def _stage_for(self, pr: dict) -> dict:
        issue = {"title": "t", "html_url": "u", "state": "open"}
        with mock.patch.object(dashboard, "request_json", return_value=issue), \
                mock.patch.object(dashboard, "linked_pr", return_value=pr):
            return dashboard.workflow_item("o/r", {"issue": 9, "status": "blocked"})

    def test_pr_labeled_hold_maps_to_hold_stage(self):
        item = self._stage_for({"number": 34, "html_url": "p", "state": "open", "labels": [{"name": "hold"}]})
        self.assertEqual(item["workflow_stage"], "hold")
        self.assertTrue(item["needs_human"])

    def test_draft_pr_without_hold_is_ai_review_work(self):
        item = self._stage_for({"number": 34, "html_url": "p", "state": "open", "draft": True, "labels": []})
        self.assertEqual(item["workflow_stage"], "review")
        self.assertFalse(item.get("needs_human"))


class ParallelDispatchTests(unittest.TestCase):
    def _run(self, items):
        from scripts import orchestrate
        outputs = {}
        with mock.patch.object(orchestrate, "DATA_PATH") as path, \
                mock.patch.object(orchestrate, "failure_gate", return_value=(False, 0, False)), \
                mock.patch.object(orchestrate, "write_github_output", side_effect=outputs.update), \
                mock.patch("builtins.print"):
            path.exists.return_value = True
            path.read_text.return_value = __import__("json").dumps({"work_items": items})
            orchestrate.main()
        return outputs

    def test_dispatches_up_to_two_ready_issues_while_reviews_run(self):
        items = [
            {"repo": "o/r", "issue": 1, "workflow_stage": "review"},
            {"repo": "o/r", "issue": 2, "workflow_stage": "ready"},
            {"repo": "o/r", "issue": 3, "workflow_stage": "ready"},
            {"repo": "o/r", "issue": 4, "workflow_stage": "ready"},
        ]
        out = self._run(items)
        self.assertEqual(out["should_dispatch"], "true")
        self.assertEqual([i["issue"] for i in __import__("json").loads(out["dispatch_items"])], ["2", "3"])
        self.assertEqual(out["should_review"], "true")

    def test_no_dispatch_when_builders_are_at_capacity(self):
        items = [
            {"repo": "o/r", "issue": 1, "workflow_stage": "building"},
            {"repo": "o/r", "issue": 2, "workflow_stage": "coding"},
            {"repo": "o/r", "issue": 3, "workflow_stage": "ready"},
        ]
        out = self._run(items)
        self.assertEqual(out["should_dispatch"], "false")
        self.assertEqual(out["dispatch_items"], "[]")


if __name__ == "__main__":
    unittest.main()
