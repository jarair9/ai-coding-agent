

import asyncio
import difflib
from pathlib import Path
from rich.spinner import Spinner
from rich.panel import Panel
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.table import Table
from rich import print
from rich.syntax import Syntax
from rich.live import Live
from rich.panel import Panel
from rich import box


class TUI:
    def __init__(self):
        self.console = Console()

    def header(self, model):
    
        panel =Panel(f"Model : {model}\nCommands : /help , /model, /usage\nMode : Auto approve Actions",title="[purple]AI Agent[/purple]",title_align="left",highlight=True,style="cyan")
        self.console.print(panel)


    def error(self,error):
        panel = Panel(error,title_align="center",expand= True,style="bold red")
        self.console.print(panel)


    def code_ui(self, code, tool_name):
        # Safety: if code is None or empty, show a fallback
        if code is None or code == "":
            fallback = "[yellow]No content to display (file may be empty or binary)[/yellow]"
            panel = Panel(fallback, title=tool_name, title_align="center", expand=True, style="dim")
            self.console.print(panel)
            return

        # Ensure code is a string
        if not isinstance(code, str):
            code = str(code)

        # Now safe to create Syntax
        syntax = Syntax(
            code,
            "python",   # or auto-detect from file extension
            theme="monokai",
            
            # line_numbers=True
        )
        panel = Panel(syntax, title=tool_name, title_align="center", expand=True,highlight=True)
        self.console.print(panel)

    def write_code_ui(self, content, tool_name):
        if not content or content == "":
            content = "[File content is empty]"
        syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
        panel = Panel(syntax, title=tool_name, border_style="green")
        self.console.print(panel)
    def get_language(self, file_path: str) -> str:
        """Return a language name for syntax highlighting based on file extension."""
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
    
    def diff_panels(self, old_content: str, new_content: str, path: str):
        """Show old content (red) and new content (syntax highlighted) in two panels."""
        lang = self.get_language(path)   # implement auto‑detect
        old_panel = Panel(
            Syntax(old_content, lang, theme="monokai") if old_content else "[italic]empty[/italic]",
            title="[red]Old version[/red]",
            border_style="red"
        )
        new_panel = Panel(
            Syntax(new_content, lang, theme="monokai") if new_content else "[italic]empty[/italic]",
            title="[green]New version[/green]",
            border_style="green"
        )
        self.console.print(old_panel)
        self.console.print(new_panel)
    
    def white_panel(self, content, title):
        if isinstance(content, list):
            content = "\n".join(str(item) for item in content)
        panel = Panel(content, title=title, expand=True, highlight=True)
        self.console.print(panel)

            
    def white_panel(self, content, title):
        # Convert content to a readable string
        if content is None:
            content_str = "[No content]"
        elif isinstance(content, list):
            content_str = "\n".join(str(item) for item in content)
        elif isinstance(content, dict):
            content_str = "\n".join(f"{k}: {v}" for k, v in content.items())
        else:
            content_str = str(content)
        
        # If still empty, show a placeholder
        if not content_str.strip():
            content_str = "[Empty directory or no files]"
        
        panel = Panel(content_str, title=title, expand=True, highlight=True,style="green")
        self.console.print(panel)
    def shell_panel(self, content: str,colour : str ,title: str = "shell", ):
        if not content or content.strip() == "":
            content = "[No output]"
        panel = Panel(content, title=f"[{colour}]{title}[/{colour}]", border_style="red", expand=True)
        self.console.print(panel)   



    async def status_indicator(self,generator,status):
        """Wrap an async generator to show a spinner until first chunk arrives."""
        first_chunk_received = False
        spinner_task = None

        async def show_spinner():
            with self.console.status(f"[bold yellow]{status}...[/bold yellow]", spinner="dots"):
                while not first_chunk_received:
                    await asyncio.sleep(0.1)

        # Start the spinner in a background task
        spinner_task = asyncio.create_task(show_spinner())

        try:
            async for chunk in generator:
                if not first_chunk_received:
                    first_chunk_received = True
                    spinner_task.cancel()
                    try:
                        await spinner_task
                    except asyncio.CancelledError:
                        pass
                yield chunk
        finally:
            if not first_chunk_received:
                spinner_task.cancel()