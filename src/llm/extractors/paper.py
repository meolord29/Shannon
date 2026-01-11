"""Full paper extraction."""
from typing import Any, Optional

from src.core.types import ExtractionResult, ExtractedPaper
from src.llm.client import LLMClient
from src.llm.extractors.base import BaseExtractor
from src.llm.prompts.templates import PromptTemplate, SYSTEM_ACADEMIC_EXPERT
from src.llm.prompts.extraction import EXTRACT_PAPER_STRUCTURE


class PaperExtractor(BaseExtractor):
    """Extracts structured information from a full paper."""
    
    def __init__(self, client: LLMClient):
        super().__init__(client, SYSTEM_ACADEMIC_EXPERT)
    
    @property
    def extraction_type(self) -> str:
        return "full_paper"
    
    @property
    def prompt_template(self) -> PromptTemplate:
        return EXTRACT_PAPER_STRUCTURE
    
    def _process_response(self, response: str) -> dict[str, Any]:
        """Process JSON response from paper extraction."""
        return self._parse_json_response(response)
    
    def _get_expected_keys(self) -> list[str]:
        return [
            "summary",
            "key_contributions",
            "sections",
            "main_concepts",
            "suggested_tags",
        ]
    
    async def extract_to_model(
        self,
        content: str,
        title: str,
    ) -> tuple[Optional[ExtractedPaper], ExtractionResult]:
        """Extract and return a typed model."""
        result = await self.extract(content, context={"title": title})
        
        if not result.success:
            return None, result
        
        try:
            paper = ExtractedPaper(
                title=title,
                summary=result.data.get("summary", ""),
                key_contributions=result.data.get("key_contributions", []),
                sections=[],  # Would need nested extraction
                main_concepts=result.data.get("main_concepts", []),
                algorithms=result.data.get("algorithms", []),
                suggested_tags=result.data.get("suggested_tags", []),
                suggested_pages=[],
            )
            return paper, result
        except Exception as e:
            result.errors.append(f"Model conversion error: {e}")
            return None, result