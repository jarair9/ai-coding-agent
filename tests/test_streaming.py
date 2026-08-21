import openai 
import os 
from dotenv import load_dotenv

from config.config import get_model
from tools.tool_schema import Tools

load_dotenv()


# testing wiether the llm send the usage or not (streaming response).

def run(text):
    client = openai.OpenAI(
        api_key="sk-JDIxIeYQc6BqCbkzr7fdbmvroggdbTjMrCuRn26FCKOdpiPN",
        base_url="https://agentrouter.org/v1"
    )
    
    response = client.chat.completions.create(
        model="gpt-5.5",
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