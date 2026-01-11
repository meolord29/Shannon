"""Section-level extraction."""
from typing import Any

from src.llm.client import LLMClient
from src.llm.extractors.base import BaseExtractor
from src.llm.prompts.templates import PromptTemplate, SYSTEM_NOTE_WRITER
from src.llm.prompts.extraction import EXTRACT_SECTION_NOTES


class SectionExtractor(BaseExtractor):
    """Extracts detailed notes from a paper section."""
    
    def __init__(self, client: LLMClient):
        super().__init__(client, SYSTEM_NOTE_WRITER)
    
    @property
    def extraction_type(self) -> str:
        return "section"
    
    @property
    def prompt_template(self) -> PromptTemplate:
        return EXTRACT_SECTION_NOTES
    
    def _process_response(self, response: str) -> dict[str, Any]:
        """Process markdown response from section extraction."""
        sections = self._parse_markdown_response(response)
        
        # Also extract any concepts, formulas found
        return {
            "raw_markdown": response,
            "sections": sections,
            "summary": sections.get("summary", ""),
            "key_points": self._extract_list(sections.get("key_points", "")),
            "concepts": self._extract_concepts(sections),
            "formulas": self._extract_formulas(response),
        }
    
    def _extract_list(self, text: str) -> list[str]:
        """Extract bullet points from text."""
        items = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                items.append(line[2:].strip())
        return items
    
    def _extract_concepts(self, sections: dict) -> list[dict[str, str]]:
        """Extract concept definitions from sections."""
        concepts = []
        concepts_text = sections.get("concepts_introduced", "")
        
        current_name = None
        current_content = []
        
        for line in concepts_text.split("\n"):
            if line.startswith("### "):
                if current_name:
                    concepts.append({
                        "name": current_name,
                        "definition": "\n".join(current_content).strip(),
                    })
                current_name = line[4:].strip()
                current_content = []
            elif current_name:
                current_content.append(line)
        
        if current_name:
            concepts.append({
                "name": current_name,
                "definition": "\n".join(current_content).strip(),
            })
        
        return concepts
    
    def _extract_formulas(self, text: str) -> list[dict[str, str]]:
        """Extract LaTeX formulas from text."""
        import re
        
        formulas = []
        
        # Find block formulas
        block_pattern = r"\$\$(.*?)\$\$"
        for match in re.finditer(block_pattern, text, re.DOTALL):
            formulas.append({
                "latex": match.group(1).strip(),
                "type": "block",
            })
        
        # Find inline formulas (excluding already captured blocks)
        inline_pattern = r"(?<!\$)\$([^$]+)\$(?!\$)"
        for match in re.finditer(inline_pattern, text):
            formulas.append({
                "latex": match.group(1).strip(),
                "type": "inline",
            })
        
        return formulas
    
    def _get_expected_keys(self) -> list[str]:
        return ["summary", "key_points"]