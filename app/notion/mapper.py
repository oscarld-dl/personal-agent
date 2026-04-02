def map_project_to_notion(project: dict, goal: str) -> dict:
    return {
        "Project name": project["name"],
        "Priority": project["priority"],
        "Status": "Not started",
        "Goal description": goal,
    }


def map_task_to_notion(task: dict, project_name: str) -> dict:
    depends_on = task.get("depends_on", [])
    depends_text = ", ".join(depends_on) if depends_on else ""

    return {
        "Task name": task["title"],
        "Project name": project_name,
        "Priority": task["priority"],
        "Status": "Not started",
        "Summary": task.get("estimated_effort", ""),
        "Description": depends_text,
    }