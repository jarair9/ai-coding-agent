import openai 
import os 
from dotenv import load_dotenv

from config.setting import get_model

load_dotenv()


# testing wiether the llm send the usage or not at the  of response (streaming response).

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
        
res = run(text="hi how are you what can you do")

for char in res:
    print(char)
    print()