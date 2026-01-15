# PDF to text conversion

"""PDF parsing for paper content extraction."""
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class ParsedPDF:
    """Parsed PDF content."""
    text: str
    pages: list[str]
    metadata: dict[str, str]
    page_count: int


class PDFParser:
    """Parses PDF files for text extraction."""
    
    def __init__(self):
        # Lazy import to avoid dependency if not needed
        self._pymupdf = None
    
    def _get_pymupdf(self):
        """Lazy load PyMuPDF."""
        if self._pymupdf is None:
            try:
                import pymupdf
                self._pymupdf = pymupdf
            except ImportError:
                raise ImportError(
                    "PyMuPDF is required for PDF parsing. "
                    "Install with: pip install pymupdf"
                )
        return self._pymupdf
    
    def parse(self, pdf_path: Path) -> ParsedPDF:
        """Parse a PDF file and extract text."""
        pymupdf = self._get_pymupdf()
        
        doc = pymupdf.open(pdf_path)
        
        pages = []
        for page in doc:
            text = page.get_text()
            # Clean up common PDF artifacts
            text = self._clean_text(text)
            pages.append(text)
        
        metadata = {
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
        }
        
        doc.close()
        
        return ParsedPDF(
            text="\n\n".join(pages),
            pages=pages,
            metadata=metadata,
            page_count=len(pages),
        )
    
    def parse_with_layout(self, pdf_path: Path) -> ParsedPDF:
        """Parse PDF preserving more layout information."""
        pymupdf = self._get_pymupdf()
        
        doc = pymupdf.open(pdf_path)
        
        pages = []
        for page in doc:
            # Get text blocks with position info
            blocks = page.get_text("blocks")
            # Sort by vertical then horizontal position
            blocks.sort(key=lambda b: (b[1], b[0]))
            
            page_text = []
            for block in blocks:
                if block[6] == 0:  # Text block
                    text = self._clean_text(block[4])
                    if text.strip():
                        page_text.append(text)
            
            pages.append("\n".join(page_text))
        
        metadata = {
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
        }
        
        doc.close()
        
        return ParsedPDF(
            text="\n\n".join(pages),
            pages=pages,
            metadata=metadata,
            page_count=len(pages),
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean up common PDF extraction artifacts."""
        # Remove excessive whitespace
        text = re.sub(r" +", " ", text)
        # Fix hyphenation at line breaks
        text = re.sub(r"-\n(\w)", r"\1", text)
        # Remove page numbers (common patterns)
        text = re.sub(r"\n\d+\n", "\n", text)
        # Normalize line endings
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
    
    def extract_sections(self, parsed: ParsedPDF) -> dict[str, str]:
        """Attempt to extract sections by headers."""
        sections = {}
        current_section = "preamble"
        current_content = []
        
        # Common section header patterns
        header_patterns = [
            r"^(\d+\.?\s+)?(abstract|introduction|background|related work|methodology|method|approach|experiments|results|discussion|conclusion|references)s?\s*$",
            r"^(\d+\.?\s+)?([A-Z][A-Za-z\s]+)$",  # Numbered sections
        ]
        
        for line in parsed.text.split("\n"):
            is_header = False
            for pattern in header_patterns:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    # Save previous section
                    if current_content:
                        sections[current_section] = "\n".join(current_content)
                    current_section = line.strip().lower()
                    current_content = []
                    is_header = True
                    break
            
            if not is_header:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = "\n".join(current_content)
        
        return sections