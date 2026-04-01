from app.planner.mock_planner import MockPlanner
from app.planner.openai_planner import OpenAIPlanner
from config.settings import PLANNER_TYPE


def get_planner():
    if PLANNER_TYPE == "mock":
        return MockPlanner()
    if PLANNER_TYPE == "openai":
        return OpenAIPlanner()
    raise ValueError(f"Unsupported planner type: {PLANNER_TYPE}")