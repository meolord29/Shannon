"""LLM configuration and model registry."""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from src.core.types import LLMBackend


@dataclass
class ModelInfo:
    """Information about a supported model."""
    name: str
    context_window: int
    description: str
    recommended_for: list[str] = field(default_factory=list)


# Model registry
MODELS = {
    # GPT-OSS models
    "gpt-oss-20b": ModelInfo(
        name="gpt-oss-20b",
        context_window=8192,
        description="GPT-OSS 20B - Default model for text extraction",
        recommended_for=["extraction", "summarization", "general"],
    ),
    "gpt-oss-20b-q4_k_m": ModelInfo(
        name="gpt-oss-20b-q4_k_m",
        context_window=8192,
        description="GPT-OSS 20B 4-bit quantized",
        recommended_for=["extraction", "summarization"],
    ),
    "gpt-oss-20b-q8_0": ModelInfo(
        name="gpt-oss-20b-q8_0",
        context_window=8192,
        description="GPT-OSS 20B 8-bit quantized",
        recommended_for=["extraction", "summarization"],
    ),
}


@dataclass
class BackendConfig:
    """Configuration for a specific backend."""
    base_url: str
    api_key: Optional[str] = None
    default_model: str = "gpt-oss-20b"
    timeout: float = 120.0
    max_retries: int = 3


# Default backend configurations
BACKEND_DEFAULTS = {
    LLMBackend.LM_STUDIO: BackendConfig(
        base_url="http://localhost:1234/v1",
        default_model="gpt-oss-20b",
    ),
    LLMBackend.LLAMA_CPP: BackendConfig(
        base_url="http://localhost:8080/v1",
        default_model="gpt-oss-20b",
    ),
    LLMBackend.OPENROUTER: BackendConfig(
        base_url="https://openrouter.ai/api/v1",
        default_model="gpt-oss/gpt-oss-20b",
        api_key="",  # Required for OpenRouter
    ),
}


@dataclass
class LLMConfig:
    """Complete LLM configuration."""
    backend: LLMBackend = LLMBackend.LM_STUDIO
    base_url: Optional[str] = None  # Override backend default
    api_key: Optional[str] = None
    model: str = "gpt-oss-20b"
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: float = 120.0
    max_retries: int = 3
    cache_enabled: bool = True
    
    def get_base_url(self) -> str:
        """Get the effective base URL."""
        if self.base_url:
            return self.base_url
        return BACKEND_DEFAULTS[self.backend].base_url
    
    def get_api_key(self) -> Optional[str]:
        """Get the effective API key."""
        if self.api_key:
            return self.api_key
        return BACKEND_DEFAULTS[self.backend].api_key
    
    def get_model_info(self) -> ModelInfo:
        """Get info about the configured model."""
        return MODELS.get(
            self.model,
            ModelInfo(
                name=self.model,
                context_window=8192,
                description="Custom model",
            ),
        )
    
    @property
    def context_window(self) -> int:
        """Get context window size for current model."""
        return self.get_model_info().context_window


def get_default_config() -> LLMConfig:
    """Get default LLM configuration."""
    return LLMConfig(
        backend=LLMBackend.LM_STUDIO,
        model="gpt-oss-20b",
    )