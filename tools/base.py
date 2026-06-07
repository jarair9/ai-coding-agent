from tools.built_in.write_file import write_file
from tools.built_in.edit_file import edit_file
from tools.built_in.list_dir import list_dir
from tools.built_in.grep import grep
from tools.built_in.glob import glob
from tools.built_in.read_file import read_file
from tools.built_in.shell import shell

tool_registry = {
    "read_file": read_file,
    "write_file": write_file,
    "shell": shell,
    "list_dir": list_dir,
    "grep": grep,
    "glob": glob,
    "edit_file": edit_file
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



