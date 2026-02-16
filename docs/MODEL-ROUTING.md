# Model Routing

## Overview

Different tasks require different models. This guide covers when to use which model.

## Decision Tree

```
                    WHAT'S THE TASK?
                          │
    ┌─────────┬───────────┼───────────┬───────────┐
    ▼         ▼           ▼           ▼           ▼
 CONVO     SWARM      AUTOMATION   CREATIVE    SIMPLE
(Hanns)  (parallel)   (cron)      (code)      (lookup)
    │         │           │           │           │
    ▼         ▼           ▼           ▼           ▼
┌───────┐ ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
│OPUS   │ │OPUS   │  │SONNET │  │ PONY  │  │ FREE  │
│ 4.5   │ │ 4.6   │  │       │  │       │  │models │
└───────┘ └───────┘  └───────┘  └───────┘  └───────┘
```

## Model Profiles

### Opus 4.5 (`anthropic/claude-opus-4-5`)
- **Alias:** `opus45`
- **Use for:** Conversations, complex reasoning, strategy
- **Cost:** High (~$15/M input, $75/M output)
- **Context:** 200K tokens

### Opus 4.6 (`anthropic/claude-opus-4-6`)
- **Alias:** `opus`
- **Use for:** Agent swarms, parallel coordination
- **Features:** Agent teams, 1M context window
- **Cost:** High (same as 4.5)

### Sonnet 4 (`anthropic/claude-sonnet-4`)
- **Alias:** `sonnet`
- **Use for:** Cron jobs, routine automation, research
- **Cost:** Medium (~$3/M input, $15/M output) — **5x cheaper than Opus**
- **Context:** 200K tokens

### Pony (`openrouter/pony-alpha`)
- **Alias:** `pony`
- **Use for:** Code generation, creative writing
- **Cost:** FREE
- **Note:** Always end prompts with "End with written summary, not tool call"

### Free Models
- `gemma` — Google Gemma 27B
- `glm` — GLM 4.5 Air
- `qwen` — Qwen Turbo

## Configuration

### Allowlist

Models must be in the allowlist to be used:

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

### In Chat

```
/model opus      → Switch to Opus 4.6
/model opus45    → Switch to Opus 4.5
/model sonnet    → Switch to Sonnet
/model pony      → Switch to Pony (free)
```

### In Cron Jobs

```json
{
  "payload": {
    "kind": "agentTurn",
    "model": "anthropic/claude-sonnet-4",
    "message": "Run the scan..."
  }
}
```

### In Sub-Agents

```javascript
sessions_spawn({
  task: "Research this topic",
  model: "anthropic/claude-sonnet-4"
})
```

## Cron Job Assignments

| Job Type | Model | Reason |
|----------|-------|--------|
| Nightly goal assessment | Opus | Needs reasoning |
| Trading scanner | Sonnet | Routine, fast |
| Crypto scanner | Sonnet | Routine, fast |
| Security audit | Sonnet | Routine checks |
| Memory curation | Sonnet | Batch processing |
| OpenClaw updates | Sonnet | Simple task |
| Session watcher | Default | Uses session model |

## Cost Optimization

| Strategy | Savings |
|----------|---------|
| Sonnet for cron | ~10x vs Opus |
| Pony for code gen | 100% (free) |
| Free models for lookups | 100% (free) |
| Batch similar work | Reduces API calls |

## Fallbacks

Configure fallback models for reliability:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-5",
        "fallbacks": ["anthropic/claude-sonnet-4"]
      }
    }
  }
}
```
