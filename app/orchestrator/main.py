import json
from pathlib import Path

from jsonschema import validate, ValidationError

from app.planner.mock_planner import MockPlanner
from config.settings import SCHEMA_PATH, SAMPLE_GOAL_PATH


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as f:
        return f.read().strip()


def main() -> None:
    schema = load_json(SCHEMA_PATH)
    goal = load_text(SAMPLE_GOAL_PATH)

    planner = MockPlanner()
    plan = planner.generate_plan(goal)

    print(f"Goal received: {goal}")

    try:
        validate(instance=plan, schema=schema)
        print("Plan is valid.")
        print(json.dumps(plan, indent=2))
    except ValidationError as e:
        print("Plan is invalid.")
        print(f"Validation error: {e.message}")


if __name__ == "__main__":
    main()