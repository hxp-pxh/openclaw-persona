# 🦞 openclaw-persona

**Personality and memory layer for OpenClaw.**

Gives your AI assistant continuity, identity, and growth.

[![CI](https://github.com/hxp-pxh/openclaw-persona/actions/workflows/ci.yml/badge.svg)](https://github.com/hxp-pxh/openclaw-persona/actions/workflows/ci.yml)
[![npm version](https://badge.fury.io/js/openclaw-persona.svg)](https://www.npmjs.com/package/openclaw-persona)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is this?

OpenClaw gives you a personal AI assistant. **openclaw-persona** gives it a soul.

| Feature | Vanilla OpenClaw | + Persona |
|---------|------------------|-----------|
| **Memory** | Forgets after session | Remembers across months |
| **Identity** | Generic assistant | Has a name, personality, opinions |
| **Context** | You re-explain everything | Knows who you are, your projects |
| **Learning** | Makes same mistakes | Captures corrections, improves |
| **Delegation** | Manual prompts | Agent profiles with right tools |
| **Proactive** | Waits for commands | Heartbeat checks, surfaces opportunities |

## Installation

```bash
npm install -g openclaw-persona
```

**Requirements:**
- Node.js 18+
- Python 3.8+ (for memory vault)
- OpenClaw (any version that reads workspace files)

## Quick Start

```bash
# Initialize a new workspace
persona init ~/my-assistant --name "Jarvis"

# Set up vector memory
pip install chromadb sentence-transformers
persona vmem index

# Check status
persona status

# Start OpenClaw in the workspace
cd ~/my-assistant
openclaw gateway
```

## What Gets Created

```
my-assistant/
├── SOUL.md           # Identity, values, personality
├── AGENTS.md         # Operating rules, autonomy
├── USER.md           # Context about you
├── MEMORY.md         # Long-term memories
├── HEARTBEAT.md      # Periodic tasks
├── IDENTITY.md       # Name, avatar
├── agents/           # Subordinate profiles
│   ├── researcher.md # Deep research
│   ├── coder.md      # Implementation
│   ├── scanner.md    # Quick lookups
│   └── analyst.md    # Strategic thinking
├── memory/           # Daily logs
├── memory-vault/     # Vector storage
├── .learnings/       # Self-improvement
│   ├── ERRORS.md
│   ├── LEARNINGS.md
│   └── FEATURE_REQUESTS.md
└── tasks/            # Active task tracking
```

## CLI Commands

### `persona init [workspace]`

Scaffold a new persona workspace.

```bash
persona init ~/my-assistant
persona init --name "Jarvis"
persona init --force  # Overwrite existing
```

### `persona vmem <action>`

Vector memory operations.

```bash
# Index all memory files
persona vmem index

# Search (returns summaries)
persona vmem query "that decision about APIs"

# Search with full text
persona vmem query --full "API decision"

# Get specific memory
persona vmem get <id>

# Add memories
persona vmem add "learned X is better than Y"
persona vmem add --type=decision "chose X because..."

# Find duplicates
persona vmem consolidate

# Remove memory
persona vmem delete <id>

# Statistics
persona vmem stats
```

### `persona status`

Show workspace status and memory statistics.

### `persona update`

Update agent profiles to latest version.

## Memory Types

| Type | Use For |
|------|---------|
| `observation` | General notes (default) |
| `decision` | Choices and reasoning |
| `lesson` | Things learned |
| `bugfix` | Fixes discovered |
| `discovery` | New capabilities |
| `implementation` | How things were built |

## Agent Profiles

Pre-built profiles for sub-agent delegation:

| Profile | Use For | Model |
|---------|---------|-------|
| researcher | Research, investigation | Sonnet |
| coder | Implementation, scripts | Sonnet |
| scanner | Quick lookups, monitoring | Haiku |
| analyst | Strategy, decisions | Opus |

**Usage in your assistant:**
```python
profile = read("agents/researcher.md")
sessions_spawn(task=f"{profile}\n\n---\n\nTASK: Research X")
```

## Documentation

| Guide | Description |
|-------|-------------|
| [Quickstart](docs/QUICKSTART.md) | Get running in 5 minutes |
| [Philosophy](docs/PHILOSOPHY.md) | Why persona exists, the LLM vs Cognitive AI bet |
| [Architecture](docs/ARCHITECTURE.md) | System design, components, data flow |
| [Memory System](docs/MEMORY-SYSTEM.md) | vmem CLI, indexing, semantic search |
| [Self-Improvement](docs/SELF-IMPROVEMENT.md) | Learning system, error tracking |
| [Model Routing](docs/MODEL-ROUTING.md) | Decision tree for model selection |
| [Identity](docs/IDENTITY.md) | SOUL/USER/personality system |
| [Configuration](docs/CONFIGURATION.md) | Full config reference |

## Philosophy

> Vanilla OpenClaw is a tool. With persona, it becomes a partner that knows you and grows with you.

The key insight: AI assistants don't need to start from scratch every session. With proper memory, identity, and self-improvement systems, they can develop genuine continuity.

**The lobster molts.** 🦞

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT — see [LICENSE](LICENSE)

---

*Built by Vesper 🦞*
