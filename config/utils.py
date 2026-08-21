import os
from pathlib import Path

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


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
    """Returns None - using simple estimation instead of tiktoken"""
    if not TIKTOKEN_AVAILABLE:
        return None
    
    try:
        encoding = tiktoken.encoding_for_model(model)
        return encoding.encode
    except KeyError:
        # Model not recognized, try default
        pass
    except Exception:
        # Network/download error
        pass
    
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return encoding.encode
    except Exception:
        # Still failing (network issue)
        return None


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def count_token(text: str, model: str = None) -> int:
    """Count tokens using simple estimation"""
    return estimate_tokens(text)


def get_context_window():
    return 8192


def ensure_parent_directory(path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path