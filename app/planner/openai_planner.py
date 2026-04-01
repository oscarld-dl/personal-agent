from app.planner.base import Planner


class OpenAIPlanner(Planner):
    def generate_plan(self, goal: str) -> dict:
        """
        Future real planner implementation.

        This class will later call the language model using the planner prompt
        and return a structured JSON plan.
        """
        raise NotImplementedError("OpenAIPlanner is not implemented yet.")