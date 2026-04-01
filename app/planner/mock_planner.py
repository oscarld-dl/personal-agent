from app.planner.base import Planner


class MockPlanner(Planner):
    def generate_plan(self, goal: str) -> dict:
        """
        Temporary mock planner.

        Generates a simple deterministic plan from the input goal.
        Later, this class can be replaced by a real model-backed planner.
        """
        project_name = self._build_project_name(goal)

        return {
            "goal": goal,
            "project": {
                "name": project_name,
                "priority": "high",
            },
            "tasks": [
                {
                    "title": "Clarify project scope",
                    "priority": "high",
                    "estimated_effort": "30m",
                    "depends_on": [],
                },
                {
                    "title": "Break goal into actionable tasks",
                    "priority": "high",
                    "estimated_effort": "45m",
                    "depends_on": ["Clarify project scope"],
                },
                {
                    "title": "Prepare initial implementation plan",
                    "priority": "medium",
                    "estimated_effort": "1h",
                    "depends_on": ["Break goal into actionable tasks"],
                },
            ],
        }

    def _build_project_name(self, goal: str) -> str:
        cleaned = goal.strip()
        if not cleaned:
            return "Untitled Project"

        words = cleaned.split()
        short_name = " ".join(words[:6])

        if len(words) > 6:
            short_name += "..."

        return short_name