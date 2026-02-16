# Configuration

## Workspace Structure

```
workspace/
├── SOUL.md              # Identity (required)
├── IDENTITY.md          # Name, emoji (required)
├── USER.md              # Human context (required)
├── AGENTS.md            # Operating rules (required)
├── MEMORY.md            # Long-term memories
├── HEARTBEAT.md         # Periodic tasks
├── TOOLS.md             # Environment notes
│
├── memory/              # Daily logs
│   ├── YYYY-MM-DD.md    # Daily notes
│   ├── context-handoff.md
│   └── *.md             # Topical files
│
├── memory-vault/        # Vector database
│   ├── vault.py
│   ├── chroma_db/
│   └── bin/             # Python venv
│
├── agents/              # Sub-agent profiles
│   ├── researcher.md
│   ├── coder.md
│   └── scanner.md
│
├── .learnings/          # Self-improvement
│   ├── LEARNINGS.md
│   ├── ERRORS.md
│   └── FEATURE_REQUESTS.md
│
└── tasks/               # Active task files
    └── TEMPLATE.md
```

## Environment Variables

```bash
# Memory vault location (optional)
export VMEM_DIR=/path/to/vault

# Or use .vmem file
echo "/path/to/vault" > .vmem
```

## OpenClaw Configuration

### Workspace Path

```json
{
  "agents": {
    "defaults": {
      "workspace": "/home/user/my-assistant"
    }
  }
}
```

### Model Allowlist

```json
{
  "agents": {
    "defaults": {
      "models": {
        "anthropic/claude-opus-4-5": { "alias": "opus45" },
        "anthropic/claude-opus-4-6": { "alias": "opus" },
        "anthropic/claude-sonnet-4": { "alias": "sonnet" },
        "openrouter/pony-alpha": { "alias": "pony" }
      }
    }
  }
}
```

### Cron Jobs

See [OpenClaw cron docs](/automation/cron-jobs) for full reference.

Key jobs for persona:

```json
{
  "cron": {
    "enabled": true
  }
}
```

## Memory Vault

### vault.py Configuration

At top of file:

```python
# Files to index
INDEX_FILES = [
    "SOUL.md", "AGENTS.md", "USER.md", "MEMORY.md",
    "TOOLS.md", "HEARTBEAT.md", "IDENTITY.md"
]

# Directories to scan
INDEX_DIRS = ["memory", ".learnings"]

# Secret patterns (not stored)
SECRETS_PATTERNS = [
    r'(?i)(api[_-]?key|apikey)',
    r'(?i)(password|passwd)',
    r'(?i)(token|bearer)',
    # ... more patterns
]
```

### Embedding Model

Default: `sentence-transformers/all-MiniLM-L6-v2`

For better quality (larger):
```python
MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
```

## Agent Profiles

### Template

```markdown
# Agent: Researcher

## Role
Deep research across multiple sources.

## Capabilities
- Web search
- Document analysis
- Source verification

## Style
- Thorough
- Cites sources
- Presents multiple viewpoints

## Use When
- Complex information gathering
- Fact-checking
- Market research
```

### Loading in Sessions

```javascript
// Read profile
profile = read("agents/researcher.md")

// Spawn with profile
sessions_spawn({
  task: `${profile}\n\n---\n\nTASK: Research X`,
  model: "anthropic/claude-sonnet-4"
})
```

## Heartbeat Configuration

### HEARTBEAT.md

```markdown
# HEARTBEAT.md

## Quick Skip Rules
If only empty lines/headers/completed boxes, reply HEARTBEAT_OK

## Checks (rotate through)
- [ ] Email inbox
- [ ] Calendar next 24h
- [ ] Active positions

## Proactive Tasks
- Memory maintenance
- Security checks
```

### Frequency

Set in OpenClaw config:

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "1h"
      }
    }
  }
}
```

## Self-Improvement

### .learnings Structure

```
.learnings/
├── LEARNINGS.md          # Insights, corrections
├── ERRORS.md             # Failures, stack traces
└── FEATURE_REQUESTS.md   # Missing capabilities
```

### Auto-Logging

Agent logs automatically when:
- Commands fail
- User corrects
- Knowledge gaps found
- Better approaches discovered

### Weekly Review

Cron job analyzes patterns and proposes improvements.

## Security

### Secrets Location

```
~/.secrets/
└── credentials.env    # API keys, passwords
```

Never in workspace files.

### Memory Boundaries

- MEMORY.md not loaded in group chats
- Personal context filtered from external sessions
- Credentials pattern-matched and excluded

### Vaultwarden Integration

```bash
# Store secrets in Vaultwarden
bw login
bw sync

# Reference in scripts
source ~/.secrets/credentials.env
```
