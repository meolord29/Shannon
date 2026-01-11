# Shannon System Architecture

## Executive Summary

Shannon is a collaborative knowledge management system for academic papers, built as a terminal-based application (TUI) that synchronizes with Git for version control and collaboration. The system transforms dense academic papers into interconnected, searchable notes using Obsidian-compatible markdown files.

### Key Features

- **Paper Import**: Fetch papers from OpenReview with metadata and PDF
- **LLM Extraction**: Automated note generation using local LLMs (GPT-OSS 20B)
- **Full-Text Search**: Tantivy-powered search across all content
- **Git Integration**: Branch-based workflow with automatic commits
- **Obsidian Compatible**: Markdown files work directly in Obsidian

---

## System Context

```mermaid
flowchart TB
    subgraph External["External Systems"]
        OR[("OpenReview\nAPI")]
        GH[("GitHub\nRepository")]
        OB[("Obsidian\nClient")]
    end
    
    subgraph Shannon["Shannon Application"]
        TUI["TUI Interface\n(Textual)"]
        CLI["CLI Interface\n(Typer)"]
        CORE["Core Application"]
    end
    
    subgraph Storage["Local Storage"]
        DB[("SQLite\nDatabase")]
        IDX[("Tantivy\nSearch Index")]
        FS[("Vault Files\nMarkdown")]
    end
    
    subgraph LLM["Local LLM"]
        LMS["LM Studio\nlocalhost:1234"]
        LLC["llama.cpp\nlocalhost:8080"]
    end
    
    OR -->|"Paper metadata\nPDF downloads"| Shannon
    Shannon <-->|"Push/Pull\nBranch management"| GH
    OB -->|"Reads vault\nfiles directly"| FS
    
    TUI --> CORE
    CLI --> CORE
    
    CORE <--> DB
    CORE <--> IDX
    CORE <--> FS
    CORE <-->|"OpenAI-compatible API"| LLM
```

---

## High-Level Architecture

Shannon follows a layered architecture with clear separation of concerns:

```mermaid
flowchart TB
    subgraph Presentation["Presentation Layer"]
        direction LR
        Screens["Screens\n(Textual)"]
        Widgets["Widgets\n(Textual)"]
        Components["Components\n(Textual)"]
        CLICmds["CLI Commands\n(Typer)"]
    end
    
    subgraph Application["Application Layer"]
        direction LR
        PaperSvc["Paper\nService"]
        PageSvc["Page\nService"]
        NoteSvc["Note\nService"]
        SearchSvc["Search\nService"]
        SyncSvc["Sync\nService"]
        ExtractionSvc["Extraction\nService"]
    end
    
    subgraph Domain["Domain Layer"]
        direction LR
        Models["Models"]
        Enums["Enums"]
        Exceptions["Exceptions"]
        Events["Events"]
    end
    
    subgraph Infrastructure["Infrastructure Layer"]
        direction LR
        Repos["Repositories\n(SQLite)"]
        GitMgr["Git\nManager"]
        Search["Search\n(Tantivy)"]
        LLMClient["LLM\nClient"]
    end
    
    subgraph Core["Core Layer"]
        direction LR
        Protocols["Protocols\n(Interfaces)"]
        Base["Base\nClasses"]
        Types["Types\n(TypeHints)"]
        Results["Results\n(Ok/Err)"]
    end
    
    Presentation --> Application
    Application --> Domain
    Application --> Infrastructure
    Infrastructure --> Core
    Domain --> Core
```

---

## Layer Descriptions

### Core Layer (`src/core/`)

The foundation providing abstractions and contracts for the entire application.

| Component | File | Purpose |
|-----------|------|---------|
| Protocols | `protocols.py` | Interface definitions for dependency injection |
| Base Classes | `base.py` | Abstract implementations with shared logic |
| Types | `types.py` | Type aliases, TypedDicts, NewTypes |
| Results | `results.py` | Result monad (Ok/Err) for error handling |
| Events | `events.py` | Event definitions and EventBus |

> **See also**: [Core Module Summary](core_module_summary.md) for detailed API documentation.

### Domain Layer (`src/domain/`)

Pure business logic and domain models with no external dependencies.

```mermaid
classDiagram
    class User {
        +user_id: UserId
        +email: str
        +is_active: bool
    }
    
    class Paper {
        +paper_id: PaperId
        +title: str
        +slug: str
        +status: PaperStatus
        +directory: Directory
    }
    
    class Page {
        +page_id: PageId
        +paper_id: PaperId
        +title: str
        +category: PageCategory
    }
    
    class Note {
        +note_id: NoteId
        +page_id: PageId
        +content_id: ContentId
        +note_type: NoteType
    }
    
    class Content {
        +content_id: ContentId
        +body: str
        +body_plain: str
        +content_type: ContentType
    }
    
    User "1" --> "*" Paper : creates
    Paper "1" --> "*" Page : contains
    Page "1" --> "*" Note : contains
    Note "1" --> "1" Content : has
    Paper "1" --> "0..1" Content : abstract
```

### Infrastructure Layer

External system integrations and data persistence.

```mermaid
flowchart TB
    subgraph Database["Database Module"]
        Conn["Connection\n(SQLite)"]
        Repos["Repositories"]
        Migrations["Migrations"]
    end
    
    subgraph Git["Git Module"]
        GitManager["GitManager\n(GitPython)"]
        BranchOps["Branch Ops"]
        CommitOps["Commit Ops"]
    end
    
    subgraph Search["Search Module"]
        Indexer["Indexer\n(Tantivy)"]
        Query["Query Builder"]
    end
    
    subgraph LLM["LLM Module"]
        Client["LLMClient"]
        Extractors["Extractors"]
        Processors["Processors"]
    end
```

> **See also**: [Database Schema](database_schema.md) for complete table definitions.

### Application Layer (`src/services/`)

Orchestrates domain logic and coordinates between infrastructure components.

```mermaid
flowchart LR
    subgraph Services
        PaperSvc["PaperService"]
        PageSvc["PageService"]
        NoteSvc["NoteService"]
        SearchSvc["SearchService"]
        SyncSvc["SyncService"]
        ExtractionSvc["ExtractionService"]
    end
    
    ExtractionSvc --> PaperSvc
    ExtractionSvc --> PageSvc
    ExtractionSvc --> NoteSvc
    SyncSvc --> PaperSvc
    SyncSvc --> PageSvc
    SyncSvc --> NoteSvc
    NoteSvc --> SearchSvc
```

### Presentation Layer (`src/tui/`, `src/cli/`)

User interface components.

```mermaid
stateDiagram-v2
    [*] --> Home
    
    Home --> Inbox: i
    Home --> Papers: p
    Home --> Search: /
    Home --> GitStatus: g
    
    Inbox --> PaperDetail: Select
    Papers --> PaperDetail: Select
    Search --> PaperDetail: Select
    
    PaperDetail --> Editor: Edit
    Editor --> PaperDetail: Save
```

> **See also**: [Directory Summary](directory_summary.md) for complete file structure.

---

## Data Flow Diagrams

### Paper Import Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant TUI
    participant PaperService
    participant OpenReviewService
    participant ContentRepo
    participant PaperRepo
    participant SearchService
    participant GitManager
    
    User->>TUI: Import paper (OpenReview ID)
    TUI->>PaperService: import_from_openreview(id)
    PaperService->>OpenReviewService: fetch_paper(id)
    OpenReviewService-->>PaperService: PaperData
    PaperService->>OpenReviewService: download_pdf(id, path)
    PaperService->>ContentRepo: save(abstract)
    PaperService->>PaperRepo: save(paper)
    PaperService->>SearchService: index_content(abstract_id)
    PaperService->>GitManager: commit("Add paper")
    PaperService-->>TUI: Result[Paper]
```

### LLM Extraction Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant TUI
    participant ExtractionSvc
    participant PDFParser
    participant LLMClient
    participant Backend["LM Studio"]
    participant PageSvc
    participant NoteSvc
    
    User->>TUI: Extract paper
    TUI->>ExtractionSvc: extract_paper(input)
    ExtractionSvc->>ExtractionSvc: health_check()
    ExtractionSvc->>PDFParser: parse(pdf_path)
    PDFParser-->>ExtractionSvc: ParsedPDF
    
    ExtractionSvc->>LLMClient: complete(messages)
    LLMClient->>Backend: POST /v1/chat/completions
    Note over Backend: gpt-oss-20b
    Backend-->>LLMClient: Response
    LLMClient-->>ExtractionSvc: LLMResponse
    
    ExtractionSvc->>PageSvc: create_page(data)
    ExtractionSvc->>NoteSvc: create_note(data)
    ExtractionSvc-->>TUI: ExtractedPaper
```

### Git Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant TUI
    participant GitManager
    participant GitHub
    
    User->>TUI: Start editing
    TUI->>GitManager: create_branch("paper/slug")
    
    loop Editing
        User->>TUI: Edit notes
        TUI->>GitManager: commit("WIP")
    end
    
    User->>TUI: Publish
    TUI->>GitManager: rebase_onto("main")
    TUI->>GitManager: checkout("main")
    TUI->>GitManager: merge(ff_only=True)
    TUI->>GitManager: push("origin")
    GitManager->>GitHub: Push
```

---

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

```mermaid
flowchart LR
    subgraph Client["LLMClient"]
        Config["LLMConfig"]
        Cache["ResponseCache"]
    end
    
    subgraph Backends["Backends"]
        LMS["LM Studio\n:1234"]
        LLC["llama.cpp\n:8080"]
        OR["OpenRouter"]
    end
    
    Client -->|"OpenAI API"| LMS
    Client -->|"OpenAI API"| LLC
    Client -->|"OpenAI API"| OR
```

---

## Event System

Components communicate through a publish/subscribe event bus.

```mermaid
flowchart TB
    subgraph Publishers
        PaperSvc["PaperService"]
        NoteSvc["NoteService"]
        ExtractionSvc["ExtractionService"]
        GitMgr["GitManager"]
    end
    
    subgraph EventBus["EventBus (Singleton)"]
        Publish["publish(event)"]
        Subscribe["subscribe(type, handler)"]
    end
    
    subgraph Subscribers
        SearchIndexer["Search Indexer"]
        UINotifier["UI Notifier"]
        StatsUpdater["Stats Updater"]
    end
    
    Publishers --> EventBus
    EventBus --> Subscribers
```

### Event Types

| Event | Trigger | Subscribers |
|-------|---------|-------------|
| `PaperCreatedEvent` | Paper imported | Search indexer, UI |
| `NoteUpdatedEvent` | Note edited | Search indexer |
| `ExtractionCompletedEvent` | LLM extraction done | UI notifier |
| `GitCommitEvent` | Changes committed | Stats updater |

---

## Deployment

### Installation

```bash
curl -LsSf https://raw.githubusercontent.com/user/shannon/main/scripts/install.sh | sh
```

### Local Architecture

```mermaid
flowchart TB
    subgraph User["User's Machine"]
        subgraph App["Shannon"]
            Binary["shannon CLI"]
            TUI["TUI"]
        end
        
        subgraph Data["Data"]
            DB[("shannon.db")]
            Index[("search_index/")]
            Vault["Vault/"]
        end
        
        subgraph LLM["LLM Backend"]
            LMStudio["LM Studio"]
        end
    end
    
    subgraph Remote
        GitHub[("GitHub")]
        OpenReview[("OpenReview")]
    end
    
    App <--> Data
    App <--> LLM
    Vault <--> GitHub
    App --> OpenReview
```

---

## Technology Stack

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

---

## Design Principles

1. **Local-First**: All data stored locally, works offline
2. **Git-Native**: Every change is versioned
3. **Protocol-Based**: Interfaces enable testing and flexibility
4. **Event-Driven**: Decoupled components via pub/sub
5. **Result Types**: Explicit error handling without exceptions
6. **Obsidian Compatible**: Standard markdown, wiki-links

---

## Related Documentation

- [Core Module Summary](core_module_summary.md) - Detailed core module API
- [Database Schema](database_schema.md) - Complete database documentation
- [Directory Summary](directory_summary.md) - Project file structure
