from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

STAGES = {"SPARK", "EXPLORE", "VALIDATE", "INCUBATE", "BUILD", "PARK", "REJECT"}
RECOMMENDATIONS = {"PROMOTE", "STAY", "PARK", "REJECT"}
CONFIDENCE = {"low", "medium", "high"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "product-incubator" / "idea.schema.json"


def validate_schema(record: dict) -> None:
    schema = json.loads(SCHEMA_PATH.read_text())
    errors = sorted(Draft202012Validator(schema).iter_errors(record), key=lambda error: list(error.path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.path) or "<root>"
        raise ValueError(f"schema validation failed at {location}: {error.message}")


def validate(record: dict) -> None:
    validate_schema(record)
    require(isinstance(record.get("idea_issue"), int) and record["idea_issue"] > 0, "idea_issue must be a positive integer")
    stage = record.get("stage")
    require(stage in STAGES, f"invalid stage: {stage!r}")

    thesis = record.get("thesis")
    require(isinstance(thesis, dict), "thesis must be an object")

    decision = record.get("decision")
    require(isinstance(decision, dict), "decision must be an object")
    require(decision.get("recommendation") in RECOMMENDATIONS, "invalid decision.recommendation")
    require(decision.get("confidence") in CONFIDENCE, "invalid decision.confidence")
    for field in ("strongest_reason", "biggest_uncertainty", "next_action"):
        require(bool(str(decision.get(field, "")).strip()), f"decision.{field} is required")

    if stage in {"EXPLORE", "VALIDATE", "INCUBATE", "BUILD"}:
        for field in ("problem", "target_user", "product_hypothesis"):
            require(bool(str(thesis.get(field, "")).strip()), f"thesis.{field} is required at stage {stage}")

    if stage in {"VALIDATE", "INCUBATE", "BUILD"}:
        validation = record.get("validation")
        require(isinstance(validation, dict), f"validation is required at stage {stage}")
        require(bool(str(validation.get("riskiest_assumption", "")).strip()), "validation.riskiest_assumption is required")
        require(bool(str(validation.get("cheapest_next_validation", "")).strip()), "validation.cheapest_next_validation is required")

    if stage in {"INCUBATE", "BUILD"}:
        mvp = record.get("mvp")
        require(isinstance(mvp, dict), f"mvp is required at stage {stage}")
        require(bool(mvp.get("capabilities")), "mvp.capabilities must not be empty")
        require(bool(mvp.get("non_goals")), "mvp.non_goals must not be empty")
        require(bool(mvp.get("core_user_journey")), "mvp.core_user_journey must not be empty")

    if stage == "BUILD":
        handoff = record.get("build_handoff")
        require(isinstance(handoff, dict), "build_handoff is required at BUILD")
        require(bool(handoff.get("epics")), "build_handoff.epics must not be empty")
        require(bool(str(handoff.get("human_acceptance_gate", "")).strip()), "build_handoff.human_acceptance_gate is required")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate an Idea Cauldron product incubation record")
    parser.add_argument("record", type=Path)
    args = parser.parse_args()

    record = json.loads(args.record.read_text())
    validate(record)
    print(f"Valid incubation record: {args.record}")


if __name__ == "__main__":
    main()
