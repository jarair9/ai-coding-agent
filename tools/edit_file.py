from pathlib import Path
import asyncio
import sys
from config.utils import get_cwd, resolve_paths



async def edit_file(path: str, old_content: str, new_content: str, replace_all: bool = False):
    
    
    file_path = resolve_paths(get_cwd(), path)

    if file_path.is_dir():
        return {"success": False, "error": "Path is a directory, not a file"}
    
    if not file_path.exists():
        return {"success": False, "error": "File does not exist"}

    try:
        original = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        original = file_path.read_text(encoding="latin-1")

    if not original:
        return {"success": False, "error": "File is empty, cannot replace content"}


    if old_content not in original:
        return {"success": False, "error": "Old content not found in file"}

   
    if replace_all:
        updated = original.replace(old_content, new_content)
        replacements = original.count(old_content)
    else:
        updated = original.replace(old_content, new_content, 1)
        replacements = 1

   
    file_path.write_text(updated, encoding="utf-8")

    
    return {
        "success": True,
        "path": str(path),
        "old_content": original,     
        "new_content": updated,       
        "replacements": replacements
    }