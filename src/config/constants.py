"""Application-wide constants."""

# Paper statuses
class PaperStatus:
    INBOX = "inbox"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"

# Note types
class NoteType:
    TEXT = "text"
    FORMULA = "formula"
    CODE = "code"
    IMAGE = "image"
    CALLOUT = "callout"

# Page categories
class PageCategory:
    INTRODUCTION = "introduction"
    METHODOLOGY = "methodology"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    ALGORITHM = "algorithm"
    CONCEPT = "concept"

# User roles
class UserRole:
    ADMIN = "admin"
    WRITER = "writer"
    REVIEWER = "reviewer"

# Contributor roles
class ContributorRole:
    LEAD = "lead"
    CONTRIBUTOR = "contributor"
    REVIEWER = "reviewer"

# Content types (for Tantivy)
class ContentType:
    NOTE = "note"
    ABSTRACT = "abstract"
    PURPOSE = "purpose"
    CITATION = "citation"