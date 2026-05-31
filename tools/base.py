from tools.write_file import write_file
from tools.edit_file import edit_file
from tools.list_dir import list_dir
from tools.grep import grep
from tools.glob import Glob
from tools.read_file import Readfile
from tools.shell import shell


tool_registry = {
    "read_file": Readfile,
    "write_file": write_file,
    "shell": shell,
    "list_dir": list_dir,
    "grep": grep,
    "glob": Glob,
    "edit_file": edit_file
}


async def execute_tool(name : str , **kwargs):
    tool = tool_registry.get(name)

    if not tool:
        return {
            "error" : f"Invalid tool name : {tool}"
        }
    try: 
        result = await tool(**kwargs)

        return {
            "success": True,
            "result" : result
        }
    except Exception as e:
        return {
            "success": False,
            "tool": name,
            "error": str(e),
        }



