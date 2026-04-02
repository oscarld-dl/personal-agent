def normalize_status(status: str | None) -> str:
    if not status:
        return "Not started"

    normalized = status.strip().lower().replace("_", " ").replace("-", " ")
    status_map = {
        "not started": "Not started",
        "in progress": "In progress",
        "completed": "Completed",
    }

    return status_map.get(normalized, status.strip())


def map_project_to_notion(project: dict, goal: str) -> dict:
    return {
        "Project name": project["name"],
        "Priority": project["priority"],
        "Status": normalize_status(project.get("status")),
        "Goal description": goal,
    }


def map_task_to_notion(
    task: dict,
    project_name: str,
    project_page_id: str | None = None,
) -> dict:
    depends_on = task.get("depends_on", [])
    depends_text = ", ".join(depends_on) if depends_on else ""

    notion_task = {
        "Task name": task["title"],
        "Project name": project_name,
        "Priority": task["priority"],
        "Status": normalize_status(task.get("status")),
        "Summary": task.get("estimated_effort", ""),
        "Description": depends_text,
    }

    if project_page_id:
        notion_task["Projects"] = [{"id": project_page_id}]

    if task.get("Attachment URLs"):
        notion_task["Attachment URLs"] = task["Attachment URLs"]

    if task.get("Attachment Paths"):
        notion_task["Attachment Paths"] = task["Attachment Paths"]

    if task.get("Notes"):
        notion_task["Notes"] = task["Notes"]

    return notion_task
