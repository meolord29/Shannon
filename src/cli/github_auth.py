"""
GitHub CLI Authentication - No OAuth App Required.

Opens GitHub's token creation page with pre-selected scopes.
User creates token and pastes it back into the CLI.
"""

from __future__ import annotations

import webbrowser
from typing import TYPE_CHECKING
from urllib.parse import urlencode

import httpx
import keyring
import typer

if TYPE_CHECKING:
    from typing import Optional

# Constants
GITHUB_API_BASE = "https://api.github.com"
KEYRING_SERVICE = "shannon-cli"
KEYRING_USERNAME = "github-token"

# Pre-configured scopes for token creation
# See: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps
DEFAULT_SCOPES = ["repo", "read:user"]


def get_stored_token() -> Optional[str]:
    """Retrieve the stored GitHub token from the system keyring."""
    try:
        return keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
    except Exception:
        return None


def store_token(token: str) -> None:
    """Store the GitHub token in the system keyring."""
    keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, token)


def delete_token() -> None:
    """Delete the stored GitHub token from the system keyring."""
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
    except keyring.errors.PasswordDeleteError:
        pass


def get_authenticated_client() -> httpx.Client:
    """Create an authenticated GitHub API client."""
    token = get_stored_token()

    if not token:
        typer.secho(
            "✗ Not authenticated. Run 'shannon auth login' first.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)

    return httpx.Client(
        base_url=GITHUB_API_BASE,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        timeout=30.0,
    )


def validate_token(token: str) -> dict:
    """Validate a token and return user info."""
    with httpx.Client(
        base_url=GITHUB_API_BASE,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        timeout=30.0,
    ) as client:
        response = client.get("/user")
        response.raise_for_status()
        return response.json()


def generate_token_url(scopes: list[str], description: str = "Shannon CLI") -> str:
    """
    Generate a GitHub URL that opens the token creation page with pre-selected scopes.
    """
    params = {
        "description": description,
        "scopes": ",".join(scopes),
    }
    return f"https://github.com/settings/tokens/new?{urlencode(params)}"


def generate_fine_grained_token_url() -> str:
    """Generate URL for fine-grained token creation."""
    return "https://github.com/settings/personal-access-tokens/new"


def _validate_and_store_token(token: str) -> None:
    """Validate token and store if valid."""
    if not token:
        typer.secho("✗ No token provided", fg=typer.colors.RED)
        raise typer.Exit(1)

    # Basic format validation
    valid_prefixes = ("ghp_", "github_pat_", "gho_", "ghu_", "ghs_")
    if not token.startswith(valid_prefixes):
        typer.secho(
            "⚠ Token format not recognized. Attempting validation anyway...",
            fg=typer.colors.YELLOW,
        )

    typer.echo("Validating token...")

    try:
        user_info = validate_token(token)
        store_token(token)

        typer.echo()
        typer.secho(
            f"✓ Successfully logged in as {user_info['login']}", fg=typer.colors.GREEN
        )

        if user_info.get("name"):
            typer.echo(f"  Name: {user_info['name']}")
        if user_info.get("email"):
            typer.echo(f"  Email: {user_info['email']}")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            typer.secho("✗ Invalid token", fg=typer.colors.RED)
        else:
            typer.secho(f"✗ Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)
