from abc import ABC, abstractmethod


class Planner(ABC):
    @abstractmethod
    def generate_plan(self, goal: str) -> dict:
        """Generate a structured plan from a user goal."""
        pass