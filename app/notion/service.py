from app.notion.client import NotionClient
from app.notion.mapper import map_project_to_notion, map_task_to_notion
from config.settings import EXISTING_PROJECT_NAME


class NotionService:
    def __init__(self, client: NotionClient) -> None:
        self.client = client

    def save_plan(self, plan: dict) -> None:
        goal = plan["goal"]
        project = plan["project"]
        tasks = plan["tasks"]

        if EXISTING_PROJECT_NAME:
            project_name = EXISTING_PROJECT_NAME
            project_page_id = self.client.find_project_page_id_by_name(project_name)
            print(f"[Notion] Found existing project: {project_name}")
            print(f"[Notion] Existing project page ID: {project_page_id}")
        else:
            mapped_project = map_project_to_notion(project, goal)
            created_project = self.client.create_project(mapped_project)
            project_name = project["name"]
            project_page_id = created_project.get("id")
            print(f"[Notion] Project page URL: {created_project.get('url')}")
            print(f"[Notion] Project page ID: {project_page_id}")

        for task in tasks:
            mapped_task = map_task_to_notion(task, project_name, project_page_id)
            created_task = self.client.create_task(mapped_task)
            print(f"[Notion] Task page URL: {created_task.get('url')}")
