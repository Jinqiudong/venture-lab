from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "dashboard" / "projects.json"
OUTPUT_PATH = ROOT / "dashboard" / "data.json"
API = "https://api.github.com"
TOKEN = os.getenv("PORTFOLIO_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")

HUMAN_STAGES = {"decision", "human_handoff", "blocked_on_human"}
AI_STAGES = {"ready", "coding", "building", "ci", "review", "reviewing", "qa", "changes_requested"}
DONE_STAGES = {"done", "merged"}


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
    result = {"open_issues": None, "open_prs": None, "ci": "unknown", "latest_activity": None, "live": False, "error": None}
    try:
        repo_info = request_json(f"/repos/{repo}")
        issues = request_json(f"/repos/{repo}/issues?state=open&per_page=100")
        pulls = request_json(f"/repos/{repo}/pulls?state=open&per_page=100")
        runs = request_json(f"/repos/{repo}/actions/runs?per_page=1")
        result["open_issues"] = sum(1 for item in issues if "pull_request" not in item)
        result["open_prs"] = len(pulls)
        result["latest_activity"] = repo_info.get("pushed_at")
        workflow_runs = runs.get("workflow_runs", []) if isinstance(runs, dict) else []
        result["ci"] = (workflow_runs[0].get("conclusion") or workflow_runs[0].get("status") or "unknown") if workflow_runs else "no-runs"
        result["live"] = True
    except urllib.error.HTTPError as exc:
        result["error"] = "Private repository data unavailable. Configure PORTFOLIO_GITHUB_TOKEN." if exc.code in {401, 403, 404} else f"GitHub API error: HTTP {exc.code}"
    except Exception as exc:
        result["error"] = f"Unable to refresh: {exc.__class__.__name__}"
    return result


def closes_issue(body: str | None, issue_number: int, repo: str) -> bool:
    if not body:
        return False
    owner, name = repo.split("/", 1)
    references = [rf"#\s*{issue_number}\b", rf"{re.escape(owner)}/{re.escape(name)}#\s*{issue_number}\b"]
    verbs = r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)"
    return any(re.search(rf"(?i)\b{verbs}\s+{ref}", body) for ref in references)


def linked_pr(repo: str, issue_number: int) -> dict | None:
    timeline = request_json(f"/repos/{repo}/issues/{issue_number}/timeline?per_page=100")
    candidates: list[dict] = []
    for event in timeline if isinstance(timeline, list) else []:
        if event.get("event") != "cross-referenced":
            continue
        source_issue = (event.get("source") or {}).get("issue") or {}
        if source_issue.get("pull_request") and closes_issue(source_issue.get("body"), issue_number, repo):
            candidates.append(source_issue)
    if not candidates:
        return None
    candidates.sort(key=lambda pr: pr.get("updated_at") or pr.get("created_at") or "", reverse=True)
    return candidates[0]


def workflow_item(repo: str, item: dict) -> dict:
    enriched = dict(item)
    issue_number = item.get("issue")
    enriched.setdefault("repo", repo)
    enriched.setdefault("issue_url", None)
    enriched.setdefault("issue_state", None)
    enriched.setdefault("pr", None)
    enriched.setdefault("pr_url", None)
    enriched.setdefault("ci", None)
    enriched.setdefault("workflow_stage", item.get("status", "ready"))
    enriched.setdefault("human_handoff", item.get("human_handoff"))
    if not issue_number:
        enriched.setdefault("title", item.get("title", "Work item"))
        return enriched
    try:
        issue = request_json(f"/repos/{repo}/issues/{issue_number}")
        enriched["title"] = issue.get("title") or f"Issue #{issue_number}"
        enriched["issue_url"] = issue.get("html_url")
        enriched["issue_state"] = issue.get("state")
        pr = linked_pr(repo, issue_number)
        if pr:
            enriched["pr"] = pr.get("number")
            enriched["pr_url"] = pr.get("html_url")
            enriched["workflow_stage"] = "review" if pr.get("state") == "open" else "merged"
        if issue.get("state") == "closed" and not enriched.get("pr"):
            enriched["workflow_stage"] = "done"
    except Exception:
        enriched.setdefault("title", f"Issue #{issue_number}")
    return enriched


def resolve_dependencies(items: list[dict]) -> list[dict]:
    by_issue = {item.get("issue"): item for item in items if item.get("issue")}
    for item in items:
        blockers = item.get("blocked_by") or []
        if not blockers or item.get("workflow_stage") in DONE_STAGES | AI_STAGES | HUMAN_STAGES:
            continue
        unresolved = []
        for number in blockers:
            blocker = by_issue.get(number)
            if blocker is None:
                unresolved.append(number)
                continue
            complete = blocker.get("issue_state") == "closed" or blocker.get("workflow_stage") in DONE_STAGES
            if not complete:
                unresolved.append(number)
        item["blocked_by"] = unresolved
        item["workflow_stage"] = "blocked" if unresolved else "ready"
        if not unresolved and item.get("issue_state") == "open":
            item["next_action"] = item.get("ready_action") or f"Builder should start Issue #{item.get('issue')}"
    return items


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text())
    projects = []
    work_items = []
    for project in config["projects"]:
        repo = project["repo"]
        project_items = resolve_dependencies([workflow_item(repo, item) for item in project.get("work_items", [])])
        projects.append({**project, **repo_metrics(repo), "work_items": project_items})
        work_items.extend({**item, "project_name": project["name"], "project_stage": project["stage"]} for item in project_items)

    needs_you = [item for item in work_items if item.get("needs_human") or item.get("workflow_stage") in HUMAN_STAGES]
    ai_team = [item for item in work_items if item.get("workflow_stage") in AI_STAGES and not item.get("needs_human")]
    queue = [item for item in work_items if item.get("workflow_stage") == "blocked"]

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "needs_you": needs_you,
        "ai_team": ai_team,
        "queue": queue,
        "work_items": work_items,
        "projects": projects,
    }
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
