import openai 
import os 
from dotenv import load_dotenv

from config.config import get_model
from tools.built_in.tool_schema import Tools

load_dotenv()


# testing wiether the llm send the usage or not (streaming response).

def run(text):
    client = openai.OpenAI(
        api_key=os.getenv("API_KEY"),
        base_url=os.getenv("BASE_URL")
    )
    
    response = client.chat.completions.create(
        model=get_model(),
        messages=[{"role": "user","content": text}],
        stream=True
    )
    for chunks in response:
        yield chunks


user = input("-> ")
res = run(text=user)

for char in res:
    print(char)
    print()