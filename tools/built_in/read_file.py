from config.utils import get_cwd, is_binary_file, resolve_paths


async def read_file(path, offset=None, limit=None):
    MAX_FILE_SIZE = 1024 * 1024 * 10
    path = resolve_paths(get_cwd(), path)

    if not path.exists():
        return {"success": False, "error": "File not found"}
    if not path.is_file():
        return {"success": False, "error": "Path is not a file"}

    file_size = path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        return {"success": False, "error": f"File too large ({file_size / (1024*1024):.1f}MB). Maximum {MAX_FILE_SIZE/(1024*1024):.1f}MB"}

    if is_binary_file(path):
        size_str = f"{file_size/(1024*1024):.2f}MB" if file_size >= 1024*1024 else f"{file_size} bytes"
        return {"success": True, "error": f"Cannot read binary file: {path.name} ({size_str}). Only text files."}

    try:
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="latin-1")

        lines = content.splitlines()
        total_lines = len(lines)
        if total_lines == 0:
            return {"success": False, "error": "The file is empty"}

        if offset is not None:
            start_idx = max(0, offset - 1)
        else:
            start_idx = 0

        if limit is not None:
            end_idx = min(start_idx + limit, total_lines)
        else:
            end_idx = total_lines

        selected_lines = lines[start_idx:end_idx]
        formatted_lines = []
        for i, line in enumerate(selected_lines, start=start_idx + 1):
            formatted_lines.append(f"{i:6} | {line}")

        return {"success": True, "content": "\n".join(formatted_lines)}

    except Exception as e:
        return {"success": False, "error": f"Error: {e}"}