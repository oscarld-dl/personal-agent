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
        created_project = self.client.create_project(mapped_project)
        print(f"[Notion] Project page URL: {created_project.get('url')}")
        print(f"[Notion] Full project response: {created_project}")

        for task in tasks:
            mapped_task = map_task_to_notion(task, project["name"])
            created_task = self.client.create_task(mapped_task)
            print(f"[Notion] Task page URL: {created_task.get('url')}")