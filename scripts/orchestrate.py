from __future__ import annotations

import json
from pathlib import Path

from orchestrator.state import classify_stage, first_ready

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "dashboard" / "data.json"


def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit("dashboard/data.json not found; run generate_dashboard.py first")

    data = json.loads(DATA_PATH.read_text())
    items = data.get("work_items", [])
    active = [item for item in items if classify_stage(item.get("workflow_stage", "blocked")) == "ai_team" and item.get("workflow_stage") != "ready"]
    next_ready = None if active else first_ready(items)

    decision = {
        "active_ai_work": [
            {
                "project": item.get("project_name"),
                "repo": item.get("repo"),
                "issue": item.get("issue"),
                "stage": item.get("workflow_stage"),
            }
            for item in active
        ],
        "next_ready": None,
    }

    if next_ready:
        decision["next_ready"] = {
            "project": next_ready.get("project_name"),
            "repo": next_ready.get("repo"),
            "issue": next_ready.get("issue"),
            "title": next_ready.get("title"),
            "action": "dispatch_builder",
        }

    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
