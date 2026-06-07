from pathlib import Path
import asyncio
import sys
# Ensure project root is in sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.utils import ensure_parent_directory, get_cwd, resolve_paths

# If you want to keep your config.setting functions, they should be implemented like this:
# def resolve_path(p: Path) -> Path:
#     return p.resolve()  # returns absolute path, resolves symlinks, cleans '..'

# def ensure_parent_directory(p: Path) -> None:
#     p.parent.mkdir(parents=True, exist_ok=True)

async def write_file(path: str, content: str):
    try:
    
        p = resolve_paths(get_cwd(),path)

        # 3. Check if file already exists (after resolving)
        is_new_file = not p.exists()

        # 4. Read old content only if file exists
        old_content = ""
        if not is_new_file:
            # If file exists, its parent directory must exist, so safe to read
            old_content = p.read_text(encoding="utf-8", errors="replace")

        # 5. Ensure parent directory exists (for write operation)
        # Standard way without custom function:
        ensure_parent_directory(p)
        # Or call your ensure_parent_directory(p)

        # 6. Write the file
        p.write_text(content, encoding="utf-8")

        return {
            "success": True,
            "message": f"File written: {p}",
            "is_new_file": is_new_file,
            "old_content": old_content,
            "new_content": content,
        }

    except Exception as e:
        return {"success": False,"error": str(e),}
    
# async def main():
#     result = await write_file(path=r"C:\Users\JarairAhmad\Desktop\AI coding agent\Names.txt",content="hi ")
#     print(result)

# if __name__ == "__main__":
#     asyncio.run(main())