from __future__ import annotations

import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "dashboard" / "projects.json"
OUTPUT = ROOT / "dashboard" / "checkpoints.json"
API = "https://api.github.com"
TOKEN = os.getenv("PORTFOLIO_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")


def request_json(path: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "venture-lab-checkpoints",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    request = urllib.request.Request(f"{API}{path}", headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def closes_issue(body: str | None, issue_number: int) -> bool:
    if not body:
        return False
    return bool(re.search(rf"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#\s*{issue_number}\b", body))


def linked_pr(repo: str, issue_number: int) -> dict | None:
    timeline = request_json(f"/repos/{repo}/issues/{issue_number}/timeline?per_page=100")
    matches = []
    for event in timeline if isinstance(timeline, list) else []:
        if event.get("event") != "cross-referenced":
            continue
        source = (event.get("source") or {}).get("issue") or {}
        if source.get("pull_request") and closes_issue(source.get("body"), issue_number):
            matches.append(source)
    if not matches:
        return None
    matches.sort(key=lambda item: item.get("updated_at") or item.get("created_at") or "", reverse=True)
    return matches[0]


def first_plain_line(body: str) -> str:
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("<!--") or line.startswith("###") or line.startswith("####"):
            continue
        line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
        line = re.sub(r"`([^`]+)`", r"\1", line)
        if line.startswith("-"):
            line = line.lstrip("- ")
        return line[:220]
    return "Checkpoint recorded."


def checkpoint_from_comment(comment: dict, url: str) -> dict | None:
    body = comment.get("body") or ""
    created_at = comment.get("created_at")
    if "venture-checkpoint:agent-failed" in body:
        title = "Agent failed"
        match = re.search(r"###\s+❌\s+(.+)", body)
        if match:
            title = match.group(1).strip()
        return {"kind": "error", "title": title, "note": first_plain_line(body), "at": created_at, "url": url}
    if "venture-checkpoint:builder-start" in body:
        return {"kind": "builder", "title": "Builder started", "note": first_plain_line(body), "at": created_at, "url": url}
    if "venture-review:" in body:
        verdict = re.search(r"Verdict:\*\*\s*`?([^`\n]+)", body)
        label = verdict.group(1).strip() if verdict else "reviewed"
        return {"kind": "review", "title": f"Reviewer: {label}", "note": first_plain_line(body), "at": created_at, "url": url}
    if "venture-qa:" in body:
        verdict = re.search(r"Verdict:\*\*\s*`?([^`\n]+)", body)
        label = verdict.group(1).strip() if verdict else "completed"
        return {"kind": "qa", "title": f"QA: {label}", "note": first_plain_line(body), "at": created_at, "url": url}
    if "venture-human-ready:" in body:
        return {"kind": "human", "title": "Ready for you", "note": "AI review and QA reached the human checkpoint.", "at": created_at, "url": url}
    return None


def item_checkpoints(repo: str, issue_number: int) -> list[dict]:
    checkpoints: list[dict] = []
    issue_url = f"https://github.com/{repo}/issues/{issue_number}"
    comments = request_json(f"/repos/{repo}/issues/{issue_number}/comments?per_page=100")
    for comment in comments if isinstance(comments, list) else []:
        item = checkpoint_from_comment(comment, issue_url)
        if item:
            checkpoints.append(item)

    pr = linked_pr(repo, issue_number)
    if pr:
        pr_number = pr.get("number")
        pr_url = pr.get("html_url")
        checkpoints.append({
            "kind": "pr",
            "title": f"PR #{pr_number} opened",
            "note": "Builder output is ready for independent review.",
            "at": pr.get("created_at"),
            "url": pr_url,
        })
        pr_comments = request_json(f"/repos/{repo}/issues/{pr_number}/comments?per_page=100")
        for comment in pr_comments if isinstance(pr_comments, list) else []:
            item = checkpoint_from_comment(comment, pr_url)
            if item:
                checkpoints.append(item)

    checkpoints = [item for item in checkpoints if item.get("at")]
    checkpoints.sort(key=lambda item: item["at"], reverse=True)
    return checkpoints[:5]


def main() -> None:
    config = json.loads(PROJECTS.read_text())
    items = []
    for project in config.get("projects", []):
        repo = project["repo"]
        for work in project.get("work_items", []):
            issue = work.get("issue")
            if not issue:
                continue
            try:
                checkpoints = item_checkpoints(repo, issue)
            except Exception as exc:
                checkpoints = [{
                    "kind": "error",
                    "title": "Checkpoint sync unavailable",
                    "note": exc.__class__.__name__,
                    "at": datetime.now(timezone.utc).isoformat(),
                    "url": f"https://github.com/{repo}/issues/{issue}",
                }]
            items.append({
                "project": project["name"],
                "repo": repo,
                "issue": issue,
                "checkpoints": checkpoints,
            })

    OUTPUT.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "items": items,
    }, ensure_ascii=False, indent=2) + "\n")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
