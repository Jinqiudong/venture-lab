from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


def run(*args: str, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=check,
    )


def snapshot(source: Path, worktree: Path) -> None:
    run(
        "rsync",
        "-a",
        "--delete",
        "--exclude=.git",
        f"{source}/",
        f"{worktree}/",
    )


def push_checkpoint(worktree: Path, branch: str, issue: int, run_id: str) -> bool:
    run("git", "add", "-A", cwd=worktree)
    if run("git", "diff", "--cached", "--quiet", cwd=worktree, check=False).returncode == 0:
        return False
    run("git", "config", "user.name", "venture-lab-checkpoint[bot]", cwd=worktree)
    run("git", "config", "user.email", "venture-lab-checkpoint@users.noreply.github.com", cwd=worktree)
    run("git", "commit", "-m", f"checkpoint: issue #{issue} run {run_id}", cwd=worktree)
    run("git", "push", "origin", f"HEAD:refs/heads/{branch}", "--force", cwd=worktree)
    print(f"Persisted Builder checkpoint to {branch}", flush=True)
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--issue", required=True, type=int)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--interval", type=int, default=90)
    args = parser.parse_args()

    source = Path(args.source).resolve()
    branch = f"checkpoint/issue-{args.issue}/run-{args.run_id}"
    temp_root = Path(tempfile.mkdtemp(prefix=f"venture-checkpoint-{args.run_id}-"))
    worktree = temp_root / "worktree"

    try:
        run("git", "worktree", "add", "--detach", str(worktree), "origin/main", cwd=source)
        while True:
            try:
                snapshot(source, worktree)
                push_checkpoint(worktree, branch, args.issue, args.run_id)
            except Exception as exc:
                print(f"Checkpoint watcher warning: {exc}", flush=True)
            time.sleep(args.interval)
    finally:
        run("git", "worktree", "remove", "--force", str(worktree), cwd=source, check=False)
        shutil.rmtree(temp_root, ignore_errors=True)


if __name__ == "__main__":
    main()
