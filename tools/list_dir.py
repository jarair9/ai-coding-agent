
import sys
from pathlib import Path
import asyncio
# sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.utils import get_cwd, resolve_paths


async def list_dir(path, hidden_file: bool = False):
    path = resolve_paths(get_cwd(), path)

    if not path.exists() or not path.is_dir():
        return {"success": False, "error": "Directory does not exist"}
    if path.is_file():
        return {"success": False, "error": "Path is a file, not a directory"}

    output_lines = []
    items = path.iterdir()

    for item in items:
        # Skip hidden files/directories if not requested
        if not hidden_file and item.name.startswith('.'):
            continue
        if item.is_dir():
            output_lines.append(f"{item.name}/")
        else:
            output_lines.append(item.name)

    return {
        "success": True,
        "output": "\n".join(output_lines)   
    }

