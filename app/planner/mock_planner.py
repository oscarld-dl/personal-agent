import json
from pathlib import Path


def generate_plan_from_goal(goal: str) -> dict:
    """
    Temporary mock planner.

    For now, it ignores the input goal and returns a fixed sample plan.
    Later, this function will call the real planning model.
    """
    root = Path(__file__).resolve().parents[2]
    sample_plan_path = root / "tests" / "sample_plan.json"

    with sample_plan_path.open("r", encoding="utf-8") as f:
        return json.load(f)