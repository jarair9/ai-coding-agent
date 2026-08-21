from tools.write_file import write_file
from tools.edit_file import edit_file
from tools.list_dir import list_dir
from tools.grep import grep
from tools.glob_tool import glob_tool
from tools.read_file import read_file
from tools.shell import shell
from tools.webfetch import webfetch
from tools.websearch import websearch

tool_registry = {
    "read_file": read_file,
    "write_file": write_file,
    "shell": shell,
    "list_dir": list_dir,
    "grep": grep,
    "glob": glob_tool,
    "edit_file": edit_file,
    "webfetch": webfetch,
    "websearch": websearch
}


async def execute_tool(name : str , **kwargs):
    tool = tool_registry.get(name)

    if not tool:
        return {
            "error" : f"Invalid tool name : {name}"
        }
    try: 
        return await tool(**kwargs)
    
    
    except Exception as e:
        return {
            "success": False,
            "tool": name,
            "error": str(e),
        }



