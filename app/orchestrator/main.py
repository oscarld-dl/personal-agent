# app/orchestrator/main.py

import json
from pathlib import Path

from jsonschema import validate, ValidationError


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    root = Path(__file__).resolve().parents[2]

    schema_path = root / "schemas" / "plan_schema.json"
    sample_path = root / "tests" / "sample_plan.json"

    schema = load_json(schema_path)
    sample_plan = load_json(sample_path)

    try:
        validate(instance=sample_plan, schema=schema)
        print("Plan is valid.")
    except ValidationError as e:
        print("Plan is invalid.")
        print(f"Validation error: {e.message}")


if __name__ == "__main__":
    main()