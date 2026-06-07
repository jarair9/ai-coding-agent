from client.llm import llmClient
import asyncio
from config.config import get_model
from context.context_manager import ContextManager
from client.llm import handler
from tui.Tui import TUI
from colorama import Fore
from rich.text import Text
import os

os.system('cls' if os.name == 'nt' else 'clear')


llm = llmClient()
manager = ContextManager()

tui = TUI()

async def main():
    tui.header(get_model())
    pending_tool_name = None
    pending_tool_args = None

    while True:
        user = tui.console.input("\n[purple]>[/purple] ").strip()
        if user.lower() == "exit":
            break
        elif user.startswith("/") and user == "/usage":
           usage = handler.return_usage()
           print(usage)
           continue

        manager.add_user_message(user)
        async for chunk in llm.streaming_response():
           
            if chunk["type"] == "text":
                content = chunk["content"]
                tui.console.print(
                    Text(content, style="green"),
                    end=""
                )

            elif chunk["type"] == "tool_call":
                pending_tool_name = chunk["tool_call"]["tool_name"]
                pending_tool_args = chunk["tool_call"]["tool_args"]
                tui.start_tool_spinner(pending_tool_name)
                
                
            elif chunk["type"] == "tool_result":
                tui.stop_tool_spinner()
                print()
                tool_result = chunk["tool_result"]

                
                if pending_tool_name == "read_file":
                    if isinstance(tool_result, list) and tool_result:
                        tool_result = tool_result[0]
                        
                    if pending_tool_args.get("path",""):
                        path = pending_tool_args.get("path","")
                    if isinstance(tool_result, dict) and tool_result.get("success"):
                        
                        content = tool_result.get("content") or tool_result.get("result")
                        if isinstance(content, dict):
                            content = content.get("content") or content.get("result") or ""
                            
                        if not content:
                            content = tool_result.get("output", "")
                        if content:
                            tui.read_file_ui(content, tool_name="read_file",file_path=path)
                        else:
                            tui.error("Read file returned empty content")
                    else:
                        tui.error(tool_result.get("error", "Read failed") if isinstance(tool_result, dict) else "Invalid tool result")



                elif pending_tool_name == "write_file":
                    path = pending_tool_args.get("path", "unknown")
                    content = pending_tool_args.get("content" , "Empty")
                    
                    tui.write_file(content=content,tool_name=f"write file",file_path=path)
                    
                    if not content or not path:
                        tui.error(tool_result.get("error", "Write failed"))
                   


                # the edit ui should be like old text in red colour and new in green
                
                elif pending_tool_name == "edit_file":
                    if pending_tool_args:
                        old_content = pending_tool_args.get("new_content","")
                        new_content = pending_tool_args.get("old_content","")
                        file_path = pending_tool_args.get("path","")
                        tui.edit_file(old_content=old_content,new_content=new_content,file_path=file_path)
                    else:
                        tui.error(tool_result.get("error", "Edit failed"))



                elif pending_tool_name == "list_dir":
                    if isinstance(tool_result, dict):
                       
                        if tool_result.get("success"):
                            output_data = tool_result.get("output")   
                            if output_data is None:
                                
                                inner = tool_result.get("result", {})
                                if isinstance(inner, dict):
                                    output_data = inner.get("output")
                            if output_data is None:
                                output_data = []   
                            tui.white_panel(output_data, title="list_dir")
                        else:
                            tui.error(tool_result.get("error", "List dir failed"))
                    else:
                        tui.white_panel(str(tool_result), title="list_dir")
                
                
                
                
                elif pending_tool_name == "glob":
                    if isinstance(tool_result, dict):
                        if tool_result.get("success"):
                            
                            output = tool_result.get("output", "")
                            if not output:
                                output = "[No files matched]"
                            tui.white_panel(output, title="glob")
                        else:
                            tui.error(tool_result.get("error", "Glob failed"))
                    else:
                        tui.white_panel(str(tool_result), title="glob")



                elif pending_tool_name == "grep":
                    if isinstance(tool_result, dict):
                        if tool_result.get("success"):
                            output = tool_result.get("output", "")
                            if not output:
                                output = "[No matches found]"
                            tui.white_panel(output, title="grep")
                        else:
                            tui.error(tool_result.get("error", "Grep failed"))
                    else:
                        tui.white_panel(str(tool_result), title="grep") 
                        
                        
                elif pending_tool_name == "shell":
                    command = pending_tool_args.get("command","unknown")
                    tui.shell_panel(content=command,colour="cyan")
                    if isinstance(tool_result, dict):
                        
                        output = tool_result.get("output")
                        if output is None:
                            inner = tool_result.get("result", {})
                            if isinstance(inner, dict):
                                output = inner.get("output")
                        if not output and tool_result.get("success"):
                            
                            output = tool_result.get("result") if isinstance(tool_result.get("result"), str) else ""
                            
                        if not output:
                            output = "[No output]"
                        tui.shell_panel(output, title="shell",colour="green")
                    else:
                        tui.shell_panel(str(tool_result), title="shell",colour="green")
                        
            elif chunk["type"] == "status":
                tui.error(chunk["message"])
                
                
            elif chunk["type"] == "error":
                tui.error(chunk["error"])

        pending_tool_name = None
        pending_tool_args = None

            
          

if __name__ == "__main__":
    asyncio.run(main())