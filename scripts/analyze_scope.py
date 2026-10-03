from __future__ import annotations

import json
import os
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "dashboard" / "data.json"
OUTPUT_PATH = ROOT / "dashboard" / "scope-analysis.json"
API = "https://api.github.com"
TOKEN = os.getenv("PORTFOLIO_GITHUB_TOKEN") or os.getenv("AGENT_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")

DOMAIN_RULES = {
    "config": [r"\bconfig", r"dependency", r"sdk", r"package", r"plist", r"secret", r"credential"],
    "state": [r"session", r"persist", r"restore", r"refresh", r"keychain", r"storage", r"state"],
    "api": [r"\bapi\b", r"endpoint", r"bearer", r"authorization", r"http", r"/me\b"],
    "ui": [r"\bui\b", r"swiftui", r"screen", r"view", r"profile", r"form", r"loading"],
    "ci": [r"\bci\b", r"workflow", r"github actions", r"xcodebuild", r"simulator", r"testflight", r"deploy"],
    "live": [r"live", r"real credential", r"external service", r"device", r"manual checklist", r"human acceptance"],
}


def request_json(path: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "venture-lab-scope-gate",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    request = urllib.request.Request(f"{API}{path}", headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def count_acceptance_items(body: str) -> int:
    lines = body.splitlines()
    in_acceptance = False
    count = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_acceptance = "acceptance" in stripped.lower()
            continue
        if in_acceptance and re.match(r"^[-*]\s+", stripped):
            count += 1
    return count


def detect_domains(text: str) -> list[str]:
    lowered = text.lower()
    found = []
    for name, patterns in DOMAIN_RULES.items():
        if any(re.search(pattern, lowered) for pattern in patterns):
            found.append(name)
    return found


def analyze(title: str, body: str) -> dict:
    combined = f"{title}\n{body}"
    domains = detect_domains(combined)
    acceptance_items = count_acceptance_items(body)
    headings = len(re.findall(r"(?m)^##\s+", body))
    allowed_file_lines = len(re.findall(r"(?m)^-\s+[^\n]*(?:/|\.swift|\.py|\.yml|\.yaml|\.json|\.md)\b", body))

    score = 0
    signals: list[str] = []

    if len(domains) >= 4:
        score += 3
        signals.append(f"spans {len(domains)} implementation domains: {', '.join(domains)}")
    elif len(domains) == 3:
        score += 2
        signals.append(f"spans 3 implementation domains: {', '.join(domains)}")
    elif len(domains) == 2:
        score += 1
        signals.append(f"spans 2 implementation domains: {', '.join(domains)}")

    if acceptance_items >= 8:
        score += 3
        signals.append(f"has {acceptance_items} acceptance bullets")
    elif acceptance_items >= 5:
        score += 2
        signals.append(f"has {acceptance_items} acceptance bullets")
    elif acceptance_items >= 3:
        score += 1

    if headings >= 6:
        score += 1
        signals.append(f"contains {headings} structured sections")

    if allowed_file_lines >= 6:
        score += 1
        signals.append("touches many explicitly scoped files/directories")

    if "live" in domains and "ci" in domains:
        score += 1
        signals.append("mixes deterministic automation with live/manual validation")

    if score >= 6:
        verdict = "oversized"
        confidence = "high"
    elif score >= 4:
        verdict = "oversized"
        confidence = "medium"
    else:
        verdict = "bounded"
        confidence = "high" if score <= 2 else "medium"

    return {
        "verdict": verdict,
        "confidence": confidence,
        "score": score,
        "signals": signals or ["single focused implementation surface detected"],
        "domains": domains,
        "acceptance_items": acceptance_items,
        "shadow_mode": True,
    }


def main() -> None:
    if not DATA_PATH.exists():
        raise SystemExit("dashboard/data.json not found; run generate_dashboard.py first")

    data = json.loads(DATA_PATH.read_text())
    results = []

    for item in data.get("work_items", []):
        if item.get("workflow_stage") != "ready":
            continue
        repo = item.get("repo")
        issue_number = item.get("issue")
        if not repo or not issue_number:
            continue
        try:
            issue = request_json(f"/repos/{repo}/issues/{issue_number}")
            title = issue.get("title") or item.get("title") or f"Issue #{issue_number}"
            body = issue.get("body") or ""
            assessment = analyze(title, body)
            results.append(
                {
                    "repo": repo,
                    "issue": issue_number,
                    "title": title,
                    **assessment,
                }
            )
        except Exception as exc:
            results.append(
                {
                    "repo": repo,
                    "issue": issue_number,
                    "title": item.get("title") or f"Issue #{issue_number}",
                    "verdict": "needs_human",
                    "confidence": "low",
                    "score": None,
                    "signals": [f"scope analysis unavailable: {exc.__class__.__name__}"],
                    "domains": [],
                    "acceptance_items": None,
                    "shadow_mode": True,
                }
            )

    payload = {"mode": "shadow", "results": results}
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
