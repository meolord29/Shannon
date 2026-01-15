# abstract base classes"""Abstract base classes for common patterns."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import TypeVar, Generic, Optional, Sequence, Any
import sqlite3

from src.core.types import EntityId, PaginatedResult

T = TypeVar("T")
ID = TypeVar("ID", bound=EntityId)


# =============================================================================
# BASE MODEL
# =============================================================================

@dataclass
class BaseModel(ABC):
    """Abstract base for all domain models."""
    
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    @abstractmethod
    def id(self) -> EntityId:
        """Return the entity's unique identifier."""
        ...
    
    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        from dataclasses import asdict
        return asdict(self)
    
    @classmethod
    @abstractmethod
    def from_row(cls, row: sqlite3.Row) -> "BaseModel":
        """Create instance from database row."""
        ...


# =============================================================================
# BASE REPOSITORY
# =============================================================================

class BaseRepository(ABC, Generic[T, ID]):
    """Abstract base repository with common CRUD operations."""
    
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """Return the database table name."""
        ...
    
    @property
    @abstractmethod
    def id_column(self) -> str:
        """Return the primary key column name."""
        ...
    
    @abstractmethod
    def _row_to_entity(self, row: sqlite3.Row) -> T:
        """Convert a database row to an entity."""
        ...
    
    @abstractmethod
    def _entity_to_params(self, entity: T) -> dict[str, Any]:
        """Convert an entity to parameters for SQL."""
        ...
    
    def get_by_id(self, entity_id: ID) -> Optional[T]:
        """Retrieve an entity by ID."""
        query = f"SELECT * FROM {self.table_name} WHERE {self.id_column} = ?"
        cursor = self._conn.execute(query, (entity_id,))
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None
    
    def get_all(self) -> Sequence[T]:
        """Retrieve all entities."""
        query = f"SELECT * FROM {self.table_name}"
        cursor = self._conn.execute(query)
        return [self._row_to_entity(row) for row in cursor.fetchall()]
    
    def exists(self, entity_id: ID) -> bool:
        """Check if entity exists."""
        query = f"SELECT 1 FROM {self.table_name} WHERE {self.id_column} = ?"
        cursor = self._conn.execute(query, (entity_id,))
        return cursor.fetchone() is not None
    
    def delete(self, entity_id: ID) -> bool:
        """Delete an entity."""
        query = f"DELETE FROM {self.table_name} WHERE {self.id_column} = ?"
        cursor = self._conn.execute(query, (entity_id,))
        self._conn.commit()
        return cursor.rowcount > 0
    
    def count(self, filters: Optional[dict[str, Any]] = None) -> int:
        """Count entities with optional filters."""
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        params: list[Any] = []
        
        if filters:
            conditions = [f"{k} = ?" for k in filters.keys()]
            query += " WHERE " + " AND ".join(conditions)
            params = list(filters.values())
        
        cursor = self._conn.execute(query, params)
        return cursor.fetchone()[0]
    
    def get_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[dict[str, Any]] = None,
        order_by: Optional[str] = None,
    ) -> PaginatedResult[T]:
        """Retrieve entities with pagination."""
        offset = (page - 1) * page_size
        total = self.count(filters)
        
        query = f"SELECT * FROM {self.table_name}"
        params: list[Any] = []
        
        if filters:
            conditions = [f"{k} = ?" for k in filters.keys()]
            query += " WHERE " + " AND ".join(conditions)
            params = list(filters.values())
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        query += " LIMIT ? OFFSET ?"
        params.extend([page_size, offset])
        
        cursor = self._conn.execute(query, params)
        items = [self._row_to_entity(row) for row in cursor.fetchall()]
        
        return PaginatedResult(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size,
        )
    
    @abstractmethod
    def save(self, entity: T) -> T:
        """Save (insert or update) an entity."""
        ...


# =============================================================================
# BASE SERVICE
# =============================================================================

class BaseService(ABC):
    """Abstract base service."""
    
    def health_check(self) -> bool:
        """Default health check returns True."""
        return True
    
    @abstractmethod
    def _validate(self, data: dict[str, Any]) -> None:
        """Validate input data. Raises ValueError on invalid data."""
        ...


class BaseCRUDService(BaseService, Generic[T, ID]):
    """Abstract base for services with CRUD operations."""
    
    def __init__(self, repository: BaseRepository[T, ID]):
        self._repo = repository
    
    def get(self, entity_id: ID) -> Optional[T]:
        """Get entity by ID."""
        return self._repo.get_by_id(entity_id)
    
    def list(self, filters: Optional[dict[str, Any]] = None) -> Sequence[T]:
        """List all entities with optional filters."""
        if filters:
            return self._repo.get_paginated(page=1, page_size=1000, filters=filters).items
        return self._repo.get_all()
    
    def delete(self, entity_id: ID) -> bool:
        """Delete an entity."""
        return self._repo.delete(entity_id)
    
    @abstractmethod
    def create(self, data: dict[str, Any]) -> T:
        """Create a new entity."""
        ...
    
    @abstractmethod
    def update(self, entity_id: ID, data: dict[str, Any]) -> T:
        """Update an existing entity."""
        ...


# =============================================================================
# BASE TUI COMPONENTS
# =============================================================================

class BaseScreen(ABC):
    """Abstract base for TUI screens."""
    
    @property
    @abstractmethod
    def title(self) -> str:
        """Screen title for header."""
        ...
    
    @abstractmethod
    def compose(self) -> Any:
        """Compose the screen's widgets."""
        ...
    
    def on_mount(self) -> None:
        """Called when screen is mounted. Override for initialization."""
        pass
    
    def on_unmount(self) -> None:
        """Called when screen is unmounted. Override for cleanup."""
        pass


class BaseWidget(ABC):
    """Abstract base for TUI widgets."""
    
    @abstractmethod
    def compose(self) -> Any:
        """Compose the widget's children."""
        ...
    
    @abstractmethod
    def refresh_data(self) -> None:
        """Refresh the widget's data."""
        ...


