import json
import sys
from pathlib import Path

from jsonschema import validate, ValidationError
from openai import RateLimitError

from app.notion.client import NotionClient
from app.notion.service import NotionService
from app.planner.factory import get_fallback_planner, get_planner
from config.settings import SAMPLE_GOAL_PATH, SCHEMA_PATH


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as f:
        return f.read().strip()


def get_goal_from_input() -> str:
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()
    return load_text(SAMPLE_GOAL_PATH)


def main() -> None:
    schema = load_json(SCHEMA_PATH)
    goal = get_goal_from_input()

    planner = get_planner()

    try:
        plan = planner.generate_plan(goal)
    except RateLimitError as e:
        print("OpenAI planner unavailable due to quota/rate limit. Falling back to mock planner.")
        print(f"Original error: {e}")
        planner = get_fallback_planner()
        plan = planner.generate_plan(goal)

    print(f"Goal received: {goal}")

    try:
        validate(instance=plan, schema=schema)
    except ValidationError as e:
        print("Plan is invalid.")
        print(f"Validation error: {e.message}")
        return

    notion_client = NotionClient()
    notion_service = NotionService(notion_client)

    try:
        notion_service.save_plan(plan)
        print("Plan saved to Notion successfully!")
    except Exception as e:
        print(f"Error saving plan to Notion: {e}")


if __name__ == "__main__":
    main()