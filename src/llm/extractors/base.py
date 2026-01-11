"""Base extractor class."""
from abc import ABC, abstractmethod
from typing import Any, Optional
import json
import re

from src.core.types import ExtractionResult, LLMMessage, LLMRole
from src.llm.client import LLMClient
from src.llm.prompts.templates import PromptTemplate


class BaseExtractor(ABC):
    """Abstract base class for content extractors."""
    
    def __init__(
        self,
        client: LLMClient,
        system_prompt: PromptTemplate,
    ):
        self._client = client
        self._system_prompt = system_prompt
    
    @property
    @abstractmethod
    def extraction_type(self) -> str:
        """Type of extraction this extractor performs."""
        ...
    
    @property
    @abstractmethod
    def prompt_template(self) -> PromptTemplate:
        """The main prompt template for extraction."""
        ...
    
    def _build_messages(
        self,
        user_content: str,
        system_override: Optional[str] = None,
    ) -> list[LLMMessage]:
        """Build the message sequence for the LLM."""
        return [
            LLMMessage(
                role=LLMRole.SYSTEM,
                content=system_override or self._system_prompt.template,
            ),
            LLMMessage(
                role=LLMRole.USER,
                content=user_content,
            ),
        ]
    
    def _parse_json_response(self, response: str) -> dict[str, Any]:
        """Extract JSON from LLM response."""
        # Try to find JSON block in markdown code fence
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find raw JSON object
        json_match = re.search(r"\{[\s\S]*\}", response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Return raw text as fallback
        return {"raw_text": response, "parse_error": True}
    
    def _parse_markdown_response(self, response: str) -> dict[str, Any]:
        """Parse structured markdown response into sections."""
        sections = {}
        current_section = None
        current_content = []
        
        for line in response.split("\n"):
            if line.startswith("## "):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = line[3:].strip().lower().replace(" ", "_")
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = "\n".join(current_content).strip()
        
        return sections
    
    async def extract(
        self,
        content: str,
        context: Optional[dict[str, Any]] = None,
    ) -> ExtractionResult:
        """Perform extraction on the provided content."""
        context = context or {}
        
        # Validate required variables
        template_vars = {"content": content, **context}
        missing = self.prompt_template.validate_variables(**template_vars)
        if missing:
            return ExtractionResult(
                extraction_type=self.extraction_type,
                success=False,
                data={},
                confidence=0.0,
                raw_response="",
                errors=[f"Missing required variables: {missing}"],
            )
        
        # Render prompt
        user_content = self.prompt_template.render(**template_vars)
        messages = self._build_messages(user_content)
        
        try:
            # Call LLM with low temperature for consistent extraction
            response = await self._client.complete(
                messages=messages,
                temperature=0.1,
            )
            
            # Process response
            data = self._process_response(response.content)
            
            return ExtractionResult(
                extraction_type=self.extraction_type,
                success=True,
                data=data,
                confidence=self._calculate_confidence(data),
                raw_response=response.content,
                usage=response.usage,
            )
            
        except Exception as e:
            return ExtractionResult(
                extraction_type=self.extraction_type,
                success=False,
                data={},
                confidence=0.0,
                raw_response="",
                errors=[str(e)],
            )
    
    @abstractmethod
    def _process_response(self, response: str) -> dict[str, Any]:
        """Process the LLM response into structured data."""
        ...
    
    def _calculate_confidence(self, data: dict[str, Any]) -> float:
        """Calculate confidence score for the extraction."""
        if not data or data.get("parse_error"):
            return 0.0
        
        expected_keys = self._get_expected_keys()
        if not expected_keys:
            return 0.8
        
        present_keys = sum(1 for k in expected_keys if k in data and data[k])
        return present_keys / len(expected_keys)
    
    def _get_expected_keys(self) -> list[str]:
        """Get expected keys in the extraction result."""
        return []
    
    def validate(self, result: ExtractionResult) -> bool:
        """Validate an extraction result."""
        return result.success and result.confidence > 0.5