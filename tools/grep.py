import asyncio
import os
from pathlib import Path
import re
import sys


# sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import the functions correctly
from config.utils import is_binary_file, resolve_paths, get_cwd

def _find_files(search_files):
    files = []
    for root, dirs, filenames in os.walk(search_files):
        dirs[:] = [d for d in dirs if d not in {"node_modules", "__pycache__", ".git", ".venv", "venv"}]
        for filename in filenames:
            if filename.startswith("."): 
                continue 
            file_path = Path(root) / filename
            if not is_binary_file(file_path):
                files.append(file_path)
                if len(files) >= 500:
                    break
    return files

async def grep(regex, case_insensitive: bool, path: str):
    # CORRECTED: Call the function, don't use 'path.' prefix
    search_path = resolve_paths(get_cwd(), path)

    if not search_path.exists():
        return{ "success": False,"error":"The Path does not exist"}

    try: 
        flag = re.IGNORECASE if case_insensitive else 0
        pattern = re.compile(regex, flag)
    except re.error as e:
        return {"success": False,"error": f'The pattern is invalid: {e}'}
    
    files = _find_files(search_path) if search_path.is_dir() else [search_path]
    
    output_lines = []
    matches = 0

    for filepath in files:
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception:
            continue

        lines = content.splitlines()
        file_matches = False

        for i, line in enumerate(lines, start=1):
            # CORRECTED: Search 'line', not the pattern object
            if pattern.search(line): 
                matches += 1
                if not file_matches:
                    # Added try-except for relative path in case files are outside cwd
                    try:
                        rel_path = filepath.relative_to(get_cwd())
                    except ValueError:
                        rel_path = filepath
                    output_lines.append(f"=== {rel_path} ===")
                    file_matches = True
                output_lines.append(f"{i}: {line}")

        if file_matches:
            output_lines.append("")

    if not output_lines:
        return {"error": f"No matches found for pattern '{regex}'"}

    return {
        "success": True,
        "matches": matches,
        "output": "\n".join(output_lines)
    }

# async def main():
#     result = await grep(regex="import os", case_insensitive=False, path=r"C:\Users\JarairAhmad\Desktop\AI coding agent")
#     print(result)

# if __name__ == "__main__":
#     asyncio.run(main())