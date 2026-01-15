"""LLM response caching."""
from dataclasses import dataclass
from typing import Optional
import time
import sqlite3
import json
from pathlib import Path

from src.core.types import LLMResponse, TokenUsage, CachedResponse


class ResponseCache:
    """SQLite-based cache for LLM responses."""
    
    def __init__(
        self,
        db_path: Path,
        default_ttl: Optional[int] = None,  # None = no expiry
    ):
        self._db_path = db_path
        self._default_ttl = default_ttl
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize the cache database."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS llm_cache (
                    cache_key TEXT PRIMARY KEY,
                    response_content TEXT NOT NULL,
                    model TEXT NOT NULL,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    finish_reason TEXT,
                    created_at REAL NOT NULL,
                    expires_at REAL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_expires 
                ON llm_cache(expires_at)
            """)
    
    async def get(self, cache_key: str) -> Optional[CachedResponse]:
        """Retrieve a cached response."""
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM llm_cache 
                WHERE cache_key = ? 
                AND (expires_at IS NULL OR expires_at > ?)
                """,
                (cache_key, time.time()),
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            response = LLMResponse(
                content=row["response_content"],
                model=row["model"],
                usage=TokenUsage(
                    input_tokens=row["input_tokens"] or 0,
                    output_tokens=row["output_tokens"] or 0,
                ),
                finish_reason=row["finish_reason"] or "stop",
                cached=True,
            )
            
            return CachedResponse(
                response=response,
                created_at=row["created_at"],
                expires_at=row["expires_at"],
            )
    
    async def set(
        self,
        cache_key: str,
        response: LLMResponse,
        ttl: Optional[int] = None,
    ) -> None:
        """Store a response in the cache."""
        ttl = ttl or self._default_ttl
        created_at = time.time()
        expires_at = created_at + ttl if ttl else None
        
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO llm_cache 
                (cache_key, response_content, model, input_tokens, 
                 output_tokens, finish_reason, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cache_key,
                    response.content,
                    response.model,
                    response.usage.input_tokens,
                    response.usage.output_tokens,
                    response.finish_reason,
                    created_at,
                    expires_at,
                ),
            )
    
    async def delete(self, cache_key: str) -> bool:
        """Delete a cached response."""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM llm_cache WHERE cache_key = ?",
                (cache_key,),
            )
            return cursor.rowcount > 0
    
    async def clear_expired(self) -> int:
        """Remove expired entries."""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM llm_cache WHERE expires_at IS NOT NULL AND expires_at < ?",
                (time.time(),),
            )
            return cursor.rowcount
    
    async def clear_all(self) -> int:
        """Clear all cached responses."""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute("DELETE FROM llm_cache")
            return cursor.rowcount
    
    async def get_stats(self) -> dict:
        """Get cache statistics."""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_entries,
                    SUM(input_tokens + output_tokens) as total_tokens,
                    COUNT(CASE WHEN expires_at IS NOT NULL AND expires_at < ? THEN 1 END) as expired_entries
                FROM llm_cache
            """, (time.time(),))
            row = cursor.fetchone()
            
            return {
                "total_entries": row[0] or 0,
                "total_tokens_cached": row[1] or 0,
                "expired_entries": row[2] or 0,
            }