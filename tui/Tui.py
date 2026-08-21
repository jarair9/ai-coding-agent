import time
from pathlib import Path
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.syntax import Syntax
from rich.text import Text
from rich.markdown import Markdown

class TUI:

    def __init__(self):
        self.console = Console()
        self._reasoning_active = False
from pathlib import Path
from rich.spinner import Spinner
from rich.panel import Panel
from rich.console import Console , Group
from rich.text import Text
from rich.live import Live  
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import Collapsible, Label


class TUI:
    def __init__(self):
        self.console = Console()
        self._reasoning_active = False

    def header(self, model):
        panel = Panel(
            f"Model : {model}\nCommands : /help , /model, /usage\nMode : Auto approve Actions",
            title="[purple]AI Agent[/purple]",
            title_align="left",
            highlight=True,
            style="cyan",
        )
        self.console.print(panel)

    def printmd(self, text):
        md = Markdown(text)
        # Apply the style directly to the Markdown object or the console print
        self.console.print(md, style="cyan", end="")
        
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
    
    def error(self, error):
        panel = Panel(
            error, title_align="center", expand=True, style="bold red"
        )
        self.console.print(panel)
    

    def read_file_ui(self, code, tool_name,file_path):
        lang = self.get_language(file_path=file_path)
       
        if code is None or code == "":
            fallback = "[yellow]No content to display (file may be empty or binary)[/yellow]"
            panel = Panel(fallback, title=f"{tool_name} : {file_path}", title_align="center", expand=True, style="dim")
            self.console.print(panel)
            return
        if not isinstance(code, str):
            code = str(code[:1000])
        
        syntax = Syntax(
            code[:1000],
            lang,   
            theme="monokai",
        
           
        )
        panel = Panel(syntax, title=tool_name, title_align="center", expand=True,highlight=True)
        self.console.print(panel)

    
    def edit_file(self,old_content,new_content,file_path):
        lang = self.get_language(file_path=file_path)

        group = Group(
            Syntax(
                old_content,
                lang,
                theme="dracula",
                line_numbers=True
            ),
            # Text(""),
            Text("─" * 1000, style="bold green"),
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
            content[:1000],
            lang,   
            theme="monokai",
            line_numbers=True
            
           
        )
        # panel = Panel(syntax, title=tool_name, title_align="center", expand=True,highlight=True)
        self.console.print(syntax)

            
    def list_files(self, content, title):

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
        
        panel = Panel(content_str, title=title, expand=True, highlight=True)
        self.console.print(panel)
        
    def shell_panel(self, content: str,colour : str ,title: str = "shell", ):
        if not content or content.strip() == "":
            content = "[No output]"
        panel = Panel(content, title=f"[{colour}]{title}[/{colour}]", expand=True)
        self.console.print(panel)   

   
    def print_reasoning(self, content):
        self.console.print(Text(content, style="#888888 italic"), end="")


    

    