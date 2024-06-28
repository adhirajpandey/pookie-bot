from integrations.notion.journal import get_journal_data, get_current_date

SUMMARISATION_PROMPT = """Use following information to summarise the given journal entry for Adhiraj: 
1. Currency is Rs(INR). 
2. 0 Values means not upto satisfaction. 
3. -1 means values not entered in notion journal database
4. Metric scale is from 1-5

Add a seperate section for Tasks."""

DATE_EXTRACTION_PROMPT = f"""Current Date is {get_current_date()}. Extract the date from following message in YYYY-MM-DD format. 
Response format - date should be key and actual extracted date should be value"""

FILTER_SELECTION_PROMPT = """Choose the most suitable status string from following message. Only choose from exactly 'In progress' or 'Done' or 'Not started'.
Response format - status should be key and actual extracted status should be value"""
