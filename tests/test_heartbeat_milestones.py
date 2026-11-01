import json
import tempfile
import unittest
from unittest import mock

from scripts import generate_dashboard as dashboard
from scripts import heartbeat, milestones

UTC = heartbeat.timezone.utc


class QuotaResetTests(unittest.TestCase):
    def test_reset_clock_time_is_the_next_occurrence(self):
        failed = heartbeat.datetime(2026, 10, 31, 5, 16, tzinfo=UTC)
        message = "Claude Code failed (exit 1): You've hit your 5-hour limit · resets 8am (UTC)"
        self.assertEqual(heartbeat.quota_reset_at(message, failed), heartbeat.datetime(2026, 10, 31, 8, 0, tzinfo=UTC))

    def test_reset_earlier_in_the_day_means_tomorrow_and_minutes_are_kept(self):
        failed = heartbeat.datetime(2026, 10, 31, 22, 0, tzinfo=UTC)
        reset = heartbeat.quota_reset_at("You've hit your 5-hour limit · resets 1:30am (UTC)", failed)
        self.assertEqual(reset, heartbeat.datetime(2026, 11, 1, 1, 30, tzinfo=UTC))

    def test_pm_and_unparsed_limits(self):
        failed = heartbeat.datetime(2026, 10, 31, 9, 0, tzinfo=UTC)
        self.assertEqual(heartbeat.quota_reset_at("hit your limit · resets 12pm (UTC)", failed).hour, 12)
        self.assertEqual(heartbeat.quota_reset_at("You've hit your weekly limit", failed), failed + heartbeat.QUOTA_FALLBACK)
        self.assertIsNone(heartbeat.quota_reset_at("Process completed with exit code 1.", failed))

    def setUp(self):
        budget = {"remaining": 4000, "limit": 5000, "used": 1000, "reset": "2026-10-31T10:00:00+00:00"}
        for name, value in (("work_waiting", 2), ("api_budget", budget)):
            patcher = mock.patch.object(heartbeat, name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_tick_waits_out_the_limit_without_dispatching(self):
        now = heartbeat.datetime(2026, 10, 31, 6, 0, tzinfo=UTC)
        with mock.patch.object(heartbeat, "paused_until", return_value=now.replace(hour=8)), \
                mock.patch.object(heartbeat, "dispatch") as dispatch:
            sample = heartbeat.tick(now)
        self.assertEqual(sample["state"], "paused")
        self.assertEqual(sample["resume"], "2026-10-31T08:00:00+00:00")
        dispatch.assert_not_called()

    def test_tick_protects_a_nearly_spent_api_budget(self):
        now = heartbeat.datetime(2026, 10, 31, 9, 0, tzinfo=UTC)
        low = {"remaining": 120, "limit": 5000, "used": 4880, "reset": "2026-10-31T09:40:00+00:00"}
        with mock.patch.object(heartbeat, "paused_until", return_value=None), \
                mock.patch.object(heartbeat, "api_budget", return_value=low), \
                mock.patch.object(heartbeat, "dispatch") as dispatch:
            sample = heartbeat.tick(now)
        self.assertEqual(sample["state"], "api_guard")
        dispatch.assert_not_called()

    def test_tick_dispatches_only_when_idle_and_labels_the_state(self):
        now = heartbeat.datetime(2026, 10, 31, 9, 0, tzinfo=UTC)
        with mock.patch.object(heartbeat, "paused_until", return_value=None), \
                mock.patch.object(heartbeat.milestones, "advance", return_value=[]), \
                mock.patch.object(heartbeat, "agent_busy", side_effect=[True, False]), \
                mock.patch.object(heartbeat, "dispatch") as dispatch:
            self.assertEqual(heartbeat.tick(now)["state"], "working")
            dispatch.assert_not_called()
            self.assertEqual(heartbeat.tick(now)["state"], "idle_with_work")
            dispatch.assert_called_once_with("orchestrator.yml")


class MilestoneTests(unittest.TestCase):
    def test_slug(self):
        self.assertEqual(milestones.slug("M1: Meet your cat!"), "m1-meet-your-cat")
        self.assertEqual(milestones.slug("梦"), "milestone")

    def test_only_a_plain_owner_comment_after_the_checklist_accepts(self):
        since = "2026-10-31T10:00:00Z"
        owner = {"login": "Jinqiudong"}
        ok = {"created_at": "2026-10-31T11:00:00Z", "user": owner, "body": "looks great /accept"}
        zh = {"created_at": "2026-10-31T11:00:00Z", "user": owner, "body": "验收通过"}
        early = {**ok, "created_at": "2026-10-31T09:00:00Z"}
        agent = {**ok, "body": "<!-- venture-try:5 -->\\nthen comment /accept"}
        other = {**ok, "user": {"login": "someone"}}
        quoted = {**ok, "body": "comment `/accept` to ship"}
        self.assertTrue(milestones.owner_accepts(ok, "Jinqiudong", since))
        self.assertTrue(milestones.owner_accepts(zh, "Jinqiudong", since))
        for comment in (early, agent, other, quoted):
            self.assertFalse(milestones.owner_accepts(comment, "Jinqiudong", since))

    def test_qa_try_note_only_when_qa_asked_for_a_person(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump({"verdict": "pass", "needs_human": True, "human_validation": "Hold the ring and speak."}, handle)
        self.assertEqual(milestones.qa_try_note(handle.name), "Hold the ring and speak.")
        with open(handle.name, "w") as again:
            json.dump({"verdict": "pass", "needs_human": False, "human_validation": "x"}, again)
        self.assertEqual(milestones.qa_try_note(handle.name), "")
        self.assertEqual(milestones.qa_try_note(None), "")

    def test_ci_state_of_the_milestone_pr(self):
        run = lambda status="completed", conclusion="success", rid=1: {
            "id": rid, "event": "pull_request", "status": status, "conclusion": conclusion}
        ran = lambda r: [{"steps": [{"name": "build"}]}]
        refused = lambda r: [{"steps": []}]
        self.assertEqual(milestones.ci_state([], ran), "none")
        self.assertEqual(milestones.ci_state([{**run(), "event": "workflow_run"}], ran), "none")
        self.assertEqual(milestones.ci_state([run(), run("in_progress", None)], ran), "pending")
        self.assertEqual(milestones.ci_state([run(), run(conclusion="skipped")], ran), "passed")
        self.assertEqual(milestones.ci_state([run(conclusion="failure")], ran), "failed")
        self.assertEqual(milestones.ci_state([run(conclusion="failure")], refused), "blocked")

    def test_after_merge_into_the_default_branch_does_nothing(self):
        with mock.patch.object(milestones, "gh") as gh:
            milestones.after_merge("o/r", 5, 9, "main", "main", None)
        gh.assert_not_called()

    def test_after_merge_into_a_milestone_closes_the_issue_and_opens_the_milestone_pr(self):
        with mock.patch.object(milestones, "gh") as gh, \
                mock.patch.object(milestones, "open_pr") as open_pr, \
                mock.patch.object(milestones, "add_try_note") as add_note:
            milestones.after_merge("o/r", 5, 9, "milestone/m1", "main", None)
        self.assertEqual(gh.call_args.args[:3], ("issue", "close", "9"))
        open_pr.assert_called_once_with("o/r", "milestone/m1")
        add_note.assert_called_once_with("o/r", "milestone/m1", 5, "")


class AcceptanceOnDashboardTests(unittest.TestCase):
    def test_finished_milestone_waits_for_the_owner_until_accepted(self):
        pr = {"number": 12, "state": "open", "title": "🏁 Milestone: M1", "html_url": "p12",
              "head": {"ref": "milestone/m1", "sha": "abc"}}

        def comment(body, created):
            return {"issue_url": "https://api.github.com/repos/o/r/issues/12", "body": body, "created_at": created,
                    "user": {"login": "o"}, "html_url": "c"}

        checklist = comment("<!-- venture-acceptance-ready:abc -->\\n## ready", "2026-10-31T10:00:00Z")
        index = {"pulls": [pr], "comments": [checklist]}
        [item] = dashboard.pending_acceptances("o/r", index)
        self.assertTrue(item["acceptance"])
        index["comments"].append(comment("/accept", "2026-10-31T11:00:00Z"))
        self.assertEqual(dashboard.pending_acceptances("o/r", index), [])


if __name__ == "__main__":
    unittest.main()
