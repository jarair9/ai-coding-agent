from pathlib import Path
import asyncio
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config.setting import get_cwd, resolve_paths

async def edit_file(path: str, old_content: str, new_content: str, replace_all: bool = False):
    file_path = resolve_paths(get_cwd(), path)

    if file_path.is_dir():
        return {"success": False, "error": "Path is a directory, not a file"}
    if not file_path.exists():
        return {"success": False, "error": "File does not exist"}
# 923710919163
    # Read the file with fallback encoding
    try:
        original = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        original = file_path.read_text(encoding="latin-1")

    if not original:
        return {"success": False, "error": "File is empty, cannot replace content"}

    # Check if old_content exists
    if old_content not in original:
        return {"success": False, "error": "Old content not found in file"}

    # Perform replacement
    if replace_all:
        updated = original.replace(old_content, new_content)
        replacements = original.count(old_content)
    else:
        updated = original.replace(old_content, new_content, 1)
        replacements = 1

    # Write the updated content back
    file_path.write_text(updated, encoding="utf-8")

    # Return enough information for diff display
    return {
        "success": True,
        "path": str(path),
        "old_content": original,      # whole original content (or just the changed portion)
        "new_content": updated,       # whole new content
        "replacements": replacements
    }