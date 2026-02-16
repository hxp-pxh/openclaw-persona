# Quickstart

Get openclaw-persona running in 5 minutes.

## Prerequisites

- Node.js 18+
- Python 3.8+
- OpenClaw installed
- Anthropic API key (recommended)

## Installation

```bash
# Install CLI globally
npm install -g openclaw-persona

# Verify installation
persona --version
```

## Initialize Workspace

```bash
# Create new workspace with identity
persona init ~/my-assistant --name "Atlas"

# Or initialize in existing OpenClaw workspace
cd ~/existing-workspace
persona init . --name "Atlas"
```

This creates:
```
~/my-assistant/
├── SOUL.md           # Identity and values
├── IDENTITY.md       # Name, emoji
├── USER.md           # About your human
├── AGENTS.md         # Operating rules
├── MEMORY.md         # Long-term memories
├── HEARTBEAT.md      # Periodic tasks
├── memory/           # Daily logs
├── memory-vault/     # Vector database
├── agents/           # Sub-agent profiles
└── .learnings/       # Self-improvement
```

## Set Up Memory Vault

```bash
# Install Python dependencies
cd ~/my-assistant
python3 -m venv memory-vault
source memory-vault/bin/activate
pip install chromadb sentence-transformers

# Index workspace files
vmem index

# Test it
vmem query "test"
vmem stats
```

## Configure OpenClaw

Edit `~/.openclaw/openclaw.json`:

```json
{
  "agents": {
    "defaults": {
      "workspace": "~/my-assistant"
    }
  }
}
```

## Start OpenClaw

```bash
cd ~/my-assistant
openclaw gateway
```

## First Conversation

Message your assistant via WhatsApp/Telegram:

```
You: What's your name?
Atlas: I'm Atlas! 🦞 Just woke up in this new workspace.
       Still learning about you and figuring things out.
```

## Set Up Cron Jobs

```bash
# Session watcher (extracts memories)
openclaw cron add \
  --name "session-watcher" \
  --cron "*/15 * * * *" \
  --session isolated \
  --message "Extract important items from recent sessions"

# Context monitor (flushes before compaction)
openclaw cron add \
  --name "context-check" \
  --cron "*/10 * * * *" \
  --session main \
  --system-event "CONTEXT CHECK: If >70%, flush to memory"

# Weekly curation
openclaw cron add \
  --name "weekly-curation" \
  --cron "0 10 * * 0" \
  --tz "America/Toronto" \
  --session isolated \
  --message "Curate week's memories into MEMORY.md"
```

## Verify Setup

```bash
# Check status
persona status

# Should show:
# ✅ Identity: Atlas
# ✅ Memory vault: 50 chunks
# ✅ Cron jobs: 3 active
# ✅ OpenClaw: connected
```

## Next Steps

1. **Customize identity** — Edit SOUL.md, IDENTITY.md
2. **Add user context** — Fill in USER.md
3. **Create agent profiles** — Add to agents/
4. **Set up automations** — More cron jobs
5. **Review weekly** — Check .learnings/

See [Configuration](./CONFIGURATION.md) for advanced setup.
