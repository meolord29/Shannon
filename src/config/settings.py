"""Application settings management."""
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

from src.core.types import LLMBackend

class Settings(BaseSettings):
    """Application settings loaded from environment and config file."""
    
    model_config = SettingsConfigDict(
        env_prefix="SHANNON_",
        env_file=".env",
        extra="ignore",
    )
    
    # Paths
    app_dir: Path = Path.home() / ".shannon"
    vault_path: Path = Path.cwd()
    
    # Database
    database_name: str = "shannon.db"
    
    # Directories (matching config.ini)
    dir_inbox: str = "01_Inbox"
    dir_papers: str = "10_Papers"
    dir_concepts: str = "20_Concepts"
    dir_algorithms: str = "30_Algorithms"
    
    # Git
    default_branch: str = "main"
    auto_commit: bool = True
    
    # Search
    search_index_dir: str = "search_index"
    
    # OpenReview
    openreview_base_url: str = "https://api.openreview.net"
    
    @property
    def database_path(self) -> Path:
        return self.app_dir / "data" / self.database_name
    
    @property
    def search_index_path(self) -> Path:
        return self.app_dir / "data" / self.search_index_dir
    
    @property
    def directories(self) -> dict[str, str]:
        return {
            "inbox": self.dir_inbox,
            "papers": self.dir_papers,
            "concepts": self.dir_concepts,
            "algorithms": self.dir_algorithms,
        }

        # Backend selection

    # ==========================================================================
    # LLM Configuration
    # ==========================================================================

    llm_backend: LLMBackend = LLMBackend.LM_STUDIO
    
    # Connection settings
    llm_base_url: Optional[str] = None  # Override default for backend
    llm_api_key: Optional[str] = None   # Required for OpenRouter
    
    # Model settings
    llm_model: str = "gpt-oss-20b"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096
    llm_timeout: float = 120.0
    llm_max_retries: int = 3
    
    # Cache settings
    llm_cache_enabled: bool = True
    llm_cache_ttl: Optional[int] = None  # None = no expiry
    
    @property
    def llm_cache_path(self) -> Path:
        return self.app_dir / "data" / "llm_cache.db"
    
    def get_llm_config(self) -> "LLMConfig":
        """Build LLMConfig from settings."""
        from src.llm.config import LLMConfig
        
        return LLMConfig(
            backend=self.llm_backend,
            base_url=self.llm_base_url,
            api_key=self.llm_api_key,
            model=self.llm_model,
            temperature=self.llm_temperature,
            max_tokens=self.llm_max_tokens,
            timeout=self.llm_timeout,
            max_retries=self.llm_max_retries,
            cache_enabled=self.llm_cache_enabled,
        )

@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()