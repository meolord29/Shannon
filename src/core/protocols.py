"""Protocol definitions (interfaces) for dependency injection and testing."""
from typing import Protocol, TypeVar, Generic, Sequence, Any, Optional, AsyncIterator, runtime_checkable
from pathlib import Path

from src.core.types import EntityId, SearchResult, GitStatus, PaginatedResult
from src.core.types import (
    ExtractionResult,
    LLMResponse,
    LLMMessage,
    TokenUsage,
)


T = TypeVar("T")
ID = TypeVar("ID", bound=EntityId)


# =============================================================================
# REPOSITORY PROTOCOLS
# =============================================================================

@runtime_checkable
class Repository(Protocol[T, ID]):
    """Base repository protocol for data access."""
    
    def get_by_id(self, entity_id: ID) -> Optional[T]:
        """Retrieve an entity by its ID."""
        ...
    
    def get_all(self) -> Sequence[T]:
        """Retrieve all entities."""
        ...
    
    def save(self, entity: T) -> T:
        """Save (insert or update) an entity."""
        ...
    
    def delete(self, entity_id: ID) -> bool:
        """Delete an entity by ID. Returns True if deleted."""
        ...
    
    def exists(self, entity_id: ID) -> bool:
        """Check if an entity exists."""
        ...


@runtime_checkable
class PaginatedRepository(Repository[T, ID], Protocol):
    """Repository with pagination support."""
    
    def get_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[dict[str, Any]] = None,
    ) -> PaginatedResult[T]:
        """Retrieve entities with pagination."""
        ...


@runtime_checkable
class ContentRepository(Protocol):
    """Specialized protocol for content (Tantivy-indexed) data."""
    
    def get_by_id(self, content_id: str) -> Optional[Any]:
        ...
    
    def save(self, entity: Any) -> Any:
        ...
    
    def get_all_for_indexing(self) -> Sequence[Any]:
        """Get all content records for search indexing."""
        ...
    
    def get_modified_since(self, timestamp: float) -> Sequence[Any]:
        """Get content modified since timestamp for incremental indexing."""
        ...


# =============================================================================
# SERVICE PROTOCOLS
# =============================================================================

@runtime_checkable
class Service(Protocol):
    """Base service protocol."""
    
    def health_check(self) -> bool:
        """Check if the service is operational."""
        ...


@runtime_checkable
class CRUDService(Protocol[T, ID]):
    """Service with standard CRUD operations."""
    
    def get(self, entity_id: ID) -> Optional[T]:
        ...
    
    def list(self, filters: Optional[dict[str, Any]] = None) -> Sequence[T]:
        ...
    
    def create(self, data: dict[str, Any]) -> T:
        ...
    
    def update(self, entity_id: ID, data: dict[str, Any]) -> T:
        ...
    
    def delete(self, entity_id: ID) -> bool:
        ...


@runtime_checkable
class PaperServiceProtocol(Protocol):
    """Protocol for paper management service."""
    
    def import_from_openreview(self, openreview_id: str) -> Any:
        """Import a paper from OpenReview."""
        ...
    
    def move_to_directory(self, paper_id: str, directory: str) -> Any:
        """Move paper to a different directory (inbox -> papers, etc)."""
        ...
    
    def update_status(self, paper_id: str, status: str) -> Any:
        """Update paper status."""
        ...
    
    def assign_contributor(self, paper_id: str, user_id: str, role: str) -> Any:
        """Assign a contributor to a paper."""
        ...


# =============================================================================
# SEARCH PROTOCOLS
# =============================================================================

@runtime_checkable
class SearchEngine(Protocol):
    """Protocol for full-text search operations."""
    
    def index(self, content_id: str, body: str, metadata: dict[str, Any]) -> None:
        """Index a single document."""
        ...
    
    def bulk_index(self, documents: Sequence[dict[str, Any]]) -> int:
        """Bulk index documents. Returns count indexed."""
        ...
    
    def search(
        self,
        query: str,
        filters: Optional[dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Sequence[SearchResult]:
        """Execute a search query."""
        ...
    
    def delete(self, content_id: str) -> bool:
        """Remove a document from the index."""
        ...
    
    def clear(self) -> None:
        """Clear the entire index."""
        ...
    
    def commit(self) -> None:
        """Commit pending changes to the index."""
        ...


# =============================================================================
# GIT PROTOCOLS
# =============================================================================

@runtime_checkable
class GitProvider(Protocol):
    """Protocol for Git operations."""
    
    @property
    def current_branch(self) -> str:
        """Get current branch name."""
        ...
    
    @property
    def is_dirty(self) -> bool:
        """Check for uncommitted changes."""
        ...
    
    def get_status(self) -> GitStatus:
        """Get repository status."""
        ...
    
    def create_branch(self, branch_name: str) -> None:
        """Create and checkout a new branch."""
        ...
    
    def checkout(self, branch_name: str) -> None:
        """Checkout an existing branch."""
        ...
    
    def stage(self, paths: Sequence[str] | str) -> None:
        """Stage files for commit."""
        ...
    
    def stage_all(self) -> None:
        """Stage all changes."""
        ...
    
    def commit(self, message: str) -> str:
        """Commit staged changes. Returns commit hash."""
        ...
    
    def rebase_onto(self, target_branch: str) -> bool:
        """Rebase current branch onto target."""
        ...
    
    def push(self, remote: str = "origin") -> None:
        """Push to remote."""
        ...
    
    def pull(self, remote: str = "origin") -> None:
        """Pull from remote."""
        ...


# =============================================================================
# LINTER PROTOCOLS
# =============================================================================

@runtime_checkable
class LintResult(Protocol):
    """Protocol for lint result."""
    
    @property
    def file_path(self) -> Path:
        ...
    
    @property
    def line(self) -> int:
        ...
    
    @property
    def column(self) -> int:
        ...
    
    @property
    def message(self) -> str:
        ...
    
    @property
    def rule_id(self) -> str:
        ...
    
    @property
    def is_fixable(self) -> bool:
        ...


@runtime_checkable
class Linter(Protocol):
    """Protocol for code/content linting."""
    
    def lint(self, path: Path) -> Sequence[LintResult]:
        """Lint a file or directory."""
        ...
    
    def lint_content(self, content: str, filename: str = "<string>") -> Sequence[LintResult]:
        """Lint content string."""
        ...
    
    def fix(self, path: Path) -> int:
        """Auto-fix issues. Returns count of fixes applied."""
        ...
    
    def fix_content(self, content: str, filename: str = "<string>") -> str:
        """Auto-fix content string. Returns fixed content."""
        ...


# =============================================================================
# FILESYSTEM PROTOCOLS
# =============================================================================

@runtime_checkable
class FileSystem(Protocol):
    """Protocol for filesystem operations (enables testing with fake FS)."""
    
    def read_text(self, path: Path) -> str:
        """Read file as text."""
        ...
    
    def write_text(self, path: Path, content: str) -> None:
        """Write text to file."""
        ...
    
    def exists(self, path: Path) -> bool:
        """Check if path exists."""
        ...
    
    def is_file(self, path: Path) -> bool:
        """Check if path is a file."""
        ...
    
    def is_dir(self, path: Path) -> bool:
        """Check if path is a directory."""
        ...
    
    def mkdir(self, path: Path, parents: bool = False, exist_ok: bool = False) -> None:
        """Create directory."""
        ...
    
    def rmtree(self, path: Path) -> None:
        """Remove directory tree."""
        ...
    
    def iterdir(self, path: Path) -> Sequence[Path]:
        """Iterate directory contents."""
        ...
    
    def glob(self, path: Path, pattern: str) -> Sequence[Path]:
        """Glob pattern matching."""
        ...


# =============================================================================
# EVENT PROTOCOLS
# =============================================================================

@runtime_checkable
class Event(Protocol):
    """Base event protocol."""
    
    @property
    def event_type(self) -> str:
        """Event type identifier."""
        ...
    
    @property
    def timestamp(self) -> float:
        """Event timestamp."""
        ...


@runtime_checkable
class EventPublisher(Protocol):
    """Protocol for publishing events."""
    
    def publish(self, event: Event) -> None:
        """Publish an event."""
        ...


@runtime_checkable
class EventSubscriber(Protocol):
    """Protocol for subscribing to events."""
    
    def subscribe(self, event_type: str, handler: Any) -> None:
        """Subscribe to an event type."""
        ...
    
    def unsubscribe(self, event_type: str, handler: Any) -> None:
        """Unsubscribe from an event type."""
        ...


# =============================================================================
# HTTP CLIENT PROTOCOLS
# =============================================================================

@runtime_checkable
class HttpClient(Protocol):
    """Protocol for HTTP operations."""
    
    async def get(self, url: str, params: Optional[dict] = None) -> dict:
        """HTTP GET request."""
        ...
    
    async def post(self, url: str, data: Optional[dict] = None) -> dict:
        """HTTP POST request."""
        ...



@runtime_checkable
class LLMProvider(Protocol):
    """Protocol for LLM API providers."""
    
    @property
    def model_name(self) -> str:
        """Get the model identifier."""
        ...
    
    @property
    def max_context_tokens(self) -> int:
        """Maximum context window size."""
        ...
    
    async def complete(
        self,
        messages: Sequence[LLMMessage],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate a completion."""
        ...
    
    async def stream(
        self,
        messages: Sequence[LLMMessage],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Stream a completion."""
        ...
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        ...


@runtime_checkable
class Extractor(Protocol):
    """Protocol for content extractors."""
    
    @property
    def extraction_type(self) -> str:
        """Type of content this extractor handles."""
        ...
    
    async def extract(
        self,
        content: str,
        context: Optional[dict[str, Any]] = None,
    ) -> ExtractionResult:
        """Extract structured information from content."""
        ...
    
    def validate(self, result: ExtractionResult) -> bool:
        """Validate extraction result."""
        ...


@runtime_checkable
class TextProcessor(Protocol):
    """Protocol for text processing operations."""
    
    def process(self, text: str) -> str:
        """Process text content."""
        ...


@runtime_checkable
class Chunker(Protocol):
    """Protocol for text chunking."""
    
    def chunk(
        self,
        text: str,
        max_tokens: int,
        overlap: int = 0,
    ) -> Sequence[str]:
        """Split text into chunks."""
        ...


@runtime_checkable
class PromptTemplate(Protocol):
    """Protocol for prompt templates."""
    
    @property
    def template(self) -> str:
        """The prompt template string."""
        ...
    
    def render(self, **kwargs: Any) -> str:
        """Render the template with variables."""
        ...
    
    def get_required_variables(self) -> set[str]:
        """Get required template variables."""
        ...


@runtime_checkable
class LLMClient(Protocol):
    """Protocol for OpenAI-compatible LLM clients."""
    
    @property
    def model(self) -> str:
        """Current model identifier."""
        ...
    
    @property
    def base_url(self) -> str:
        """API base URL."""
        ...
    
    @property
    def max_context_tokens(self) -> int:
        """Maximum context window size."""
        ...
    
    async def complete(
        self,
        messages: Sequence["LLMMessage"],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[list[str]] = None,
    ) -> "LLMResponse":
        """Generate a completion."""
        ...
    
    async def stream(
        self,
        messages: Sequence["LLMMessage"],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[list[str]] = None,
    ) -> AsyncIterator[str]:
        """Stream a completion."""
        ...
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        ...
    
    async def health_check(self) -> bool:
        """Check if the backend is available."""
        ...


@runtime_checkable
class Extractor(Protocol):
    """Protocol for content extractors."""
    
    @property
    def extraction_type(self) -> str:
        """Type of content this extractor handles."""
        ...
    
    async def extract(
        self,
        content: str,
        context: Optional[dict[str, Any]] = None,
    ) -> "ExtractionResult":
        """Extract structured information from content."""
        ...
    
    def validate(self, result: "ExtractionResult") -> bool:
        """Validate extraction result."""
        ...