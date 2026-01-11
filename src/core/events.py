"""Event system for decoupled communication."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Any
from collections import defaultdict


# =============================================================================
# BASE EVENT
# =============================================================================

@dataclass(frozen=True)
class BaseEvent:
    """Base class for all events."""
    
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    
    @property
    def event_type(self) -> str:
        return self.__class__.__name__


# =============================================================================
# DOMAIN EVENTS
# =============================================================================

@dataclass(frozen=True)
class PaperCreatedEvent(BaseEvent):
    """Fired when a new paper is created."""
    paper_id: str
    title: str
    created_by: str


@dataclass(frozen=True)
class PaperStatusChangedEvent(BaseEvent):
    """Fired when a paper's status changes."""
    paper_id: str
    old_status: str
    new_status: str


@dataclass(frozen=True)
class PageCreatedEvent(BaseEvent):
    """Fired when a new page is created."""
    page_id: str
    paper_id: str
    title: str


@dataclass(frozen=True)
class NoteCreatedEvent(BaseEvent):
    """Fired when a new note is created."""
    note_id: str
    page_id: str
    content_id: str


@dataclass(frozen=True)
class NoteUpdatedEvent(BaseEvent):
    """Fired when a note is updated."""
    note_id: str
    content_id: str


@dataclass(frozen=True)
class ContentIndexedEvent(BaseEvent):
    """Fired when content is indexed in Tantivy."""
    content_id: str


@dataclass(frozen=True)
class GitCommitEvent(BaseEvent):
    """Fired when changes are committed."""
    commit_hash: str
    message: str
    files_changed: int


@dataclass(frozen=True)
class GitBranchCreatedEvent(BaseEvent):
    """Fired when a new branch is created."""
    branch_name: str
    base_branch: str


@dataclass(frozen=True)
class SyncCompletedEvent(BaseEvent):
    """Fired when file/DB sync completes."""
    files_processed: int
    errors: int


# =============================================================================
# EVENT BUS
# =============================================================================

EventHandler = Callable[[BaseEvent], None]


class EventBus:
    """Simple synchronous event bus for publishing and subscribing to events."""
    
    _instance: "EventBus | None" = None
    
    def __new__(cls) -> "EventBus":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers = defaultdict(list)
        return cls._instance
    
    def __init__(self) -> None:
        # Only initialize once (singleton)
        if not hasattr(self, "_subscribers"):
            self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)
    
    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe a handler to an event type."""
        self._subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Unsubscribe a handler from an event type."""
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
    
    def publish(self, event: BaseEvent) -> None:
        """Publish an event to all subscribers."""
        event_type = event.event_type
        for handler in self._subscribers[event_type]:
            try:
                handler(event)
            except Exception as e:
                # Log but don't crash on handler errors
                print(f"Event handler error for {event_type}: {e}")
        
        # Also notify wildcard subscribers
        for handler in self._subscribers["*"]:
            try:
                handler(event)
            except Exception as e:
                print(f"Wildcard handler error: {e}")
    
    def clear(self) -> None:
        """Clear all subscribers. Useful for testing."""
        self._subscribers.clear()


def get_event_bus() -> EventBus:
    """Get the singleton event bus instance."""
    return EventBus()