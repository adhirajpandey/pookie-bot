from datetime import datetime
import pytz
import os
import requests
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
JOURNAL_DB_ID = os.getenv("JOURNAL_DB_ID")


# get current date in YYYY-MM-DD format
def get_current_date() -> str:
    ist = pytz.timezone("Asia/Calcutta")
    current_datetime = datetime.now(ist)

    formatted_datetime = current_datetime.strftime("%Y-%m-%d")

    return formatted_datetime


# read notion database optimally(timeframe) by finding date-days difference
def read_notion_db_optimally(database_id: str, date_str: str) -> dict:
    try:
        today_date = datetime.strptime(get_current_date(), "%Y-%m-%d")
        input_date = datetime.strptime(date_str, "%Y-%m-%d")
        days_dif = (today_date - input_date).days

        if days_dif <= 6:
            payload = {
                "filter": {
                    "property": "Created At",
                    "date": {
                        "past_week": {}
                        # "equals": "2024-06-20"
                    },
                }
            }
        else:
            payload = {}

        headers = {
            "Authorization": "Bearer " + NOTION_API_TOKEN,
            "Content-Type": "application/json",
            "Notion-Version": "2022-02-22",
        }

        api_url = f"https://api.notion.com/v1/databases/{database_id}/query"
        response = requests.request("POST", api_url, json=payload, headers=headers)

        response.raise_for_status()
        response_data = response.json()

        return response_data

    except Exception as e:
        print(f"Error occured while fetching notion db: {e}")


# get today's page id from journal database
def get_pageid_from_journal_db(journal_db: dict, date_str: str) -> str:
    try:
        found = False
        for page in journal_db["results"]:
            if page["properties"]["Name"]["title"][0]["plain_text"] == date_str:
                found = True
                return page["id"]
        if not found:
            print("Journal page not found in notion API response")
            exit()
    except Exception as e:
        print(f"Error occured while fetching pageid: {e}")


# read block content
def read_block_content(blockid: str) -> dict:
    try:
        url = f"https://api.notion.com/v1/blocks/{blockid}"

        headers = {
            "Notion-Version": "2022-06-28",
            "Authorization": "Bearer " + NOTION_API_TOKEN,
        }

        response = requests.request("GET", url, headers=headers)

        response.raise_for_status()
        response_data = response.json()

        return response_data

    except Exception as e:
        print(f"Error while reading block content {e}")
        return []


# read block children
def read_block_children(blockid: str) -> dict:
    try:
        url = f"https://api.notion.com/v1/blocks/{blockid}/children"

        headers = {
            "Notion-Version": "2022-06-28",
            "Authorization": "Bearer " + NOTION_API_TOKEN,
        }

        response = requests.request("GET", url, headers=headers)

        response.raise_for_status()
        response_data = response.json()

        return response_data

    except Exception as e:
        print(f"Error while reading block children {e}")
        return []


# extract page properties
def get_page_properties(journal_db: dict, date_str: str) -> dict:
    try:
        props = {}
        metrics = {
            "Sleep_Hours": -1,
            "Stress_Level": -1,
            "Satisfaction_Level": -1,
            "Steps_Count": -1,
        }

        satisfied_with = {"Explored": -1, "Physical": -1, "Sleep": -1, "Tasks": -1}

        for page in journal_db["results"]:
            if page["properties"]["Name"]["title"][0]["plain_text"] == date_str:
                if page["properties"]["Explored"]["checkbox"]:
                    satisfied_with["Explored"] = 1
                else:
                    satisfied_with["Explored"] = 0
                if page["properties"]["Physical"]["checkbox"]:
                    satisfied_with["Physical"] = 1
                else:
                    satisfied_with["Physical"] = 0
                if page["properties"]["Sleep"]["checkbox"]:
                    satisfied_with["Sleep"] = 1
                else:
                    satisfied_with["Sleep"] = 0
                if page["properties"]["Tasks"]["checkbox"]:
                    satisfied_with["Tasks"] = 1
                else:
                    satisfied_with["Tasks"] = 0
                if page["properties"]["Sleep Hours"]["select"] is not None:
                    metrics["Sleep_Hours"] = int(
                        page["properties"]["Sleep Hours"]["select"]["name"]
                    )
                if page["properties"]["Stress Level"]["select"] is not None:
                    metrics["Stress_Level"] = int(
                        page["properties"]["Stress Level"]["select"]["name"]
                    )
                if page["properties"]["Satisfaction Level"]["select"] is not None:
                    metrics["Satisfaction_Level"] = int(
                        page["properties"]["Satisfaction Level"]["select"]["name"]
                    )
                if page["properties"]["Steps Count"]["number"]:
                    metrics["Steps_Count"] = int(
                        page["properties"]["Steps Count"]["number"]
                    )
        props["satisfied_with"] = satisfied_with
        props["metrics"] = metrics

        return props

    except Exception as e:
        print(f"Error occured while extracting page properties: {e}")


# main wrapper function, date format - YYYY/MM/DD
def get_journal_data(date: str = get_current_date()) -> dict:

    CURRENT_DATE = date
    # CURRENT_DATE = "2024-06-19"

    page_data = {}
    page_data["date"] = CURRENT_DATE

    journaldb = read_notion_db_optimally(JOURNAL_DB_ID, CURRENT_DATE)
    # pprint(journaldb)

    page_props = get_page_properties(journaldb, CURRENT_DATE)
    # pprint(page_props)
    page_data["properties"] = page_props

    today_page_id = get_pageid_from_journal_db(journaldb, CURRENT_DATE)
    all_blocks = read_block_children(today_page_id)
    # pprint(all_blocks)

    # miscellaneous_string = all_blocks["results"][-1]["paragraph"]["rich_text"][0]["plain_text"]
    # page_data["miscellaneous"] = miscellaneous_string

    tasks_block_id = all_blocks["results"][0]["id"]
    today_tasks_children = read_block_children(tasks_block_id)
    # pprint(today_tasks_children)

    tasks = []
    for entry in today_tasks_children["results"]:
        if entry["to_do"]["rich_text"]:
            task = {
                "text": entry["to_do"]["rich_text"][0]["plain_text"],
                "completed": entry["to_do"]["checked"],
            }
            tasks.append(task)

    # pprint(tasks)
    page_data["tasks"] = tasks

    explore_block_id = all_blocks["results"][1]["id"]
    explore_children = read_block_children(explore_block_id)
    # pprint(explore_children)

    explored = []
    for entry in explore_children["results"]:
        # check for no explore string
        if len(entry["heading_3"]["rich_text"]) > 0:
            explore = entry["heading_3"]["rich_text"][0]["plain_text"]
            explored.append(explore)

    # pprint(explored)
    page_data["explored_topics"] = explored

    finance_block_id = all_blocks["results"][2]["id"]
    finance_children = read_block_children(finance_block_id)
    finance_columns_parent_id = finance_children["results"][0]["id"]
    finance_columns_parent_block = read_block_children(finance_columns_parent_id)

    finance_columns_ids = (
        finance_columns_parent_block["results"][0]["id"],
        finance_columns_parent_block["results"][1]["id"],
    )
    debited_table_id = read_block_children(finance_columns_ids[0])["results"][1]["id"]
    credited_table_id = read_block_children(finance_columns_ids[1])["results"][1]["id"]

    debited_data = read_block_children(debited_table_id)

    debited = []
    for entry in debited_data["results"][1:]:
        if len(entry["table_row"]["cells"][0]) > 0:
            destination = entry["table_row"]["cells"][0][0]["plain_text"]
            amount = entry["table_row"]["cells"][1][0]["plain_text"]

            transaction = {"destination": destination, "amount": amount}
            debited.append(transaction)

    # pprint(debited)
    page_data["finances"] = {}
    page_data["finances"]["debited"] = debited

    credited_data = read_block_children(credited_table_id)

    credited = []
    for entry in credited_data["results"][1:]:
        if len(entry["table_row"]["cells"][0]) > 0:
            source = entry["table_row"]["cells"][0][0]["plain_text"]
            amount = entry["table_row"]["cells"][1][0]["plain_text"]

            transaction = {"source": source, "amount": amount}
            credited.append(transaction)

    # pprint(credited)
    page_data["finances"]["credited"] = credited

    return page_data


if __name__ == "__main__":
    pprint(get_journal_data())
