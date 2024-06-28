from twilio.rest import Client
from flask import Flask, request
import os
import json
from dotenv import load_dotenv
from integrations.notion.journal import get_journal_data, get_current_date
from integrations.notion.tasks import get_filtered_task
from llms.gemini import gemini_call, gemini_call_json
from prompts import (
    SUMMARISATION_PROMPT,
    DATE_EXTRACTION_PROMPT,
    FILTER_SELECTION_PROMPT,
)

load_dotenv()


ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("FROM_NUMBER")
TO_NUMBER = os.getenv("TO_NUMBER")


def send_whatsapp_message(message):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
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

    whatsapp_data_dict = {
        "status": status,
        "tonum": tonum,
        "msgid": msgid,
        "message_text": Body,
    }

    print(whatsapp_data_dict)

    # todo - add another check if message is from allowed numbers
    if status == "received":
        gemini_date_resp = gemini_call_json(
            DATE_EXTRACTION_PROMPT.format(current_date=get_current_date())
            + whatsapp_data_dict["message_text"]
        )

        notion_data = get_journal_data(gemini_date_resp["date"])

        # todo - use another llm api call to check if it's required to fetch tasks
        if "tasks" in whatsapp_data_dict["message_text"]:
            gemini_status_resp = gemini_call_json(
                FILTER_SELECTION_PROMPT + whatsapp_data_dict["message_text"]
            )

            tasks = get_filtered_task(gemini_status_resp["status"])

            resp = gemini_call(SUMMARISATION_PROMPT + str(notion_data) + str(tasks))
            send_whatsapp_message(resp)

        else:
            resp = gemini_call(SUMMARISATION_PROMPT + str(notion_data))
            send_whatsapp_message(resp)

    return whatsapp_data_dict


if __name__ == "__main__":
    app.run()
