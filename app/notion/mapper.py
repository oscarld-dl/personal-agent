def map_project_to_notion(project: dict, goal: str) -> dict:
    """
    Convert planner project data into a Notion-ready project payload.
    """
    return {
        "Name": project["name"],
        "Priority": project["priority"],
        "Source Goal": goal,
    }


def map_task_to_notion(task: dict, project_name: str) -> dict:
    """
    Convert planner task data into a Notion-ready task payload.
    """
    return {
        "Title": task["title"],
        "Project": project_name,
        "Priority": task["priority"],
        "Estimated Effort": task.get("estimated_effort", ""),
        "Depends On": task.get("depends_on", []),
        "Status": "Not started",
    }