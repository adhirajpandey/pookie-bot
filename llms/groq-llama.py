from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.environ.get("GROQ_API_KEY")

# todo - add model name from config file
llama3_8b = "llama3-8b-8192"
llama3_70b = "llama3-70b-8192"

model = ChatGroq(model=llama3_8b, api_key=GROK_API_KEY)


def grok_llama3_call(query: str) -> str:
    response = model.invoke(query)
    return response.content


def grok_llama3_call_json(query: str, pydantic_obj=None) -> dict:
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
