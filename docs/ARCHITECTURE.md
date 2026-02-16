# Architecture

## Overview

openclaw-persona is a **layer on top of OpenClaw** that provides identity, memory lifecycle, and self-improvement without forking the core.

```
┌─────────────────────────────────────────────────────────────┐
│                        OpenClaw                              │
│  Gateway → Agent → Model (Claude/GPT) → Response             │
│                         │                                    │
│              reads workspace files                           │
└─────────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────────────────────────────────────────┐
│                    openclaw-persona                          │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Identity │  │  Memory  │  │  Self-   │  │  Agent   │    │
│  │ (SOUL)   │  │ (Vault)  │  │ Improve  │  │ Profiles │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Core Principle: Files ARE the Interface

OpenClaw reads workspace files. Persona scaffolds and maintains those files.

| File | Purpose | Updated By |
|------|---------|------------|
| `SOUL.md` | Identity, values, personality | User + Persona |
| `AGENTS.md` | Operating rules, autonomy | User + Persona |
| `USER.md` | About the human | User |
| `MEMORY.md` | Long-term curated memories | Persona (auto) |
| `IDENTITY.md` | Name, emoji, avatar | User |
| `HEARTBEAT.md` | Periodic check tasks | User + Persona |
| `memory/*.md` | Daily logs, topical notes | Persona (auto) |
| `memory-vault/` | Vector DB (semantic search) | Persona (auto) |
| `.learnings/` | Errors, corrections | Persona (auto) |
| `agents/` | Sub-agent profiles | User |

## Why Layer, Not Fork?

1. **Stability** — OpenClaw updates don't break persona
2. **Simplicity** — Files are a stable interface
3. **Graceful degradation** — Can run without persona
4. **Easier maintenance** — Separate concerns

## Components

### 1. Identity System

Creates and maintains identity files:

```
SOUL.md      → Who am I? Values, personality, style
IDENTITY.md  → Name, emoji, avatar
USER.md      → Who is my human?
AGENTS.md    → How do I operate?
```

### 2. Memory Vault

ChromaDB-based semantic memory:

```
memory-vault/
├── vault.py          # Main vault code
├── chroma_db/        # Vector database
├── model_server.py   # Embedding server
└── summarize.py      # Text summarization
```

**Operations:**
- `vmem query "text"` — Semantic search (returns summaries)
- `vmem get <id>` — Full memory by ID
- `vmem add "text"` — Add observation
- `vmem index` — Re-index workspace files
- `vmem consolidate` — Find duplicates to merge

### 3. Memory Lifecycle

```
Formation → Storage → Access → Decay → Pruning
    │          │         │        │        │
    ▼          ▼         ▼        ▼        ▼
Extract    ChromaDB   Track    Score    Remove
from       vectors    access   unused   stale
session               count    items    items
```

**Importance Scoring:**
- Access frequency
- Recency of access
- Source type (decisions > observations)
- User confirmation

### 4. Self-Improvement Engine

```
.learnings/
├── LEARNINGS.md      # Corrections, insights
├── ERRORS.md         # Command failures
└── FEATURE_REQUESTS.md # Things I can't do yet
```

**Scripts:**
- `self-improve.py analyze` — Find patterns in errors
- `self-improve.py propose` — Suggest improvements
- `self-improve.py apply` — Apply safe fixes

### 5. Agent Profiles

```
agents/
├── researcher.md     # Deep research tasks
├── coder.md          # Code implementation
├── scanner.md        # Quick lookups
└── analyst.md        # Strategic thinking
```

Used with `sessions_spawn` for specialized sub-agents.

### 6. Context Handoff

Survives context window limits:

```python
# Before compaction
context_handoff.py save

# Creates memory/context-handoff.md with:
# - Active tasks
# - Recent decisions
# - Open threads
# - Important context
```

## Data Flow

### Conversation → Memory

```
1. User message arrives
2. OpenClaw processes with agent
3. Session watcher (cron) extracts important items
4. Items added to memory-vault
5. Daily log updated (memory/YYYY-MM-DD.md)
6. Weekly: curate into MEMORY.md
```

### Memory → Retrieval

```
1. Agent receives query
2. Calls memory_search (OpenClaw tool)
3. vmem does semantic search
4. Returns top matches with summaries
5. Agent calls memory_get for full text
6. Uses context in response
```

## Cron Jobs

| Job | Frequency | Purpose |
|-----|-----------|---------|
| session-watcher | 15 min | Extract memories from sessions |
| context-monitor | 10 min | Flush if context >70% |
| nightly-index | Daily 7 AM | Re-index memory vault |
| weekly-curation | Sunday | Distill into MEMORY.md |
| weekly-self-improve | Sunday | Analyze errors, propose fixes |

## Security

### What's NOT Stored

Regex filters prevent storing:
- API keys, tokens, passwords
- Wallet addresses
- Private keys
- Credit card numbers

### Memory Boundaries

- `MEMORY.md` not loaded in group chats
- Credentials in `~/.secrets/`, not workspace
- Personal context protected from external sessions
