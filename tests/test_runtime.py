import unittest

from orchestrator.runtime import (
    MAX_AUTO_FIX_CYCLES,
    auto_stop_marker,
    classify_runtime,
    fix_cycle_count,
    next_fix_marker,
)


class RuntimeGuardTests(unittest.TestCase):
    def test_fixer_attempt_is_counted_only_for_exact_head(self):
        comments = [
            "<!-- venture-fixer-attempt:abc1234 -->",
            "<!-- venture-fixer-attempt:def5678 -->",
        ]
        self.assertEqual(fix_cycle_count(comments, "abc1234"), 1)
        self.assertEqual(fix_cycle_count(comments, "fedcba9"), 0)
        self.assertEqual(
            next_fix_marker(comments, "fedcba9"),
            "<!-- venture-fixer-attempt:fedcba9 -->",
        )

    def test_legacy_fixer_comments_do_not_consume_new_head_budget(self):
        comments = [
            "### 🔧 Fixer\n\nAddressed reviewer findings.",
            "### 🔧 QA Fixer\n\nFixed test failure.",
        ]
        state = classify_runtime(comments, "fedcba9")
        self.assertEqual(state.fix_cycles, 0)
        self.assertFalse(state.stopped)
        self.assertTrue(state.auto_fix_allowed)

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

    def test_one_attempt_stops_exact_head(self):
        self.assertEqual(MAX_AUTO_FIX_CYCLES, 1)
        comments = ["<!-- venture-fixer-attempt:fedcba9 -->"]
        state = classify_runtime(comments, "fedcba9")
        self.assertEqual(state.fix_cycles, 1)
        self.assertTrue(state.stopped)
        self.assertEqual(state.stage, "human_handoff")
        self.assertFalse(state.auto_fix_allowed)

    def test_attempt_on_old_head_does_not_stop_new_head(self):
        comments = ["<!-- venture-fixer-attempt:old0001 -->"]
        state = classify_runtime(comments, "new0002")
        self.assertEqual(state.fix_cycles, 0)
        self.assertFalse(state.stopped)
        self.assertTrue(state.auto_fix_allowed)

    def test_explicit_auto_stop_marker(self):
        marker = auto_stop_marker("abcdef1")
        state = classify_runtime([marker], "abcdef1")
        self.assertTrue(state.stopped)
        self.assertEqual(state.stage, "human_handoff")


if __name__ == "__main__":
    unittest.main()
