"""Service for orchestrating LLM-based paper extraction."""
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass

from src.core.types import (
    ExtractionResult,
    ExtractedPaper,
    PaperExtractionInput,
    PaperId,
    PageId,
)
from src.core.results import Result, Ok, Err
from src.core.events import get_event_bus, BaseEvent

from src.llm.client import LLMClient
from src.llm.config import LLMConfig
from src.llm.extractors.paper import PaperExtractor
from src.llm.extractors.section import SectionExtractor
from src.llm.processors.pdf_parser import PDFParser
from src.llm.processors.chunker import TextChunker
from src.llm.cache.response_cache import ResponseCache

from src.services.paper_service import PaperService
from src.services.page_service import PageService
from src.services.note_service import NoteService
from src.config.settings import get_settings


@dataclass(frozen=True)
class ExtractionStartedEvent(BaseEvent):
    """Fired when extraction begins."""
    paper_id: str
    extraction_types: list[str]


@dataclass(frozen=True)
class ExtractionCompletedEvent(BaseEvent):
    """Fired when extraction completes."""
    paper_id: str
    success: bool
    pages_created: int
    notes_created: int


@dataclass(frozen=True)
class ExtractionProgressEvent(BaseEvent):
    """Fired during extraction to report progress."""
    paper_id: str
    stage: str
    progress: float  # 0.0 to 1.0
    message: str


class ExtractionService:
    """Orchestrates LLM-based extraction from academic papers."""
    
    def __init__(
        self,
        paper_service: PaperService,
        page_service: PageService,
        note_service: NoteService,
        llm_config: Optional[LLMConfig] = None,
    ):
        self._paper_service = paper_service
        self._page_service = page_service
        self._note_service = note_service
        self._event_bus = get_event_bus()
        
        settings = get_settings()
        self._config = llm_config or settings.get_llm_config()
        
        # Initialize cache
        self._cache: Optional[ResponseCache] = None
        if self._config.cache_enabled:
            self._cache = ResponseCache(db_path=settings.llm_cache_path)
        
        # Initialize LLM client
        self._client = LLMClient(config=self._config, cache=self._cache)
        
        # Initialize processors
        self._pdf_parser = PDFParser()
        self._chunker = TextChunker(token_counter=self._client.count_tokens)
        
        # Initialize extractors
        self._paper_extractor = PaperExtractor(self._client)
        self._section_extractor = SectionExtractor(self._client)
    
    async def check_backend_health(self) -> bool:
        """Check if the LLM backend is available."""
        return await self._client.health_check()
    
    async def extract_paper(
        self,
        input_data: PaperExtractionInput,
    ) -> Result[ExtractedPaper, Exception]:
        """
        Extract structured information from a paper.
        
        Args:
            input_data: Paper extraction parameters
            
        Returns:
            Result containing ExtractedPaper or error
        """
        self._event_bus.publish(ExtractionStartedEvent(
            paper_id=input_data.paper_id,
            extraction_types=[et.value for et in input_data.extraction_types],
        ))
        
        try:
            # Check backend availability
            if not await self.check_backend_health():
                return Err(ConnectionError(
                    f"LLM backend not available at {self._config.get_base_url()}. "
                    "Please start LM Studio or llama.cpp server."
                ))
            
            self._publish_progress(input_data.paper_id, "parsing", 0.1, "Parsing PDF...")
            
            # Parse PDF
            pdf_path = Path(input_data.pdf_path)
            if not pdf_path.exists():
                return Err(FileNotFoundError(f"PDF not found: {pdf_path}"))
            
            parsed = self._pdf_parser.parse(pdf_path)
            
            self._publish_progress(input_data.paper_id, "analyzing", 0.2, "Analyzing content...")
            
            # Check if content fits in context window
            total_tokens = self._client.count_tokens(parsed.text)
            max_tokens = self._client.max_context_tokens - 4000  # Reserve for response
            
            if total_tokens > max_tokens:
                self._publish_progress(
                    input_data.paper_id, "chunking", 0.3,
                    f"Content too large ({total_tokens} tokens), processing in chunks..."
                )
                result = await self._extract_chunked(input_data, parsed.text, max_tokens)
            else:
                self._publish_progress(
                    input_data.paper_id, "extracting", 0.4,
                    "Extracting paper structure..."
                )
                result = await self._extract_full(input_data, parsed.text)
            
            if not result.success:
                return Err(Exception(f"Extraction failed: {result.errors}"))
            
            self._publish_progress(input_data.paper_id, "finalizing", 0.9, "Building structure...")
            
            # Convert to model
            extracted = self._result_to_model(input_data.title, result)
            
            self._publish_progress(input_data.paper_id, "complete", 1.0, "Extraction complete")
            
            self._event_bus.publish(ExtractionCompletedEvent(
                paper_id=input_data.paper_id,
                success=True,
                pages_created=len(extracted.suggested_pages),
                notes_created=0,
            ))
            
            return Ok(extracted)
            
        except Exception as e:
            self._event_bus.publish(ExtractionCompletedEvent(
                paper_id=input_data.paper_id,
                success=False,
                pages_created=0,
                notes_created=0,
            ))
            return Err(e)
    
    def _publish_progress(
        self,
        paper_id: str,
        stage: str,
        progress: float,
        message: str,
    ) -> None:
        """Publish extraction progress event."""
        self._event_bus.publish(ExtractionProgressEvent(
            paper_id=paper_id,
            stage=stage,
            progress=progress,
            message=message,
        ))
    
    async def _extract_full(
        self,
        input_data: PaperExtractionInput,
        content: str,
    ) -> ExtractionResult:
        """Extract from full paper content."""
        return await self._paper_extractor.extract(
            content=content,
            context={"title": input_data.title},
        )
    
    async def _extract_chunked(
        self,
        input_data: PaperExtractionInput,
        content: str,
        max_tokens: int,
    ) -> ExtractionResult:
        """Extract from chunked content and merge results."""
        chunks = self._chunker.chunk(content, max_tokens=max_tokens)
        
        all_sections = []
        all_concepts = []
        all_algorithms = []
        
        for i, chunk in enumerate(chunks):
            self._publish_progress(
                input_data.paper_id,
                "extracting",
                0.3 + (0.5 * (i / len(chunks))),
                f"Processing chunk {i + 1} of {len(chunks)}..."
            )
            
            result = await self._section_extractor.extract(
                content=chunk.text,
                context={
                    "paper_title": input_data.title,
                    "section_title": f"Part {chunk.index + 1}",
                    "section_type": "content",
                },
            )
            
            if result.success:
                all_sections.extend(result.data.get("sections", {}).items())
                all_concepts.extend(result.data.get("concepts", []))
        
        return ExtractionResult(
            extraction_type="full_paper",
            success=True,
            data={
                "summary": "",
                "key_contributions": [],
                "sections": dict(self._deduplicate_pairs(all_sections)),
                "main_concepts": self._deduplicate(all_concepts, "name"),
                "algorithms": all_algorithms,
                "suggested_tags": [],
            },
            confidence=0.7,
            raw_response="",
        )
    
    def _deduplicate(self, items: list[dict], key: str) -> list[dict]:
        """Remove duplicate items based on a key."""
        seen = set()
        result = []
        for item in items:
            item_key = item.get(key, "").lower()
            if item_key and item_key not in seen:
                seen.add(item_key)
                result.append(item)
        return result
    
    def _deduplicate_pairs(self, pairs: list[tuple]) -> list[tuple]:
        """Remove duplicate key-value pairs."""
        seen = set()
        result = []
        for key, value in pairs:
            if key not in seen:
                seen.add(key)
                result.append((key, value))
        return result
    
    def _result_to_model(self, title: str, result: ExtractionResult) -> ExtractedPaper:
        """Convert extraction result to typed model."""
        return ExtractedPaper(
            title=title,
            summary=result.data.get("summary", ""),
            key_contributions=result.data.get("key_contributions", []),
            sections=[],
            main_concepts=result.data.get("main_concepts", []),
            algorithms=result.data.get("algorithms", []),
            suggested_tags=result.data.get("suggested_tags", []),
            suggested_pages=self._generate_page_suggestions(result),
        )
    
    def _generate_page_suggestions(self, result: ExtractionResult) -> list[dict[str, Any]]:
        """Generate suggested page structure from extraction."""
        pages = []
        position = 0
        
        # Create pages from sections
        sections_data = result.data.get("sections", {})
        if isinstance(sections_data, dict):
            for title, content in sections_data.items():
                pages.append({
                    "title": title.replace("_", " ").title(),
                    "category": "section",
                    "position": position,
                    "suggested_content": content if isinstance(content, str) else "",
                })
                position += 1
        
        # Create pages for concepts
        for concept in result.data.get("main_concepts", []):
            pages.append({
                "title": concept.get("name", "Concept"),
                "category": "concept",
                "position": position,
                "suggested_content": concept.get("definition", ""),
            })
            position += 1
        
        # Create pages for algorithms
        for algo in result.data.get("algorithms", []):
            pages.append({
                "title": algo.get("name", "Algorithm"),
                "category": "algorithm",
                "position": position,
                "suggested_content": algo.get("purpose", ""),
            })
            position += 1
        
        return pages
    
    async def create_pages_from_extraction(
        self,
        paper_id: PaperId,
        extracted: ExtractedPaper,
        auto_create_notes: bool = True,
    ) -> Result[list[PageId], Exception]:
        """Create pages and notes from extracted structure."""
        created_pages = []
        
        try:
            for page_data in extracted.suggested_pages:
                page = self._page_service.create({
                    "paper_id": paper_id,
                    "title": page_data["title"],
                    "category": page_data["category"],
                    "position": page_data["position"],
                })
                
                if page:
                    created_pages.append(page.page_id)
                    
                    if auto_create_notes and page_data.get("suggested_content"):
                        self._note_service.create({
                            "page_id": page.page_id,
                            "content": page_data["suggested_content"],
                            "note_type": "text",
                            "position": 0,
                        })
            
            return Ok(created_pages)
            
        except Exception as e:
            return Err(e)
    
    async def get_cache_stats(self) -> dict:
        """Get LLM cache statistics."""
        if self._cache:
            return await self._cache.get_stats()
        return {"enabled": False}
    
    async def clear_cache(self) -> int:
        """Clear the LLM response cache."""
        if self._cache:
            return await self._cache.clear_all()
        return 0
    
    async def close(self) -> None:
        """Clean up resources."""
        await self._client.close()