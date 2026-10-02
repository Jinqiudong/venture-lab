import unittest

from orchestrator.runtime import (
    MAX_AUTO_FIX_CYCLES,
    auto_stop_marker,
    classify_runtime,
    fix_cycle_count,
    next_fix_marker,
)


class RuntimeGuardTests(unittest.TestCase):
    def test_fix_cycle_count_and_next_marker(self):
        comments = [
            "<!-- venture-fix-cycle:1 sha:abc1234 -->",
            "<!-- venture-fix-cycle:2 sha:def5678 -->",
        ]
        self.assertEqual(fix_cycle_count(comments), 2)
        self.assertEqual(
            next_fix_marker(comments, "fedcba9"),
            "<!-- venture-fix-cycle:3 sha:fedcba9 -->",
        )

    def test_existing_fixer_comments_count_as_cycles(self):
        comments = [
            "### 🔧 Fixer\n\nAddressed reviewer findings.",
            "### 🔧 QA Fixer\n\nFixed test failure.",
            "### 🔧 Fixer\n\nSecond reviewer pass fix.",
        ]
        self.assertEqual(fix_cycle_count(comments), 3)
        state = classify_runtime(comments, "fedcba9")
        self.assertTrue(state.stopped)
        self.assertFalse(state.auto_fix_allowed)

    def test_human_ready_wins_for_current_sha(self):
        state = classify_runtime([
            "<!-- venture-review:abcdef1 -->",
            "<!-- venture-human-ready:abcdef1 -->",
        ], "abcdef1")
        self.assertEqual(state.stage, "human_handoff")
        self.assertTrue(state.human_ready)
        self.assertFalse(state.auto_fix_allowed)

    def test_review_marker_for_current_sha(self):
        state = classify_runtime(["<!-- venture-review:abcdef1 -->"], "abcdef1")
        self.assertEqual(state.stage, "reviewing")
        self.assertTrue(state.auto_fix_allowed)

    def test_retry_cap_stops_automation(self):
        shas = ["abc0001", "abc0002", "abc0003"]
        comments = [
            f"<!-- venture-fix-cycle:{i} sha:{shas[i - 1]} -->"
            for i in range(1, MAX_AUTO_FIX_CYCLES + 1)
        ]
        state = classify_runtime(comments, "fedcba9")
        self.assertEqual(state.fix_cycles, MAX_AUTO_FIX_CYCLES)
        self.assertTrue(state.stopped)
        self.assertEqual(state.stage, "human_handoff")
        self.assertFalse(state.auto_fix_allowed)

    def test_explicit_auto_stop_marker(self):
        marker = auto_stop_marker("abcdef1")
        state = classify_runtime([marker], "abcdef1")
        self.assertTrue(state.stopped)
        self.assertEqual(state.stage, "human_handoff")


if __name__ == "__main__":
    unittest.main()
