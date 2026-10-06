from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "product-incubator" / "records"
OUTPUT = ROOT / "dashboard" / "incubation.json"


def main() -> None:
    ideas = []
    if RECORDS.exists():
        for path in sorted(RECORDS.glob("*.json"), key=lambda p: int(p.stem) if p.stem.isdigit() else p.stem):
            ideas.append(json.loads(path.read_text()))
    OUTPUT.write_text(json.dumps({"ideas": ideas}, ensure_ascii=False, indent=2) + "\n")
    print(f"Generated {OUTPUT.relative_to(ROOT)} with {len(ideas)} idea(s)")


if __name__ == "__main__":
    main()
