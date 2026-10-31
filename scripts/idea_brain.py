"""Product Brain turns on idea issues.

`prompt` turns an idea issue and its conversation into a prompt for the Product
Brain agent. `post` publishes the agent's reply as an issue comment with the
updated incubation record embedded, so the issue stays the system of record.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD_MARKER = "idea-cauldron-record"
RECORD_PATTERN = re.compile(rf"<!--\s*{RECORD_MARKER}\s*(\{{.*?\}})\s*-->", re.S)
# Typing one of these in an owner comment approves the move to BUILD; nothing else can.
BUILD_APPROVAL = re.compile(r"(?i)(/approve-build|批准开发)")


def gh_json(path: str, paginate: bool = False) -> list | dict:
    cmd = ["gh", "api", path, *(["--paginate", "--slurp"] if paginate else [])]
    data = json.loads(subprocess.run(cmd, check=True, capture_output=True, text=True).stdout)
    # --slurp wraps each page in an outer array.
    return [item for page in data for item in page] if paginate else data


def is_trusted(author: str | None, owner: str) -> bool:
    return author in {owner, "github-actions[bot]"}


def record_from(body: str | None) -> dict | None:
    match = RECORD_PATTERN.search(body or "")
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def latest_record(comments: list[dict]) -> dict | None:
    for comment in reversed(comments):
        if (comment.get("user") or {}).get("login") != "github-actions[bot]":
            continue
        record = record_from(comment.get("body"))
        if record:
            return record
    return None


def visible_text(body: str | None) -> str:
    return RECORD_PATTERN.sub("", body or "").strip()


def owner_approved_build(comments: list[dict], owner: str) -> bool:
    owner_comments = [c for c in comments if (c.get("user") or {}).get("login") == owner]
    return bool(owner_comments) and bool(BUILD_APPROVAL.search(owner_comments[-1].get("body") or ""))


def build_prompt(issue: dict, comments: list[dict], owner: str) -> str:
    agent = (ROOT / "agents" / "product-incubator.md").read_text(encoding="utf-8")
    playbook = (ROOT / "product-incubator" / "PLAYBOOK.md").read_text(encoding="utf-8")
    previous = latest_record(comments)
    transcript = []
    for comment in comments:
        author = (comment.get("user") or {}).get("login")
        if not is_trusted(author, owner):
            continue
        who = "Product Owner" if author == owner else "Product Brain (you, earlier)"
        transcript.append(f"### {who} · {comment.get('created_at')}\n\n{visible_text(comment.get('body'))}")
    if previous is None:
        first_step = "Frame the idea: problem, target user, job to be done, current alternatives, hypothesis."
    else:
        first_step = "Fold the Product Owner's latest reply into the record. Do not ask again what they already answered."
    return f"""{agent}

---

{playbook}

---

# This turn

You are the Product Brain for Idea #{issue['number']} in Venture Lab. You are running unattended in
GitHub Actions; your reply is posted on the idea issue and the Product Owner answers there (often from a phone).

## The idea, as the Product Owner wrote it

Title: {issue.get('title')}

{issue.get('body') or '(empty)'}

## Previous incubation record

{json.dumps(previous, ensure_ascii=False, indent=2) if previous else 'None. This is the first turn: the idea starts at SPARK.'}

## Conversation so far

{chr(10).join(transcript) or '(no replies yet)'}

## What to do

1. {first_step}
2. Do the routine PM work yourself. Use WebSearch/WebFetch for decision-relevant desk research:
   direct competitors and substitutes (name real products, pricing, what users praise or complain about),
   signs of demand, and why-now. Cite sources in `evidence` with an honest `strength`. Separate evidence from inference.
3. Rank the riskiest assumptions and propose the cheapest validation that could kill or strengthen the idea.
4. Decide PROMOTE / STAY / PARK / REJECT with confidence. Move `stage` at most one step per turn.
   Never set stage BUILD: that needs the Product Owner to type /approve-build.
   Be willing to say an idea is weak; agreeing with everything is a failure.
5. Ask at most 3 strategic questions that only the Product Owner can answer. Offer a recommended default for each.

## The reply (`comment_markdown`)

- The Product Owner is a non-technical, Chinese-speaking founder. Write the reply in Simplified Chinese,
  plain and short, with no jargon; teach a PM concept in one sentence only when it is used.
- Structure: one-line verdict → what I found (3–6 bullets, with links) → biggest risk → next step →
  numbered questions with your recommended answer. Keep it under ~350 Chinese characters plus links where possible.
- The `record` is the canonical data: write its fields in English, except `title_zh` and `guidance.current_zh`.
- `guidance.step`/`total_steps` follow the six Playbook phases (Problem=1 … Build=6). `guidance.current` is one
  English sentence on what happens next; `current_zh` is the same sentence in Chinese.
"""


def render_comment(result: dict, approved: bool) -> tuple[str, dict]:
    record = dict(result["record"])
    if record.get("stage") == "BUILD" and not approved:
        record["stage"] = "INCUBATE"
    payload = json.dumps(record, ensure_ascii=False, indent=2).replace("-->", "--\\u003e")
    body = f"{result['comment_markdown'].strip()}\n\n<!-- {RECORD_MARKER}\n{payload}\n-->"
    return body, record


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("prompt", "post"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--repo", required=True)
        cmd.add_argument("--issue", type=int, required=True)
        cmd.add_argument("--owner", required=True)
        cmd.add_argument("file", type=Path)
    args = parser.parse_args()

    issue = gh_json(f"repos/{args.repo}/issues/{args.issue}")
    comments = gh_json(f"repos/{args.repo}/issues/{args.issue}/comments?per_page=100", paginate=True)
    if args.command == "prompt":
        args.file.write_text(build_prompt(issue, comments, args.owner), encoding="utf-8")
        return

    result = json.loads(args.file.read_text(encoding="utf-8"))
    body, record = render_comment(result, owner_approved_build(comments, args.owner))
    subprocess.run(
        ["gh", "api", f"repos/{args.repo}/issues/{args.issue}/comments", "-f", f"body={body}"],
        check=True,
        capture_output=True,
    )
    print(f"Posted Product Brain turn on #{args.issue}: stage {record['stage']}, {record['decision']['recommendation']}")


if __name__ == "__main__":
    main()
