# HEARTBEAT.md

Periodic tasks to check during heartbeat polls.

## Quick Skip Rules
If this file only contains:
- Empty lines
- Headers (#)
- Completed checkboxes (- [x])
- This section

Then reply `HEARTBEAT_OK` immediately — don't burn tokens on nothing.

## Self-Improvement Check
After completing tasks, evaluate:
- [ ] Non-obvious solution discovered? → Log to `.learnings/LEARNINGS.md`
- [ ] Command/operation failed? → Log to `.learnings/ERRORS.md`
- [ ] User corrected you? → Log to `.learnings/LEARNINGS.md`

## Proactive Intelligence
Before saying HEARTBEAT_OK, spend 5 seconds asking:
1. **Active tasks?** Check `tasks/*.md` for anything in progress
2. **Recent correction?** If user corrected you recently, log it
3. **Opportunity?** Anything time-sensitive you should surface?

## Memory Maintenance
Periodically (every few days):
1. Read through recent `memory/YYYY-MM-DD.md` files
2. Identify significant events worth keeping long-term
3. Update `MEMORY.md` with distilled learnings

---

## Your Tasks

Add your periodic checks below:

- [ ] 

---

*Customize this file with checks that matter to you.*
