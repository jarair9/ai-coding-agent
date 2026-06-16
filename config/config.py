import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

_client = None  # cache client to reuse connection (was creating new one every call)

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
    return   "zai-glm-4.7"  # "gpt-oss-120b" 



