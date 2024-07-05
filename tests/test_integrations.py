import pytest
from integrations.notion.journal import get_journal_data
from integrations.notion.tasks import get_filtered_task
from tests.sample_data import SAMPLE_DATE, JOURNAL_DATA_FOR_SAMPLE_DATE, SAMPLE_FILTER_STRING, EXISTING_TASK_FOR_SAMPLE_FILTER


def test_notion_journal_for_sample_date():
    fetched_journal_data_for_sample_date = get_journal_data(SAMPLE_DATE)
    assert fetched_journal_data_for_sample_date == dict(JOURNAL_DATA_FOR_SAMPLE_DATE)

def test_notion_tasks_for_sample_filter_string():
    fetched_filter_tasks_for_sample_filter_string = get_filtered_task(SAMPLE_FILTER_STRING)
    assert any(EXISTING_TASK_FOR_SAMPLE_FILTER in task['Name'] for task in fetched_filter_tasks_for_sample_filter_string)
