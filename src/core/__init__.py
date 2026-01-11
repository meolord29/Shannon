"""Core abstractions, protocols, and types for Shannon."""
from src.core.protocols import (
    Repository,
    Service,
    SearchEngine,
    GitProvider,
    Linter,
    FileSystem,
    EventPublisher,
    EventSubscriber,
)
from src.core.base import (
    BaseRepository,
    BaseService,
    BaseModel,
    BaseScreen,
    BaseWidget,
)
from src.core.types import (
    EntityId,
    UserId,
    PaperId,
    PageId,
    NoteId,
    ContentId,
    SearchResult,
    PaginatedResult,
    GitStatus,
)
from src.core.results import Result, Ok, Err

__all__ = [
    # Protocols
    "Repository",
    "Service",
    "SearchEngine",
    "GitProvider",
    "Linter",
    "FileSystem",
    "EventPublisher",
    "EventSubscriber",
    # Base classes
    "BaseRepository",
    "BaseService",
    "BaseModel",
    "BaseScreen",
    "BaseWidget",
    # Types
    "EntityId",
    "UserId",
    "PaperId",
    "PageId",
    "NoteId",
    "ContentId",
    "SearchResult",
    "PaginatedResult",
    "GitStatus",
    # Results
    "Result",
    "Ok",
    "Err",
]