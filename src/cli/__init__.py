"""
Shannon CLI Module.

Provides command-line interface for Shannon including GitHub authentication
and repository operations.
"""

from src.cli.commands import app, auth_app, repo_app
from src.cli.github_auth import (
    delete_token,
    get_authenticated_client,
    get_stored_token,
    store_token,
    validate_token,
)

__all__ = [
    "app",
    "auth_app",
    "repo_app",
    "get_stored_token",
    "store_token",
    "delete_token",
    "validate_token",
    "get_authenticated_client",
]
