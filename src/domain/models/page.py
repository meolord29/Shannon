"""Paper domain model."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Paper:
    """Represents an academic paper from OpenReview."""
    
    paper_id: str                           # OpenReview ID
    title: str
    slug: str
    openreview_url: str
    abstract_id: Optional[str] = None
    pdf_path: Optional[str] = None
    status: str = "inbox"
    directory: str = "inbox"
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def from_openreview(cls, openreview_id: str, data: dict) -> "Paper":
        """Create Paper from OpenReview API response."""
        from src.helpers.slug import generate_slug
        
        title = data.get("title", "Untitled")
        return cls(
            paper_id=openreview_id,
            title=title,
            slug=generate_slug(title),
            openreview_url=f"https://openreview.net/forum?id={openreview_id}",
        )


@dataclass
class PaperContributor:
    """Represents a user's contribution role on a paper."""
    
    paper_id: str
    user_id: str
    role: str  # 'lead', 'contributor', 'reviewer'