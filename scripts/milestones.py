"""Milestone branches: the owner reviews a milestone once instead of every PR.

An Issue assigned to an open GitHub milestone is built on `milestone/<slug>` instead of the
default branch. Its task PR is reviewed, QA'd and auto-merged into that branch as usual. One
milestone PR (milestone branch -> default branch) collects the work. When the milestone has no
open issues left, the milestone PR is marked ready, which runs platform CI once for the whole
milestone. Once CI passes it gets an acceptance checklist and becomes the owner's single review
point. The owner merges it, or comments `/accept` (or `验收通过`) and the heartbeat merges it.

Commands used by the workflows:
  milestones.py base --repo R --issue N       print the base branch for Issue N (creating it if needed)
  milestones.py open-pr --repo R --branch B   make sure the milestone PR for branch B exists
  milestones.py after-merge --repo R --pr N --issue I --base B --default D
                                              after a task PR merges into a milestone branch: close its Issue,
                                              open the milestone PR, and add QA's "try this" note
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "milestone/"
MILESTONE_MARKER = re.compile(r"<!-- venture-milestone:(\d+) -->")
ACCEPTANCE_MARKER = "<!-- venture-acceptance-ready:{sha} -->"
TRY_MARKER = "<!-- venture-try:{pr} -->"
ACCEPT_WORDS = re.compile(r"(^|\s)(/accept|验收通过)(\s|$)", re.I)


def gh(*args: str, check: bool = True) -> str:
    out = subprocess.run(["gh", *args], text=True, capture_output=True)
    if check and out.returncode:
        raise RuntimeError(out.stderr.strip() or out.stdout.strip())
    return out.stdout


def api(path: str, *fields: str, method: str = "GET", check: bool = True):
    args = ["api", "--method", method, path]
    for field in fields:
        args += ["-f", field]
    text = gh(*args, check=check)
    return json.loads(text) if text.strip() else None


def slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (title or "").lower()).strip("-")[:48] or "milestone"


def default_branch(repo: str) -> str:
    return api(f"repos/{repo}")["default_branch"]


def branch_exists(repo: str, branch: str) -> bool:
    return subprocess.run(["gh", "api", f"repos/{repo}/branches/{branch}"], capture_output=True).returncode == 0


def base_branch(repo: str, issue: int) -> str:
    """Milestone branch for an Issue in an open milestone, otherwise the default branch."""
    main = default_branch(repo)
    milestone = (api(f"repos/{repo}/issues/{issue}") or {}).get("milestone")
    if not milestone or milestone.get("state") != "open":
        return main
    branch = PREFIX + slug(milestone["title"])
    if not branch_exists(repo, branch):
        sha = api(f"repos/{repo}/git/ref/heads/{main}")["object"]["sha"]
        api(f"repos/{repo}/git/refs", f"ref=refs/heads/{branch}", f"sha={sha}", method="POST")
    else:
        # Keep the milestone current with the default branch; a conflict is left for review to surface.
        api(f"repos/{repo}/merges", f"base={branch}", f"head={main}", f"commit_message=Sync {main} into {branch}", method="POST", check=False)
    return branch


def milestone_for_branch(repo: str, branch: str) -> dict | None:
    for milestone in api(f"repos/{repo}/milestones?state=all&per_page=100") or []:
        if PREFIX + slug(milestone["title"]) == branch:
            return milestone
    return None


def milestone_pr(repo: str, branch: str) -> dict | None:
    owner = repo.split("/")[0]
    pulls = api(f"repos/{repo}/pulls?state=open&head={owner}:{branch}&per_page=1") or []
    return pulls[0] if pulls else None


def open_pr(repo: str, branch: str) -> dict | None:
    """Create the milestone PR once the branch has work on it."""
    existing = milestone_pr(repo, branch)
    if existing:
        return existing
    milestone = milestone_for_branch(repo, branch)
    if not milestone:
        return None
    body = (
        f"<!-- venture-milestone:{milestone['number']} -->\n"
        f"## 🏁 Milestone: {milestone['title']}\n\n"
        "Task PRs for this milestone are reviewed, tested and merged into this branch automatically.\n\n"
        "When every issue in the milestone is closed, an acceptance checklist is posted here. "
        "This PR is the Product Owner's review point: merge it, or comment `/accept`, to ship the milestone to the default branch.\n"
    )
    created = gh("pr", "create", "--repo", repo, "--base", default_branch(repo), "--head", branch,
                 "--draft", "--title", f"🏁 Milestone: {milestone['title']}", "--body", body, check=False)
    return milestone_pr(repo, branch) if created else None


def add_try_note(repo: str, branch: str, pr: int, text: str) -> None:
    target = open_pr(repo, branch)
    if not target or not text.strip():
        return
    body = f"{TRY_MARKER.format(pr=pr)}\n**Try after #{pr}:** {text.strip()}"
    gh("pr", "comment", str(target["number"]), "--repo", repo, "--body", body, check=False)


def qa_try_note(path: str | None) -> str:
    """QA's human_validation text, if QA wanted a person to look at something."""
    if not path or not Path(path).exists():
        return ""
    try:
        result = json.loads(Path(path).read_text())
    except ValueError:
        return ""
    return (result.get("human_validation") or "").strip() if result.get("needs_human") else ""


def after_merge(repo: str, pr: int, issue: int, base: str, default: str, qa_result: str | None) -> None:
    if base == default or not base.startswith(PREFIX):
        return
    # "Closes #N" only fires on the default branch, so dependent Issues would never become ready.
    gh("issue", "close", str(issue), "--repo", repo, "--comment",
       f"Merged into `{base}` by #{pr}. It ships with the milestone after the Product Owner accepts it.", check=False)
    open_pr(repo, base)
    add_try_note(repo, base, pr, qa_try_note(qa_result))


def acceptance_body(repo: str, pr: dict, milestone: dict, comments: list[dict]) -> str:
    merged = [
        p for p in api(f"repos/{repo}/pulls?state=closed&base={pr['head']['ref']}&per_page=100") or []
        if p.get("merged_at")
    ]
    tries = [c["body"].split("\n", 1)[1] for c in comments if "<!-- venture-try:" in (c.get("body") or "") and "\n" in c["body"]]
    lines = [
        ACCEPTANCE_MARKER.format(sha=pr["head"]["sha"]),
        f"## 👤 Milestone ready for you: {milestone['title']}",
        "",
        f"All {milestone['closed_issues']} issues are done, every task PR passed review and QA, and CI passed on this PR.",
        "",
        "### What shipped",
        *[f"- #{p['number']} {p['title']}" for p in sorted(merged, key=lambda p: p["merged_at"])],
        "",
        "### Try these",
        *([f"- [ ] {t}" for t in tries] or ["- [ ] Use the new flow end to end on a real device."]),
        "",
        "### Then",
        "- Happy with it: merge this PR, or comment `/accept`.",
        "- Something to change: comment what you saw. Fixes go into this same milestone before it ships.",
    ]
    return "\n".join(lines)


def ci_state(runs: list[dict], jobs_of) -> str:
    """CI on a milestone PR head: none, pending, blocked (GitHub never started it), failed or passed."""
    runs = [r for r in runs if r.get("event") == "pull_request"]
    if not runs:
        return "none"
    if any(r.get("status") != "completed" for r in runs):
        return "pending"
    failed = [r for r in runs if r.get("conclusion") not in {"success", "skipped", "neutral"}]
    if not failed:
        return "passed"
    if all(not job.get("steps") for r in failed for job in jobs_of(r)):
        return "blocked"
    return "failed"


def head_ci(repo: str, sha: str) -> str:
    runs = (api(f"repos/{repo}/actions/runs?head_sha={sha}&per_page=50") or {}).get("workflow_runs", [])
    return ci_state(runs, lambda run: (api(f"repos/{repo}/actions/runs/{run['id']}/jobs") or {}).get("jobs", []))


def owner_accepts(comment: dict, owner: str, since: str) -> bool:
    """An owner comment after the checklist that says /accept. Agents post as the owner too, so marked comments never count."""
    body = comment.get("body") or ""
    return (
        comment.get("created_at", "") > since
        and (comment.get("user") or {}).get("login") == owner
        and "<!-- venture-" not in body
        and bool(ACCEPT_WORDS.search(body))
    )


def advance(now: datetime | None = None) -> list[str]:
    """Post acceptance checklists for finished milestones and merge accepted ones."""
    actions = []
    projects = json.loads((ROOT / "dashboard" / "projects.json").read_text())["projects"]
    for project in projects:
        repo = project["repo"]
        owner = repo.split("/")[0]
        try:
            pulls = api(f"repos/{repo}/pulls?state=open&per_page=100") or []
        except RuntimeError:
            continue
        for pr in pulls:
            if not pr["head"]["ref"].startswith(PREFIX):
                continue
            match = MILESTONE_MARKER.search(pr.get("body") or "")
            if not match:
                continue
            milestone = api(f"repos/{repo}/milestones/{match.group(1)}")
            if milestone["open_issues"]:
                continue
            comments = api(f"repos/{repo}/issues/{pr['number']}/comments?per_page=100") or []
            marker = ACCEPTANCE_MARKER.format(sha=pr["head"]["sha"])
            posted = [c for c in comments if marker in (c.get("body") or "")]
            if not posted:
                # Platform CI runs once per milestone: marking the PR ready starts it. The Review Cycle sends a
                # failure to Fixer on this branch; the owner only sees the milestone once CI is green.
                if pr.get("draft"):
                    gh("pr", "ready", str(pr["number"]), "--repo", repo, check=False)
                    actions.append(f"{repo}#{pr['number']} ready, CI started")
                    continue
                if head_ci(repo, pr["head"]["sha"]) not in {"passed", "none"}:
                    continue
                gh("pr", "comment", str(pr["number"]), "--repo", repo, "--body", acceptance_body(repo, pr, milestone, comments))
                actions.append(f"{repo}#{pr['number']} acceptance posted")
                continue
            accepted = any(owner_accepts(c, owner, posted[-1]["created_at"]) for c in comments)
            if accepted:
                gh("pr", "merge", str(pr["number"]), "--repo", repo, "--merge", "--delete-branch")
                api(f"repos/{repo}/milestones/{milestone['number']}", "state=closed", method="PATCH", check=False)
                actions.append(f"{repo}#{pr['number']} accepted and merged")
    return actions


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    base = sub.add_parser("base")
    base.add_argument("--repo", required=True)
    base.add_argument("--issue", type=int, required=True)
    pr = sub.add_parser("open-pr")
    pr.add_argument("--repo", required=True)
    pr.add_argument("--branch", required=True)
    merged = sub.add_parser("after-merge")
    merged.add_argument("--repo", required=True)
    merged.add_argument("--pr", type=int, required=True)
    merged.add_argument("--issue", type=int, required=True)
    merged.add_argument("--base", required=True)
    merged.add_argument("--default", required=True)
    merged.add_argument("--qa-result", default=os.getenv("QA_RESULT"))
    sub.add_parser("advance")
    args = parser.parse_args()
    if args.command == "base":
        print(base_branch(args.repo, args.issue))
    elif args.command == "open-pr":
        open_pr(args.repo, args.branch)
    elif args.command == "after-merge":
        after_merge(args.repo, args.pr, args.issue, args.base, args.default, args.qa_result)
    else:
        print("\n".join(advance()) or "nothing to advance")


if __name__ == "__main__":
    main()
