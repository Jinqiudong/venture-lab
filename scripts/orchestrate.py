from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestrator.state import classify_stage

DATA_PATH = ROOT / "dashboard" / "data.json"
API = "https://api.github.com"
TOKEN = os.getenv("PORTFOLIO_GITHUB_TOKEN") or os.getenv("AGENT_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")
FAILURE_MARKER = "venture-checkpoint:agent-failed"
AUTO_STOP_MARKER = "venture-auto-stop"


def write_github_output(values: dict[str, str]) -> None:
    output_path = os.getenv("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as handle:
        for key, value in values.items():
            safe = str(value).replace("\n", " ").replace("\r", " ")
            handle.write(f"{key}={safe}\n")


def request_json(path: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "venture-lab-orchestrator",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    request = urllib.request.Request(f"{API}{path}", headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def failure_gate(repo: str, issue: int) -> tuple[bool, int]:
    """Return (auto_stop, failure_count) for unresolved repeated Builder failures."""
    try:
        comments = request_json(f"/repos/{repo}/issues/{issue}/comments?per_page=100")
    except Exception:
        # Fail open on telemetry trouble: never block work because GitHub comments could not be read.
        return False, 0

    bodies = [item.get("body") or "" for item in comments if isinstance(item, dict)]
    if any(AUTO_STOP_MARKER in body for body in bodies):
        return True, sum(FAILURE_MARKER in body for body in bodies)

    failure_count = sum(FAILURE_MARKER in body for body in bodies)
    return failure_count >= 2, failure_count


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
    review_pending = [
        item for item in active if item.get("workflow_stage") in {"review", "reviewing", "qa", "changes_requested"}
    ]

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
        "review_wakeup": bool(review_pending),
        "next_ready": None,
        "auto_stop": None,
    }

    outputs = {
        "should_dispatch": "false",
        "should_review": "true" if review_pending else "false",
        "auto_stop": "false",
        "repo": "",
        "issue": "",
        "project": "",
        "title": "",
        "failure_count": "0",
    }

    if not active:
        for candidate in items:
            if candidate.get("workflow_stage") != "ready":
                continue
            repo = candidate.get("repo") or ""
            issue = candidate.get("issue")
            if not repo or not issue:
                continue

            stopped, count = failure_gate(repo, int(issue))
            if stopped:
                decision["auto_stop"] = {
                    "project": candidate.get("project_name"),
                    "repo": repo,
                    "issue": issue,
                    "failure_count": count,
                    "action": "human_intervention",
                }
                outputs.update(
                    {
                        "auto_stop": "true",
                        "repo": repo,
                        "issue": str(issue),
                        "project": candidate.get("project_name") or "",
                        "title": candidate.get("title") or "",
                        "failure_count": str(count),
                    }
                )
                break

            decision["next_ready"] = {
                "project": candidate.get("project_name"),
                "repo": repo,
                "issue": issue,
                "title": candidate.get("title"),
                "action": "dispatch_builder",
            }
            outputs.update(
                {
                    "should_dispatch": "true",
                    "repo": repo,
                    "issue": str(issue),
                    "project": candidate.get("project_name") or "",
                    "title": candidate.get("title") or "",
                }
            )
            break

    write_github_output(outputs)
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
