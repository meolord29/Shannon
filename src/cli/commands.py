"""
Shannon CLI Commands.

Provides command-line interface for Shannon including GitHub authentication
and repository operations.
"""

from __future__ import annotations

import base64
import webbrowser
from typing import TYPE_CHECKING

import httpx
import typer

from src.cli.github_auth import (
    DEFAULT_SCOPES,
    _validate_and_store_token,
    delete_token,
    generate_fine_grained_token_url,
    generate_token_url,
    get_authenticated_client,
    get_stored_token,
    validate_token,
)

if TYPE_CHECKING:
    from typing import Optional

# Main application
app = typer.Typer(
    name="shannon",
    help="Shannon - Collaborative knowledge management for academic papers",
    no_args_is_help=True,
)

# Sub-applications
auth_app = typer.Typer(help="GitHub authentication commands")
repo_app = typer.Typer(help="GitHub repository commands")

app.add_typer(auth_app, name="auth")
app.add_typer(repo_app, name="repo")


# =============================================================================
# AUTH COMMANDS
# =============================================================================


@auth_app.command("login")
def auth_login(
    token: Optional[str] = typer.Option(
        None,
        "--token",
        "-t",
        help="Provide token directly (skips browser)",
        hide_input=True,
    ),
    fine_grained: bool = typer.Option(
        False,
        "--fine-grained",
        "-f",
        help="Use fine-grained token (more secure, but manual scope selection)",
    ),
    scopes: Optional[str] = typer.Option(
        None,
        "--scopes",
        "-s",
        help="Comma-separated scopes (default: repo,read:user)",
    ),
) -> None:
    """
    Authenticate with GitHub.

    Opens GitHub in your browser to create a Personal Access Token.
    The token creation page will have the required permissions pre-selected.
    """
    # Check if already logged in
    existing_token = get_stored_token()
    if existing_token:
        try:
            user_info = validate_token(existing_token)
            typer.echo(f"Already logged in as {user_info['login']}")
            if not typer.confirm("Login with a different account?", default=False):
                raise typer.Exit(0)
        except httpx.HTTPStatusError:
            pass  # Token invalid, proceed

    # If token provided directly, validate and store
    if token:
        _validate_and_store_token(token)
        return

    # Parse scopes
    token_scopes = scopes.split(",") if scopes else DEFAULT_SCOPES

    # Generate appropriate URL
    if fine_grained:
        url = generate_fine_grained_token_url()
        typer.echo()
        typer.secho("=" * 65, fg=typer.colors.CYAN)
        typer.echo()
        typer.echo("  To authenticate, please:")
        typer.echo()
        typer.echo("  1. A browser window will open to GitHub")
        typer.echo("  2. Create a new Fine-Grained Personal Access Token")
        typer.echo("  3. Select the repositories you want to access")
        typer.echo("  4. Under 'Permissions', enable:")
        typer.secho("     • Contents: Read and write", fg=typer.colors.YELLOW)
        typer.secho("     • Metadata: Read-only", fg=typer.colors.YELLOW)
        typer.echo("  5. Click 'Generate token'")
        typer.echo("  6. Copy the token and paste it below")
        typer.echo()
        typer.secho("=" * 65, fg=typer.colors.CYAN)
    else:
        url = generate_token_url(token_scopes, description="shannon-cli")
        typer.echo()
        typer.secho("=" * 65, fg=typer.colors.CYAN)
        typer.echo()
        typer.echo("  To authenticate, please:")
        typer.echo()
        typer.echo("  1. A browser window will open to GitHub")
        typer.echo("  2. Sign in if needed")
        typer.echo("  3. The required permissions are pre-selected:")
        for scope in token_scopes:
            typer.secho(f"     • {scope}", fg=typer.colors.YELLOW)
        typer.echo("  4. Click 'Generate token' at the bottom")
        typer.echo("  5. Copy the token and paste it below")
        typer.echo()
        typer.secho("=" * 65, fg=typer.colors.CYAN)

    typer.echo()

    # Open browser
    if typer.confirm("Open GitHub in your browser?", default=True):
        webbrowser.open(url)
        typer.echo()
        typer.secho("Browser opened! Complete the steps above.", fg=typer.colors.GREEN)
    else:
        typer.echo()
        typer.echo(f"Open this URL manually: {url}")

    typer.echo()

    # Prompt for token
    new_token = typer.prompt(
        "Paste your token here",
        hide_input=True,
    )

    _validate_and_store_token(new_token.strip())


@auth_app.command("logout")
def auth_logout() -> None:
    """Log out from GitHub (remove stored token)."""
    token = get_stored_token()

    if not token:
        typer.echo("Not currently logged in.")
        return

    delete_token()
    typer.secho("✓ Successfully logged out.", fg=typer.colors.GREEN)


@auth_app.command("status")
def auth_status() -> None:
    """Check current authentication status."""
    token = get_stored_token()

    if not token:
        typer.secho("✗ Not logged in", fg=typer.colors.YELLOW)
        typer.echo("  Run 'shannon auth login' to authenticate.")
        raise typer.Exit(1)

    try:
        user_info = validate_token(token)
        typer.secho(f"✓ Logged in as {user_info['login']}", fg=typer.colors.GREEN)

        if user_info.get("name"):
            typer.echo(f"  Name: {user_info['name']}")
        if user_info.get("email"):
            typer.echo(f"  Email: {user_info['email']}")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            typer.secho("✗ Token is invalid or expired", fg=typer.colors.RED)
            typer.echo("  Run 'shannon auth login' to re-authenticate.")
        else:
            typer.secho(f"✗ Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@auth_app.command("refresh")
def auth_refresh() -> None:
    """
    Open GitHub to create a new token (keeps you logged in during transition).

    Useful when your token is about to expire or you need different permissions.
    """
    existing_token = get_stored_token()
    if not existing_token:
        typer.echo("Not logged in. Use 'auth login' instead.")
        raise typer.Exit(1)

    url = generate_token_url(DEFAULT_SCOPES, description="shannon-cli")

    typer.echo("Opening GitHub to create a new token...")
    typer.echo("Your current session will remain active until you provide a new token.")
    typer.echo()

    webbrowser.open(url)

    token = typer.prompt("Paste your new token here", hide_input=True)
    _validate_and_store_token(token.strip())


# =============================================================================
# REPO COMMANDS
# =============================================================================


@repo_app.command("list")
def repo_list(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of repos to display"),
) -> None:
    """List your GitHub repositories."""
    with get_authenticated_client() as client:
        response = client.get(
            "/user/repos",
            params={"per_page": limit, "sort": "updated"},
        )
        response.raise_for_status()
        repos = response.json()

    if not repos:
        typer.echo("No repositories found.")
        return

    for repo in repos:
        icon = "🔒" if repo["private"] else "📂"
        typer.echo(f"{icon} {repo['full_name']}")


@repo_app.command("get")
def repo_get_file(
    repo: str = typer.Argument(..., help="Repository (owner/repo)"),
    path: str = typer.Argument(..., help="File path"),
    ref: str = typer.Option("main", "--ref", "-r", help="Branch/tag/commit"),
) -> None:
    """Read a file from a repository."""
    with get_authenticated_client() as client:
        response = client.get(
            f"/repos/{repo}/contents/{path}",
            params={"ref": ref},
        )

        if response.status_code == 404:
            typer.secho(f"✗ Not found: {path}", fg=typer.colors.RED)
            raise typer.Exit(1)

        response.raise_for_status()
        data = response.json()

    if data.get("type") != "file":
        typer.secho(f"✗ {path} is not a file", fg=typer.colors.RED)
        raise typer.Exit(1)

    content = base64.b64decode(data["content"]).decode("utf-8")
    typer.echo(content)


@repo_app.command("put")
def repo_put_file(
    repo: str = typer.Argument(..., help="Repository (owner/repo)"),
    path: str = typer.Argument(..., help="File path"),
    message: str = typer.Option(..., "--message", "-m", help="Commit message"),
    content: Optional[str] = typer.Option(
        None, "--content", "-c", help="File content to write"
    ),
    input_file: Optional[str] = typer.Option(
        None, "--input", "-i", help="Local file to read content from"
    ),
    branch: str = typer.Option("main", "--branch", "-b", help="Target branch"),
) -> None:
    """Create or update a file in a repository."""
    if input_file:
        with open(input_file) as f:
            file_content = f.read()
    elif content:
        file_content = content
    else:
        typer.secho("✗ Provide --content or --input", fg=typer.colors.RED)
        raise typer.Exit(1)

    encoded = base64.b64encode(file_content.encode()).decode()

    with get_authenticated_client() as client:
        # Check for existing file to get SHA
        existing_sha = None
        resp = client.get(f"/repos/{repo}/contents/{path}", params={"ref": branch})
        if resp.status_code == 200:
            existing_sha = resp.json().get("sha")

        payload: dict = {"message": message, "content": encoded, "branch": branch}
        if existing_sha:
            payload["sha"] = existing_sha

        response = client.put(f"/repos/{repo}/contents/{path}", json=payload)
        response.raise_for_status()

    action = "Updated" if existing_sha else "Created"
    typer.secho(f"✓ {action} {path}", fg=typer.colors.GREEN)


# =============================================================================
# MAIN CALLBACK
# =============================================================================


@app.callback()
def main() -> None:
    """Shannon - Collaborative knowledge management for academic papers."""
    pass


if __name__ == "__main__":
    app()
