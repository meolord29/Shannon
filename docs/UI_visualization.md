# Shannon TUI Design Guide

A minimal, focused terminal interface inspired by Apple's design philosophy: clarity through simplicity, purposeful interactions, and delightful details.

---

## Design Philosophy

### Core Principles

1. **Reduce to the Essence** — Show only what matters. Every element earns its place.
2. **Content is King** — The interface disappears; your papers shine.
3. **Obvious by Design** — No manual needed. Actions reveal themselves naturally.
4. **Fluid Transitions** — Screens flow into each other with spatial consistency.
5. **Quiet Confidence** — Subtle feedback, never intrusive.

### The Shannon Way

```
Less chrome, more content.
Less clicking, more reading.
Less thinking, more doing.
```

---

## Color System

A restrained palette that lets content breathe:

```
┌─────────────────────────────────────────────────────────┐
│  BACKGROUND                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  Base        #1a1b26    Deep ink, easy on eyes          │
│  Surface     #24283b    Elevated cards                  │
│  Hover       #292e42    Subtle interaction              │
│                                                         │
│  TEXT                                                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  Primary     #c0caf5    Main content                    │
│  Secondary   #565f89    Supporting text                 │
│  Muted       #3b4261    Disabled, hints                 │
│                                                         │
│  ACCENT                                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  Blue        #7aa2f7    Primary actions, links          │
│  Green       #9ece6a    Success, complete               │
│  Amber       #e0af68    Warnings, in-progress           │
│  Red         #f7768e    Errors, destructive             │
└─────────────────────────────────────────────────────────┘
```

---

## Layout Architecture

### The Golden Layout

Shannon uses a single, consistent layout across all screens:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Shannon                                              ⌘K Search     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                                                                     │
│                                                                     │
│                         CONTENT AREA                                │
│                                                                     │
│                    (Full-width, breathing room)                     │
│                                                                     │
│                                                                     │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  ← Back                                                    ? Help   │
└─────────────────────────────────────────────────────────────────────┘
```

**Key decisions:**
- No persistent sidebar — content gets full width
- Minimal header — just branding and universal search
- Contextual footer — shows relevant actions only
- Generous whitespace — content breathes

---

## Screen Designs

### 1. Home — Your Dashboard

The home screen shows what matters: recent work and quick actions.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Shannon                                              ⌘K Search     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│     Good evening, researcher.                                       │
│                                                                     │
│     ─────────────────────────────────────────────────────────────   │
│                                                                     │
│     CONTINUE READING                                                │
│                                                                     │
│     ┌─────────────────────────────────────────────────────────┐     │
│     │  Attention Is All You Need                              │     │
│     │  Last edited 2 hours ago · 3.2 Attention Mechanism      │     │
│     └─────────────────────────────────────────────────────────┘     │
│                                                                     │
│     RECENT PAPERS                                                   │
│                                                                     │
│       Vision Transformer                           yesterday        │
│       BERT: Pre-training Deep Bidirectional        3 days ago       │
│       Diffusion Models Beat GANs                   last week        │
│                                                                     │
│     ─────────────────────────────────────────────────────────────   │
│                                                                     │
│     24 papers · 156 pages · 532 notes                               │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  P Papers   I Import   G Git                               ? Help   │
└─────────────────────────────────────────────────────────────────────┘
```

**Simplifications:**
- Removed separate "Quick Actions" and "Statistics" boxes
- Single "Continue Reading" card for immediate context
- Recent papers as simple list, not cards
- Stats as quiet footer text

---

### 2. Papers — Your Library

A clean list that scales. No visual clutter.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Shannon                                              ⌘K Search     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│     Papers                                          Filter ▾        │
│                                                                     │
│     ─────────────────────────────────────────────────────────────   │
│                                                                     │
│     ● Attention Is All You Need                                     │
│       Vaswani et al. · NeurIPS 2017 · Extracted                     │
│                                                                     │
│       Vision Transformer: An Image is Worth 16x16 Words             │
│       Dosovitskiy et al. · ICLR 2021 · Extracted                    │
│                                                                     │
│       BERT: Pre-training of Deep Bidirectional Transformers         │
│       Devlin et al. · NAACL 2019 · In Progress                      │
│                                                                     │
│       Diffusion Models Beat GANs on Image Synthesis                 │
│       Dhariwal & Nichol · NeurIPS 2021 · Inbox                      │
│                                                                     │
│       GPT-4 Technical Report                                        │
│       OpenAI · 2023 · Inbox                                         │
│                                                                     │
│                                                                     │
│                                                         Page 1 of 3 │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  ← Home   ↑↓ Navigate   ⏎ Open   I Import                  ? Help   │
└─────────────────────────────────────────────────────────────────────┘
```

**Simplifications:**
- Removed search bar (use ⌘K universal search)
- Removed sort dropdown (smart default: recent first)
- Single-line metadata per paper
- Status shown inline, not as badge
- Bullet indicates selection, not checkbox

---

### 3. Paper — Deep Dive

The paper view: metadata at a glance, structure on the side.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Shannon                                              ⌘K Search     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│     Attention Is All You Need                                       │
│     Vaswani, Shazeer, Parmar et al. · NeurIPS 2017                  │
│                                                                     │
│     ─────────────────────────────────────────────────────────────   │
│                                                                     │
│     SECTIONS                                                        │
│                                                                     │
│       1. Introduction                                               │
│          1.1 Background                                             │
│          1.2 Motivation                                             │
│       2. Related Work                                               │
│     ● 3. Model Architecture                                         │
│          3.1 Encoder and Decoder                                    │
│          3.2 Attention Mechanism                                    │
│          3.3 Position-wise Feed-Forward Networks                    │
│       4. Experiments                                                │
│       5. Conclusion                                                 │
│                                                                     │
│     ─────────────────────────────────────────────────────────────   │
│                                                                     │
│     12 pages · 48 notes · Last edited 2h ago                        │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  ← Papers   ↑↓ Navigate   ⏎ Open   E Extract   O PDF       ? Help   │
└─────────────────────────────────────────────────────────────────────┘
```

**Simplifications:**
- Removed separate metadata and actions boxes
- Metadata flows naturally under title
- Tree structure is the focus
- Actions in footer, not scattered buttons
- Stats as quiet footer text

---

### 4. Page — Reading & Editing

Where the real work happens. Content-first design.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Shannon                                              ⌘K Search     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│     3.2 Attention Mechanism                                         │
│     Attention Is All You Need                                       │
│                                                                     │
│     ─────────────────────────────────────────────────────────────   │
│                                                                     │
│     The attention mechanism computes a weighted sum of values       │
│     based on a query and keys. This allows the model to focus       │
│     on relevant parts of the input when producing each output.      │
│                                                                     │
│     ## Multi-Head Attention                                         │
│                                                                     │
│     Instead of performing a single attention function, the model    │
│     linearly projects queries, keys and values h times with         │
│     different learned projections.                                  │
│                                                                     │
│     ┌───────────────────────────────────────────────────────────┐   │
│     │                    QKᵀ                                    │   │
│     │  Attention(Q,K,V) = softmax(────)V                        │   │
│     │                     √dₖ                                   │   │
│     └───────────────────────────────────────────────────────────┘   │
│                                                                     │
│     > "Attention allows modeling dependencies without regard to     │
│     > their distance in the input or output sequences."             │
│     > — Page 2                                                      │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  ← Paper   E Edit   A Add Note   N Next Section            ? Help   │
└─────────────────────────────────────────────────────────────────────┘
```

**Simplifications:**
- Removed sidebar tree (navigate via Paper view or N/P keys)
- Full-width content for comfortable reading
- Formulas and citations styled inline
- Breadcrumb in subtitle, not separate element

---

### 5. Search — Find Anything

Universal search, accessible from anywhere with ⌘K.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Shannon                                              ⌘K Search     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│     ┌─────────────────────────────────────────────────────────┐     │
│     │  attention mechanism                                    │     │
│     └─────────────────────────────────────────────────────────┘     │
│                                                                     │
│     15 results                                                      │
│                                                                     │
│     ─────────────────────────────────────────────────────────────   │
│                                                                     │
│     ● Attention Mechanism                                           │
│       Transformer Networks → 3.2 Attention Mechanism                │
│       "...the attention mechanism computes a weighted sum..."       │
│                                                                     │
│       Self-Attention Explained                                      │
│       Transformer Networks → Notes                                  │
│       "...unlike recurrent models, the attention mechanism..."      │
│                                                                     │
│       Attention Calculation                                         │
│       Vision Transformer → Methods                                  │
│       "Attention(Q,K,V) = softmax(QKᵀ/√dₖ)V"                        │
│                                                                     │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  Esc Close   ↑↓ Navigate   ⏎ Open                          ? Help   │
└─────────────────────────────────────────────────────────────────────┘
```

**Simplifications:**
- Removed scope and sort dropdowns (search everything, rank by relevance)
- Clean result format: title, path, snippet
- No type badges (context is clear from path)
- Escape to dismiss, like Spotlight

---

### 6. Import — Add Papers

Streamlined import flow. Paste ID, see preview, import.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Shannon                                              ⌘K Search     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│     Import Paper                                                    │
│                                                                     │
│     ┌─────────────────────────────────────────────────────────┐     │
│     │  NIPS-2017-3f5ee243                                     │     │
│     └─────────────────────────────────────────────────────────┘     │
│     Paste an OpenReview ID or URL                                   │
│                                                                     │
│     ─────────────────────────────────────────────────────────────   │
│                                                                     │
│     PREVIEW                                                         │
│                                                                     │
│     Attention Is All You Need                                       │
│     Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez,              │
│     Kaiser, Polosukhin                                              │
│                                                                     │
│     NeurIPS 2017                                                    │
│                                                                     │
│     We propose a new simple network architecture, the               │
│     Transformer, based solely on attention mechanisms,              │
│     dispensing with recurrence and convolutions entirely...         │
│                                                                     │
│                                                                     │
│                                              ┌──────────────────┐   │
│                                              │  Import Paper    │   │
│                                              └──────────────────┘   │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  ← Home   ⏎ Import                                         ? Help   │
└─────────────────────────────────────────────────────────────────────┘
```

**Simplifications:**
- Single input field (accepts ID or URL)
- Preview appears automatically on valid input
- One action: Import (extraction is separate)
- No download PDF button (automatic)

---

### 7. Extract — AI Processing

Watch the AI work. Simple progress, no overwhelming detail.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Shannon                                              ⌘K Search     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│     Extracting                                                      │
│     Attention Is All You Need                                       │
│                                                                     │
│     ─────────────────────────────────────────────────────────────   │
│                                                                     │
│                                                                     │
│                                                                     │
│                    ████████████████░░░░░░░░░░░░                     │
│                              58%                                    │
│                                                                     │
│                                                                     │
│                                                                     │
│     ─────────────────────────────────────────────────────────────   │
│                                                                     │
│     ✓ Metadata                                                      │
│     ✓ Abstract                                                      │
│     ✓ Introduction                                                  │
│     ◐ Model Architecture                                            │
│     ○ Experiments                                                   │
│     ○ Conclusion                                                    │
│                                                                     │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  Extracting... Press Esc to cancel                         ? Help   │
└─────────────────────────────────────────────────────────────────────┘
```

**Simplifications:**
- Single progress bar (not per-section)
- Simple checklist below (✓ done, ◐ in progress, ○ pending)
- No start/stop/pause buttons (Esc to cancel)
- Completion auto-navigates to paper

---

### 8. Git — Version Control

Git status at a glance. Commit, push, done.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Shannon                                              ⌘K Search     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│     Git Status                                                      │
│     Branch: main · 3 uncommitted changes                            │
│                                                                     │
│     ─────────────────────────────────────────────────────────────   │
│                                                                     │
│     CHANGES                                                         │
│                                                                     │
│     ● M  papers/transformer/intro.md                                │
│       A  papers/transformer/formula1.md                             │
│       D  papers/old-notes.md                                        │
│                                                                     │
│     ─────────────────────────────────────────────────────────────   │
│                                                                     │
│     RECENT                                                          │
│                                                                     │
│       5d2e1f  Add transformer formula extraction         2h ago     │
│       a3b7c9  Update BERT model notes                    1d ago     │
│       f8e4d2  Initial extraction of Vision Transformer   3d ago     │
│                                                                     │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  ← Home   C Commit   P Push   L Pull   D Diff              ? Help   │
└─────────────────────────────────────────────────────────────────────┘
```

**Simplifications:**
- Removed branch management UI (use CLI for advanced git)
- Changes and history in one view
- Status letters (M/A/D) instead of words
- Actions in footer

---

## Components

### Minimal Components

Shannon uses few, purposeful components:

#### Selection Indicator

```
  ● Selected item
    Unselected item
    Another item
```

#### Progress States

```
  ✓ Complete
  ◐ In Progress  
  ○ Not Started
  ✗ Error
```

#### Inline Status

```
  Paper Title · Status
  Paper Title · Extracted
  Paper Title · In Progress
  Paper Title · Inbox
```

#### Divider

```
  ─────────────────────────────────────────────────────────────
```

#### Formula Block

```
  ┌───────────────────────────────────────────────────────────┐
  │                    QKᵀ                                    │
  │  Attention(Q,K,V) = softmax(────)V                        │
  │                     √dₖ                                   │
  └───────────────────────────────────────────────────────────┘
```

#### Citation Block

```
  > "Quoted text from the paper goes here."
  > — Page 2
```

#### Action Button

```
  ┌──────────────────┐
  │  Import Paper    │
  └──────────────────┘
```

---

## Interactions

### Navigation Model

Shannon uses a simple, predictable navigation:

```
Home ─────┬───── Papers ───── Paper ───── Page
          │
          ├───── Import
          │
          └───── Git
          
Search (⌘K) ───── Any destination
```

### Keyboard Shortcuts

**Global** (work everywhere):
| Key | Action |
|-----|--------|
| `⌘K` or `/` | Open search |
| `?` | Show help |
| `Esc` | Go back / Close |

**Navigation**:
| Key | Action |
|-----|--------|
| `↑` `↓` | Move selection |
| `⏎` | Open selected |
| `←` | Go back |

**Context-specific** (shown in footer):
| Screen | Keys |
|--------|------|
| Home | `P` Papers, `I` Import, `G` Git |
| Papers | `I` Import |
| Paper | `E` Extract, `O` Open PDF |
| Page | `E` Edit, `A` Add Note, `N` Next, `P` Previous |
| Git | `C` Commit, `P` Push, `L` Pull, `D` Diff |

---

## Feedback Patterns

### Toast Notifications

Appear briefly at bottom, then fade:

```
                                    ┌─────────────────────────────┐
                                    │  ✓ Paper imported           │
                                    └─────────────────────────────┘
```

### Confirmation Dialog

For destructive actions only:

```
          ┌─────────────────────────────────────────┐
          │                                         │
          │   Delete this page?                     │
          │   This cannot be undone.                │
          │                                         │
          │              Cancel    Delete           │
          │                                         │
          └─────────────────────────────────────────┘
```

### Loading States

Subtle, non-blocking:

```
  Loading...
```

Or with progress:

```
  ████████████████░░░░░░░░░░░░  58%
```

---

## Responsive Behavior

Shannon adapts gracefully to terminal size:

### Wide Terminal (120+ cols)

Full layout with comfortable margins.

### Standard Terminal (80-120 cols)

Reduced margins, full functionality.

### Narrow Terminal (< 80 cols)

```
┌────────────────────────────────┐
│ Shannon              ⌘K Search │
├────────────────────────────────┤
│                                │
│ Papers                         │
│                                │
│ ● Attention Is All You Need    │
│   Vaswani · NeurIPS 2017       │
│                                │
│   Vision Transformer           │
│   Dosovitskiy · ICLR 2021      │
│                                │
├────────────────────────────────┤
│ ← ↑↓ ⏎ I                    ?  │
└────────────────────────────────┘
```

- Truncated titles
- Abbreviated footer
- Single-column layout

---

## Design Tokens

### Spacing

```
xs:  1 char
sm:  2 chars  
md:  4 chars (default padding)
lg:  6 chars
xl:  8 chars
```

### Typography

```
Title:     Bold, primary color
Subtitle:  Regular, secondary color
Body:      Regular, primary color
Caption:   Regular, muted color
```

### Borders

```
Box:       ┌ ─ ┐ │ └ ┘
Divider:   ─────────────
Selection: ●
```

---

## Implementation Notes

### For Developers

1. **Use Textual's built-in components** where possible
2. **Avoid custom widgets** unless absolutely necessary
3. **Test at 80x24** minimum terminal size
4. **Prefer CSS over Python** for styling
5. **Keep screens under 200 lines** of code

### File Structure

```
src/tui/
├── app.py              # Main app, routing
├── screens/
│   ├── home.py         # Dashboard
│   ├── papers.py       # Paper list
│   ├── paper.py        # Paper detail
│   ├── page.py         # Page view/edit
│   ├── search.py       # Search overlay
│   ├── import.py       # Import flow
│   ├── extract.py      # Extraction progress
│   └── git.py          # Git status
├── components/
│   ├── toast.py        # Notifications
│   └── confirm.py      # Confirmation dialog
└── styles/
    └── theme.tcss      # All styles
```

---

## Summary

Shannon's TUI follows Apple's design ethos:

| Principle | Implementation |
|-----------|----------------|
| **Simplicity** | Fewer screens, fewer options, clearer paths |
| **Clarity** | Content-first, minimal chrome |
| **Deference** | UI gets out of the way |
| **Depth** | Layers of detail revealed progressively |

The result: a terminal app that feels as refined as a native macOS application.

---

*"Design is not just what it looks like and feels like. Design is how it works."*
— Steve Jobs
