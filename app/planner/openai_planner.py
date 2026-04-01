import json

from openai import OpenAI

from app.planner.base import Planner
from app.planner.prompt_loader import load_prompt
from config.settings import OPENAI_API_KEY, OPENAI_MODEL, PLANNER_PROMPT_PATH


class OpenAIPlanner(Planner):
    def __init__(self) -> None:
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in the environment.")

        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.system_prompt = load_prompt(PLANNER_PROMPT_PATH)

    def generate_plan(self, goal: str) -> dict:
        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": self.system_prompt,
                },
                {
                    "role": "user",
                    "content": f"User goal: {goal}",
                },
            ],
        )

        text_output = response.output_text.strip()
        cleaned_output = self._strip_code_fences(text_output)

        try:
            return json.loads(cleaned_output)
        except json.JSONDecodeError as e:
            raise ValueError(
                "Model output was not valid JSON. "
                f"Raw output:\n{text_output}"
            ) from e

    def _strip_code_fences(self, text: str) -> str:
        text = text.strip()

        if text.startswith("```json"):
            text = text[len("```json"):].strip()
        elif text.startswith("```"):
            text = text[len("```"):].strip()

        if text.endswith("```"):
            text = text[:-3].strip()

        return text