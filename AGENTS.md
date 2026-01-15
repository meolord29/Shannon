# Shannon - AI Agent Context

This document provides a comprehensive overview of the Shannon project to help AI agents understand the system architecture, components, and workflows.

## Project Overview

Shannon is a collaborative knowledge management system for academic papers, built as a terminal-based application (TUI) that synchronizes with Git for version control and collaboration. The system transforms dense academic papers into interconnected, searchable notes using Obsidian-compatible markdown files.

### Key Features

- **Paper Import**: Fetch papers from OpenReview with metadata and PDF
- **LLM Extraction**: Automated note generation using local LLMs (GPT-OSS 20B)
- **Full-Text Search**: Tantivy-powered search across all content
- **Git Integration**: Branch-based workflow with automatic commits
- **Obsidian Compatible**: Markdown files work directly in Obsidian

## System Architecture

Shannon follows a layered architecture with clear separation of concerns:

1. **Core Layer** (`src/core/`): Foundation providing abstractions and contracts for the entire application.
   - Protocols (interfaces for dependency injection)
   - Base Classes (abstract implementations with shared logic)
   - Types (type aliases, TypedDicts)
   - Results (Result monad for error handling)
   - Events (event definitions and EventBus)

2. **Domain Layer** (`src/domain/`): Pure business logic and domain models with no external dependencies.
   - Models (User, Paper, Page, Note, Content, etc.)
   - Enums (status values, types)
   - Exceptions (domain-specific errors)

3. **Infrastructure Layer**:
   - Database (`src/database/`): SQLite data persistence
   - Git (`src/git/`): Version control integration
   - Search (`src/search/`): Tantivy full-text search
   - LLM (`src/llm/`): Local LLM integration

4. **Application Layer** (`src/services/`): Orchestrates domain logic and coordinates between infrastructure components.
   - PaperService: Paper import, status changes, contributors
   - PageService: Page CRUD, tree operations, linking
   - NoteService: Note CRUD, content management 
   - SearchService: Tantivy search integration
   - SyncService: Synchronizes files with database
   - ExtractionService: Orchestrates LLM extraction

5. **Presentation Layer**:
   - TUI (`src/tui/`): Terminal user interface (Textual)
   - CLI (`src/cli/`): Command-line interface (Typer)

### Protocol-Based Architecture

A key aspect of Shannon's architecture is the use of protocols (interfaces) as **guardrails** that enforce rules of interaction between components. Protocols:

- Define strict boundaries and contracts between layers
- Prevent the presentation layer (TUI/CLI) from directly manipulating domain models or infrastructure
- Ensure all interactions between the UI and backend code happen through service interfaces
- Allow for dependency injection, making components replaceable and testable

The TUI never directly accesses repositories or database operations - it must go through service protocols, which enforce business rules and maintain data integrity.

## Data Model

Shannon uses a hierarchical data model:

- **Paper**: Academic papers imported from OpenReview
  - Has metadata (title, abstract, etc.)
  - Contains multiple Pages

- **Page**: Sections within a paper
  - Hierarchical (supports parent-child relationships)
  - Has a title, category, and purpose
  - Contains multiple Notes
  - Corresponds to a markdown file

- **Note**: Content blocks within pages
  - Has content (markdown text)
  - Has a type (text, formula, code, image, etc.)
  - May contain Citations

- **Content**: Centralized searchable text
  - Used for notes, abstracts, purpose descriptions
  - Indexed in Tantivy for search

## Database Structure

Shannon uses SQLite as its local database engine, designed for:
- Full-text search via Tantivy (centralized `content` table)
- Hierarchical organization (papers → pages → notes)
- Git-based collaboration (user tracking, contributors)
- OpenReview integration (paper imports)

Key tables:
- `user`: Platform users identified by GitHub username
- `paper`: Academic papers imported from OpenReview
- `page`: Sections within a paper, supporting hierarchy
- `note`: Content blocks within pages
- `content`: Centralized searchable text content for Tantivy integration
- `citation`: Direct quotes from original papers
- `bibliography`: Referenced papers in bibliography sections
- `tag`: Categorization tags

## LLM Integration

Shannon uses local LLMs for paper extraction via OpenAI-compatible APIs.

### Supported Backends

| Backend | URL | Use Case |
|---------|-----|----------|
| LM Studio | `localhost:1234` | Default, GUI-based |
| llama.cpp | `localhost:8080` | Lightweight, CLI |
| OpenRouter | `openrouter.ai` | Cloud fallback |

### Default Model
- **Model**: GPT-OSS 20B
- **Context Window**: 8,192 tokens
- **Use Cases**: Paper extraction, summarization, note generation

### LLM Module Structure

- `client.py`: Unified OpenAI-compatible client
- `config.py`: Backend configuration and model registry
- `prompts/`: Prompt templates for extraction tasks
- `extractors/`: Specialized content extractors
- `processors/`: Text chunking, PDF parsing
- `cache/`: LLM response caching

## File Structure

Shannon organizes files using a clear directory structure:

```
src/
├── shannon/             # Main application entry points
├── core/                # Foundation layer (protocols, etc.)
├── config/              # Configuration
├── domain/              # Business domain (models)
├── database/            # Data persistence (SQLite)
├── services/            # Business logic
├── git/                 # Version control
├── llm/                 # LLM integration
├── search/              # Full-text search
├── linter/              # Note standardization
├── tui/                 # Terminal UI
├── cli/                 # Command-line interface
└── helpers/             # Utilities
```

## Technical Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.12+ | Core application |
| TUI Framework | Textual | Terminal interface |
| CLI Framework | Typer | Command-line interface |
| Database | SQLite | Local data storage |
| Search | Tantivy | Full-text search |
| Git | GitPython | Version control |
| HTTP | httpx | Async HTTP client |
| LLM | OpenAI-compatible | Paper extraction |
| PDF | PyMuPDF | PDF parsing |
| Validation | Pydantic | Data validation |
| Linting | Fixit2 | Note standardization |

## Setup Instructions

### System Requirements

- Python 3.12 or higher
- Git
- Local LLM backend (LM Studio or llama.cpp)

### Installation

1. Use the installation script:

```bash
curl -LsSf https://raw.githubusercontent.com/yourusername/shannon/main/scripts/install.sh | sh
```

2. This will:
   - Install uv (Python package manager) if not present
   - Clone the repository to ~/.shannon
   - Create a virtual environment and install the package
   - Initialize the database
   - Add shannon to your PATH

3. Start the application:

```bash
shannon
```

### Manual Installation

If you prefer to install manually:

1. Clone the repository:

```bash
git clone https://github.com/yourusername/shannon.git
cd shannon
```

2. Install dependencies using uv:

```bash
pip install uv
uv venv
uv pip install -e .
```

3. Initialize the database:

```bash
uv run shannon init
```

## Setting Up LLM Backend

Shannon requires a local LLM running for paper extraction:

### Option 1: LM Studio (Recommended)

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Download the GPT-OSS 20B model or similar
3. Start the local server on port 1234
4. No additional configuration needed (Shannon uses default settings)

### Option 2: llama.cpp

1. Install [llama.cpp](https://github.com/ggerganov/llama.cpp)
2. Download a suitable model
3. Start the server:

```bash
./llama-server -m models/gpt-oss-20b.gguf --port 8080
```

4. Update Shannon's LLM config to use llama.cpp backend

## Usage Workflow

1. **Import Paper**:
   ```bash
   shannon import <OpenReview ID>
   ```

2. **Extract with LLM**:
   ```bash
   shannon extract <paper_id>
   ```

3. **View in TUI**:
   ```bash
   shannon
   ```

4. **Search Content**:
   ```bash
   shannon search "<query>"
   ```

5. **Sync with Git**:
   ```bash
   shannon sync
   ```

## Development and Testing

### Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/shannon.git
   cd shannon
   ```

2. Install development dependencies:
   ```bash
   uv venv
   uv pip install -e ".[dev]"
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running Tests

Run all tests:
```bash
pytest
```

Run with coverage report:
```bash
pytest --cov
```

Run specific test categories:
```bash
pytest tests/unit/
pytest tests/integration/
```

### Project Structure Conventions

- **Domain Models**: Define in `src/domain/models/`
- **Repositories**: Implement in `src/database/repositories/`
- **Services**: Add application logic in `src/services/`
- **UI Screens**: Add TUI screens in `src/tui/screens/`
- **CLI Commands**: Define in `src/cli/commands.py`

### Design Principles

1. **Local-First**: All data stored locally, works offline
2. **Git-Native**: Every change is versioned
3. **Protocol-Based**: Interfaces enable testing and flexibility
4. **Event-Driven**: Decoupled components via pub/sub
5. **Result Types**: Explicit error handling without exceptions
6. **Obsidian Compatible**: Standard markdown, wiki-links

## Common Tasks

### Adding a New Extractor

1. Create a new class in `src/llm/extractors/`
2. Inherit from `BaseExtractor`
3. Implement required methods
4. Register in `ExtractionService`

### Adding a TUI Screen

1. Create a new class in `src/tui/screens/`
2. Inherit from `Screen`
3. Implement required widgets and layout
4. Register in the main app

### Adding a CLI Command

1. Add a function in `src/cli/commands.py`
2. Decorate with `@app.command()`
3. Add arguments with type annotations

### Working with the Database

1. Use the repository pattern:
   ```python
   paper_repo = PaperRepository(connection)
   paper = paper_repo.get_by_id(paper_id)
   ```

2. Never access SQLite directly from services or higher layers

### Working with LLMs

1. Use the client:
   ```python
   from shannon.llm.client import LLMClient
   
   client = LLMClient()
   response = await client.complete(messages)
   ```

2. Use existing extractors where possible
3. Handle context window limitations with chunking

## Troubleshooting

### Common Issues

1. **LLM Connection Errors**:
   - Ensure LM Studio or llama.cpp is running
   - Check the port configuration
   - Verify model is loaded

2. **Database Issues**:
   - Try reinitializing: `shannon init --force`
   - Check file permissions in data directory

3. **Git Errors**:
   - Ensure git is initialized in the vault
   - Check for conflicts that need manual resolution

### Logging

Shannon uses structured logging. To increase verbosity:

```bash
shannon --log-level debug
```

Logs are saved to `~/.shannon/logs/`

## Additional Resources

- [Core Module API](docs/core_module_summary.md)
- [Database Schema](docs/database_schema.md) 
- [Architecture Overview](docs/architecture.md)
- [Directory Structure](docs/directory_summary.md)