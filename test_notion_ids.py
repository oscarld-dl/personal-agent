from app.notion.client import NotionClient
from config.settings import NOTION_PROJECTS_DB_ID, NOTION_TASKS_DB_ID

client = NotionClient()

for label, notion_id in [
    ("Projects", NOTION_PROJECTS_DB_ID),
    ("Tasks", NOTION_TASKS_DB_ID),
]:
    print(f"\n--- {label} ---")
    print(f"ID: {notion_id}")

    try:
        db = client.retrieve_database(notion_id)
        print("Works as database ID")
        print(db)
    except Exception as e:
        print(f"Not a database ID: {e}")

    try:
        ds = client.retrieve_data_source(notion_id)
        print("Works as data source ID")
        print(ds)
    except Exception as e:
        print(f"Not a data source ID: {e}")
