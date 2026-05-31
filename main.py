from client.llm import llmClient
import asyncio
from config.setting import get_model
from context.memory import ContextManager
from tui.Tui import TUI
from colorama import Fore
import os
import sys
import atexit

# # Clear screen
os.system('cls' if os.name == 'nt' else 'clear')

# # Hide cursor
sys.stdout.write('\033[?25l')
sys.stdout.flush()
atexit.register(lambda: sys.stdout.write('\033[?25h'))  # restore on exit

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
            usage = manager.usage_stats()
            print(usage)
            continue

        manager.add_user_message(user)
        async for chunk in tui.status_indicator(llm.streaming_response(), status="Thinking"):
            # if isinstance(chunk, dict) or "type" not in chunk:
            #     continue
            if chunk["type"] == "text":
                content = chunk["content"]
                print(f"{Fore.GREEN}{content}{Fore.RESET}", end="", flush=True)

            elif chunk["type"] == "tool_call":
                pending_tool_name = chunk["tool_call"]["tool_name"]
                pending_tool_args = chunk["tool_call"]["tool_args"]

            elif chunk["type"] == "tool_result":
                # Add newline to separate from streaming text
                print()
                tool_result = chunk["tool_result"]

                
                if pending_tool_name == "read_file":
                    # If tool_result is a list, take the first element (assuming single result)
                    if isinstance(tool_result, list) and tool_result:
                        tool_result = tool_result[0]

                    if isinstance(tool_result, dict) and tool_result.get("success"):
                        # Try to extract content – it could be at 'content', 'result', or nested
                        content = tool_result.get("content") or tool_result.get("result")
                        if isinstance(content, dict):
                            content = content.get("content") or content.get("result") or ""
                        if not content:
                            content = tool_result.get("output", "")
                        if content:
                            tui.code_ui(content, tool_name="read_file")
                        else:
                            tui.error("Read file returned empty content")
                    else:
                        tui.error(tool_result.get("error", "Read failed") if isinstance(tool_result, dict) else "Invalid tool result")



                elif pending_tool_name == "write_file":
                    path = pending_tool_args.get("path", "unknown")
                    content = pending_tool_args.get("content" , "Empty")
                    
                    tui.write_code_ui(content=content,tool_name=f"write file : {path}")
                    
                    if not content or not path:
                        tui.error(tool_result.get("error", "Write failed"))
                   



                elif pending_tool_name == "edit_file":
                    if isinstance(tool_result, dict) and tool_result.get("success"):
                        old = tool_result.get("old_content", "")
                        new = tool_result.get("new_content", "")
                        path = tool_result.get("path", "unknown")
                        tui.diff_panels(old, new, path)
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
                        # Try top‑level first, then inside "result"
                        output = tool_result.get("output")
                        if output is None:
                            inner = tool_result.get("result", {})
                            if isinstance(inner, dict):
                                output = inner.get("output")
                        if not output and tool_result.get("success"):
                            # Fallback: maybe the result is a plain string
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

            
            # elif chunk["type"] == "complete":
            #     print("\n[Response complete]\n")

if __name__ == "__main__":
    asyncio.run(main())