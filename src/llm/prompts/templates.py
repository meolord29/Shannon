"""Base prompt template system."""
from dataclasses import dataclass
from typing import Any
import re


@dataclass
class PromptTemplate:
    """A reusable prompt template."""
    
    name: str
    template: str
    description: str = ""
    
    def render(self, **kwargs: Any) -> str:
        """Render the template with provided variables."""
        result = self.template
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result
    
    def get_required_variables(self) -> set[str]:
        """Extract required variables from template."""
        pattern = r"\{(\w+)\}"
        return set(re.findall(pattern, self.template))
    
    def validate_variables(self, **kwargs: Any) -> list[str]:
        """Return list of missing required variables."""
        required = self.get_required_variables()
        provided = set(kwargs.keys())
        return list(required - provided)


# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

SYSTEM_ACADEMIC_EXPERT = PromptTemplate(
    name="system_academic_expert",
    template="""You are an expert academic researcher and technical writer specializing in machine learning and computer science papers.

Your responsibilities:
- Extract key concepts, methodologies, and findings with precision
- Identify and format mathematical formulas correctly in LaTeX
- Document algorithms with clear step-by-step explanations
- Maintain academic rigor while making content accessible
- Format all output in clean, structured markdown

Guidelines:
- Be precise and factual - only include information from the source
- Use $...$ for inline math and $$...$$ for block equations
- Structure output with clear headers and bullet points
- Identify connections between concepts""",
)


SYSTEM_NOTE_WRITER = PromptTemplate(
    name="system_note_writer",
    template="""You are a skilled note-taker creating study materials from academic papers.

Your goal is to create clear, interconnected notes that help readers understand complex topics.

Guidelines:
- Write in clear, accessible language without oversimplifying
- Use bullet points and headers for organization
- Include relevant formulas in LaTeX notation
- Suggest connections to related concepts using [[wiki-style links]]
- Highlight key insights and novel contributions
- Include concrete examples where helpful""",
)