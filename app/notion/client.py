import mimetypes
from pathlib import Path
from urllib.parse import urlparse

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
    FILES_PROPERTY_NAME = "Files & media"
    TEXT_CONTENT_LIMIT = 2000
    FILE_UPLOAD_SIZE_LIMIT_BYTES = 20 * 1024 * 1024

    def __init__(self) -> None:
        if not NOTION_API_KEY:
            raise ValueError("NOTION_API_KEY is not set in the environment.")

        self.headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": self.NOTION_VERSION,
        }
        self.upload_headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": self.NOTION_VERSION,
        }
        self.projects_data_source_id = NOTION_PROJECTS_DATA_SOURCE_ID or NOTION_PROJECTS_DB_ID
        self.tasks_data_source_id = NOTION_TASKS_DATA_SOURCE_ID or NOTION_TASKS_DB_ID
        self._status_options_cache: dict[str, dict] = {}
        self._data_source_cache: dict[str, dict] = {}

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

    def _get_data_source_schema(self, data_source_id: str) -> dict:
        if data_source_id not in self._data_source_cache:
            self._data_source_cache[data_source_id] = self.retrieve_data_source(data_source_id)
        return self._data_source_cache[data_source_id]

    def _get_status_schema(self, data_source_id: str) -> dict:
        if data_source_id not in self._status_options_cache:
            data_source = self._get_data_source_schema(data_source_id)
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
            {"not started", "todo", "to do", "backlog"},
            {"in progress", "doing", "active"},
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

    def tasks_has_files_media_property(self) -> bool:
        properties = self._get_data_source_schema(self.tasks_data_source_id).get("properties", {})
        files_property = properties.get(self.FILES_PROPERTY_NAME)
        return bool(files_property and files_property.get("type") == "files")

    def update_page_files_media(self, page_id: str, files: list[dict]) -> dict:
        payload = {
            "properties": {
                self.FILES_PROPERTY_NAME: {
                    "files": files
                }
            }
        }
        response = requests.patch(
            f"{self.BASE_URL}/pages/{page_id}",
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        self._raise_for_status(response)
        return response.json()

    def append_block_children(self, page_id: str, children: list[dict]) -> dict:
        payload = {"children": children}
        response = requests.patch(
            f"{self.BASE_URL}/blocks/{page_id}/children",
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        self._raise_for_status(response)
        return response.json()

    def append_task_context(
        self,
        page_id: str,
        notes: str = "",
        attachment_urls: list[str] | None = None,
        attachment_paths: list[str] | None = None,
    ) -> bool:
        children = self.build_task_context_blocks(notes, attachment_urls or [], attachment_paths or [])
        if not children:
            return False

        self.append_block_children(page_id, children)
        return True

    def build_external_file_object(self, url: str) -> dict:
        parsed = urlparse(url)
        filename = Path(parsed.path).name or parsed.netloc or "External attachment"
        return {
            "name": filename,
            "type": "external",
            "external": {
                "url": url
            },
        }

    def upload_local_file(self, file_path: str) -> dict | None:
        path = Path(file_path).expanduser()

        if not path.exists():
            print(f"[Notion Warning] Local attachment path not found: {file_path}")
            return None
        if not path.is_file():
            print(f"[Notion Warning] Local attachment path is not a file: {file_path}")
            return None
        if path.stat().st_size > self.FILE_UPLOAD_SIZE_LIMIT_BYTES:
            print(
                f"[Notion Warning] Local attachment exceeds {self.FILE_UPLOAD_SIZE_LIMIT_BYTES} bytes: "
                f"{file_path}"
            )
            return None

        create_response = requests.post(
            f"{self.BASE_URL}/file_uploads",
            headers=self.headers,
            json={},
            timeout=30,
        )
        self._raise_for_status(create_response)
        upload = create_response.json()
        upload_id = upload["id"]

        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        with path.open("rb") as file_handle:
            send_response = requests.post(
                f"{self.BASE_URL}/file_uploads/{upload_id}/send",
                headers=self.upload_headers,
                data={"filename": path.name},
                files={"file": (path.name, file_handle, mime_type)},
                timeout=120,
            )
        self._raise_for_status(send_response)

        return {
            "name": path.name,
            "type": "file_upload",
            "file_upload": {
                "id": upload_id
            },
        }

    def build_task_context_blocks(
        self,
        notes: str,
        attachment_urls: list[str],
        attachment_paths: list[str],
    ) -> list[dict]:
        children: list[dict] = []

        if notes:
            children.append(self._heading_block("Task Notes"))
            children.extend(self._paragraph_blocks(notes))

        if attachment_urls or attachment_paths:
            heading = "Attachments" if notes else "Task Attachments"
            children.append(self._heading_block(heading))

        for url in attachment_urls:
            children.extend(self._paragraph_blocks(f"URL: {url}"))

        for path in attachment_paths:
            children.extend(self._paragraph_blocks(f"Local file: {path}"))

        return children

    def _heading_block(self, text: str) -> dict:
        return {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [self._rich_text(text)]
            },
        }

    def _paragraph_blocks(self, text: str) -> list[dict]:
        blocks: list[dict] = []
        for line in text.splitlines() or [text]:
            clean_line = line.strip()
            if not clean_line:
                continue

            for chunk in self._chunk_text(clean_line):
                blocks.append(
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [self._rich_text(chunk)]
                        },
                    }
                )

        return blocks

    def _chunk_text(self, text: str) -> list[str]:
        return [
            text[index:index + self.TEXT_CONTENT_LIMIT]
            for index in range(0, len(text), self.TEXT_CONTENT_LIMIT)
        ]

    def _rich_text(self, text: str) -> dict:
        return {
            "type": "text",
            "text": {
                "content": text
            },
        }

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
