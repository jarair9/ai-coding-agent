from pathlib import Path
from config.setting import get_cwd, resolve_paths

# Directories to completely ignore (never traverse into)
EXCLUDED_DIRS = {
    ".venv", "venv", "env", "virtualenv",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".git", ".svn", ".hg",
    "node_modules", "bower_components",
    ".idea", ".vscode", ".vs",
    "dist", "build", "target", "out",
    ".next", ".nuxt",
    "site-packages", "pip-wheel-metadata",
    "logs", "tmp", "temp",
}

# File extensions to ignore (optional, e.g., binary files, logs)
EXCLUDED_EXTENSIONS = {
    ".pyc", ".pyo", ".pyd",
    ".so", ".dll", ".dylib",
    ".exe", ".msi", ".bin",
    ".log", ".lock",
    ".db", ".sqlite",
    ".class", ".jar",
}

def is_excluded(path: Path) -> bool:
    """Check if a path or any of its parents is in the excluded list."""
    # Check directory names (excluding root)
    for part in path.parents:
        if part.name in EXCLUDED_DIRS:
            return True
    # Check the file/directory itself
    if path.name in EXCLUDED_DIRS:
        return True
    # Check extension for files
    if path.is_file() and path.suffix in EXCLUDED_EXTENSIONS:
        return True
    return False

async def Glob(pattern: str, path: str):
    search_path = resolve_paths(get_cwd(), path)
    if not search_path.is_dir():
        return {"success": False, "error": "Invalid directory"}

    # Helper to filter matches and avoid walking into excluded dirs
    def collect_matches(start_path: Path, glob_pattern: str):
        """Recursively collect files matching glob_pattern, skipping excluded directories."""
        # Using pathlib's glob does not automatically skip subdirectories – we need to filter.
        # We'll use rglob but filter out excluded subdirs manually.
        matches = []
        for p in start_path.rglob(glob_pattern):
            # Check if any parent directory is excluded
            if is_excluded(p):
                continue
            if p.is_file():
                matches.append(p)
        return matches

    # Handle brace expansion (as before)
    if '{' in pattern and '}' in pattern:
        start = pattern.find('{')
        end = pattern.find('}')
        extensions = pattern[start+1:end].split(',')
        base = pattern[:start] + '{}' + pattern[end+1:]
        all_files = []
        for ext in extensions:
            full = base.format(ext)
            if '**' not in full:
                full = f'**/{full}'
            # Use the recursive collector that skips excluded dirs
            # We'll convert glob pattern to the file part (e.g., '**/*.py')
            # For simplicity, extract the file pattern part after the last '/'
            # A more robust method: use Path.rglob with the filename pattern
            # Here we assume the pattern ends with filename like '**/*.html'
            # So we take the last component as file pattern
            file_pattern = full.split('/')[-1]  # e.g., '*.html'
            # But we need to traverse from search_path and skip excluded dirs
            for p in search_path.rglob(file_pattern):
                if is_excluded(p):
                    continue
                if p.is_file():
                    all_files.append(p)
        matches = list(set(all_files))
    else:
        # Simple pattern – make recursive if needed
        if '**' not in pattern and pattern != '*':
            pattern = f'**/{pattern}'
        # Extract file pattern from the last part
        file_pattern = pattern.split('/')[-1]
        matches = []
        for p in search_path.rglob(file_pattern):
            if is_excluded(p):
                continue
            if p.is_file():
                matches.append(p)

    truncated = len(matches) > 1000
    output_lines = []
    for p in matches[:1000]:
        try:
            rel = p.relative_to(get_cwd())
        except ValueError:
            rel = p
        output_lines.append(str(rel))

    return {"success": True, "truncated": truncated, "output": "\n".join(output_lines)}