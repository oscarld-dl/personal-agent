from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]

SCHEMA_PATH = ROOT_DIR / "schemas" / "plan_schema.json"
SAMPLE_GOAL_PATH = ROOT_DIR / "tests" / "sample_goal.txt"
SAMPLE_PLAN_PATH = ROOT_DIR / "tests" / "sample_plan.json"