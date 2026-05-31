
import sys
from pathlib import Path
import asyncio
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.setting import get_cwd, resolve_paths



async def list_dir(path, hidden_file : bool = False):
    path = resolve_paths(get_cwd(),path)

    if not path.exists() or not path.is_dir():
        return {"success": False,
            "error" : "The path doesnot exists"
        }
    if path.is_file():
        return {"success": False,
            "error": "The path is invalid. the path given is file path."
        }
    output = []
    items = path.iterdir()

    for item in items :
        if item.is_dir():
            output.append(f"{item}/")
        else:
            output.append(item)

    return {
        "success": True,
        "output": output
    }

# async def main():
#     result = await List_dir(path=r"C:\Users\JarairAhmad\Desktop\AI coding agent")
#     print(result)

# if __name__ == "__main__":
#     asyncio.run(main())