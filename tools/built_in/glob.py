from pathlib import Path
from config.utils import get_cwd, resolve_paths

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

EXCLUDED_EXTENSIONS = {
    ".pyc", ".pyo", ".pyd",
    ".so", ".dll", ".dylib",
    ".exe", ".msi", ".bin",
    ".log", ".lock",
    ".db", ".sqlite",
    ".class", ".jar",
}

MAX_RESULTS = 1000


def _is_excluded(path: Path) -> bool:
    if path.suffix in EXCLUDED_EXTENSIONS:
        return True
    for parent in path.parents:
        if parent.name in EXCLUDED_DIRS:
            return True
    if path.name in EXCLUDED_DIRS:
        return True
    return False


def _expand_braces(pattern: str) -> list[str]:
    patterns = [pattern]
    while True:
        next_round = []
        found = False
        for p in patterns:
            start = p.find("{")
            if start == -1:
                next_round.append(p)
                continue
            end = p.find("}", start)
            if end == -1 or end == start + 1:
                next_round.append(p)
                continue
            found = True
            before = p[:start]
            after = p[end + 1 :]
            for variant in p[start + 1 : end].split(","):
                next_round.append(before + variant + after)
        patterns = next_round
        if not found:
            break
    return patterns


async def glob(pattern: str, path: str) -> dict:
    search_path = resolve_paths(get_cwd(), path)
    if not search_path.is_dir():
        return {"success": False, "error": "Invalid directory"}

    sub_patterns = _expand_braces(pattern)
    all_matches: list[Path] = []
    seen: set[Path] = set()
    root = get_cwd()

    for sub in sub_patterns:
        if not sub:
            continue

        if "/" in sub or "**" in sub:
            matches = search_path.glob(sub)
        else:
            matches = search_path.rglob(sub)

        for m in matches:
            if m.is_file() and m not in seen and not _is_excluded(m):
                seen.add(m)
                all_matches.append(m)

    truncated = len(all_matches) > MAX_RESULTS
    lines = []
    for m in all_matches[:MAX_RESULTS]:
        try:
            lines.append(str(m.relative_to(root)))
        except ValueError:
            lines.append(str(m))

    return {"success": True, "truncated": truncated, "output": "\n".join(lines)}