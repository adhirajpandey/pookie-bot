from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# todo - add model name from config file
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)


def gemini_call(query: str) -> str:
    response = model.invoke(query)
    return response.content


def gemini_call_json(query: str, pydantic_obj=None) -> dict:
    if pydantic_obj:
        parser = JsonOutputParser(pydantic_object=pydantic_obj)
    else:
        parser = JsonOutputParser()

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser

    response = chain.invoke({"query": query})
    return response
