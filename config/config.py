import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

_client = None  # cache client to reuse connection 

def get_client() -> AsyncOpenAI :
    global _client
    if _client is None:  # only create once, reuse on subsequent calls
        load_dotenv()
        _client = AsyncOpenAI(
            api_key=os.getenv("API_KEY"),
            base_url=os.getenv("BASE_URL")
        )
    return _client


def get_model() -> str:
    return   "openai/gpt-oss-120b"  # "gpt-oss-120b" 


def get_available_model():
    return {
        "Google model":"gemma-4-31b",
        "OpenAI Model": "gpt-oss-120b",
        "Z.AI Model": "z.ai-glm-4.7"
    }
