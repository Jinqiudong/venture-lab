from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

HUMAN_STAGES = {"decision", "human_handoff", "blocked_on_human"}
AI_STAGES = {"ready", "building", "reviewing", "qa", "changes_requested", "coding", "ci", "review"}
DONE_STAGES = {"done", "merged"}
QUEUE_STAGES = {"blocked"}

ALLOWED_TRANSITIONS = {
    "blocked": {"ready", "blocked_on_human"},
    "ready": {"building", "blocked_on_human"},
    "building": {"reviewing", "changes_requested", "blocked_on_human"},
    "reviewing": {"qa", "changes_requested", "blocked_on_human"},
    "qa": {"human_handoff", "changes_requested", "blocked_on_human"},
    "changes_requested": {"building", "blocked_on_human"},
    "human_handoff": {"done", "changes_requested"},
    "blocked_on_human": {"ready", "building", "done"},
}


@dataclass(frozen=True)
class HumanHandoff:
    type: str
    title: str
    what_changed: str
    what_you_need_to_do: str
    where_to_look: str | None = None
    questions: tuple[str, ...] = ()
    approve_action: str | None = None

    def as_dict(self) -> dict:
        return {
            "type": self.type,
            "title": self.title,
            "what_changed": self.what_changed,
            "what_you_need_to_do": self.what_you_need_to_do,
            "where_to_look": self.where_to_look,
            "questions": list(self.questions),
            "approve_action": self.approve_action,
        }


def can_transition(current: str, target: str) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())


def classify_stage(stage: str) -> str:
    if stage in HUMAN_STAGES:
        return "needs_you"
    if stage in AI_STAGES:
        return "ai_team"
    if stage in QUEUE_STAGES:
        return "queue"
    if stage in DONE_STAGES:
        return "done"
    return "queue"


def first_ready(items: Iterable[dict]) -> dict | None:
    for item in items:
        if item.get("workflow_stage") == "ready":
            return item
    return None
