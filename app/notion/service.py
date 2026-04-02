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
            self._enrich_task_page(created_task, mapped_task)

    def _enrich_task_page(self, created_task: dict, task_data: dict) -> None:
        page_id = created_task.get("id")
        if not page_id:
            return

        attachment_urls = task_data.get("Attachment URLs", [])
        attachment_paths = task_data.get("Attachment Paths", [])
        notes = task_data.get("Notes", "")

        try:
            files_property_found = self.client.tasks_has_files_media_property()
        except Exception as exc:
            print(f'[Notion Warning] Failed to inspect "{self.client.FILES_PROPERTY_NAME}": {exc}')
            files_property_found = False
        print(f'[Notion] "{self.client.FILES_PROPERTY_NAME}" found: {files_property_found}')

        files_to_attach: list[dict] = []
        urls_attached = False
        uploaded_local_files = 0

        if files_property_found and attachment_urls:
            files_to_attach.extend(
                self.client.build_external_file_object(url)
                for url in attachment_urls
            )

        if files_property_found and attachment_paths:
            for file_path in attachment_paths:
                try:
                    uploaded_file = self.client.upload_local_file(file_path)
                except Exception as exc:
                    print(f"[Notion Warning] Failed to upload local file {file_path}: {exc}")
                    uploaded_file = None

                if uploaded_file:
                    files_to_attach.append(uploaded_file)
                    uploaded_local_files += 1

        if files_property_found and files_to_attach:
            try:
                self.client.update_page_files_media(page_id, files_to_attach)
                urls_attached = bool(attachment_urls)
            except Exception as exc:
                print(f'[Notion Warning] Failed to update "{self.client.FILES_PROPERTY_NAME}": {exc}')
                urls_attached = False

        print(f"[Notion] URLs attached to files property: {urls_attached}")
        print(f"[Notion] Local files uploaded: {uploaded_local_files}")

        try:
            notes_appended = self.client.append_task_context(
                page_id,
                notes=notes,
                attachment_urls=attachment_urls,
                attachment_paths=attachment_paths,
            )
        except Exception as exc:
            print(f"[Notion Warning] Failed to append task notes/attachments block content: {exc}")
            notes_appended = False

        print(f"[Notion] Notes/attachment context appended: {notes_appended}")
