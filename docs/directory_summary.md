# Shannon Directory Summary

## Project Root

```
shannon/
├── .github/              # GitHub Actions workflows
├── scripts/              # Installation and setup scripts
├── src/                  # Main application source
├── data/                 # Local data storage (gitignored)
├── tests/                # Test suite
├── docs/                 # Documentation
├── .gitignore
├── .python-version       # Python version for uv
├── pyproject.toml        # Project configuration
├── uv.lock               # Dependency lock file
└── README.md
```

---

## Source Directory Structure

```
src/
├── __init__.py
├── shannon/
│   ├── __init__.py
│   ├── __main__.py           # python -m shannon entry point
│   └── app.py                # Main application bootstrap
│
├── core/                     # Foundation layer
│   ├── __init__.py
│   ├── protocols.py          # Interface definitions
│   ├── base.py               # Abstract base classes
│   ├── types.py              # Type aliases and TypedDicts
│   ├── results.py            # Result monad (Ok/Err)
│   └── events.py             # Event system
│
├── config/                   # Configuration
│   ├── __init__.py
│   ├── settings.py           # Pydantic settings
│   ├── constants.py          # App-wide constants
│   └── default.toml          # Default configuration
│
├── domain/                   # Business domain
│   ├── __init__.py
│   ├── models/               # Domain models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── paper.py
│   │   ├── page.py
│   │   ├── note.py
│   │   ├── content.py
│   │   ├── citation.py
│   │   ├── bibliography.py
│   │   └── tag.py
│   ├── enums.py              # Status, types enums
│   └── exceptions.py         # Domain exceptions
│
├── database/                 # Data persistence
│   ├── __init__.py
│   ├── connection.py         # SQLite connection
│   ├── migrations/
│   │   ├── __init__.py
│   │   ├── runner.py         # Migration runner
│   │   └── versions/
│   │       ├── __init__.py
│   │       └── 001_initial_schema.py
│   └── repositories/
│       ├── __init__.py
│       ├── base.py           # Base repository
│       ├── user_repo.py
│       ├── paper_repo.py
│       ├── page_repo.py
│       ├── note_repo.py
│       ├── content_repo.py
│       └── tag_repo.py
│
├── services/                 # Business logic
│   ├── __init__.py
│   ├── paper_service.py
│   ├── page_service.py
│   ├── note_service.py
│   ├── search_service.py
│   ├── sync_service.py
│   ├── extraction_service.py # LLM extraction orchestration
│   └── openreview_service.py
│
├── git/                      # Version control
│   ├── __init__.py
│   ├── manager.py            # GitPython wrapper
│   ├── branch.py             # Branch operations
│   ├── commit.py             # Commit operations
│   └── sync.py               # Push/pull/rebase
│
├── llm/                      # LLM integration
│   ├── __init__.py
│   ├── client.py             # OpenAI-compatible client
│   ├── config.py             # Model registry & config
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── templates.py      # Base template system
│   │   ├── extraction.py     # Extraction prompts
│   │   ├── summerization.py  # Summary prompts
│   │   └── structuring.py    # Note structure prompts
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── base.py           # Base extractor
│   │   ├── paper.py          # Full paper extraction
│   │   ├── section.py        # Section extraction
│   │   ├── formula.py        # Formula extraction
│   │   ├── algorithm.py      # Algorithm extraction
│   │   └── citation.py       # Citation extraction
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── chunker.py        # Text chunking
│   │   ├── pdf_parser.py     # PDF to text
│   │   └── context.py        # Context management
│   └── cache/
│       ├── __init__.py
│       └── response_cache.py # LLM response caching
│
├── search/                   # Full-text search
│   ├── __init__.py
│   ├── indexer.py            # Tantivy indexing
│   ├── query.py              # Query builder
│   └── schema.py             # Index schema
│
├── linter/                   # Note standardization
│   ├── __init__.py
│   ├── fixit_runner.py       # Fixit2 integration
│   └── rules/
│       ├── __init__.py
│       └── note_rules.py     # Custom lint rules
│
├── tui/                      # Terminal UI
│   ├── __init__.py
│   ├── app.py                # Textual App class
│   ├── styles/
│   │   ├── __init__.py
│   │   └── theme.tcss        # Textual CSS
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── base.py           # Base screen
│   │   ├── home.py           # Dashboard
│   │   ├── inbox.py          # Inbox management
│   │   ├── paper_list.py     # Paper browser
│   │   ├── paper_detail.py   # Paper view
│   │   ├── editor.py         # Note editor
│   │   ├── search.py         # Search interface
│   │   └── git_status.py     # Git operations
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── base.py           # Base widget
│   │   ├── paper_card.py
│   │   ├── page_tree.py
│   │   ├── note_block.py
│   │   ├── search_bar.py
│   │   ├── status.py
│   │   └── command.py
│   └── components/
│       ├── __init__.py
│       ├── modal.py
│       ├── toast.py
│       └── confirm.py
│
├── cli/                      # Command-line interface
│   ├── __init__.py
│   └── commands.py           # Typer commands
│
└── helpers/                  # Utilities
    ├── __init__.py
    ├── slug.py               # Slug generation
    ├── markdown.py           # Markdown utilities
    ├── checksum.py           # Content hashing
    ├── filesystem.py         # File operations
    └── validators.py         # Input validation
```

---

## Directory Descriptions

### `core/` - Foundation Layer

| File | Purpose |
|------|---------|
| `protocols.py` | Protocol classes defining interfaces for DI and testing |
| `base.py` | Abstract base classes with shared implementation |
| `types.py` | Type aliases, NewTypes, TypedDicts for type safety |
| `results.py` | Result monad (Ok/Err) for explicit error handling |
| `events.py` | Event definitions and EventBus for pub/sub |

> **See also**: [Core Module Summary](core_module_summary.md) for detailed API documentation.

### `config/` - Configuration

| File | Purpose |
|------|---------|
| `settings.py` | Pydantic Settings with env/file loading |
| `constants.py` | Enums and constants (PaperStatus, NoteType, etc.) |
| `default.toml` | Default configuration values |

### `domain/` - Business Domain

| Directory/File | Purpose |
|----------------|---------|
| `models/` | Dataclass domain models (User, Paper, Page, Note, etc.) |
| `enums.py` | Domain enumerations |
| `exceptions.py` | Custom domain exceptions |

### `database/` - Data Persistence

| Directory/File | Purpose |
|----------------|---------|
| `connection.py` | SQLite connection management |
| `migrations/` | Schema migrations with version tracking |
| `repositories/` | Data access layer implementing Repository protocol |

> **See also**: [Database Schema](database_schema.md) for complete table definitions.

### `services/` - Business Logic

| File | Purpose |
|------|---------|
| `paper_service.py` | Paper import, status changes, contributors |
| `page_service.py` | Page CRUD, tree operations, linking |
| `note_service.py` | Note CRUD, content management |
| `search_service.py` | Tantivy integration, search queries |
| `sync_service.py` | File ↔ database synchronization |
| `extraction_service.py` | LLM extraction orchestration |
| `openreview_service.py` | OpenReview API client |

### `git/` - Version Control

| File | Purpose |
|------|---------|
| `manager.py` | Main GitPython wrapper |
| `branch.py` | Branch create, checkout, delete |
| `commit.py` | Stage, commit operations |
| `sync.py` | Push, pull, rebase with remote |

### `llm/` - LLM Integration

| Directory/File | Purpose |
|----------------|---------|
| `client.py` | Unified OpenAI-compatible client |
| `config.py` | Backend config, model registry |
| `prompts/` | Prompt templates for extraction tasks |
| `extractors/` | Specialized content extractors |
| `processors/` | Text chunking, PDF parsing |
| `cache/` | LLM response caching |

### `search/` - Full-Text Search

| File | Purpose |
|------|---------|
| `indexer.py` | Tantivy index management |
| `query.py` | Search query building |
| `schema.py` | Index schema definition |

### `linter/` - Note Standardization

| File | Purpose |
|------|---------|
| `fixit_runner.py` | Fixit2 integration |
| `rules/note_rules.py` | Custom linting rules for notes |

### `tui/` - Terminal Interface

| Directory/File | Purpose |
|----------------|---------|
| `app.py` | Main Textual application |
| `styles/` | Textual CSS theming |
| `screens/` | Full-screen views |
| `widgets/` | Reusable UI components |
| `components/` | Modals, toasts, dialogs |

### `cli/` - Command-Line Interface

| File | Purpose |
|------|---------|
| `commands.py` | Typer CLI commands (run, init, search, sync, extract) |

### `helpers/` - Utilities

| File | Purpose |
|------|---------|
| `slug.py` | Generate filesystem-safe slugs |
| `markdown.py` | Parse, strip, transform markdown |
| `checksum.py` | Content hashing for change detection |
| `filesystem.py` | File/directory operations |
| `validators.py` | Input validation utilities |

---

## Data Directory

```
data/
├── .gitkeep
├── shannon.db          # SQLite database (gitignored)
├── search_index/       # Tantivy index (gitignored)
└── llm_cache.db        # LLM response cache (gitignored)
```

---

## Test Directory

```
tests/
├── __init__.py
├── conftest.py         # Pytest fixtures
├── unit/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_repositories.py
│   ├── test_services.py
│   └── test_heklpers.py
├── integration/
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_git_operations.py
│   └── test_search.py
└── fixtures/
    ├── sample_paper.md
    └── sample_notes/
```

---

## Scripts Directory

```
scripts/
├── install.sh          # curl-able installation script
└── dev-setup.sh        # Developer environment setup
```

---

## Architecture Mapping

| Directory | Architecture Layer |
|-----------|-------------------|
| `core/` | Core Layer |
| `domain/` | Domain Layer |
| `database/` | Infrastructure Layer |
| `git/` | Infrastructure Layer |
| `search/` | Infrastructure Layer |
| `llm/` | Infrastructure Layer |
| `services/` | Application Layer |
| `tui/` | Presentation Layer |
| `cli/` | Presentation Layer |
| `config/` | Cross-Cutting |
| `helpers/` | Cross-Cutting |
| `linter/` | Cross-Cutting |

> **See also**: [Architecture](architecture.md) for layer descriptions and diagrams.

---

## Key Entry Points

| Entry | File | Command |
|-------|------|---------|
| CLI | `shannon/app.py` | `shannon` |
| Module | `shannon/__main__.py` | `python -m shannon` |
| TUI | `tui/app.py` | `shannon run` |

---

## File Counts by Module

| Module | Files | Description |
|--------|-------|-------------|
| `core/` | 5 | Foundation abstractions |
| `config/` | 3 | Configuration management |
| `domain/` | 10 | Business models |
| `database/` | 10 | Data persistence |
| `services/` | 7 | Business logic |
| `git/` | 4 | Version control |
| `llm/` | 14 | LLM integration |
| `search/` | 3 | Full-text search |
| `linter/` | 3 | Note standardization |
| `tui/` | 17 | Terminal interface |
| `cli/` | 2 | Command-line |
| `helpers/` | 5 | Utilities |
| **Total** | **~83** | |

---

## Related Documentation

- [Architecture](architecture.md) - System architecture overview
- [Core Module Summary](core_module_summary.md) - Core module API
- [Database Schema](database_schema.md) - Database table definitions
