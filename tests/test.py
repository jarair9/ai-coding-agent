from textual.app import App, ComposeResult
from textual.widgets import Collapsible, Label

class ChevronAccordionApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    Collapsible {
        width: 60;
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        # Standard accordion / collapsible with chevron
        with Collapsible(title="Click to expand (Advanced Settings)", collapsed=True):
            yield Label(
                "Here is the extended text!\n\n"
                "• Feature A: Enabled\n"
                "• Feature B: Disabled\n"
                "• Custom API Key: **********"
            )

        with Collapsible(title="Click to view Logs", collapsed=True):
            yield Label(
                "2026-08-12 10:00:00 - System started\n"
                "2026-08-12 10:00:05 - Connected to database\n"
                "2026-08-12 10:01:23 - Worker process initialized"
            )

if __name__ == "__main__":
    app = ChevronAccordionApp()
    app.run()