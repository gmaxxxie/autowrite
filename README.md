# AutoWrite CLI

<p align="center">
  <img src="https://img.shields.io/badge/GitHub%20Stars-Open-blue?style=flat-square" alt="Stars">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Python-3.8+-yellow.svg?style=flat-square" alt="Python">
</p>

<p align="center">
  <img src="https://cdn.hiapi.ai/relays/ali_image/2026-05/a8e1a717b533bad3.png" width="100%" alt="AutoWrite CLI Workflow">
</p>

---

> **AI Native book writing CLI. Give it a book title, get a complete book.**</p>

AutoWrite CLI is an **Agent-Friendly** book writing framework — driven by **Hermes Agent** by default, and compatible with Codex, Claude Code, or any AI Agent that can execute shell commands.

**中文版**：[README_zh.md](README_zh.md)

---

## Best For

AutoWrite CLI is purpose-built for **non-fiction books**, especially:

| Genre | Examples |
|-------|----------|
| Business & Management | Product methodology, business strategy, management |
| Tech & AI | AI applications, programming guides, technical thinking |
| Self-Improvement | Career growth, learning methods, career planning |
| Investing & Finance | Investment philosophy, financial planning, economic thinking |

**Why these books work well:**

- **Structured** — Business/tech books have clear chapter patterns AI can follow
- **Evidence-based** — Concept cards → case library → body text, layer by layer
- **Audited** — 6-layer audit chain ensures claims are sourced, data is real, tone is natural
- **Styled** — Style fingerprint keeps the whole book consistent

> Fiction and literary books are not AutoWrite's target — they rely more on personal narrative and creativity, where AutoWrite's structured audit chain could limit expression.

---

## Quick Start

```bash
# Install
git clone https://github.com/gmaxxxie/autowrite.git && cd autowrite
export PATH="$PWD:$PATH"

# Use
autowrite init mybook --genre non-fiction   # Initialize a book
autowrite write next mybook                  # Write next chapter
autowrite status mybook                     # Check status
```

---

## Table of Contents

- [Highlights](#highlights)
- [Best For](#best-for)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [AI Agent Integration](#ai-agent-integration)
- [Architecture](#architecture)
- [Audit Chain](#audit-chain)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

---

## Highlights

- **Agent-Native Design**: CLI as Agent interface, driven by Hermes / Codex / Claude Code
- **End-to-End Book Writing**: init → plan → write → audit → revise
- **Token Budget Control**: built-in `budget.py` engine prevents context overflow on long books
- **Context Assembly**: `composer.py` auto-aggregates concept cards, case library, truth files
- **Style Fingerprint**: `fingerprint.py` keeps the whole book consistent
- **Modular CLI**: each command is independent, composable
- **Pure Bash + Python**: no heavy dependencies, `book-agent-core` uses stdlib only

---

## Installation

### Requirements

| Dependency | Version | Note |
|------------|---------|------|
| Bash | ≥ 4.0 | Main CLI entry |
| Python | ≥ 3.8 | Only needed for `book-agent-core` |
| `pyyaml` | — | Optional, only for token budget config |

### Method 1: Git Clone (Recommended)

```bash
git clone https://github.com/gmaxxxie/autowrite.git
cd autowrite

# Add to PATH (choose one)
export PATH="$PWD:$PATH"                     # Current session only
echo 'export PATH="$PWD:$PATH"' >> ~/.bashrc # Permanent
```

### Method 2: Symlink to `~/.local/bin`

```bash
git clone https://github.com/gmaxxxie/autowrite.git
cd autowrite
mkdir -p ~/.local/bin
ln -s "$(pwd)/autowrite" ~/.local/bin/autowrite
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Method 3: Run Directly (For Quick Try)

Don't want to configure PATH? Clone and run directly:

```bash
git clone https://github.com/gmaxxxie/autowrite.git
cd autowrite

# Must be in the autowrite directory each time
./autowrite init mybook       # Initialize book
./autowrite write next mybook  # Write next chapter
./autowrite status mybook     # Check status
```

**Limitation**: Must be inside the autowrite directory, not globally accessible. Use Method 1 or 2 for regular use.

### Verify Installation

```bash
autowrite --help
```

---

## Usage

### Main Commands

```bash
autowrite --help              # Main help
autowrite init --help         # Init subcommand help
autowrite write --help        # Write subcommand help
autowrite audit --help        # Audit subcommand help
```

### Command Reference

| Command | Description |
|---------|-------------|
| `autowrite init <name>` | Initialize book workspace |
| `autowrite write next <name>` | Write next chapter (full pipeline) |
| `autowrite write count <name> <N>` | Write N chapters continuously |
| `autowrite audit <name> [chapter]` | Audit specific chapter |
| `autowrite revise <name> [chapter]` | Revise chapter |
| `autowrite status <name>` | View status |
| `autowrite status <name> --detail` | Detailed status |
| `autowrite plan <name>` | Generate chapter plan |
| `autowrite brief <name> --direction` | Direction negotiation |
| `autowrite validate <name>` | Validate manuscript |
| `autowrite list` | List all books |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BOOKS_DIR` | `~/books` | Book workspace root |
| `AUTOWRITE_ROOT` | CLI dir | Framework root |

```bash
# Custom book directory
BOOKS_DIR=/data/my-books autowrite init mybook
```

### Book Workspace Structure

```
~/books/<name>/
├── 00-index/              # TOC + truth files
│   ├── book-structure.md
│   ├── book-review.md
│   └── style-composition.md
├── 01-raw-material/        # Raw materials (PDF/Word/text)
├── 02-concept-cards/        # Concept沉淀
├── 03-method-cards/         # Method沉淀
├── 04-case-library/         # Case积累
├── 05-chapter-drafts/       # Chapter output
│   ├── CN/                # Chinese draft
│   └── tickets/            # Audit tickets
└── 06-published/            # Final
```

---

## AI Agent Integration

### Hermes Agent (Default)

AutoWrite CLI is driven by **Hermes** by default. Hermes reads routing rules from `AGENTS.md` and dispatches Skills automatically.

```bash
# Hermes receives natural language
hermes "Create a book about AI product management, write the first 3 chapters"

# Internally executes
autowrite init "AI产品经理"
autowrite write count "AI产品经理" 3
```

### Codex

```
# Drive Codex with natural language
codex "Use autowrite to create a book about Go language design, write the first 5 chapters"
# Codex internally calls
autowrite init "Go语言设计"
autowrite write count "Go语言设计" 5
```

### Claude Code

```bash
claude "Run: autowrite init golang-design && autowrite write count golang-design 5"
```

### Any Agent

Any AI Agent that can execute shell commands can drive AutoWrite — just call `autowrite <command>`.

---

## Architecture

```
autowrite/
├── autowrite                   # Main entry (bash)
├── autowrite-init              # Initialize book workspace
├── autowrite-write             # Chapter writing pipeline
├── autowrite-audit             # Audit chain
├── autowrite-status            # Status view
├── autowrite-brief             # Direction/Brief negotiation
├── autowrite-plan              # Chapter planning
├── autowrite-validate          # Manuscript validation
├── autowrite-state             # State machine
├── autowrite-model-gate        # Model routing gate
├── book-agent-core/            # Core framework (Python)
│   ├── budget.py            # Token budget engine
│   ├── composer.py          # Context assembly (cards/library/truth)
│   ├── planner.py           # Chapter planning
│   ├── settler.py           # State extraction
│   ├── rule_engine.py       # Deterministic rule engine
│   └── fingerprint.py       # Style fingerprint
└── AGENTS.md                  # Agent routing spec
```

### Execution Flow

```
User/Agent calls autowrite command
        ↓
    bash CLI parses command
        ↓
    Calls book-agent-core (Python)
        ↓
    Assembles context package (budget + context)
        ↓
    Routes to specific Skill (Hermes)
        ↓
    Execute → Audit chain → State update → git commit
```

---

## Audit Chain

Every chapter automatically passes through 6 audit layers:

| Step | Skill | Description |
|------|-------|-------------|
| 1 | `book-auto-revisor` | 8 auto-fixes (logic/fact/format) |
| 2 | `book-chapter-quality-audit` | Quality audit (claims/evidence/structure) |
| 3 | `book-de-ai-audit` | Remove AI flavor (eliminate machine tone) |
| 4 | `book-cn-localization-audit` | Chinese localization (natural expression) |
| 5 | `book-persona-audit` | 8-path persona review |
| 6 | `book-chapter-revise` | Revise based on audit results |

---

## FAQ

**Q: Do I need an extra AI API Key?**

A: AutoWrite CLI itself does not call AI — it relies on the upstream Agent (e.g. Hermes) for AI capability. Make sure your Agent has AI API configured.

**Q: Does it support English books?**

A: Yes. Specify `--genre en` when running `autowrite init`. The audit chain will automatically switch to English review models.

**Q: Can I use it without Hermes?**

A: Yes. AutoWrite CLI only depends on shell commands. Any Agent that can execute `autowrite <command>` can drive it.

**Q: How to customize token budget?**

A: Via environment variables or `book.conf`. See `book-agent-core/budget.py`.

---

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md).

**Dev workflow:**

```bash
# 1. Fork this repo
# 2. Create feature branch
git checkout -b feat/your-feature

# 3. Commit changes
git commit -m "feat: add your feature"

# 4. Push branch
git push origin feat/your-feature

# 5. Create Pull Request
```

**Dev requirements:**
- Bash 4.0+
- Python 3.8+
- `shellcheck` (optional, for bash linting)

---

## License

MIT License - see [LICENSE](LICENSE) file.
