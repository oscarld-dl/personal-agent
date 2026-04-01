from app.planner.base import Planner
from app.planner.prompt_loader import load_prompt
from config.settings import PLANNER_PROMPT_PATH


class OpenAIPlanner(Planner):
    def generate_plan(self, goal: str) -> dict:
        """
        Future real planner implementation.

        This class will later call the language model using the planner prompt
        and return a structured JSON plan.
        """
        prompt = load_prompt(PLANNER_PROMPT_PATH)

        raise NotImplementedError(
            "OpenAIPlanner is not implemented yet. "
            f"Prompt loaded successfully ({len(prompt)} characters). "
            f"Goal received: {goal}"
        )