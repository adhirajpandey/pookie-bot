from twilio.rest import Client
from flask import Flask, request
import os
import json
from dotenv import load_dotenv
from integrations.notion.journal import get_journal_data, get_current_date
from integrations.notion.tasks import get_filtered_task
from llms.gemini import gemini_call, gemini_call_json

load_dotenv()


QUERY1 = "Use following information to summarise the given journal entry for Adhiraj: 1. Currency is Rs. 2. 0 Values means not upto satisfaction. Add a seperate section for Tasks"
QUERY2 = f"Current Date is {get_current_date()}. Extract the date from following message in YYYY-MM-DD format. Response format - date should be key and actual extracted date should be value"
QUERY3 = "Choose the most suitable status string from following message. Only choose from exactly 'In progress' or 'Done' or 'Not started'. Response format - status should be key and actual extracted status should be value"

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("FROM_NUMBER")
fTO_NUMBER = os.getenv("TO_NUMBER")


# replace to and from numbers as per requirement
FROM_NUMBER = "whatsapp:+14155238886"
TO_NUMBER = "whatsapp:+918791335061"


def send_whatsapp_message(message):
    client = Client(account_sid, auth_token)
    message = client.messages.create(from_=FROM_NUMBER, body=message, to=TO_NUMBER)
    return message.sid


send_whatsapp_message("Pookie Bot")


# flask server to receive webhook from twilio
app = Flask(__name__)


@app.route("/twilio", methods=["POST"])
def twilio():
    status = request.values.get("SmsStatus")
    tonum = request.values.get("To")
    msgid = request.values.get("MessageSid")
    Body = request.form.get("Body")

    datadict = {"status": status, "tonum": tonum, "msgid": msgid, "message_text": Body}

    print(datadict)

    if status == "received":
        gemini_date_resp = json.loads(
            gemini_call_json(QUERY2 + datadict["message_text"])
        )
        notion_data = get_journal_data(gemini_date_resp["date"])

        if "tasks" in datadict["message_text"]:
            gemini_status_resp = json.loads(
                gemini_call_json(QUERY3 + datadict["message_text"])
            )
            tasks = notion_tasks.get_filtered_task(gemini_status_resp["status"])

            resp = gemini_call(QUERY1 + str(notion_data) + str(tasks))
            send_whatsapp_message(resp)

        else:
            resp = gemini_call(QUERY1 + str(notion_data))
            send_whatsapp_message(resp)

    return datadict


if __name__ == "__main__":
    app.run()
