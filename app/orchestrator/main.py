import json
from pathlib import Path

from jsonschema import validate, ValidationError

from app.notion.client import NotionClient
from app.notion.service import NotionService
from app.planner.factory import get_planner
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

    planner = get_planner()
    plan = planner.generate_plan(goal)

    print(f"Goal received: {goal}")

    try:
        validate(instance=plan, schema=schema)
        print("Plan is valid.")
        print(json.dumps(plan, indent=2))

        notion_client = NotionClient()
        notion_service = NotionService(notion_client)
        notion_service.save_plan(plan)

    except ValidationError as e:
        print("Plan is invalid.")
        print(f"Validation error: {e.message}")


if __name__ == "__main__":
    main()