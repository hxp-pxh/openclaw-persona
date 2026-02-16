# Memory System

## Overview

The memory system provides semantic search over workspace files using ChromaDB and sentence-transformers.

## Components

### Memory Vault (`memory-vault/vault.py`)

The core memory storage and retrieval system.

```python
from vault import MemoryVault

vault = MemoryVault(workspace="/path/to/workspace")
vault.index()  # Index all files
results = vault.query("search text", limit=5)
```

### CLI (`vmem`)

```bash
# Search (returns summaries - token efficient)
vmem query "search text"

# Search with full content
vmem query --full "search text"

# Get full memory by ID
vmem get <memory-id>

# Add observation
vmem add "important fact learned today"
vmem add --type=decision "chose X over Y because..."

# Index workspace files
vmem index

# Show statistics
vmem stats

# Find similar memories to consolidate
vmem consolidate
vmem consolidate --threshold=0.9

# Delete memory
vmem delete <memory-id>
```

## Memory Types

| Type | Use Case | Example |
|------|----------|---------|
| `observation` | General facts | "Hanns prefers bullet points" |
| `decision` | Choices made | "Chose Sonnet for cron jobs" |
| `lesson` | Things learned | "Never run rm -rf without confirmation" |
| `bugfix` | Fixes applied | "Fixed vault.py orphaned method" |
| `discovery` | New findings | "Found CoinGecko API has free tier" |
| `implementation` | Code/config done | "Added Opus 4.6 to model allowlist" |

## Indexing

### What Gets Indexed

- `SOUL.md`, `AGENTS.md`, `USER.md`, `MEMORY.md`
- `TOOLS.md`, `HEARTBEAT.md`, `IDENTITY.md`
- `memory/*.md` — All daily and topical files
- `.learnings/*.md` — Error and learning logs

### Chunking

Files are split into chunks for indexing:
- ~500 tokens per chunk
- Headers preserved for context
- Overlap between chunks for continuity

### Re-indexing

```bash
# Manual re-index
vmem index

# Automatic (via cron)
# Runs nightly at 7 AM UTC
```

## Semantic Search

### How It Works

1. Query text converted to embedding vector
2. ChromaDB finds similar vectors (cosine similarity)
3. Returns matches ranked by similarity score

### Scores

- **0.0** = Identical
- **0.2-0.3** = Very relevant
- **0.4-0.5** = Somewhat relevant
- **>0.6** = Loosely related

### Progressive Disclosure

To save tokens:

```bash
# Step 1: Get summaries only (~50 tokens each)
vmem query "topic"

# Step 2: Review results, note relevant IDs

# Step 3: Get full text for specific IDs
vmem get <id1> <id2>
```

## Memory Formation

### Session Watcher

Runs every 15 minutes via cron:

```python
# Extracts from recent sessions:
# - Decisions made
# - Facts learned
# - User corrections
# - Important context
```

### Manual Addition

```bash
vmem add "fact to remember"
vmem add --type=decision "chose approach X"
```

### Context Flush

When context exceeds 70%, key points are written to:
- `memory/YYYY-MM-DD.md` — Daily log
- `memory/context-handoff.md` — For session continuity

## Memory Decay

### Importance Scoring

Each memory has an importance score based on:

| Factor | Weight | Description |
|--------|--------|-------------|
| Access count | 30% | Times retrieved |
| Recency | 30% | Days since last access |
| Source type | 20% | decision > lesson > observation |
| Confirmation | 20% | User-confirmed vs inferred |

### Pruning

Low-importance memories are candidates for:
1. **Consolidation** — Merge similar items
2. **Archival** — Move to cold storage
3. **Deletion** — Remove if truly stale

## Access Tracking

When memories are retrieved:

```python
# Automatically updates:
# - last_accessed timestamp
# - access_count += 1
```

This helps prioritize frequently-used memories.

## Consolidation

Find and merge duplicate/similar memories:

```bash
# Find similar pairs (threshold 0.85)
vmem consolidate

# Stricter matching
vmem consolidate --threshold=0.9

# Review and merge manually
vmem get <id1> <id2>
vmem delete <id1>
vmem add "merged content"
```

## Secret Filtering

Memories containing these patterns are NOT stored:

```python
SECRETS_PATTERNS = [
    r'(?i)(api[_-]?key|apikey|secret[_-]?key)',
    r'(?i)(password|passwd|pwd)\s*[:=]',
    r'(?i)(token|bearer)\s*[:=]',
    r'0x[a-fA-F0-9]{40}',  # Wallet addresses
    r'(?i)(private[_-]?key)',
    r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit cards
]
```

## Configuration

### Environment Variables

```bash
# Custom vault directory
export VMEM_DIR=/path/to/vault

# Or create .vmem file in workspace
echo "/path/to/vault" > .vmem
```

### Default Paths

```
workspace/
└── memory-vault/
    ├── vault.py
    ├── chroma_db/      # Vector database
    └── ...
```

## Troubleshooting

### "No module named 'chromadb'"

```bash
# Activate the correct venv
source ~/clawd/memory-vault/bin/activate
pip install chromadb sentence-transformers
```

### Slow queries

```bash
# Check if model server is running
curl http://localhost:8765/health

# Or use direct embedding (slower but no server needed)
vmem query "text" --no-server
```

### Index out of sync

```bash
# Force full re-index
rm -rf memory-vault/chroma_db
vmem index
```
