import tiktoken
import os
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv


model_context_window =  124000 # The context window of the model

def get_client() -> AsyncOpenAI :
    load_dotenv()
    return AsyncOpenAI(
        api_key=os.getenv("API_KEY"),
        base_url=os.getenv("BASE_URL")
    )


def get_model() -> str:

    return   "zai-glm-4.7"#"gpt-oss-120b" 



def resolve_paths(base: str | Path, path: str | Path):

    path = Path(path)
    
    
    if path.is_absolute():
        return path.resolve()
    
    
    return Path(base).resolve() / path



def get_cwd():
    cwd = os.getcwd()
    return cwd
    

def is_binary_file(path: str | Path) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
            return b"\x00" in chunk
    except (OSError, IOError):
        return False
    


def get_tokenizer(model: str):
    try:
        encoding = tiktoken.encoding_for_model(model)
        return encoding.encode
    except Exception:
        encoding = tiktoken.get_encoding("cl100k_base")
        return encoding.encode
    
def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)

def count_token(text):
    tokenizer = get_tokenizer(text)

    if tokenizer:
        return len(tokenizer(text))

    return estimate_tokens(text)


def get_context_window():
    if model_context_window:

        return model_context_window
    else:
        return 100000 # context window
    


def ensure_parent_directory(path: str | Path) -> Path:
    path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)
    return path