"""Git repository management."""
from pathlib import Path
from git import Repo, GitCommandError
from typing import Optional

from src.config.settings import get_settings


class GitManager:
    """Manages Git operations for the vault."""
    
    def __init__(self, repo_path: Optional[Path] = None):
        settings = get_settings()
        self.repo_path = repo_path or settings.vault_path
        self._repo: Optional[Repo] = None
    
    @property
    def repo(self) -> Repo:
        """Lazy-load the Git repository."""
        if self._repo is None:
            self._repo = Repo(self.repo_path)
        return self._repo
    
    @property
    def current_branch(self) -> str:
        """Get current branch name."""
        return self.repo.active_branch.name
    
    @property
    def is_dirty(self) -> bool:
        """Check if there are uncommitted changes."""
        return self.repo.is_dirty(untracked_files=True)
    
    def create_branch(self, branch_name: str) -> None:
        """Create and checkout a new branch."""
        self.repo.create_head(branch_name)
        self.repo.heads[branch_name].checkout()
    
    def checkout(self, branch_name: str) -> None:
        """Checkout an existing branch."""
        self.repo.heads[branch_name].checkout()
    
    def stage_all(self) -> None:
        """Stage all changes."""
        self.repo.git.add(A=True)
    
    def commit(self, message: str) -> str:
        """Commit staged changes and return commit hash."""
        commit = self.repo.index.commit(message)
        return commit.hexsha
    
    def rebase_onto_main(self, branch_name: str) -> bool:
        """Rebase a branch onto main and merge."""
        settings = get_settings()
        main_branch = settings.default_branch
        
        try:
            # Checkout the feature branch
            self.checkout(branch_name)
            
            # Rebase onto main
            self.repo.git.rebase(main_branch)
            
            # Checkout main and merge
            self.checkout(main_branch)
            self.repo.git.merge(branch_name, ff_only=True)
            
            # Delete the feature branch
            self.repo.delete_head(branch_name)
            
            return True
        except GitCommandError as e:
            # Abort rebase on conflict
            self.repo.git.rebase(abort=True)
            raise RuntimeError(f"Rebase failed: {e}")
    
    def get_status(self) -> dict:
        """Get repository status."""
        return {
            "branch": self.current_branch,
            "dirty": self.is_dirty,
            "staged": [item.a_path for item in self.repo.index.diff("HEAD")],
            "modified": [item.a_path for item in self.repo.index.diff(None)],
            "untracked": self.repo.untracked_files,
        }