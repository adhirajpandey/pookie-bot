import pytest
from llms.gemini import gemini_call, gemini_call_json
from llms.grok import grok_llama3_call, grok_llama3_call_json

def test_gemini_call():
    sample_query = "Who are you? Respond in less than 10 words"
    gemini_response = gemini_call(sample_query)
    assert isinstance(gemini_response, str)

def test_gemini_call_json():
    sample_query = "Who are you? Respond in less than 10 words in question:answer json format."
    gemini_response = gemini_call_json(sample_query)
    assert isinstance(gemini_response, dict)

def test_grok_call():
    sample_query = "Who are you? Respond in less than 10 words"
    grok_response = grok_llama3_call(sample_query)
    assert isinstance(grok_response, str)

def test_grok_call_json():
    sample_query = "Who are you? Respond in less than 10 words in question:answer json format."
    grok_response = grok_llama3_call_json(sample_query)
    assert isinstance(grok_response, dict)
