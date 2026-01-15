# Text chunking for context windows

"""Text chunking for context window management."""
from dataclasses import dataclass
from typing import Sequence, Callable

from src.core.types import ChunkInfo


@dataclass
class ChunkingConfig:
    """Configuration for text chunking."""
    max_tokens: int = 4000
    overlap_tokens: int = 200
    separator: str = "\n\n"
    fallback_separators: tuple[str, ...] = ("\n", ". ", " ")


class TextChunker:
    """Splits text into chunks that fit within token limits."""
    
    def __init__(
        self,
        token_counter: Callable[[str], int],
        config: ChunkingConfig | None = None,
    ):
        self._count_tokens = token_counter
        self._config = config or ChunkingConfig()
    
    def chunk(
        self,
        text: str,
        max_tokens: int | None = None,
        overlap: int | None = None,
    ) -> list[ChunkInfo]:
        """Split text into chunks."""
        max_tokens = max_tokens or self._config.max_tokens
        overlap = overlap or self._config.overlap_tokens
        
        # If text fits in one chunk, return it
        total_tokens = self._count_tokens(text)
        if total_tokens <= max_tokens:
            return [
                ChunkInfo(
                    index=0,
                    total_chunks=1,
                    start_char=0,
                    end_char=len(text),
                    token_count=total_tokens,
                    text=text,
                )
            ]
        
        chunks = []
        current_pos = 0
        chunk_index = 0
        
        while current_pos < len(text):
            # Find the end position for this chunk
            chunk_end = self._find_chunk_end(
                text, current_pos, max_tokens
            )
            
            chunk_text = text[current_pos:chunk_end]
            chunks.append(
                ChunkInfo(
                    index=chunk_index,
                    total_chunks=0,  # Will update after
                    start_char=current_pos,
                    end_char=chunk_end,
                    token_count=self._count_tokens(chunk_text),
                    text=chunk_text,
                )
            )
            
            # Move position, accounting for overlap
            overlap_chars = self._tokens_to_chars(overlap, chunk_text)
            current_pos = chunk_end - overlap_chars
            chunk_index += 1
        
        # Update total_chunks
        total = len(chunks)
        return [
            ChunkInfo(
                index=c.index,
                total_chunks=total,
                start_char=c.start_char,
                end_char=c.end_char,
                token_count=c.token_count,
                text=c.text,
            )
            for c in chunks
        ]
    
    def _find_chunk_end(
        self,
        text: str,
        start: int,
        max_tokens: int,
    ) -> int:
        """Find the best end position for a chunk."""
        # Binary search for approximate position
        low, high = start, len(text)
        
        while high - low > 100:
            mid = (low + high) // 2
            tokens = self._count_tokens(text[start:mid])
            if tokens <= max_tokens:
                low = mid
            else:
                high = mid
        
        # Find a good break point
        candidate = low
        for sep in (self._config.separator,) + self._config.fallback_separators:
            # Look for separator near the candidate position
            sep_pos = text.rfind(sep, start, candidate + len(sep) * 2)
            if sep_pos > start:
                candidate = sep_pos + len(sep)
                break
        
        return min(candidate, len(text))
    
    def _tokens_to_chars(self, tokens: int, reference_text: str) -> int:
        """Estimate character count from token count."""
        if not reference_text:
            return tokens * 4  # Rough estimate
        
        ref_tokens = self._count_tokens(reference_text)
        if ref_tokens == 0:
            return tokens * 4
        
        chars_per_token = len(reference_text) / ref_tokens
        return int(tokens * chars_per_token)