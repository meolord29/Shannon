import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from Meta.cli import util

app = typer.Typer()
console = Console()


@app.command()
def list_papers(directory: str = typer.Argument(..., help="Directory key from config.ini (e.g., papers, concepts, algorithms) or 'all'.")):
    """
    Lists papers from the specified directory and optionally downloads a paper.
    """
    papers = []
    if directory.lower() == 'all':
        papers.extend(util.get_paper_urls('papers'))
        papers.extend(util.get_paper_urls('concepts'))
        papers.extend(util.get_paper_urls('algorithms'))
    else:
        papers = util.get_paper_urls(directory)

    if not papers:
        console.print("No papers found.")
        return

    table = Table(title="Papers", border_style="cyan", header_style="bold magenta")
    table.add_column("#", style="dim", width=4)
    table.add_column("Folder", style="green", justify="right")
    table.add_column("URL", style="yellow")
    table.add_column("Downloaded", style="blue")

    for i, paper in enumerate(papers):
        table.add_row(str(i + 1), paper["folder"], paper["url"], paper["downloaded"])

    console.print(table)

    while True:
        choice = Prompt.ask("Enter the number of the paper to download (or 'q' to quit)")
        if choice.lower() == 'q':
            break
        
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(papers):
                paper_to_download = papers[choice_index]
                if paper_to_download['downloaded'] == 'Yes':
                    console.print(f"Paper \"{paper_to_download['folder']}\" is already downloaded.")
                    continue
                util.download_paper(paper_to_download["url"], paper_to_download["folder"])
                # Refresh the table
                list_papers(directory)
                break
            else:
                console.print("Invalid number. Please try again.")
        except ValueError:
            console.print("Invalid input. Please enter a number or 'q'.")


if __name__ == "__main__":
    app()
