from app.notion.client import NotionClient
from app.notion.mapper import map_project_to_notion, map_task_to_notion


class NotionService:
    def __init__(self, client: NotionClient) -> None:
        self.client = client

    def save_plan(self, plan: dict) -> None:
        goal = plan["goal"]
        project = plan["project"]
        tasks = plan["tasks"]

        mapped_project = map_project_to_notion(project, goal)
        self.client.create_project(mapped_project)

        for task in tasks:
            mapped_task = map_task_to_notion(task, project["name"])
            self.client.create_task(mapped_task)