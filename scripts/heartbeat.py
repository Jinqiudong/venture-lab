"""AI team heartbeat: wake the Orchestrator on a steady cadence instead of relying on GitHub cron.

GitHub drops most scheduled runs on busy days, so a stalled pipeline could sit idle for hours.
This loop runs inside one long Actions job. Every tick it:

1. pauses while a Claude usage window is exhausted, until the reset time the agent reported;
2. otherwise dispatches the Orchestrator when no Orchestrator or Review Cycle run is queued or running;
3. moves milestones forward (see scripts/milestones.py);
4. refreshes the dashboard at most once per tick.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import milestones  # noqa: E402

REPO = os.getenv("GITHUB_REPOSITORY") or "Jinqiudong/venture-lab"
AGENT_WORKFLOWS = ("orchestrator.yml", "review-cycle.yml")
# Claude Code prints e.g. "You've hit your 5-hour limit · resets 8am (UTC)" or "resets 8:30pm (UTC)".
QUOTA_PATTERN = re.compile(r"hit your .*?limit.*?resets\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)\s*\(UTC\)", re.I)
QUOTA_FALLBACK = timedelta(minutes=30)


def gh_json(*args: str):
    out = subprocess.run(["gh", "api", *args], text=True, capture_output=True)
    if out.returncode:
        raise RuntimeError(out.stderr.strip())
    return json.loads(out.stdout or "null")


def quota_reset_at(message: str, failed_at: datetime) -> datetime | None:
    """The next UTC time matching the reset clock time in a Claude usage-limit message."""
    match = QUOTA_PATTERN.search(message or "")
    if not match:
        if re.search(r"hit your .*?limit", message or "", re.I):
            return failed_at + QUOTA_FALLBACK
        return None
    hour = int(match.group(1)) % 12 + (12 if match.group(3).lower() == "pm" else 0)
    reset = failed_at.replace(hour=hour, minute=int(match.group(2) or 0), second=0, microsecond=0)
    if reset <= failed_at:
        reset += timedelta(days=1)
    return reset


def run_annotations(run: dict) -> str:
    """Error annotations of a failed run's jobs, joined; the quota message surfaces there."""
    texts = []
    jobs = gh_json(f"repos/{REPO}/actions/runs/{run['id']}/jobs?per_page=50").get("jobs", [])
    for job in jobs:
        if job.get("conclusion") != "failure":
            continue
        for note in gh_json(f"repos/{REPO}/check-runs/{job['id']}/annotations"):
            texts.append(note.get("message") or "")
    return "\n".join(texts)


def paused_until(now: datetime) -> datetime | None:
    """If the newest finished agent run failed on a usage limit that has not reset yet, when it resets."""
    latest = None
    for workflow in AGENT_WORKFLOWS:
        runs = gh_json(f"repos/{REPO}/actions/workflows/{workflow}/runs?status=completed&per_page=5").get("workflow_runs", [])
        for run in runs:
            if run.get("conclusion") in {"skipped", "cancelled"}:
                continue
            if latest is None or run["updated_at"] > latest["updated_at"]:
                latest = run
            break
    if not latest or latest.get("conclusion") != "failure":
        return None
    failed_at = datetime.fromisoformat(latest["updated_at"].replace("Z", "+00:00"))
    reset = quota_reset_at(run_annotations(latest), failed_at)
    return reset if reset and reset > now else None


def agent_busy() -> bool:
    for workflow in AGENT_WORKFLOWS:
        for status in ("queued", "in_progress"):
            runs = gh_json(f"repos/{REPO}/actions/workflows/{workflow}/runs?status={status}&per_page=1")
            if runs.get("total_count"):
                return True
    return False


def dispatch(workflow: str) -> None:
    subprocess.run(["gh", "workflow", "run", workflow, "--repo", REPO, "--ref", "main"], check=False)


def tick(now: datetime) -> str:
    resume = paused_until(now)
    if resume:
        return f"paused: Claude usage limit, resumes {resume.isoformat()}"
    milestones.advance(now)
    if agent_busy():
        return "busy: an agent run is already queued or running"
    dispatch("orchestrator.yml")
    return "dispatched orchestrator"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--minutes", type=float, default=340, help="how long this loop runs before re-arming")
    parser.add_argument("--every", type=int, default=600, help="seconds between ticks")
    args = parser.parse_args()
    deadline = time.monotonic() + args.minutes * 60
    while True:
        now = datetime.now(timezone.utc)
        try:
            print(f"{now:%H:%M} {tick(now)}", flush=True)
        except Exception as exc:  # one bad tick must not end the loop
            print(f"{now:%H:%M} tick failed: {exc}", flush=True)
        dispatch("dashboard.yml")
        if time.monotonic() + args.every > deadline:
            break
        time.sleep(args.every)


if __name__ == "__main__":
    main()
