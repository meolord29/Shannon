"""Main TUI application."""
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer

from src.tui.screens.home import HomeScreen
from src.tui.screens.inbox import InboxScreen
from src.tui.screens.paper_list import PaperListScreen
from src.tui.screens.search import SearchScreen
from src.tui.screens.git_status import GitStatusScreen


class ShannonTUI(App):
    """Shannon TUI Application."""
    
    TITLE = "Shannon"
    SUB_TITLE = "Collaborative Knowledge Management"
    CSS_PATH = "styles/theme.tcss"
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("h", "push_screen('home')", "Home"),
        Binding("i", "push_screen('inbox')", "Inbox"),
        Binding("p", "push_screen('papers')", "Papers"),
        Binding("/", "push_screen('search')", "Search"),
        Binding("g", "push_screen('git')", "Git Status"),
        Binding("?", "toggle_help", "Help"),
    ]
    
    SCREENS = {
        "home": HomeScreen,
        "inbox": InboxScreen,
        "papers": PaperListScreen,
        "search": SearchScreen,
        "git": GitStatusScreen,
    }
    
    def compose(self) -> ComposeResult:
        """Compose the main application layout."""
        yield Header()
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the application."""
        self.push_screen("home")
    
    def action_toggle_help(self) -> None:
        """Toggle help overlay."""
        self.bell()  # Placeholder for help modal