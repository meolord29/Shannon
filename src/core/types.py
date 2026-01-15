# type aliases and typedDicts"""Type aliases and TypedDicts for type safety."""
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Sequence, TypedDict, NewType, Any, Optional
from datetime import datetime
from enum import Enum


# =============================================================================
# ENTITY ID TYPES
# =============================================================================

EntityId = NewType("EntityId", str)
UserId = NewType("UserId", str)      # GitHub username
PaperId = NewType("PaperId", str)    # OpenReview ID
PageId = NewType("PageId", str)
NoteId = NewType("NoteId", str)
ContentId = NewType("ContentId", str)
TagId = NewType("TagId", str)
CitationId = NewType("CitationId", str)
BibliographyId = NewType("BibliographyId", str)

T = TypeVar("T")


# =============================================================================
# GENERIC CONTAINERS
# =============================================================================

@dataclass(frozen=True)
class PaginatedResult(Generic[T]):
    """Container for paginated query results."""
    
    items: Sequence[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages
    
    @property
    def has_previous(self) -> bool:
        return self.page > 1


@dataclass(frozen=True)
class SearchResult:
    """A single search result from Tantivy."""
    
    content_id: ContentId
    score: float
    snippet: str
    content_type: str
    # Denormalized for display
    paper_id: Optional[PaperId] = None
    paper_title: Optional[str] = None
    page_id: Optional[PageId] = None
    page_title: Optional[str] = None
    note_id: Optional[NoteId] = None


# =============================================================================
# GIT TYPES
# =============================================================================

@dataclass(frozen=True)
class GitStatus:
    """Git repository status."""
    
    branch: str
    is_dirty: bool
    staged: Sequence[str]
    modified: Sequence[str]
    untracked: Sequence[str]
    ahead: int = 0
    behind: int = 0
    
    @property
    def has_changes(self) -> bool:
        return bool(self.staged or self.modified or self.untracked)


@dataclass(frozen=True)
class GitCommit:
    """Git commit information."""
    
    hash: str
    short_hash: str
    message: str
    author: str
    timestamp: datetime


# =============================================================================
# INPUT TYPEDDICTS (for validation)
# =============================================================================

class CreatePaperInput(TypedDict, total=False):
    """Input for creating a paper."""
    
    openreview_id: str          # Required
    title: str                  # Required
    abstract: str
    pdf_url: str


class UpdatePaperInput(TypedDict, total=False):
    """Input for updating a paper."""
    
    title: str
    status: str
    directory: str


class CreatePageInput(TypedDict, total=False):
    """Input for creating a page."""
    
    paper_id: str               # Required
    title: str                  # Required
    category: str
    purpose: str
    position: int
    parent_page_id: str


class UpdatePageInput(TypedDict, total=False):
    """Input for updating a page."""
    
    title: str
    category: str
    purpose: str
    position: int


class CreateNoteInput(TypedDict, total=False):
    """Input for creating a note."""
    
    page_id: str                # Required
    content: str                # Required
    note_type: str
    position: int


class UpdateNoteInput(TypedDict, total=False):
    """Input for updating a note."""
    
    content: str
    note_type: str
    position: int


class CreateContentInput(TypedDict):
    """Input for creating content."""
    
    body: str                   # Required
    content_type: str           # Required


class SearchInput(TypedDict, total=False):
    """Input for search queries."""
    
    query: str                  # Required
    content_type: str           # Filter by type
    paper_id: str               # Filter by paper
    limit: int
    offset: int


# =============================================================================
# OUTPUT TYPES
# =============================================================================

class PaperSummary(TypedDict):
    """Summary view of a paper for lists."""
    
    paper_id: str
    title: str
    slug: str
    status: str
    directory: str
    contributor_count: int
    page_count: int
    created_at: str


class PageTreeNode(TypedDict):
    """Node in a page tree structure."""
    
    page_id: str
    title: str
    slug: str
    category: str
    position: int
    depth: int
    children: list["PageTreeNode"]


class NoteWithContent(TypedDict):
    """Note with its content body."""
    
    note_id: str
    page_id: str
    note_type: str
    position: int
    content_id: str
    body: str
    body_plain: str


# =============================================================================
# CONFIGURATION TYPES
# =============================================================================

class DirectoryConfig(TypedDict):
    """Directory configuration."""
    
    inbox: str
    papers: str
    concepts: str
    algorithms: str


class DatabaseConfig(TypedDict):
    """Database configuration."""
    
    path: str
    name: str


class GitConfig(TypedDict):
    """Git configuration."""
    
    default_branch: str
    auto_commit: bool
    remote: str


class AppConfig(TypedDict):
    """Full application configuration."""
    
    directories: DirectoryConfig
    database: DatabaseConfig
    git: GitConfig




# =============================================================================
# LLM TYPES
# =============================================================================

class LLMBackend(str, Enum):
    """Supported LLM backends."""
    LM_STUDIO = "lm_studio"
    LLAMA_CPP = "llama_cpp"
    OPENROUTER = "openrouter"


class LLMRole(str, Enum):
    """Message roles for LLM conversations."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True)
class LLMMessage:
    """A single message in an LLM conversation."""
    role: LLMRole
    content: str
    
    def to_dict(self) -> dict[str, str]:
        """Convert to OpenAI-compatible format."""
        return {"role": self.role.value, "content": self.content}


@dataclass(frozen=True)
class TokenUsage:
    """Token usage statistics."""
    prompt_tokens: int
    completion_tokens: int
    
    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass(frozen=True)
class LLMResponse:
    """Response from an LLM."""
    content: str
    model: str
    usage: Optional[TokenUsage] = None
    finish_reason: str = "stop"
    cached: bool = False


@dataclass
class ExtractionResult:
    """Result of an extraction operation."""
    extraction_type: str
    success: bool
    data: dict[str, Any]
    confidence: float
    raw_response: str
    usage: Optional[TokenUsage] = None
    errors: list[str] = field(default_factory=list)


# =============================================================================
# EXTRACTION TYPES
# =============================================================================

class ExtractionType(str, Enum):
    """Types of extraction operations."""
    FULL_PAPER = "full_paper"
    SECTION = "section"
    ABSTRACT = "abstract"
    METHODOLOGY = "methodology"
    RESULTS = "results"
    ALGORITHM = "algorithm"
    FORMULA = "formula"
    CITATION = "citation"
    KEY_CONCEPTS = "key_concepts"
    SUMMARY = "summary"


@dataclass
class PaperExtractionInput:
    """Input for paper extraction."""
    paper_id: str
    pdf_path: str
    title: str
    existing_abstract: Optional[str] = None
    extraction_types: list[ExtractionType] = field(
        default_factory=lambda: [ExtractionType.FULL_PAPER]
    )


@dataclass
class ExtractedSection:
    """Extracted section data."""
    title: str
    summary: str
    key_points: list[str]
    concepts: list[str]
    formulas: list[dict[str, str]]
    citations: list[str]
    suggested_notes: list[dict[str, str]]


@dataclass
class ExtractedPaper:
    """Complete extracted paper structure."""
    title: str
    summary: str
    key_contributions: list[str]
    sections: list[ExtractedSection]
    main_concepts: list[dict[str, str]]
    algorithms: list[dict[str, str]]
    suggested_tags: list[str]
    suggested_pages: list[dict[str, Any]]


@dataclass
class ChunkInfo:
    """Information about a text chunk."""
    index: int
    total_chunks: int
    start_char: int
    end_char: int
    token_count: int
    text: str

# =============================================================================
# EXTRACTION INPUT/OUTPUT TYPES
# =============================================================================

class ExtractionType(str, Enum):
    """Types of extraction operations."""
    FULL_PAPER = "full_paper"
    SECTION = "section"
    ABSTRACT = "abstract"
    METHODOLOGY = "methodology"
    RESULTS = "results"
    ALGORITHM = "algorithm"
    FORMULA = "formula"
    CITATION = "citation"
    KEY_CONCEPTS = "key_concepts"
    SUMMARY = "summary"


@dataclass
class PaperExtractionInput:
    """Input for full paper extraction."""
    paper_id: str
    pdf_path: str
    title: str
    existing_abstract: Optional[str] = None
    extraction_types: list[ExtractionType] = field(
        default_factory=lambda: [ExtractionType.FULL_PAPER]
    )


@dataclass
class SectionExtractionInput:
    """Input for section extraction."""
    paper_id: str
    section_text: str
    section_type: str
    page_numbers: Optional[str] = None


@dataclass
class ExtractedSection:
    """Extracted section data."""
    title: str
    summary: str
    key_points: list[str]
    concepts: list[str]
    formulas: list[dict[str, str]]
    citations: list[str]
    suggested_notes: list[dict[str, str]]


@dataclass
class ExtractedPaper:
    """Complete extracted paper structure."""
    title: str
    summary: str
    key_contributions: list[str]
    sections: list[ExtractedSection]
    main_concepts: list[dict[str, str]]
    algorithms: list[dict[str, str]]
    suggested_tags: list[str]
    suggested_pages: list[dict[str, Any]]


@dataclass
class ChunkInfo:
    """Information about a text chunk."""
    index: int
    total_chunks: int
    start_char: int
    end_char: int
    token_count: int
    text: str


# =============================================================================
# CACHE TYPES
# =============================================================================

@dataclass
class CacheKey:
    """Key for caching LLM responses."""
    prompt_hash: str
    model: str
    temperature: float


@dataclass
class CachedResponse:
    """Cached LLM response."""
    response: LLMResponse
    created_at: float
    expires_at: Optional[float] = None