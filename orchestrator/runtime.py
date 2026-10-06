from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

MAX_AUTO_FIX_CYCLES = 1

FIX_MARKER_RE = re.compile(r"<!--\s*venture-fix-cycle:(\d+)(?:\s+sha:([0-9a-f]{7,40}))?\s*-->", re.I)
REVIEW_MARKER_RE = re.compile(r"<!--\s*venture-review:([0-9a-f]{7,40})\s*-->", re.I)
QA_MARKER_RE = re.compile(r"<!--\s*venture-qa:([0-9a-f]{7,40})\s*-->", re.I)
HUMAN_MARKER_RE = re.compile(r"<!--\s*venture-human-ready:([0-9a-f]{7,40})\s*-->", re.I)
AUTO_STOP_RE = re.compile(r"<!--\s*venture-auto-stop(?::([0-9a-f]{7,40}))?\s*-->", re.I)


@dataclass(frozen=True)
class RuntimeState:
    stage: str
    fix_cycles: int
    auto_fix_allowed: bool
    human_ready: bool
    stopped: bool


def _matches(pattern: re.Pattern[str], comments: Iterable[str]) -> list[re.Match[str]]:
    found: list[re.Match[str]] = []
    for body in comments:
        found.extend(pattern.finditer(body or ""))
    return found


def fix_cycle_count(comments: Iterable[str], head_sha: str = "") -> int:
    wanted = (head_sha or "").lower()
    if not wanted:
        return 0
    return sum(
        1 for match in _matches(FIX_MARKER_RE, comments)
        if (match.group(1) or "").lower() == wanted
    )


def has_sha_marker(pattern: re.Pattern[str], comments: Iterable[str], head_sha: str) -> bool:
    wanted = (head_sha or "").lower()
    if not wanted:
        return False
    return any((match.group(1) or "").lower() == wanted for match in _matches(pattern, comments))


def is_auto_stopped(comments: Iterable[str], head_sha: str) -> bool:
    wanted = (head_sha or "").lower()
    for match in _matches(AUTO_STOP_RE, comments):
        marker_sha = (match.group(1) or "").lower()
        if not marker_sha or marker_sha == wanted:
            return True
    return False


def classify_runtime(comments: Iterable[str], head_sha: str) -> RuntimeState:
    bodies = list(comments)
    cycles = fix_cycle_count(bodies, head_sha)
    human_ready = has_sha_marker(HUMAN_MARKER_RE, bodies, head_sha)
    stopped = is_auto_stopped(bodies, head_sha) or cycles >= MAX_AUTO_FIX_CYCLES

    if human_ready or stopped:
        stage = "human_handoff"
    elif has_sha_marker(QA_MARKER_RE, bodies, head_sha):
        stage = "qa"
    elif has_sha_marker(REVIEW_MARKER_RE, bodies, head_sha):
        stage = "reviewing"
    else:
        stage = "review_pending"

    return RuntimeState(
        stage=stage,
        fix_cycles=cycles,
        auto_fix_allowed=not stopped and not human_ready,
        human_ready=human_ready,
        stopped=stopped,
    )


def next_fix_marker(comments: Iterable[str], head_sha: str) -> str:
    return f"<!-- venture-fixer-attempt:{head_sha} -->"


def auto_stop_marker(head_sha: str) -> str:
    return f"<!-- venture-auto-stop:{head_sha} -->"
