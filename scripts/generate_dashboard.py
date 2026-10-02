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

        result["open_issues"] = sum(1 for item in issues if "pull_request" not in item)
        result["open_prs"] = len(pulls)
        result["latest_activity"] = repo_info.get("pushed_at")

        workflow_runs = runs.get("workflow_runs", []) if isinstance(runs, dict) else []
        if workflow_runs:
            latest = workflow_runs[0]
            result["ci"] = latest.get("conclusion") or latest.get("status") or "unknown"
        else:
            result["ci"] = "no-runs"
        result["live"] = True
    except urllib.error.HTTPError as exc:
        if exc.code in {401, 403, 404}:
            result["error"] = "Private repository data unavailable. Configure PORTFOLIO_GITHUB_TOKEN."
        else:
            result["error"] = f"GitHub API error: HTTP {exc.code}"
    except Exception as exc:
        result["error"] = f"Unable to refresh: {exc.__class__.__name__}"
    return result


def closes_issue(body: str | None, issue_number: int, repo: str) -> bool:
    if not body:
        return False
    owner, name = repo.split("/", 1)
    references = [
        rf"#\s*{issue_number}\b",
        rf"{re.escape(owner)}/{re.escape(name)}#\s*{issue_number}\b",
    ]
    verbs = r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)"
    return any(re.search(rf"(?i)\b{verbs}\s+{ref}", body) for ref in references)


def linked_pr(repo: str, issue_number: int) -> dict | None:
    """Return a PR that explicitly closes/fixes/resolves this issue.

    GitHub timeline cross-references include any PR that merely mentions an issue, so
    we additionally require a closing keyword in the PR body. This avoids treating
    text like `unblocks #4` as if the PR belongs to issue #4.
    """
    timeline = request_json(f"/repos/{repo}/issues/{issue_number}/timeline?per_page=100")
    candidates: list[dict] = []
    for event in timeline if isinstance(timeline, list) else []:
        if event.get("event") != "cross-referenced":
            continue
        source_issue = (event.get("source") or {}).get("issue") or {}
        if not source_issue.get("pull_request"):
            continue
        if closes_issue(source_issue.get("body"), issue_number, repo):
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
            if pr.get("state") == "open":
                enriched["workflow_stage"] = "review"
            elif pr.get("state") == "closed":
                enriched["workflow_stage"] = "merged"

        if issue.get("state") == "closed" and not enriched.get("pr"):
            enriched["workflow_stage"] = "done"
    except Exception:
        enriched.setdefault("title", f"Issue #{issue_number}")

    return enriched


def resolve_dependencies(items: list[dict]) -> list[dict]:
    by_issue = {item.get("issue"): item for item in items if item.get("issue")}
    for item in items:
        blockers = item.get("blocked_by") or []
        if not blockers or item.get("workflow_stage") in {"done", "merged", "review", "ci", "coding"}:
            continue
        unresolved = []
        for number in blockers:
            blocker = by_issue.get(number)
            if blocker is None:
                unresolved.append(number)
                continue
            complete = blocker.get("issue_state") == "closed" or blocker.get("workflow_stage") in {"done", "merged"}
            if not complete:
                unresolved.append(number)
        item["blocked_by"] = unresolved
        item["workflow_stage"] = "blocked" if unresolved else "ready"
        if not unresolved and item.get("issue_state") == "open":
            item["next_action"] = item.get("ready_action") or f"Start Issue #{item.get('issue')}"
    return items


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text())
    projects = []
    work_items = []

    for project in config["projects"]:
        repo = project["repo"]
        project_items = [workflow_item(repo, item) for item in project.get("work_items", [])]
        project_items = resolve_dependencies(project_items)
        enriched_project = {**project, **repo_metrics(repo), "work_items": project_items}
        projects.append(enriched_project)
        for item in project_items:
            work_items.append({**item, "project_name": project["name"], "project_stage": project["stage"]})

    actionable_stages = {"ready", "decision", "review"}
    needs_you = [
        item
        for item in work_items
        if item.get("workflow_stage") not in {"done", "merged", "blocked"}
        and (item.get("needs_human") or item.get("workflow_stage") in actionable_stages)
    ]

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "needs_you": needs_you,
        "work_items": work_items,
        "projects": projects,
    }
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
