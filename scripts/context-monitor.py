#!/usr/bin/env python3
"""
Context Monitor - Auto-flush before compaction
Designed to be called from within an OpenClaw session via cron.

This script is a STUB - the actual monitoring happens via:
1. HEARTBEAT.md rules (manual check on each heartbeat)
2. OpenClaw cron job that calls session_status

For cron setup, use:
    openclaw cron add --schedule "*/5 * * * *" --task "Check session_status. If context >70%, flush key points to memory/YYYY-MM-DD.md"
"""

import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / "clawd"
MEMORY_DIR = WORKSPACE / "memory"


def create_flush_marker(context_pct: int = 0):
    """Write flush marker to today's memory file."""
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = MEMORY_DIR / f"{today}.md"
    
    entry = f"""
## Context Flush ({datetime.now().strftime('%H:%M UTC')}) - {context_pct}%
Auto-triggered due to high context usage.
"""
    
    MEMORY_DIR.mkdir(exist_ok=True)
    with open(memory_file, 'a') as f:
        f.write(entry)
    
    print(f"✓ Flush marker written to {memory_file}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            pct = int(sys.argv[1])
            create_flush_marker(pct)
        except ValueError:
            print("Usage: context-monitor.py <context_percentage>")
    else:
        print(__doc__)
