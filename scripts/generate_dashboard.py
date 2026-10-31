from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from scripts import idea_brain, milestones
except ImportError:  # run as `python3 scripts/generate_dashboard.py`
    import idea_brain
    import milestones

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "dashboard" / "projects.json"
OUTPUT_PATH = ROOT / "dashboard" / "data.json"
API = "https://api.github.com"
TOKEN = os.getenv("PORTFOLIO_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")

# "hold": the linked PR carries the `hold` label, so the AI team leaves it alone.
HUMAN_STAGES = {"decision", "human_handoff", "blocked_on_human", "hold"}
AI_STAGES = {"ready", "coding", "building", "ci", "review", "reviewing", "qa", "changes_requested"}
DONE_STAGES = {"done", "merged"}
AUTO_STOP_MARKER = "venture-auto-stop"
HANDOFF_MARKER = re.compile(r"<!-- venture-human-ready:([0-9a-f]+) -->")
DECISION_MARKER = "<!-- venture-human-decision -->"
INCUBATION_RECORDS = ROOT / "product-incubator" / "records"
RECENT_DAYS = 30
TREND_WEEKS = 8
# A project with open work and no push for this long is shown as stalled.
STALL_DAYS = 3
# Product lifecycle shown on the dashboard timeline, in order.
LIFECYCLE = ["idea", "explore", "validate", "build", "beta", "launch"]
INCUBATION_TO_LIFECYCLE = {
    "SPARK": "idea",
    "EXPLORE": "explore",
    "VALIDATE": "validate",
    "INCUBATE": "validate",
    "BUILD": "build",
    "PARK": "idea",
    "REJECT": "idea",
}
IDEA_REPO = os.getenv("GITHUB_REPOSITORY") or "Jinqiudong/venture-lab"
IDEA_LABEL = "idea"
CONTROL_WORKFLOWS = {"orchestrator": "orchestrator.yml", "review": "review-cycle.yml"}


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


def fetch_pulls(repo: str, max_pages: int = 5) -> list[dict]:
    """Pull requests newest-updated first, paged until the trend window is covered."""
    cutoff = datetime.now(timezone.utc) - timedelta(weeks=TREND_WEEKS + 1)
    pulls: list[dict] = []
    for page in range(1, max_pages + 1):
        batch = request_json(f"/repos/{repo}/pulls?state=all&sort=updated&direction=desc&per_page=100&page={page}")
        if not isinstance(batch, list):
            break
        pulls.extend(batch)
        if len(batch) < 100 or parse_time(batch[-1].get("updated_at") or "1970-01-01T00:00:00Z") < cutoff:
            break
    return pulls


def repo_index(repo: str) -> dict | None:
    """Fetch a repository's issues, pull requests and auto-stop markers in a few bulk calls.

    Looking these up per work item cost hundreds of API calls per refresh and exhausted
    the 5,000-per-hour token budget, so every work item is resolved from this index.
    """
    try:
        issues: dict[int, dict] = {}
        for page in (1, 2, 3):
            batch = request_json(f"/repos/{repo}/issues?state=all&per_page=100&page={page}")
            for issue in batch if isinstance(batch, list) else []:
                issues[issue["number"]] = issue
            if not isinstance(batch, list) or len(batch) < 100:
                break
        pulls = fetch_pulls(repo)
        comments = request_json(f"/repos/{repo}/issues/comments?sort=created&direction=desc&per_page=100")
        comments = comments if isinstance(comments, list) else []
        # The repo-wide feed holds only the newest 100 comments, so an open PR's own thread is
        # fetched too; otherwise a pending handoff silently drops out once the repo gets busy.
        seen = {c.get("id") for c in comments}
        for pr in pulls:
            if pr.get("state") == "open":
                thread = request_json(f"/repos/{repo}/issues/{pr['number']}/comments?per_page=100")
                for c in thread if isinstance(thread, list) else []:
                    if c.get("id") not in seen:
                        seen.add(c.get("id"))
                        comments.append(c)
    except Exception:
        return None
    milestones: list[dict] = []
    milestones_ok = True
    try:
        for page in (1, 2, 3):
            batch = request_json(f"/repos/{repo}/milestones?state=all&per_page=100&page={page}")
            if not isinstance(batch, list):
                milestones_ok = False
                break
            milestones.extend(batch)
            if len(batch) < 100:
                break
    except Exception:
        milestones_ok = False
    stops = set()
    for comment in comments if isinstance(comments, list) else []:
        if AUTO_STOP_MARKER in (comment.get("body") or ""):
            try:
                stops.add(int((comment.get("issue_url") or "").rstrip("/").split("/")[-1]))
            except ValueError:
                pass
    return {
        "issues": issues,
        "pulls": pulls if isinstance(pulls, list) else [],
        "stops": stops,
        "comments": comments if isinstance(comments, list) else [],
        "milestones": milestones,
        "milestones_ok": milestones_ok,
    }


def comment_target(comment: dict) -> int | None:
    try:
        return int((comment.get("issue_url") or "").rstrip("/").split("/")[-1])
    except ValueError:
        return None


def handoff_section(body: str, heading: str) -> str:
    match = re.search(rf"### {heading}\n(.*?)(?:\n###|\Z)", body, re.S)
    return match.group(1).strip() if match else ""


def pending_handoffs(repo: str, index: dict) -> list[dict]:
    """Open PRs where Review Cycle handed the current HEAD to the Product Owner and no decision followed."""
    heads = {pr["number"]: pr for pr in index["pulls"] if pr.get("state") == "open"}
    latest: dict[int, dict] = {}
    decided: dict[int, str] = {}
    for comment in index["comments"]:
        number = comment_target(comment)
        if number not in heads:
            continue
        body = comment.get("body") or ""
        created = comment.get("created_at") or ""
        if DECISION_MARKER in body:
            decided[number] = max(decided.get(number, ""), created)
        match = HANDOFF_MARKER.search(body)
        if match and created > (latest.get(number) or {}).get("created_at", ""):
            latest[number] = {**comment, "sha": match.group(1)}
    handoffs = []
    for number, comment in latest.items():
        pr = heads[number]
        if comment["sha"] != (pr.get("head") or {}).get("sha") or decided.get(number, "") > comment["created_at"]:
            continue
        handoffs.append(
            {
                "repo": repo,
                "pr": number,
                "pr_url": pr.get("html_url"),
                "title": pr.get("title"),
                "ask": handoff_section(comment.get("body") or "", "Your job"),
                "since": comment["created_at"],
                "url": comment.get("html_url") or pr.get("html_url"),
            }
        )
    return handoffs


def pending_acceptances(repo: str, index: dict) -> list[dict]:
    """Milestone PRs whose checklist is posted for the current HEAD and that the owner has not accepted yet."""
    owner = repo.split("/")[0]
    milestone_prs = {
        pr["number"]: pr for pr in index["pulls"]
        if pr.get("state") == "open" and ((pr.get("head") or {}).get("ref") or "").startswith("milestone/")
    }
    ready: dict[int, dict] = {}
    for comment in index["comments"]:
        number = comment_target(comment)
        pr = milestone_prs.get(number)
        if not pr:
            continue
        if f"<!-- venture-acceptance-ready:{(pr.get('head') or {}).get('sha')} -->" in (comment.get("body") or ""):
            ready[number] = comment
    acceptances = []
    for number, checklist in ready.items():
        accepted = any(
            comment_target(c) == number and milestones.owner_accepts(c, owner, checklist.get("created_at") or "")
            for c in index["comments"]
        )
        if accepted:
            continue
        pr = milestone_prs[number]
        acceptances.append(
            {
                "repo": repo,
                "pr": number,
                "pr_url": pr.get("html_url"),
                "title": pr.get("title"),
                "acceptance": True,
                "ask": "Try the finished milestone, then merge it or comment /accept",
                "since": checklist.get("created_at"),
                "url": checklist.get("html_url") or pr.get("html_url"),
            }
        )
    return acceptances


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def delivery_stats(pulls: list[dict], now: datetime) -> dict:
    """Weekly merged counts for the trend chart and the median hours from PR open to merge."""
    merged = [pr for pr in pulls if pr.get("merged_at")]
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    weeks = []
    for back in range(TREND_WEEKS - 1, -1, -1):
        start = week_start - timedelta(weeks=back)
        end = start + timedelta(weeks=1)
        weeks.append({"week": start.date().isoformat(), "merged": sum(1 for pr in merged if start <= parse_time(pr["merged_at"]) < end)})
    recent = [pr for pr in merged if parse_time(pr["merged_at"]) >= now - timedelta(days=RECENT_DAYS) and pr.get("created_at")]
    durations = sorted((parse_time(pr["merged_at"]) - parse_time(pr["created_at"])).total_seconds() / 3600 for pr in recent)
    median = durations[len(durations) // 2] if durations else None
    # Throughput over the last four full-or-current weeks drives the milestone projection.
    per_week = sum(week["merged"] for week in weeks[-4:]) / 4
    return {"weekly": weeks, "median_hours_to_merge": round(median, 1) if median is not None else None, "per_week": round(per_week, 2)}


def milestone_plan(milestones: list[dict], per_week: float, now: datetime) -> list[dict]:
    """GitHub milestones with a projected finish date from recent throughput."""
    plan = []
    for milestone in sorted(milestones, key=lambda m: (m.get("due_on") or "9999", m.get("number") or 0)):
        open_count = milestone.get("open_issues") or 0
        projected = None
        if open_count and per_week > 0:
            projected = (now + timedelta(weeks=open_count / per_week)).date().isoformat()
        plan.append(
            {
                "title": milestone.get("title"),
                "url": milestone.get("html_url"),
                "state": milestone.get("state"),
                "due_on": (milestone.get("due_on") or "")[:10] or None,
                "open": open_count,
                "closed": milestone.get("closed_issues") or 0,
                "projected_on": projected,
            }
        )
    return plan


def owner_decision(item: dict) -> bool:
    """Only product judgment waits on the owner; a hold is the owner's own pause and an auto-stop is an engineering failure."""
    stage = item.get("workflow_stage")
    if stage in DONE_STAGES or stage in {"hold", "blocked_on_human"}:
        return False
    return stage in {"decision", "human_handoff"} or bool(item.get("needs_human"))


def project_status(items: list[dict], handoffs: list[dict], metrics: dict, now: datetime) -> str:
    """One traffic light per project: needs_you, stuck, moving, or quiet."""
    if handoffs or any(owner_decision(item) for item in items):
        return "needs_you"
    open_work = [item for item in items if item.get("workflow_stage") not in DONE_STAGES | {"hold"}]
    if any(item.get("workflow_stage") == "blocked_on_human" for item in items):
        return "stuck"
    if not open_work:
        return "quiet"
    pushed = metrics.get("latest_activity")
    if pushed and now - parse_time(pushed) > timedelta(days=STALL_DAYS):
        return "stalled"
    return "moving"


def indexed_linked_pr(index: dict, repo: str, issue_number: int) -> dict | None:
    candidates = [pr for pr in index["pulls"] if closes_issue(pr.get("body"), issue_number, repo)]
    if not candidates:
        return None
    candidates.sort(key=lambda pr: pr.get("updated_at") or pr.get("created_at") or "", reverse=True)
    return candidates[0]


def recent_merged(repo: str, now: datetime, index: dict | None = None) -> list[dict]:
    """Merged PRs in the last RECENT_DAYS days, newest first."""
    since = now - timedelta(days=RECENT_DAYS)
    if index is not None:
        pulls = index["pulls"]
    else:
        try:
            pulls = request_json(f"/repos/{repo}/pulls?state=closed&sort=updated&direction=desc&per_page=50")
        except Exception:
            return []
    merged = []
    for pr in pulls if isinstance(pulls, list) else []:
        merged_at = pr.get("merged_at")
        if not merged_at or datetime.fromisoformat(merged_at.replace("Z", "+00:00")) < since:
            continue
        merged.append({"number": pr.get("number"), "title": pr.get("title"), "url": pr.get("html_url"), "merged_at": merged_at})
    merged.sort(key=lambda pr: pr["merged_at"], reverse=True)
    return merged


def pipeline_health() -> dict:
    """Latest conclusions of the control-plane workflows; a repeat failure means the AI team is stalled."""
    repo = os.getenv("GITHUB_REPOSITORY") or "Jinqiudong/venture-lab"
    health = {"status": "unknown", "workflows": {}}
    failing = False
    for key, workflow in CONTROL_WORKFLOWS.items():
        try:
            runs = request_json(f"/repos/{repo}/actions/workflows/{workflow}/runs?per_page=5&status=completed")
        except Exception:
            continue
        conclusions = [run.get("conclusion") for run in runs.get("workflow_runs", []) if run.get("conclusion") != "skipped"]
        latest = (runs.get("workflow_runs") or [{}])[0]
        health["workflows"][key] = {"conclusion": conclusions[0] if conclusions else None, "url": latest.get("html_url"), "at": latest.get("updated_at")}
        failing = failing or conclusions[:2] == ["failure", "failure"]
    if health["workflows"]:
        health["status"] = "failing" if failing else "ok"
    return health


def idea_card(record: dict) -> dict:
    guidance = record.get("guidance") or {}
    return {
        "name": record.get("title") or f"Idea #{record.get('idea_issue')}",
        "name_zh": record.get("title_zh"),
        "kind": "idea",
        "repo": None,
        "issue_url": f"https://github.com/{IDEA_REPO}/issues/{record.get('idea_issue')}",
        "lifecycle": INCUBATION_TO_LIFECYCLE.get(record.get("stage"), "idea"),
        "current_focus": guidance.get("current") or (record.get("decision") or {}).get("next_action"),
        "current_focus_zh": guidance.get("current_zh"),
        "progress": {"done": max(0, int(guidance.get("step") or 1) - 1), "total": int(guidance.get("total_steps") or 6), "active": 0},
        "done_steps": guidance.get("completed", []),
        "next_steps": guidance.get("up_next", []),
    }


def issue_idea_records() -> list[dict]:
    """Ideas captured through the issue form; the Product Brain keeps each record in its latest reply."""
    try:
        issues = request_json(f"/repos/{IDEA_REPO}/issues?labels={IDEA_LABEL}&state=open&per_page=100")
    except Exception:
        return []
    records = []
    for issue in issues if isinstance(issues, list) else []:
        if "pull_request" in issue:
            continue
        record = None
        try:
            comments = request_json(f"/repos/{IDEA_REPO}/issues/{issue['number']}/comments?per_page=100")
        except Exception:
            comments = []
        for comment in reversed(comments if isinstance(comments, list) else []):
            if (comment.get("user") or {}).get("login") == "github-actions[bot]":
                record = idea_brain.record_from(comment.get("body"))
                if record:
                    break
        if record is None:
            # Captured but not yet researched.
            title = re.sub(r"^\[Idea\]\s*", "", issue.get("title") or "").strip()
            record = {
                "stage": "SPARK",
                "title": title or None,
                "guidance": {"current": "Product Brain is researching this idea", "current_zh": "AI 产品经理正在调研这个想法", "step": 1},
            }
        records.append({**record, "idea_issue": issue["number"]})
    return records


def incubation_projects(represented: set[int] | None = None, issue_records: list[dict] | None = None) -> list[dict]:
    """Ideas still in incubation appear as projects without a repository.

    An idea that already has a product repo is shown once, by its repo card. A record file
    in product-incubator/records wins over the copy kept on the issue.
    """
    represented = represented or set()
    records: dict[int, dict] = {}
    for record in issue_records or []:
        records[record.get("idea_issue")] = record
    for path in sorted(INCUBATION_RECORDS.glob("*.json")) if INCUBATION_RECORDS.exists() else []:
        record = json.loads(path.read_text())
        records[record.get("idea_issue")] = record
    projects = []
    for number in sorted(records, key=lambda n: n or 0):
        record = records[number]
        if record.get("stage") in {"BUILD", "REJECT"}:
            continue
        if record.get("product_repo") or number in represented:
            continue
        projects.append(idea_card(record))
    return projects


def project_progress(items: list[dict]) -> dict:
    total = [item for item in items if item.get("issue")]
    done = [item for item in total if item.get("workflow_stage") in DONE_STAGES or item.get("issue_state") == "closed"]
    active = [item for item in total if item.get("workflow_stage") in AI_STAGES - {"ready"}]
    return {"done": len(done), "total": len(total), "active": len(active)}


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


def pr_is_held(pr: dict) -> bool:
    return any((label.get("name") or "").lower() == "hold" for label in pr.get("labels") or [])


def has_auto_stop(repo: str, issue_number: int) -> bool:
    try:
        comments = request_json(f"/repos/{repo}/issues/{issue_number}/comments?per_page=100")
    except Exception:
        return False
    return any(AUTO_STOP_MARKER in (item.get("body") or "") for item in comments if isinstance(item, dict))


def workflow_item(repo: str, item: dict, index: dict | None = None) -> dict:
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
        issue = (index or {}).get("issues", {}).get(issue_number) or request_json(f"/repos/{repo}/issues/{issue_number}")
        enriched["title"] = issue.get("title") or f"Issue #{issue_number}"
        enriched["issue_url"] = issue.get("html_url")
        enriched["issue_state"] = issue.get("state")
        pr = indexed_linked_pr(index, repo, issue_number) if index is not None else linked_pr(repo, issue_number)
        if pr:
            enriched["pr"] = pr.get("number")
            enriched["pr_url"] = pr.get("html_url")
            if pr.get("state") != "open":
                enriched["workflow_stage"] = "merged"
            elif pr_is_held(pr):
                enriched["workflow_stage"] = "hold"
                enriched["needs_human"] = True
                enriched["next_action"] = f"PR #{pr.get('number')} is labeled hold; remove the label to resume automation"
            else:
                enriched["workflow_stage"] = "review"
        elif issue.get("state") == "closed":
            enriched["workflow_stage"] = "done"
        elif (int(issue_number) in index["stops"]) if index is not None else has_auto_stop(repo, int(issue_number)):
            enriched["workflow_stage"] = "blocked_on_human"
            enriched["needs_human"] = True
            enriched["next_action"] = "Diagnose Builder runtime or rescope the task before retrying"
    except Exception:
        enriched.setdefault("title", f"Issue #{issue_number}")
    return enriched


def resolve_dependencies(items: list[dict]) -> list[dict]:
    by_issue = {item.get("issue"): item for item in items if item.get("issue")}
    for item in items:
        blockers = item.get("blocked_by") or []
        # Dependency-backed items must always be re-evaluated from live blocker state.
        # Preserve terminal/active/human stages, but do not let a stale configured
        # "ready" or "blocked" value bypass dependency resolution.
        stage = item.get("workflow_stage")
        if not blockers or stage in DONE_STAGES | HUMAN_STAGES or stage in (AI_STAGES - {"ready"}):
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


def idea_summary(issue: int) -> dict | None:
    """Incubation context for a repo project that grew out of an idea."""
    path = INCUBATION_RECORDS / f"{issue}.json"
    if not path.exists():
        return None
    record = json.loads(path.read_text())
    guidance = record.get("guidance") or {}
    return {
        "issue": issue,
        "issue_url": f"https://github.com/Jinqiudong/venture-lab/issues/{issue}",
        "title": record.get("title"),
        "done_steps": guidance.get("completed", []),
        "next_steps": guidance.get("up_next", []),
    }


def project_slug(project: dict) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (project.get("repo") or project.get("name") or "").split("/")[-1].lower()).strip("-")


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text())
    now = datetime.now(timezone.utc)
    projects = []
    work_items = []
    handoffs = []
    for project in config["projects"]:
        repo = project["repo"]
        index = repo_index(repo)
        project_items = resolve_dependencies([workflow_item(repo, item, index) for item in project.get("work_items", [])])
        metrics = repo_metrics(repo)
        project_handoffs = (pending_acceptances(repo, index) + pending_handoffs(repo, index)) if index else []
        stats = delivery_stats(index["pulls"], now) if index else {"weekly": [], "median_hours_to_merge": None, "per_week": 0}
        projects.append(
            {
                **project,
                **metrics,
                "slug": project_slug(project),
                "kind": "repo",
                "work_items": project_items,
                "progress": project_progress(project_items),
                "recent_merged": recent_merged(repo, now, index),
                "delivery": stats,
                "milestones": milestone_plan(index["milestones"], stats["per_week"], now) if index else [],
                "milestones_error": bool(index) and not index.get("milestones_ok", True),
                "handoffs": project_handoffs,
                "status": project_status(project_items, project_handoffs, metrics, now),
                "idea": idea_summary(project["idea_issue"]) if project.get("idea_issue") else None,
            }
        )
        handoffs.extend({**handoff, "project_name": project["name"], "project_slug": project_slug(project)} for handoff in project_handoffs)
        work_items.extend({**item, "project_name": project["name"], "project_slug": project_slug(project), "project_stage": project["stage"]} for item in project_items)

    needs_you = [
        {"kind": "handoff", **handoff} for handoff in handoffs
    ] + [
        {"kind": "decision", **item} for item in work_items if owner_decision(item)
    ]
    ai_team = [item for item in work_items if item.get("workflow_stage") in AI_STAGES and not item.get("needs_human")]
    queue = [item for item in work_items if item.get("workflow_stage") == "blocked"]

    output = {
        "generated_at": now.isoformat(),
        "lifecycle": LIFECYCLE,
        "pipeline": pipeline_health(),
        "ideas": incubation_projects({p["idea_issue"] for p in config["projects"] if p.get("idea_issue")}, issue_idea_records()),
        "new_idea_url": f"https://github.com/{IDEA_REPO}/issues/new?template=idea.yml",
        "needs_you": needs_you,
        "paused": [item for item in work_items if item.get("workflow_stage") == "hold"],
        "ai_team": ai_team,
        "queue": queue,
        "work_items": work_items,
        "projects": projects,
    }
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
