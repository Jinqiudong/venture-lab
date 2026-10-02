from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestrator.runtime import MAX_AUTO_FIX_CYCLES, auto_stop_marker, classify_runtime

PROJECTS = ROOT / "dashboard" / "projects.json"


def gh(*args: str) -> str:
    result = subprocess.run(
        ["gh", *args],
        check=True,
        text=True,
        capture_output=True,
        env=os.environ.copy(),
    )
    return result.stdout


def comments(repo: str, pr: int) -> list[str]:
    raw = gh("api", f"repos/{repo}/issues/{pr}/comments", "--paginate")
    return [item.get("body") or "" for item in json.loads(raw or "[]")]


def post(repo: str, pr: int, body: str) -> None:
    gh("pr", "comment", str(pr), "--repo", repo, "--body", body)


def main() -> None:
    if not PROJECTS.exists():
        raise SystemExit("dashboard/projects.json missing")

    projects = json.loads(PROJECTS.read_text(encoding="utf-8")).get("projects", [])
    stopped = 0

    for project in projects:
        repo = project.get("repo")
        if not repo:
            continue
        prs_raw = gh(
            "pr", "list", "--repo", repo, "--state", "open", "--limit", "50",
            "--json", "number,headRefOid,title,body"
        )
        for pr in json.loads(prs_raw or "[]"):
            body = pr.get("body") or ""
            if "Closes #" not in body:
                continue
            number = int(pr["number"])
            head = pr.get("headRefOid") or ""
            bodies = comments(repo, number)
            state = classify_runtime(bodies, head)
            if state.human_ready:
                continue
            if state.fix_cycles < MAX_AUTO_FIX_CYCLES and not state.stopped:
                continue

            marker = auto_stop_marker(head)
            if any(marker in existing for existing in bodies):
                continue

            message = (
                f"{marker}\n"
                f"<!-- venture-human-ready:{head} -->\n"
                "## 👤 Needs You — automation stopped\n\n"
                f"The AI team reached the safety cap of **{MAX_AUTO_FIX_CYCLES} automatic fix cycles** for this PR. "
                "No more automatic code changes will be attempted on the current revision.\n\n"
                "### Your job\n"
                "Review the latest Reviewer / QA findings and decide whether to change product direction, clarify the Issue contract, or ask the AI team for another explicitly approved attempt.\n\n"
                "A new human-approved commit can start a fresh review cycle."
            )
            post(repo, number, message)
            stopped += 1
            print(f"Stopped automation for {repo} PR #{number} after {state.fix_cycles} cycles")

    print(json.dumps({"stopped": stopped}, indent=2))


if __name__ == "__main__":
    main()
