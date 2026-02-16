#!/usr/bin/env python3
"""
Memory Maintenance - Extract & prune memories from session transcripts.

Usage:
    python memory-maintenance.py extract [--hours=24] [--dry-run]
    python memory-maintenance.py prune [--threshold=0.75] [--dry-run]
    python memory-maintenance.py full [--dry-run]
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

SCRIPT_DIR = Path(__file__).parent
VAULT_DIR = SCRIPT_DIR.parent / "memory-vault"
sys.path.insert(0, str(VAULT_DIR))

SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
STATE_FILE = SCRIPT_DIR / ".maintenance-state.json"

try:
    from vault import MemoryVault
    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False

# Skip system/automated messages
SKIP_PATTERNS = [
    r"HEARTBEAT", r"Pre-compaction", r"scheduled reminder", r"cron job",
    r"message_id:", r"\[WhatsApp.*UTC\]", r"DO NOT message",
]

# Skip secrets/credentials
SECRET_PATTERNS = [
    r"password", r"phrase", r"secret", r"token", r"key", r"credential",
    r"wallet", r"seed", r"api.?key", r"auth", r"private",
]

# Extract conversational memories
MEMORY_PATTERNS = [
    (r"I (?:really )?(?:like|prefer|want) (.{8,60})", "preference"),
    (r"(?:moving forward|from now on),? (.{10,80})", "instruction"),
    (r"you (?:should|must|can|will) (?:always )?(.{10,60})", "instruction"),
    (r"(?:make sure|ensure) (.{10,60})", "instruction"),
    (r"(?:I am|I'm) (.{5,40})", "fact"),
    (r"(?:let's|we'll) (.{8,50})", "decision"),
]


def load_state() -> Dict:
    return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {"last_processed": {}}


def save_state(state: Dict):
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))


def is_secret(text: str) -> bool:
    """Check if text contains secrets/credentials."""
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in SECRET_PATTERNS)


def should_skip(text: str) -> bool:
    if len(text) < 15 or len(text) > 200:
        return True
    if any(re.search(p, text, re.I) for p in SKIP_PATTERNS):
        return True
    if is_secret(text):
        return True
    # Skip URLs and technical strings
    if re.search(r'https?://|www\.', text):
        return True
    return False


def clean_message(text: str) -> str:
    text = re.sub(r'\[WhatsApp[^\]]+\]\s*', '', text)
    text = re.sub(r'\[message_id:[^\]]+\]', '', text)
    return text.strip()


def parse_transcript(session_file: Path, after_line: int = 0) -> List[Dict]:
    messages = []
    with open(session_file) as f:
        for i, line in enumerate(f):
            if i < after_line:
                continue
            try:
                entry = json.loads(line.strip())
                if entry.get("type") == "message":
                    msg = entry.get("message", {})
                    if msg.get("role") == "user":
                        content = msg.get("content", "")
                        if isinstance(content, list):
                            content = " ".join(b.get("text", "") for b in content if isinstance(b, dict))
                        content = clean_message(str(content).strip())
                        if content and not should_skip(content):
                            messages.append({"content": content, "line": i})
            except:
                continue
    return messages


def extract_memories(text: str) -> List[Dict]:
    candidates = []
    for pattern, mem_type in MEMORY_PATTERNS:
        for match in re.findall(pattern, text, re.I):
            clean = match.strip().rstrip('.,!?')
            if 8 < len(clean) < 100 and not should_skip(clean) and not is_secret(clean):
                candidates.append({"text": clean, "type": mem_type, "importance": 0.65})
    return candidates


def get_vault():
    workspace_vault = Path.cwd() / "memory-vault" / "vault.py"
    if workspace_vault.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("vault", workspace_vault)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.MemoryVault(lazy_load=True)
    return MemoryVault(lazy_load=True) if VAULT_AVAILABLE else None


def cmd_extract(hours: int = 24, dry_run: bool = False):
    vault = get_vault()
    if not vault:
        return print("Error: No vault")
    
    state = load_state()
    sessions = sorted([f for f in SESSIONS_DIR.glob("*.jsonl") 
                       if datetime.fromtimestamp(f.stat().st_mtime) > datetime.now() - timedelta(hours=hours)],
                      key=lambda f: f.stat().st_mtime) if SESSIONS_DIR.exists() else []
    
    print(f"Scanning {len(sessions)} sessions from last {hours}h")
    total = 0
    
    for sf in sessions:
        sid = sf.stem
        messages = parse_transcript(sf, state.get("last_processed", {}).get(sid, 0))
        if not messages:
            continue
        
        for msg in messages:
            for mem in extract_memories(msg["content"]):
                if dry_run:
                    print(f"  [{mem['type']}] {mem['text'][:70]}")
                    total += 1
                else:
                    existing = vault.query(mem["text"], n_results=1)
                    if existing and existing[0]["score"] > 0.85:
                        continue
                    vault.add_observation(mem["text"], obs_type=mem["type"])
                    print(f"  [+] {mem['type']}: {mem['text'][:50]}")
                    total += 1
        
        state.setdefault("last_processed", {})[sid] = messages[-1]["line"] + 1 if messages else 0
    
    if not dry_run:
        state["last_run"] = datetime.now().isoformat()
        save_state(state)
    print(f"\n✓ {'Found' if dry_run else 'Added'} {total} memories")


def cmd_prune(threshold: float = 0.75, dry_run: bool = False):
    vault = get_vault()
    if not vault:
        return print("Error: No vault")
    
    vault._init_db()
    data = vault.collection.get(include=["metadatas", "documents"])
    now = datetime.now()
    to_prune = []
    
    for mid, meta, doc in zip(data["ids"], data["metadatas"], data["documents"]):
        try:
            created = datetime.fromisoformat(meta.get("indexed_at", now.isoformat()))
            accessed = datetime.fromisoformat(meta.get("last_accessed", created.isoformat()))
        except:
            created = accessed = now
        
        decay = (
            min(1.0, (now - created).days / 180) * 0.2 +
            min(1.0, (now - accessed).days / 30) * 0.3 +
            (1.0 / (meta.get("access_count", 1) + 1)) * 0.2 +
            (1.0 - float(meta.get("importance", 0.5))) * 0.3
        )
        
        if decay > threshold:
            to_prune.append({"id": mid, "decay": decay, "preview": doc[:50]})
    
    print(f"{len(to_prune)} memories above decay threshold {threshold}")
    for mem in sorted(to_prune, key=lambda x: -x["decay"])[:10]:
        if dry_run:
            print(f"  [{mem['decay']:.2f}] {mem['preview']}...")
        else:
            vault.delete_memory(mem["id"])
    
    if not dry_run and to_prune:
        print(f"✓ Pruned {len(to_prune)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    else:
        cmd, dry = sys.argv[1], "--dry-run" in sys.argv
        if cmd == "extract":
            cmd_extract(int(next((a.split("=")[1] for a in sys.argv if "--hours=" in a), 24)), dry)
        elif cmd == "prune":
            cmd_prune(float(next((a.split("=")[1] for a in sys.argv if "--threshold=" in a), 0.75)), dry)
        elif cmd == "full":
            cmd_extract(dry_run=dry)
            cmd_prune(dry_run=dry)
