
from pathlib import Path
from rich.spinner import Spinner
from rich.panel import Panel
from rich.console import Console , Group
from rich.text import Text
from rich.live import Live  # FIX: removed `from rich import print` (shadowed builtin, unused)
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text

class TUI:
    def __init__(self):
        self.console = Console()
        self._reasoning_active = False

    def header(self, model):
    
        panel =Panel(f"Model : {model}\nCommands : /help , /model, /usage\nMode : Auto approve Actions",title="[purple]AI Agent[/purple]",title_align="left",highlight=True,style="cyan")
        self.console.print(panel)


    def error(self,error):
        panel = Panel(error,title_align="center",expand= True,style="bold red")
        self.console.print(panel)


    def read_file_ui(self, code, tool_name,file_path):
        lang = self.get_language(file_path=file_path)
       
        if code is None or code == "":
            fallback = "[yellow]No content to display (file may be empty or binary)[/yellow]"
            panel = Panel(fallback, title=f"{tool_name} : {file_path}", title_align="center", expand=True, style="dim")
            self.console.print(panel)
            return

      
        if not isinstance(code, str):
            code = str(code)

      
        syntax = Syntax(
            code,
            lang,   
            theme="monokai",
            
           
        )
        panel = Panel(syntax, title=tool_name, title_align="center", expand=True,highlight=True)
        self.console.print(panel)

    
        
        
    def get_language(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".html": "html",
            ".css": "css",
            ".json": "json",
            ".md": "markdown",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".sh": "bash",
            ".txt": "text",
        }
        return lang_map.get(ext, "text")
    
    
    
    def edit_file(self,old_content,new_content,file_path):
        lang = self.get_language(file_path=file_path)

        group = Group(
            Syntax(
                old_content,
                lang,
                theme="dracula",
                line_numbers=True
            ),
            Text(""),
            Text("─" * 40, style="bold green"),
            Syntax(
                new_content,
                lang,
                theme="monokai",
                line_numbers=True
            )
        )
                
        self.console.print(
            Panel(group, title=f"edit_file: {file_path}")
        )       
    
    def write_file(self,content,file_path,tool_name):
        lang = self.get_language(file_path=file_path)
        if content is None or content == "":
            fallback = "[yellow]No content to display (file may be empty or binary)[/yellow]"
            panel = Panel(fallback, title=f"{tool_name} : {file_path}", title_align="center", expand=True, style="dim")
            self.console.print(panel)
            return

        syntax = Syntax(
            content,
            lang,   
            theme="monokai",
            line_numbers=True
            
           
        )
        panel = Panel(syntax, title=tool_name, title_align="center", expand=True,highlight=True)
        self.console.print(panel)

            
    def white_panel(self, content, title):

        if content is None:
            content_str = "[No content]"
        elif isinstance(content, list):
            content_str = "\n".join(str(item) for item in content)
        elif isinstance(content, dict):
            content_str = "\n".join(f"{k}: {v}" for k, v in content.items())
        else:
            content_str = str(content)
        
     
        if not content_str.strip():
            content_str = "[Empty directory or no files]"
        
        panel = Panel(content_str, title=title, expand=True, highlight=True,style="green")
        self.console.print(panel)
        
    def shell_panel(self, content: str,colour : str ,title: str = "shell", ):
        if not content or content.strip() == "":
            content = "[No output]"
        panel = Panel(content, title=f"[{colour}]{title}[/{colour}]", border_style="red", expand=True)
        self.console.print(panel)   

    
    def _stop_live(self):
        if hasattr(self, "live") and self.live:
            self.live.stop()
            self.live = None

    def start_thinking(self):
        self._stop_live()
        self.live = Live(
            Spinner("dots", text="thinking...", style="cyan"),
            refresh_per_second=10,
            transient=True,
            console=self.console
        )
        self.live.start()

    def stop_thinking(self):
        self._stop_live()

    # def start_reasoning(self):
    #     self._reasoning_active = True

    # def print_reasoning(self, content):
    #     self.console.print(Text(content, style="#888888 italic"), end="")

    # def stop_reasoning(self):
    #     self._reasoning_active = False
    #     self.console.print()

    def start_tool_spinner(self, tool_name):
        self._stop_live()
        self.live = Live(
            Spinner("dots", text=tool_name, style="yellow"),
            refresh_per_second=10,
            transient=True,
            console=self.console
        )
        self.live.start()

    def stop_tool_spinner(self):
        self._stop_live()

