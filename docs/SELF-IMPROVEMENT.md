# Self-Improvement System

## Overview

The self-improvement system captures errors, corrections, and learnings to enable continuous improvement.

## Directory Structure

```
.learnings/
├── LEARNINGS.md          # Corrections, insights, best practices
├── ERRORS.md             # Command failures, stack traces
└── FEATURE_REQUESTS.md   # Capabilities I don't have yet
```

## When to Log

| Situation | File | Category |
|-----------|------|----------|
| Command/operation fails | ERRORS.md | error |
| User corrects me | LEARNINGS.md | correction |
| Knowledge was outdated | LEARNINGS.md | knowledge_gap |
| Found better approach | LEARNINGS.md | best_practice |
| External API fails | ERRORS.md | external_failure |
| Can't fulfill request | FEATURE_REQUESTS.md | capability_gap |

## Entry Format

```markdown
## [LRN-YYYYMMDD-XXX] category
**Logged**: ISO timestamp | **Priority**: low/medium/high

### Summary
What was learned (one line)

### Details
Full context of what happened

### Action
How to apply this learning going forward
```

## Automatic Logging

The agent logs automatically during:

1. **After task completion** — Quick check for learnings
2. **On error** — Stack traces and context
3. **On correction** — When user says "No, that's wrong..."
4. **Weekly review** — Pattern analysis

## Scripts

### Analyze Patterns

```bash
cd ~/openclaw-persona
python3 scripts/self-improve.py analyze
```

Output:
- Most common error types
- Repeated corrections
- Improvement opportunities

### Propose Improvements

```bash
python3 scripts/self-improve.py propose
```

Generates improvement proposals based on:
- Error frequency
- Correction patterns
- Feature request themes

### Apply Improvements

```bash
python3 scripts/self-improve.py apply --id PROP-001
```

Applies safe, self-contained improvements:
- Updates to AGENTS.md rules
- New entries in TOOLS.md
- Skill configurations

## Improvement Categories

### High Confidence (Auto-Apply)

- Typo corrections in docs
- Adding learned commands to TOOLS.md
- Updating outdated version numbers

### Medium Confidence (Review First)

- New rules for AGENTS.md
- Workflow optimizations
- Tool configurations

### Low Confidence (Manual Only)

- Changes to SOUL.md
- Security-related changes
- Deletion of content

## Weekly Review

Runs via cron (Sundays):

```
1. Analyze .learnings/ for patterns
2. Check if repeating mistakes
3. Propose improvements
4. Apply high-confidence fixes
5. Log review results
```

## Integration with Memory

Learnings are also indexed in the memory vault:

```bash
vmem query "past mistakes"
vmem query "learned about trading"
```

This allows the agent to:
- Check past errors before similar tasks
- Recall user preferences
- Avoid repeating mistakes

## Example Workflow

```
1. Agent makes mistake
2. User corrects: "No, use Sonnet for cron jobs"
3. Agent logs:
   - LEARNINGS.md: [LRN-20260216-001] correction
   - Summary: Use Sonnet for cron jobs, not Opus
4. Next time similar task:
   - Agent searches: vmem query "cron job model"
   - Finds learning, applies correctly
5. Weekly review:
   - Pattern: Multiple model-choice corrections
   - Proposal: Add decision tree to TOOLS.md
   - Applied: memory/model-decision-tree.md created
```

## Metrics

Track improvement over time:

```bash
# Count learnings by category
grep -c "category: correction" .learnings/LEARNINGS.md

# Error trend
ls -la .learnings/ERRORS.md  # Size over time
```
