#!/usr/bin/env python3
"""
Context Monitor - Auto-flush before compaction
Monitors context usage and triggers memory flush when threshold exceeded.

Usage:
    python context-monitor.py [--threshold=70] [--once] [--dry-run]
"""

import sys
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
WORKSPACE = Path.home() / "clawd"
MEMORY_DIR = WORKSPACE / "memory"
FLUSH_LOG = SCRIPT_DIR / ".flush-log.json"


def get_session_status() -> dict:
    """Get current session status from OpenClaw."""
    try:
        # This would ideally use the session_status tool, but we're in a script
        # So we'll parse from openclaw CLI or use a simple heuristic
        result = subprocess.run(
            ["openclaw", "status", "--json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        pass
    
    return {}


def parse_context_percentage(status_text: str) -> int:
    """Parse context percentage from status output."""
    # Look for pattern like "Context: 150k/200k (75%)"
    match = re.search(r'Context:.*?(\d+)%', status_text)
    if match:
        return int(match.group(1))
    return 0


def load_flush_log():
    if FLUSH_LOG.exists():
        return json.loads(FLUSH_LOG.read_text())
    return {"flushes": [], "last_check": None}


def save_flush_log(log):
    log["last_check"] = datetime.now().isoformat()
    FLUSH_LOG.write_text(json.dumps(log, indent=2))


def flush_context_to_memory(dry_run: bool = False):
    """Write important context markers to today's memory file."""
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = MEMORY_DIR / f"{today}.md"
    
    flush_entry = f"""
## Auto-Flush ({datetime.now().strftime('%H:%M UTC')})
Context usage high - automatic preservation triggered.
- Active work should be logged above
- Check tasks/ for in-progress items
- Review recent tool calls for state
"""
    
    if dry_run:
        print(f"[DRY RUN] Would append to {memory_file}:")
        print(flush_entry)
    else:
        MEMORY_DIR.mkdir(exist_ok=True)
        with open(memory_file, 'a') as f:
            f.write(flush_entry)
        print(f"✓ Flushed context marker to {memory_file}")
    
    return True


def check_and_flush(threshold: int = 70, dry_run: bool = False):
    """Check context usage and flush if above threshold."""
    log = load_flush_log()
    
    # Try to get status via subprocess
    try:
        result = subprocess.run(
            ["openclaw", "status"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(WORKSPACE)
        )
        status_text = result.stdout
    except Exception as e:
        print(f"Could not get status: {e}")
        return
    
    context_pct = parse_context_percentage(status_text)
    print(f"Context usage: {context_pct}%")
    
    if context_pct >= threshold:
        print(f"⚠️  Above threshold ({threshold}%) - triggering flush")
        flushed = flush_context_to_memory(dry_run)
        if flushed and not dry_run:
            log["flushes"].append({
                "time": datetime.now().isoformat(),
                "context_pct": context_pct
            })
    else:
        print(f"✓ Below threshold ({threshold}%)")
    
    if not dry_run:
        save_flush_log(log)


def monitor_continuous(threshold: int = 70, dry_run: bool = False):
    """Continuous monitoring mode."""
    import time
    print(f"Monitoring context usage (threshold: {threshold}%)...")
    
    try:
        while True:
            check_and_flush(threshold, dry_run)
            time.sleep(300)  # Check every 5 minutes
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    once = "--once" in sys.argv
    threshold = int(next((a.split("=")[1] for a in sys.argv if "--threshold=" in a), 70))
    
    if once:
        check_and_flush(threshold, dry_run)
    else:
        monitor_continuous(threshold, dry_run)
