import unittest
from unittest import mock

from scripts import generate_dashboard as dashboard


class RepoIndexTests(unittest.TestCase):
    def test_work_items_resolve_from_the_index_without_per_item_calls(self):
        index = {
            "issues": {9: {"title": "t", "html_url": "u", "state": "open"}},
            "pulls": [{"number": 34, "html_url": "p", "state": "open", "body": "Closes #9", "labels": [], "updated_at": "2026-10-31"}],
            "stops": set(),
        }
        with mock.patch.object(dashboard, "request_json", side_effect=AssertionError("no per-item calls")):
            item = dashboard.workflow_item("o/r", {"issue": 9, "status": "blocked"}, index)
        self.assertEqual(item["workflow_stage"], "review")
        self.assertEqual(item["pr"], 34)

    def test_auto_stop_marker_comes_from_the_index(self):
        index = {"issues": {7: {"title": "t", "html_url": "u", "state": "open"}}, "pulls": [], "stops": {7}}
        with mock.patch.object(dashboard, "request_json", side_effect=AssertionError("no per-item calls")):
            item = dashboard.workflow_item("o/r", {"issue": 7, "status": "ready"}, index)
        self.assertEqual(item["workflow_stage"], "blocked_on_human")

    def test_recent_merged_reuses_index_pulls(self):
        now = dashboard.datetime(2026, 10, 31, tzinfo=dashboard.timezone.utc)
        index = {"issues": {}, "stops": set(), "pulls": [
            {"number": 1, "title": "a", "html_url": "x", "merged_at": "2026-10-30T10:00:00Z"},
            {"number": 2, "title": "b", "html_url": "y", "merged_at": None},
            {"number": 3, "title": "c", "html_url": "z", "merged_at": "2026-09-01T10:00:00Z"},
        ]}
        with mock.patch.object(dashboard, "request_json", side_effect=AssertionError("no extra calls")):
            merged = dashboard.recent_merged("o/r", now, index)
        self.assertEqual([pr["number"] for pr in merged], [1])


if __name__ == "__main__":
    unittest.main()
