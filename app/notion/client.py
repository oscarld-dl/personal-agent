import requests

from config.settings import (
    NOTION_API_KEY,
    NOTION_PROJECTS_DATA_SOURCE_ID,
    NOTION_PROJECTS_DB_ID,
    NOTION_TASKS_DATA_SOURCE_ID,
    NOTION_TASKS_DB_ID,
)


class NotionClient:
    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2026-03-11"

    def __init__(self) -> None:
        if not NOTION_API_KEY:
            raise ValueError("NOTION_API_KEY is not set in the environment.")

        self.headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": self.NOTION_VERSION,
        }
        self.projects_data_source_id = NOTION_PROJECTS_DATA_SOURCE_ID or NOTION_PROJECTS_DB_ID
        self.tasks_data_source_id = NOTION_TASKS_DATA_SOURCE_ID or NOTION_TASKS_DB_ID
        self._status_options_cache: dict[str, dict] = {}

        if not self.projects_data_source_id:
            raise ValueError("NOTION_PROJECTS_DATA_SOURCE_ID or NOTION_PROJECTS_DB_ID is not set.")
        if not self.tasks_data_source_id:
            raise ValueError("NOTION_TASKS_DATA_SOURCE_ID or NOTION_TASKS_DB_ID is not set.")

        print(f"[Notion Debug] Projects data source ID: {self.projects_data_source_id}")
        print(f"[Notion Debug] Tasks data source ID: {self.tasks_data_source_id}")

    def create_project(self, project_data: dict) -> dict:
        status_name = self.resolve_status_name(
            self.projects_data_source_id,
            project_data["Status"],
        )
        payload = {
            "parent": {
                "type": "data_source_id",
                "data_source_id": self.projects_data_source_id,
            },
            "properties": {
                "Project name": {
                    "title": [
                        {
                            "text": {
                                "content": project_data["Project name"]
                            }
                        }
                    ]
                },
                "Priority": {
                    "select": {
                        "name": project_data["Priority"].capitalize()
                    }
                },
                "Status": {
                    "status": {
                        "name": status_name
                    }
                }
            },
        }

        response = requests.post(
            f"{self.BASE_URL}/pages",
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        self._raise_for_status(response)
        return response.json()

    def create_task(self, task_data: dict) -> dict:
        status_name = self.resolve_status_name(
            self.tasks_data_source_id,
            task_data["Status"],
        )
        properties = {
            "Task name": {
                "title": [
                    {
                        "text": {
                            "content": task_data["Task name"]
                        }
                    }
                ]
            },
            "Priority": {
                "select": {
                    "name": task_data["Priority"].capitalize()
                }
            },
            "Status": {
                "status": {
                    "name": status_name
                }
            },
            "Summary": {
                "rich_text": [
                    {
                        "text": {
                            "content": task_data["Summary"]
                        }
                    }
                ]
            },
            "Description": {
                "rich_text": [
                    {
                        "text": {
                            "content": task_data["Description"]
                        }
                    }
                ]
            },
        }

        if task_data.get("Projects"):
            properties["Projects"] = {
                "relation": task_data["Projects"]
            }

        payload = {
            "parent": {
                "type": "data_source_id",
                "data_source_id": self.tasks_data_source_id,
            },
            "properties": properties,
        }

        response = requests.post(
            f"{self.BASE_URL}/pages",
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        self._raise_for_status(response)
        return response.json()

    def _raise_for_status(self, response: requests.Response) -> None:
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            try:
                error_body = response.json()
            except ValueError:
                error_body = response.text

            raise requests.HTTPError(
                f"{exc}. Response body: {error_body}",
                response=response,
            ) from exc

    def _normalize_status_key(self, status_name: str) -> str:
        return " ".join(status_name.strip().lower().replace("_", " ").replace("-", " ").split())

    def _get_status_schema(self, data_source_id: str) -> dict:
        if data_source_id not in self._status_options_cache:
            data_source = self.retrieve_data_source(data_source_id)
            status_property = data_source.get("properties", {}).get("Status")

            if not status_property or status_property.get("type") != "status":
                raise ValueError(
                    f'Data source "{data_source_id}" does not expose a "Status" status property.'
                )

            self._status_options_cache[data_source_id] = status_property["status"]

        return self._status_options_cache[data_source_id]

    def resolve_status_name(self, data_source_id: str, requested_status: str) -> str:
        status_schema = self._get_status_schema(data_source_id)
        options = status_schema.get("options", [])
        groups = status_schema.get("groups", [])
        normalized_requested = self._normalize_status_key(requested_status)

        normalized_options = {
            self._normalize_status_key(option["name"]): option["name"]
            for option in options
        }

        if normalized_requested in normalized_options:
            return normalized_options[normalized_requested]

        group_option_ids = {
            self._normalize_status_key(group["name"]): group.get("option_ids", [])
            for group in groups
        }
        options_by_id = {option["id"]: option["name"] for option in options}

        synonym_groups = (
            {"not started", "not started", "todo", "to do", "backlog"},
            {"in progress", "in progress", "doing", "active"},
            {"completed", "complete", "done", "finished"},
        )

        for synonyms in synonym_groups:
            if normalized_requested not in synonyms:
                continue

            for normalized_option_name, option_name in normalized_options.items():
                if normalized_option_name in synonyms:
                    return option_name

            for normalized_group_name, option_ids in group_option_ids.items():
                if normalized_group_name in synonyms:
                    for option_id in option_ids:
                        if option_id in options_by_id:
                            return options_by_id[option_id]

        available_statuses = ", ".join(option["name"] for option in options)
        raise ValueError(
            f'Unsupported Notion status "{requested_status}" for data source "{data_source_id}". '
            f"Available options: {available_statuses}"
        )

    def query_data_source(self, data_source_id: str, payload: dict | None = None) -> dict:
        response = requests.post(
            f"{self.BASE_URL}/data_sources/{data_source_id}/query",
            headers=self.headers,
            json=payload or {},
            timeout=30,
        )
        self._raise_for_status(response)
        return response.json()

    def find_project_page_id_by_name(self, project_name: str) -> str:
        next_cursor = None

        while True:
            payload = {"page_size": 100}
            if next_cursor:
                payload["start_cursor"] = next_cursor

            response_data = self.query_data_source(self.projects_data_source_id, payload)

            for result in response_data.get("results", []):
                properties = result.get("properties", {})
                title_property = properties.get("Project name", {})
                title_items = title_property.get("title", [])
                current_name = "".join(item.get("plain_text", "") for item in title_items).strip()

                if current_name == project_name:
                    return result["id"]

            if not response_data.get("has_more"):
                break

            next_cursor = response_data.get("next_cursor")

        raise ValueError(
            f'No project page found in the Projects data source with exact title "{project_name}".'
        )

    def retrieve_database(self, database_id: str) -> dict:
        response = requests.get(
            f"{self.BASE_URL}/databases/{database_id}",
            headers=self.headers,
            timeout=30,
        )
        self._raise_for_status(response)
        return response.json()

    def retrieve_data_source(self, data_source_id: str) -> dict:
        response = requests.get(
            f"{self.BASE_URL}/data_sources/{data_source_id}",
            headers=self.headers,
            timeout=30,
        )
        self._raise_for_status(response)
        return response.json()
