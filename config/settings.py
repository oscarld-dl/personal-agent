from pathlib import Path
import os

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]

load_dotenv(ROOT_DIR / ".env")

SCHEMA_PATH = ROOT_DIR / "schemas" / "plan_schema.json"
SAMPLE_GOAL_PATH = ROOT_DIR / "tests" / "sample_goal.txt"
SAMPLE_PLAN_PATH = ROOT_DIR / "tests" / "sample_plan.json"
PLANNER_PROMPT_PATH = ROOT_DIR / "prompts" / "planner_prompt.md"

PLANNER_TYPE = "openai"  # Change to "mock" for testing without API calls

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_TASKS_DB_ID = os.getenv("NOTION_TASKS_DB_ID")
NOTION_PROJECTS_DB_ID = os.getenv("NOTION_PROJECTS_DB_ID")
NOTION_TASKS_DATA_SOURCE_ID = os.getenv("NOTION_TASKS_DATA_SOURCE_ID")
NOTION_PROJECTS_DATA_SOURCE_ID = os.getenv("NOTION_PROJECTS_DATA_SOURCE_ID")
