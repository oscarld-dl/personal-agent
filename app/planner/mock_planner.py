import json

from app.planner.base import Planner
from config.settings import SAMPLE_PLAN_PATH


class MockPlanner(Planner):
    def generate_plan(self, goal: str) -> dict:
        """
        Temporary mock planner.

        For now, it ignores the input goal and returns a fixed sample plan.
        Later, this class can be replaced by a real model-backed planner.
        """
        with SAMPLE_PLAN_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)