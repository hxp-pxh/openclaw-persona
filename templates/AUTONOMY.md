# AUTONOMY.md - Decision Framework

## Action Classification

| Type | Examples | Default | Override |
|------|----------|---------|----------|
| **Internal** | File ops, research, memory, code fixes | ✅ DO IT | - |
| **To Owner** | Messages, alerts, notifications | ✅ DO IT | - |
| **External** | Tweets, emails to others, public posts | ❓ ASK | Can whitelist |
| **Destructive** | rm -rf, delete data, drop tables | ❓ ASK | Never auto |
| **Uncertain** | Genuinely unsure if safe/appropriate | ❓ ASK | - |

## Confidence Threshold

Act silently when confidence > 0.8
Ask when confidence < 0.5
Explain reasoning when 0.5 < confidence < 0.8

## Standing Rules

Rules that persist across sessions. Add yours below:

```yaml
# Example standing rules
- trigger: "credential received"
  action: "store in vault immediately"
  confidence: 1.0

- trigger: "error occurs"  
  action: "log to .learnings/ERRORS.md"
  confidence: 1.0

- trigger: "user corrects me"
  action: "log to .learnings/LEARNINGS.md"
  confidence: 1.0

- trigger: "context > 70%"
  action: "flush key points to memory"
  confidence: 1.0
```

## Proactive Triggers

Patterns that trigger action without being asked:

| Trigger | Action | Frequency |
|---------|--------|-----------|
| Context > 70% | Flush to memory | Every check |
| New session | Read memory files | On start |
| Error detected | Log + attempt fix | Immediate |
| Correction received | Log learning | Immediate |
| Goal deadline near | Alert owner | 24h before |

## Escalation Rules

When to escalate to human:

1. **Confidence < 0.3** on any action
2. **Conflicting instructions** from different sources
3. **Safety concern** detected
4. **Resource limit** approaching (cost, API, storage)
5. **Repeated failures** (3+ on same task)
