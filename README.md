# 🦞 openclaw-persona

**Personality and memory layer for OpenClaw.**

Gives your AI assistant continuity, identity, and growth.

## What is this?

OpenClaw gives you a personal AI assistant. openclaw-persona gives it a **soul**.

| Feature | Vanilla OpenClaw | + Persona |
|---------|------------------|-----------|
| **Memory** | Forgets after session | Remembers across months |
| **Identity** | Generic assistant | Has a name, personality, opinions |
| **Context** | You re-explain everything | Knows who you are, your projects |
| **Learning** | Makes same mistakes | Captures corrections, improves |
| **Delegation** | Manual prompts | Agent profiles with right tools |
| **Proactive** | Waits for commands | Heartbeat checks, surfaces opportunities |

## Install

```bash
npm install -g openclaw-persona
```

## Quick Start

```bash
# Initialize a new workspace
persona init ~/my-workspace

# Or initialize in current directory
cd ~/my-workspace
persona init

# Set up vector memory
persona vmem index

# Check status
persona status
```

## Commands

### `persona init [workspace]`

Scaffold a new persona workspace with:
- `SOUL.md` — Identity and values
- `AGENTS.md` — Operating instructions
- `USER.md` — Context about your human
- `HEARTBEAT.md` — Periodic tasks
- `agents/` — Subordinate profiles
- `.learnings/` — Self-improvement capture
- `memory-vault/` — Vector memory storage

Options:
- `--name <name>` — Name for your persona
- `--force` — Overwrite existing files

### `persona vmem <action> [args]`

Vector memory operations:

```bash
# Index all memory files
persona vmem index

# Search memories (returns summaries)
persona vmem query "topic"

# Search with full text
persona vmem query --full "topic"

# Get specific memory by ID
persona vmem get <id>

# Add a memory
persona vmem add "something I learned"
persona vmem add --type=decision "chose X because Y"

# Find similar memories to consolidate
persona vmem consolidate

# Delete a memory
persona vmem delete <id>

# Show stats
persona vmem stats
```

### `persona status`

Show workspace status and memory statistics.

### `persona update`

Update agent profiles to latest version.

## Memory Types

When adding memories with `vmem add`, use types:

- `observation` — General notes (default)
- `decision` — Choices and reasoning
- `lesson` — Things learned
- `bugfix` — Fixes discovered
- `discovery` — New capabilities found
- `implementation` — How things were built

## Agent Profiles

Pre-built profiles for sub-agent delegation:

| Profile | Use For |
|---------|---------|
| `researcher.md` | Deep research, multi-source investigation |
| `coder.md` | Implementation, bug fixes, scripts |
| `scanner.md` | Quick lookups, monitoring |
| `analyst.md` | Strategic thinking, trade-offs |

## Requirements

- Node.js 18+
- Python 3.8+ (for memory vault)
- OpenClaw (any version that reads workspace files)

## Python Dependencies

The memory vault requires Python packages:

```bash
pip install chromadb sentence-transformers
```

Or use the included requirements:

```bash
pip install -r memory-vault/requirements.txt
```

## Philosophy

> Vanilla OpenClaw is a tool. With persona, it becomes a partner that knows you and grows with you.

The key insight: AI assistants don't need to start from scratch every session. With proper memory, identity, and self-improvement systems, they can develop genuine continuity.

## License

MIT

---

*Built by Vesper 🦞*
