#!/usr/bin/env python3
"""
Session Watcher - Real-time memory extraction
Watches OpenClaw session files and extracts memories as they're written.

Usage:
    python session-watcher.py [--once] [--dry-run]
    
Options:
    --once      Process recent changes and exit (for cron)
    --dry-run   Don't actually add memories
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# Import from maintenance script
from importlib.util import spec_from_file_location, module_from_spec
spec = spec_from_file_location("maintenance", SCRIPT_DIR / "memory-maintenance.py")
maintenance = module_from_spec(spec)
spec.loader.exec_module(maintenance)

SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
WATCH_STATE = SCRIPT_DIR / ".watcher-state.json"


def load_watch_state():
    if WATCH_STATE.exists():
        return json.loads(WATCH_STATE.read_text())
    return {"file_positions": {}, "last_check": None}


def save_watch_state(state):
    state["last_check"] = datetime.now().isoformat()
    WATCH_STATE.write_text(json.dumps(state, indent=2))


def get_new_content(session_file: Path, last_pos: int = 0) -> tuple[str, int]:
    """Read new content from a session file since last position."""
    with open(session_file, 'rb') as f:
        f.seek(0, 2)  # End of file
        current_size = f.tell()
        
        if current_size <= last_pos:
            return "", last_pos
        
        f.seek(last_pos)
        new_bytes = f.read()
        return new_bytes.decode('utf-8', errors='ignore'), current_size


def process_new_messages(content: str, dry_run: bool = False) -> int:
    """Extract memories from new session content."""
    vault = maintenance.get_vault()
    if not vault:
        return 0
    
    extracted = 0
    for line in content.strip().split('\n'):
        if not line:
            continue
        try:
            entry = json.loads(line)
            if entry.get("type") == "message":
                msg = entry.get("message", {})
                if msg.get("role") == "user":
                    content_raw = msg.get("content", "")
                    if isinstance(content_raw, list):
                        content_raw = " ".join(b.get("text", "") for b in content_raw if isinstance(b, dict))
                    
                    text = maintenance.clean_message(str(content_raw))
                    if text and not maintenance.should_skip(text):
                        for mem in maintenance.extract_memories(text):
                            if dry_run:
                                print(f"  [DRY] {mem['type']}: {mem['text'][:50]}")
                                extracted += 1
                            else:
                                existing = vault.query(mem["text"], n_results=1)
                                if existing and existing[0]["score"] > 0.85:
                                    continue
                                vault.add_observation(mem["text"], obs_type=mem["type"])
                                print(f"  [+] {mem['type']}: {mem['text'][:50]}")
                                extracted += 1
        except:
            continue
    
    return extracted


def watch_once(dry_run: bool = False):
    """Single pass - check for changes since last run."""
    state = load_watch_state()
    
    if not SESSIONS_DIR.exists():
        print("No sessions directory")
        return
    
    # Only check files modified in last hour
    cutoff = datetime.now() - timedelta(hours=1)
    recent_files = [f for f in SESSIONS_DIR.glob("*.jsonl")
                    if datetime.fromtimestamp(f.stat().st_mtime) > cutoff]
    
    total = 0
    for sf in recent_files:
        sid = sf.stem
        last_pos = state.get("file_positions", {}).get(sid, 0)
        
        new_content, new_pos = get_new_content(sf, last_pos)
        if new_content:
            print(f"\n{sid[:8]}... ({len(new_content)} bytes new)")
            extracted = process_new_messages(new_content, dry_run)
            total += extracted
            state.setdefault("file_positions", {})[sid] = new_pos
    
    if not dry_run:
        save_watch_state(state)
    
    print(f"\n✓ Extracted {total} memories from {len(recent_files)} active sessions")


def watch_continuous(dry_run: bool = False):
    """Continuous watch mode using polling."""
    print("Starting session watcher (Ctrl+C to stop)...")
    
    try:
        while True:
            watch_once(dry_run)
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    once = "--once" in sys.argv
    
    if once:
        watch_once(dry_run)
    else:
        watch_continuous(dry_run)
