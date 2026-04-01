import json
from pathlib import Path

from app.planner.base import Planner


class MockPlanner(Planner):
    def generate_plan(self, goal: str) -> dict:
        """
        Temporary mock planner.

        For now, it ignores the input goal and returns a fixed sample plan.
        Later, this class can be replaced by a real model-backed planner.
        """
        root = Path(__file__).resolve().parents[2]
        sample_plan_path = root / "tests" / "sample_plan.json"

        with sample_plan_path.open("r", encoding="utf-8") as f:
            return json.load(f)