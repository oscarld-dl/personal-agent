import requests

from config.settings import NOTION_API_KEY, NOTION_PROJECTS_DB_ID, NOTION_TASKS_DB_ID


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

        print(f"[Notion Debug] Projects ID: {NOTION_PROJECTS_DB_ID}")
        print(f"[Notion Debug] Tasks ID: {NOTION_TASKS_DB_ID}")

    def create_project(self, project_data: dict) -> dict:
        payload = {
            "parent": {
                "type": "data_source_id",
                "data_source_id": NOTION_PROJECTS_DB_ID,
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
                        "name": project_data["Status"]
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
        response.raise_for_status()
        data = response.json()
        return data

    def create_task(self, task_data: dict) -> dict:
        
        payload = {
            "parent": {
                "type": "data_source_id",
                "data_source_id": NOTION_TASKS_DB_ID,
            },
            "properties": {
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
                        "name": task_data["Status"]
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
        }
    }
}

        response = requests.post(
            f"{self.BASE_URL}/pages",
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data
    
    def retrieve_database(self, database_id: str) -> dict:
        response = requests.get(
            f"{self.BASE_URL}/databases/{database_id}",
            headers=self.headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()


    def retrieve_data_source(self, data_source_id: str) -> dict:
        response = requests.get(
            f"{self.BASE_URL}/data_sources/{data_source_id}",
            headers=self.headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()