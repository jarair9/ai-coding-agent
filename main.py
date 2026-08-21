from client.llm_client import llmClient
from config.config import get_model,get_available_model
from client.llm_client import manager
from client.llm_client import handler
from tui.tui import TUI
from rich.text import Text  
import asyncio
import os

os.system('cls' if os.name == 'nt' else 'clear')

llm = llmClient()

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
         
        elif user.startswith("/") and user == "/messages":
            messages = manager.messages
            other_msgs = [m for m in messages if m.get("role") != "system"]
            
            print(other_msgs)
            continue
        elif user.startswith("/") and user == "/help":
            print("Feature comming soon.")
            continue
        elif user.startswith("/") and user == "/model":
            available_models = get_available_model()
            print(available_models)
            model = input("Select Model (model name only not provider): ")
            if model:
                for provider in available_models.items:
                    if model == provider.value():
                        print("ture")
            else:
                continue
        manager.add_user_message(user)
       
        
        async for chunk in llm.streaming_response():
           
           
            if chunk["type"] == "reasoning":
                tui.print_reasoning(chunk["content"])

            if chunk["type"] == "text":
                content = chunk["content"]
                
                tui.console.print(
                    Text(content, style="cyan"),
                    end=""
                )
            
            elif chunk["type"] == "tool_call":
                pending_tool_name = chunk["tool_call"]["tool_name"]
                pending_tool_args = chunk["tool_call"]["tool_args"]
              
                
            elif chunk["type"] == "tool_result":
               
                print()
                tool_result = chunk["tool_result"]

                if pending_tool_name == "read_file":
                    path = pending_tool_args["path"]
                    if isinstance(tool_result, list) and tool_result:
                        tool_result = tool_result[0]
                        
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
                    
                        
                    if not content or not path:
                        tui.error(tool_result.get("error", "Write failed"))
                    else:
                        tui.write_file(content=content,tool_name="write file",file_path=path)
                   
                elif pending_tool_name == "edit_file":
                    if pending_tool_args:
                        old_content = pending_tool_args.get("old_content","")
                        new_content = pending_tool_args.get("new_content","")
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
                            tui.list_files(output_data, title="list_dir")
                        else:
                            tui.error(tool_result.get("error", "List dir failed"))
                    else:
                        tui.list_files(str(tool_result), title="list_dir")
                
                elif pending_tool_name == "glob":
                    if isinstance(tool_result, dict):
                        if tool_result.get("success"):
                            
                            output = tool_result.get("output", "")
                            if not output:
                                output = "[No files matched]"
                            tui.list_files(output, title="glob")
                        else:
                            tui.error(tool_result.get("error", "Glob failed"))
                    else:
                        tui.list_files(str(tool_result), title="glob")

                elif pending_tool_name == "grep":
                    if isinstance(tool_result, dict):
                        if tool_result.get("success"):
                            output = tool_result.get("output", "")
                            if not output:
                                output = "[No matches found]"
                            tui.list_files(output, title="grep")
                        else:
                            tui.error(tool_result.get("error", "Grep failed"))
                    else:
                        tui.list_files(str(tool_result), title="grep") 
                  
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
            elif chunk["type"] == "complete":
                break        
            elif chunk["type"] == "status":
                tui.error(chunk["message"])
              
            elif chunk["type"] == "error":
                tui.error(chunk["error"])




        
        pending_tool_name = None
        pending_tool_args = None


if __name__ == "__main__":
    asyncio.run(main())