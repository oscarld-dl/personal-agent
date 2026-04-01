import json
from pathlib import Path

from jsonschema import validate, ValidationError

from app.planner.mock_planner import MockPlanner


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as f:
        return f.read().strip()


def main() -> None:
    root = Path(__file__).resolve().parents[2]

    schema_path = root / "schemas" / "plan_schema.json"
    goal_path = root / "tests" / "sample_goal.txt"

    schema = load_json(schema_path)
    goal = load_text(goal_path)

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