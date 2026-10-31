import unittest

from scripts import generate_dashboard as dashboard

NOW = dashboard.datetime(2026, 10, 31, 12, tzinfo=dashboard.timezone.utc)
HANDOFF = "<!-- venture-human-ready:{sha} -->\n## 👤 Needs You\n\n### Done\n- x\n\n### Your job\nTry it on a real iPhone.\n\n### How to review it\n1. y\n"


def pr(number, sha="abc", state="open"):
    return {"number": number, "state": state, "title": f"PR {number}", "html_url": f"p{number}", "head": {"sha": sha}}


def comment(number, body, created):
    return {"issue_url": f"https://api.github.com/repos/o/r/issues/{number}", "body": body, "created_at": created, "html_url": f"c{number}"}


class IndexPagingTests(unittest.TestCase):
    def test_open_pr_thread_is_fetched_beyond_the_repo_wide_comment_page(self):
        handoff = {"id": 1000, **comment(5, HANDOFF.format(sha="abc"), "2026-10-01T00:00:00Z")}
        busy = [{"id": i, **comment(7, "chatter", "2026-10-30T00:00:00Z")} for i in range(100)]

        def fake(path):
            if "/issues/5/comments" in path:
                return [handoff]
            if "/issues/comments" in path:
                return busy
            if "/pulls" in path:
                return [{**pr(5), "updated_at": "2026-10-31T00:00:00Z"}]
            if "/milestones" in path:
                raise RuntimeError("boom")
            return []

        original = dashboard.request_json
        dashboard.request_json = fake
        try:
            index = dashboard.repo_index("o/r")
        finally:
            dashboard.request_json = original
        self.assertEqual(len(dashboard.pending_handoffs("o/r", index)), 1)
        self.assertFalse(index["milestones_ok"])


class HandoffTests(unittest.TestCase):
    def test_handoff_on_current_head_needs_the_owner(self):
        index = {"pulls": [pr(5)], "comments": [comment(5, HANDOFF.format(sha="abc"), "2026-10-31T01:00:00Z")]}
        [handoff] = dashboard.pending_handoffs("o/r", index)
        self.assertEqual(handoff["pr"], 5)
        self.assertEqual(handoff["ask"], "Try it on a real iPhone.")

    def test_handoff_for_an_old_head_or_after_a_decision_is_resolved(self):
        stale = {"pulls": [pr(5, sha="new")], "comments": [comment(5, HANDOFF.format(sha="abc"), "2026-10-31T01:00:00Z")]}
        decided = {"pulls": [pr(5)], "comments": [
            comment(5, HANDOFF.format(sha="abc"), "2026-10-31T01:00:00Z"),
            comment(5, "<!-- venture-human-decision --> ship it", "2026-10-31T02:00:00Z"),
        ]}
        self.assertEqual(dashboard.pending_handoffs("o/r", stale), [])
        self.assertEqual(dashboard.pending_handoffs("o/r", decided), [])


class DeliveryTests(unittest.TestCase):
    def test_weekly_counts_median_and_projection(self):
        pulls = [
            {"created_at": "2026-10-29T10:00:00Z", "merged_at": "2026-10-29T12:00:00Z"},
            {"created_at": "2026-10-28T10:00:00Z", "merged_at": "2026-10-28T11:00:00Z"},
            {"created_at": "2026-10-20T10:00:00Z", "merged_at": "2026-10-21T10:00:00Z"},
            {"created_at": "2026-10-20T10:00:00Z", "merged_at": None},
        ]
        stats = dashboard.delivery_stats(pulls, NOW)
        self.assertEqual(len(stats["weekly"]), dashboard.TREND_WEEKS)
        self.assertEqual([w["merged"] for w in stats["weekly"][-2:]], [1, 2])
        self.assertEqual(stats["median_hours_to_merge"], 2.0)
        self.assertEqual(stats["per_week"], 0.75)
        [plan] = dashboard.milestone_plan([{"title": "M1", "open_issues": 3, "closed_issues": 1, "due_on": "2026-11-05T07:00:00Z", "state": "open"}], stats["per_week"], NOW)
        self.assertEqual(plan["due_on"], "2026-11-05")
        self.assertEqual(plan["projected_on"], "2026-11-28")


class StatusTests(unittest.TestCase):
    def test_owner_is_only_asked_for_product_judgment(self):
        self.assertTrue(dashboard.owner_decision({"workflow_stage": "decision"}))
        self.assertTrue(dashboard.owner_decision({"workflow_stage": "ready", "needs_human": True}))
        self.assertFalse(dashboard.owner_decision({"workflow_stage": "hold", "needs_human": True}))
        self.assertFalse(dashboard.owner_decision({"workflow_stage": "blocked_on_human", "needs_human": True}))

    def test_traffic_light(self):
        fresh = {"latest_activity": "2026-10-31T00:00:00Z"}
        old = {"latest_activity": "2026-10-20T00:00:00Z"}
        self.assertEqual(dashboard.project_status([{"workflow_stage": "review"}], [{"pr": 1}], fresh, NOW), "needs_you")
        self.assertEqual(dashboard.project_status([{"workflow_stage": "blocked_on_human"}], [], fresh, NOW), "stuck")
        self.assertEqual(dashboard.project_status([{"workflow_stage": "ready"}], [], old, NOW), "stalled")
        self.assertEqual(dashboard.project_status([{"workflow_stage": "ready"}], [], fresh, NOW), "moving")
        self.assertEqual(dashboard.project_status([{"workflow_stage": "merged"}], [], old, NOW), "quiet")


if __name__ == "__main__":
    unittest.main()
