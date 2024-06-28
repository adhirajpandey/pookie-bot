from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

llama3_8b = "llama3-8b-8192"
llama3_70b = "llama3-70b-8192"


def groq_llama3_call(query, model=llama3_8b):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": query,
            }
        ],
        model=llama3_8b,
    )

    return chat_completion.choices[0].message.content


def groq_llama3_call_json(query, model=llama3_8b):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": query,
            }
        ],
        model=llama3_8b,
        response_format={"type": "json_object"},
    )

    return chat_completion.choices[0].message.content
