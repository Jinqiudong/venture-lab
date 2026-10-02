from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "dashboard" / "projects.json"
OUTPUT_PATH = ROOT / "dashboard" / "data.json"
API = "https://api.github.com"
TOKEN = os.getenv("PORTFOLIO_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")


def request_json(path: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "venture-lab-dashboard",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    request = urllib.request.Request(f"{API}{path}", headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def repo_metrics(repo: str) -> dict:
    encoded = repo.replace("/", "%2F")
    result = {
        "open_issues": None,
        "open_prs": None,
        "ci": "unknown",
        "latest_activity": None,
        "live": False,
        "error": None,
    }
    try:
        repo_info = request_json(f"/repos/{repo}")
        issues = request_json(f"/repos/{repo}/issues?state=open&per_page=100")
        pulls = request_json(f"/repos/{repo}/pulls?state=open&per_page=100")
        runs = request_json(f"/repos/{repo}/actions/runs?per_page=1")

        issue_count = sum(1 for item in issues if "pull_request" not in item)
        result["open_issues"] = issue_count
        result["open_prs"] = len(pulls)
        result["latest_activity"] = repo_info.get("pushed_at")

        workflow_runs = runs.get("workflow_runs", []) if isinstance(runs, dict) else []
        if workflow_runs:
            latest = workflow_runs[0]
            conclusion = latest.get("conclusion")
            status = latest.get("status")
            result["ci"] = conclusion or status or "unknown"
        else:
            result["ci"] = "no-runs"

        result["live"] = True
    except urllib.error.HTTPError as exc:
        if exc.code in {401, 403, 404}:
            result["error"] = "Private repository data unavailable. Configure PORTFOLIO_GITHUB_TOKEN."
        else:
            result["error"] = f"GitHub API error: HTTP {exc.code}"
    except Exception as exc:  # Keep dashboard generation resilient.
        result["error"] = f"Unable to refresh: {exc.__class__.__name__}"
    return result


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text())
    projects = []
    for project in config["projects"]:
        projects.append({**project, **repo_metrics(project["repo"])})

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "projects": projects,
    }
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
