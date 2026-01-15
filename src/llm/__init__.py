"""LLM module for paper extraction and processing."""
from src.llm.client import LLMClient
from src.llm.config import LLMConfig, ModelInfo, get_default_config
from src.llm.extractors.paper import PaperExtractor
from src.llm.extractors.section import SectionExtractor
from src.llm.processors.chunker import TextChunker
from src.llm.processors.pdf_parser import PDFParser

__all__ = [
    "LLMClient",
    "LLMConfig",
    "ModelInfo",
    "get_default_config",
    "PaperExtractor",
    "SectionExtractor",
    "TextChunker",
    "PDFParser",
]