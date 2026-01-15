"""Unified LLM client for OpenAI-compatible APIs."""
import asyncio
import hashlib
from typing import Sequence, AsyncIterator, Optional
import httpx

from src.core.types import (
    LLMMessage,
    LLMResponse,
    TokenUsage,
    LLMRole,
    LLMBackend,
)
from src.llm.config import LLMConfig, get_default_config
from src.llm.cache.response_cache import ResponseCache


class LLMClient:
    """
    Unified client for OpenAI-compatible LLM APIs.
    
    Supports:
    - LM Studio (localhost:1234)
    - llama.cpp server (localhost:8080)
    - OpenRouter (openrouter.ai)
    """
    
    def __init__(
        self,
        config: Optional[LLMConfig] = None,
        cache: Optional[ResponseCache] = None,
    ):
        self._config = config or get_default_config()
        self._cache = cache
        
        # Configure HTTP client
        self._http = httpx.AsyncClient(
            base_url=self._config.get_base_url(),
            timeout=httpx.Timeout(self._config.timeout),
            headers=self._build_headers(),
        )
    
    def _build_headers(self) -> dict[str, str]:
        """Build request headers."""
        headers = {
            "Content-Type": "application/json",
        }
        
        api_key = self._config.get_api_key()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # OpenRouter specific headers
        if self._config.backend == LLMBackend.OPENROUTER:
            headers["HTTP-Referer"] = "https://github.com/shannon"
            headers["X-Title"] = "Shannon"
        
        return headers
    
    @property
    def model(self) -> str:
        return self._config.model
    
    @property
    def base_url(self) -> str:
        return self._config.get_base_url()
    
    @property
    def max_context_tokens(self) -> int:
        return self._config.context_window
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count.
        
        Uses simple heuristic: ~4 characters per token.
        For more accuracy, use tiktoken with appropriate encoding.
        """
        return len(text) // 4
    
    def _compute_cache_key(
        self,
        messages: Sequence[LLMMessage],
        temperature: float,
    ) -> str:
        """Compute cache key for request."""
        content = f"{self._config.model}:{temperature}:"
        content += "|".join(f"{m.role.value}:{m.content}" for m in messages)
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def complete(
        self,
        messages: Sequence[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[list[str]] = None,
    ) -> LLMResponse:
        """
        Generate a completion using the configured backend.
        
        Args:
            messages: Conversation messages
            temperature: Sampling temperature (default from config)
            max_tokens: Maximum tokens to generate (default from config)
            stop: Stop sequences
            
        Returns:
            LLMResponse with generated content
        """
        temperature = temperature if temperature is not None else self._config.temperature
        max_tokens = max_tokens or self._config.max_tokens
        
        # Check cache for deterministic requests
        if self._cache and temperature == 0.0:
            cache_key = self._compute_cache_key(messages, temperature)
            cached = await self._cache.get(cache_key)
            if cached:
                return LLMResponse(
                    content=cached.response.content,
                    model=cached.response.model,
                    usage=cached.response.usage,
                    finish_reason=cached.response.finish_reason,
                    cached=True,
                )
        
        # Build request payload
        payload = {
            "model": self._config.model,
            "messages": [m.to_dict() for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if stop:
            payload["stop"] = stop
        
        # Make request with retries
        last_error = None
        for attempt in range(self._config.max_retries):
            try:
                response = await self._http.post(
                    "/chat/completions",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                
                # Parse response
                choice = data["choices"][0]
                usage_data = data.get("usage", {})
                
                llm_response = LLMResponse(
                    content=choice["message"]["content"],
                    model=data.get("model", self._config.model),
                    usage=TokenUsage(
                        prompt_tokens=usage_data.get("prompt_tokens", 0),
                        completion_tokens=usage_data.get("completion_tokens", 0),
                    ) if usage_data else None,
                    finish_reason=choice.get("finish_reason", "stop"),
                )
                
                # Cache successful response
                if self._cache and temperature == 0.0:
                    await self._cache.set(cache_key, llm_response)
                
                return llm_response
                
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code >= 500:
                    # Server error, retry
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise
            except httpx.RequestError as e:
                last_error = e
                await asyncio.sleep(2 ** attempt)
                continue
        
        raise RuntimeError(f"Failed after {self._config.max_retries} retries: {last_error}")
    
    async def stream(
        self,
        messages: Sequence[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[list[str]] = None,
    ) -> AsyncIterator[str]:
        """
        Stream a completion from the configured backend.
        
        Args:
            messages: Conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stop: Stop sequences
            
        Yields:
            Text chunks as they're generated
        """
        temperature = temperature if temperature is not None else self._config.temperature
        max_tokens = max_tokens or self._config.max_tokens
        
        payload = {
            "model": self._config.model,
            "messages": [m.to_dict() for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        
        if stop:
            payload["stop"] = stop
        
        async with self._http.stream(
            "POST",
            "/chat/completions",
            json=payload,
        ) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    
                    try:
                        import json
                        chunk = json.loads(data)
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
    
    async def health_check(self) -> bool:
        """Check if the backend is available."""
        try:
            response = await self._http.get("/models")
            return response.status_code == 200
        except Exception:
            return False
    
    async def list_models(self) -> list[str]:
        """List available models from the backend."""
        try:
            response = await self._http.get("/models")
            response.raise_for_status()
            data = response.json()
            return [m["id"] for m in data.get("data", [])]
        except Exception:
            return []
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http.aclose()
    
    async def __aenter__(self) -> "LLMClient":
        return self
    
    async def __aexit__(self, *args) -> None:
        await self.close()