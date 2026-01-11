# Shannon

A collaborative knowledge management system for academic papers, built as a terminal-based application (TUI) that synchronizes with Git for version control and collaboration. Shannon transforms dense academic papers into interconnected, searchable notes using Obsidian-compatible markdown files.

![Shannon TUI](https://via.placeholder.com/800x450?text=Shannon+Terminal+UI)

## 📚 Key Features

- **Paper Import**: Fetch papers from OpenReview with metadata and PDF
- **LLM Extraction**: Automated note generation using local LLMs (GPT-OSS 20B)
- **Full-Text Search**: Tantivy-powered search across all content
- **Git Integration**: Branch-based workflow with automatic commits
- **Obsidian Compatible**: Markdown files work directly in Obsidian

## 🏛️ Architecture

Shannon follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────┐
│ Presentation Layer (TUI, CLI)                   │
├─────────────────────────────────────────────────┤
│                                                 │
│ ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│ │ Screens │  │ Widgets │  │ CLI     │          │
│ └─────────┘  └─────────┘  └─────────┘          │
│                                                 │
└───────────────────────┬─────────────────────────┘
                        │ Protocols (Guardrails)
┌───────────────────────▼─────────────────────────┐
│ Application Layer (Services)                    │
├─────────────────────────────────────────────────┤
│                                                 │
│ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│ │ Paper    │ │ Note     │ │ Extraction       │ │
│ │ Service  │ │ Service  │ │ Service          │ │
│ └──────────┘ └──────────┘ └──────────────────┘ │
│                                                 │
└───────────────────────┬─────────────────────────┘
                        │ Protocols (Guardrails)
┌───────────────────────▼─────────────────────────┐
│ Infrastructure Layer                            │
├─────────────────────────────────────────────────┤
│                                                 │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────┐ │
│ │ Database │ │ Git      │ │ Search   │ │ LLM │ │
│ └──────────┘ └──────────┘ └──────────┘ └─────┘ │
│                                                 │
└───────────────────────────────────────────────────┘
```

### Protocol-Based Design

Shannon uses **protocols as guardrails** that define and enforce the rules of interaction between components, especially between the TUI/CLI and the backend services. These protocol interfaces:

- **Establish clear boundaries** between the presentation layer and application/infrastructure layers
- **Define contracts** that components must adhere to, ensuring consistency and predictability
- **Enable dependency injection** for flexible component substitution and testing
- **Isolate concerns** so that UI components interact with backend code only through well-defined service interfaces

Example: The TUI never directly accesses repositories or the database - it always goes through service protocols that enforce business rules and maintain data integrity.

```python
# Protocol definition (guardrail)
@runtime_checkable
class PaperService(Protocol):
    def import_from_openreview(self, paper_id: str) -> Result[Paper, Error]: ...
    def get_paper(self, paper_id: PaperId) -> Result[Paper, Error]: ...
    # More methods...

# TUI component using the protocol
class PaperDetailScreen(Screen):
    def __init__(self, paper_service: PaperService):
        self.paper_service = paper_service
        
    def on_button_press(self, event: ButtonPressed) -> None:
        # TUI calls service through protocol boundary
        result = self.paper_service.get_paper(paper_id)
        # Handle the result...
```

## 🚀 Installation

### Option 1: Quick Install

```bash
curl -LsSf https://raw.githubusercontent.com/yourusername/shannon/main/scripts/install.sh | sh
```

This will:
- Install uv (Python package manager) if not present
- Clone the repository to ~/.shannon
- Create a virtual environment and install the package
- Initialize the database
- Add shannon to your PATH

### Option 2: Manual Install

```bash
# Clone the repository
git clone https://github.com/yourusername/shannon.git
cd shannon

# Install with uv (recommended)
pip install uv
uv venv
uv pip install -e .

# Initialize the database
uv run shannon init
```

## 🔧 Setup

### LLM Setup (Required for Paper Extraction)

Shannon requires a local LLM running for paper extraction:

#### Option 1: LM Studio (Recommended)

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Download the GPT-OSS 20B model or similar
3. Start the local server on port 1234

#### Option 2: llama.cpp

```bash
./llama-server -m models/gpt-oss-20b.gguf --port 8080
```

### Configuration

Default configuration is in `src/config/default.toml`. Create a custom config at `~/.shannon/config.toml`.

## 📋 Usage

### CLI Commands

```bash
# Launch TUI
shannon

# Import a paper from OpenReview
shannon import <OpenReview ID>

# Extract content with LLM
shannon extract <paper_id>

# Search across notes
shannon search "<query>"

# Sync with Git repository
shannon sync
```

### TUI Navigation

| Key | Action |
|-----|--------|
| `i` | Open inbox |
| `p` | Browse papers |
| `/` | Search |
| `g` | Git status |
| `q` | Quit |

### Terminal Flow

```
Home Screen → Inbox → Paper Detail → Editor
               ↓         ↑
           Papers    ←   ↓   →  Search
```

## 💻 Development

### Project Structure

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

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/shannon.git
cd shannon

# Create venv and install dev dependencies
uv venv
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

### Development Guidelines

- **Domain Models**: Define in `src/domain/models/`
- **Repositories**: Implement in `src/database/repositories/`
- **Services**: Add application logic in `src/services/`
- **UI Screens**: Add TUI screens in `src/tui/screens/`
- **CLI Commands**: Define in `src/cli/commands.py`

## 📐 Design Principles

1. **Local-First**: All data stored locally, works offline
2. **Git-Native**: Every change is versioned
3. **Protocol-Based**: Interfaces enable testing and flexibility
4. **Event-Driven**: Decoupled components via pub/sub
5. **Result Types**: Explicit error handling without exceptions
6. **Obsidian Compatible**: Standard markdown, wiki-links

## 📝 License

MIT

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](docs/contributing.md) for details.