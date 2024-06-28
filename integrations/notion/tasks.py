import os
import requests
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
JOURNAL_DB_ID = os.getenv("JOURNAL_DB_ID")
TASKS_DB_ID = os.getenv("TASKS_DB_ID")


def fetch_tasks(tasks_db_id: str, filter_str: str) -> dict:
    try:
        payload = {
            "filter": {
                "property": "Status",
                "status": {"equals": filter_str},
            }
        }
        headers = {
            "Authorization": "Bearer " + NOTION_API_TOKEN,
            "Content-Type": "application/json",
            "Notion-Version": "2022-02-22",
        }

        api_url = f"https://api.notion.com/v1/databases/{TASKS_DB_ID}/query"
        response = requests.request("POST", api_url, json=payload, headers=headers)

        response.raise_for_status()
        response_data = response.json()

        return response_data
    except Exception as e:
        print("Error in fetching tasks", e)


def extract_task_details(tasks: list) -> list:
    tasks_details = []

    for task in tasks:
        name = (
            task["properties"]["Name"]["title"][0]["plain_text"]
            if task["properties"]["Name"]["title"]
            else "No Task Text"
        )
        created_time = task["properties"]["Created time"]["created_time"]
        tags = [tag["name"] for tag in task["properties"]["Tags"]["multi_select"]]
        status = task["properties"]["Status"]["status"]["name"]

        task_details = {
            "Name": name,
            "Created Time": created_time,
            "Tags": tags,
            "Status": status,
        }

        tasks_details.append(task_details)

    return tasks_details


def get_filtered_task(filter_str: str) -> list:
    raw_tasks_list = fetch_tasks(TASKS_DB_ID, filter_str)
    task_details_list = extract_task_details(raw_tasks_list["results"])

    return task_details_list


if __name__ == "__main__":
    # 'Not started', 'In progress', 'Done'
    pprint(get_filtered_task("In progress"))
