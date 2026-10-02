from orchestrator.runtime import (
    MAX_AUTO_FIX_CYCLES,
    auto_stop_marker,
    classify_runtime,
    fix_cycle_count,
    next_fix_marker,
)


def test_fix_cycle_count_and_next_marker():
    comments = [
        "<!-- venture-fix-cycle:1 sha:abc1234 -->",
        "<!-- venture-fix-cycle:2 sha:def5678 -->",
    ]
    assert fix_cycle_count(comments) == 2
    assert next_fix_marker(comments, "fedcba9") == "<!-- venture-fix-cycle:3 sha:fedcba9 -->"


def test_human_ready_wins_for_current_sha():
    state = classify_runtime([
        "<!-- venture-review:abcdef1 -->",
        "<!-- venture-human-ready:abcdef1 -->",
    ], "abcdef1")
    assert state.stage == "human_handoff"
    assert state.human_ready is True
    assert state.auto_fix_allowed is False


def test_review_marker_for_current_sha():
    state = classify_runtime(["<!-- venture-review:abcdef1 -->"], "abcdef1")
    assert state.stage == "reviewing"
    assert state.auto_fix_allowed is True


def test_retry_cap_stops_automation():
    comments = [f"<!-- venture-fix-cycle:{i} sha:abc{i} -->" for i in range(1, MAX_AUTO_FIX_CYCLES + 1)]
    state = classify_runtime(comments, "latest01")
    assert state.fix_cycles == MAX_AUTO_FIX_CYCLES
    assert state.stopped is True
    assert state.stage == "human_handoff"
    assert state.auto_fix_allowed is False


def test_explicit_auto_stop_marker():
    marker = auto_stop_marker("abcdef1")
    state = classify_runtime([marker], "abcdef1")
    assert state.stopped is True
    assert state.stage == "human_handoff"
