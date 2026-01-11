# main TUI application bootstrap

"""Main application entry point."""
import typer
from pathlib import Path

from src.config.settings import get_settings
from src.database.connection import init_database
from src.tui.app import ShannonTUI

cli = typer.Typer(
    name="shannon",
    help="Collaborative knowledge management for academic papers",
    no_args_is_help=True,
)


@cli.command()
def run() -> None:
    """Launch the Shannon TUI application."""
    settings = get_settings()
    init_database(settings.database_path)
    app = ShannonTUI()
    app.run()


@cli.command()
def init(
    vault_path: Path = typer.Option(
        Path.cwd(),
        "--path", "-p",
        help="Path to initialize the vault"
    )
) -> None:
    """Initialize a new Shannon vault."""
    from src.services.sync_service import initialize_vault
    initialize_vault(vault_path)
    typer.echo(f"✅ Initialized Shannon vault at {vault_path}")


@cli.command()
def search(query: str) -> None:
    """Search notes from the command line."""
    from src.services.search_service import search_content
    from rich.console import Console
    from rich.table import Table

    console = Console()
    results = search_content(query)
    
    table = Table(title=f"Search Results: '{query}'")
    table.add_column("Paper", style="cyan")
    table.add_column("Page", style="green")
    table.add_column("Snippet", style="white")
    
    for result in results[:10]:
        table.add_row(result.paper_title, result.page_title, result.snippet)
    
    console.print(table)


@cli.command()
def sync() -> None:
    """Sync local files with database."""
    from src.services.sync_service import sync_vault
    sync_vault()
    typer.echo("✅ Vault synchronized")


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()