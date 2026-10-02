from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestrator.state import classify_stage, first_ready

DATA_PATH = ROOT / "dashboard" / "data.json"


def write_github_output(values: dict[str, str]) -> None:
    output_path = os.getenv("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as handle:
        for key, value in values.items():
            safe = str(value).replace("\n", " ").replace("\r", " ")
            handle.write(f"{key}={safe}\n")


def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit("dashboard/data.json not found; run generate_dashboard.py first")

    data = json.loads(DATA_PATH.read_text())
    items = data.get("work_items", [])
    active = [
        item
        for item in items
        if classify_stage(item.get("workflow_stage", "blocked")) == "ai_team"
        and item.get("workflow_stage") != "ready"
    ]
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

    outputs = {
        "should_dispatch": "false",
        "repo": "",
        "issue": "",
        "project": "",
        "title": "",
    }

    if next_ready:
        decision["next_ready"] = {
            "project": next_ready.get("project_name"),
            "repo": next_ready.get("repo"),
            "issue": next_ready.get("issue"),
            "title": next_ready.get("title"),
            "action": "dispatch_builder",
        }
        outputs.update(
            {
                "should_dispatch": "true",
                "repo": next_ready.get("repo") or "",
                "issue": str(next_ready.get("issue") or ""),
                "project": next_ready.get("project_name") or "",
                "title": next_ready.get("title") or "",
            }
        )

    write_github_output(outputs)
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
