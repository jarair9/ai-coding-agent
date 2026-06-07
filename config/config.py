import tiktoken
import os
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv



    
def get_client() -> AsyncOpenAI :
    load_dotenv()
    return AsyncOpenAI(
        api_key=os.getenv("API_KEY"),
        base_url=os.getenv("BASE_URL")
    )


def get_model() -> str:
    return   "zai-glm-4.7"  # "gpt-oss-120b" 



