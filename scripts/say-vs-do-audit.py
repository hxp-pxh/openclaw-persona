#!/usr/bin/env python3
"""
Say vs Do Audit - Detects when agents talk about actions without taking them.

The "completion feeling" problem: text generation creates a sense of closure
that substitutes for actual execution. This script audits session transcripts
to find intent/action mismatches.

Usage:
    python say-vs-do-audit.py <session_file.jsonl>
    python say-vs-do-audit.py --dir <sessions_dir> [--agent <agent_id>]
    python say-vs-do-audit.py --recent 5  # Last 5 sessions
"""

import json
import sys
import re
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Intent markers - phrases that suggest action should follow
INTENT_MARKERS = [
    # English
    r"valuable\s+(finding|discovery|insight)",
    r"worth\s+(following\s+up|investigating|exploring|noting)",
    r"should\s+(reply|respond|follow\s+up|contact|reach\s+out)",
    r"will\s+(follow\s+up|investigate|look\s+into|check)",
    r"needs?\s+(attention|action|follow[- ]?up)",
    r"action\s+item",
    r"todo|to-do|to do",
    r"important\s+(to|that)",
    r"must\s+(address|handle|fix|resolve)",
    r"urgent",
    r"⭐|🔥|‼️|❗|🚨",  # Emoji markers
    # Chinese
    r"有价值的发现",
    r"值得.*回",
    r"需要.*跟进",
    r"付费求助",
]

# Execution evidence - tool calls and actions
EXECUTION_PATTERNS = [
    r'"name":\s*"sessions_spawn"',
    r'"name":\s*"message"',
    r'"name":\s*"exec"',
    r'"name":\s*"Write"',
    r'"name":\s*"cron"',
    r'"name":\s*"browser"',
    r'"tool_calls":\s*\[',
    r'<invoke',
]

# Skip patterns - things that look like intents but aren't actionable
SKIP_PATTERNS = [
    r"example",
    r"documentation",
    r"if\s+you\s+(want|need)",
    r"let\s+me\s+know",
]


def extract_assistant_content(session_file: Path) -> Tuple[str, List[Dict]]:
    """Extract assistant messages and tool calls from a session file."""
    assistant_text = []
    tool_calls = []
    
    try:
        with open(session_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    if msg.get('role') == 'assistant':
                        content = msg.get('content', '')
                        if isinstance(content, str):
                            assistant_text.append(content)
                        elif isinstance(content, list):
                            for block in content:
                                if isinstance(block, dict) and block.get('type') == 'text':
                                    assistant_text.append(block.get('text', ''))
                        
                        # Track tool calls
                        if 'tool_calls' in msg:
                            for tc in msg['tool_calls']:
                                tool_calls.append({
                                    'name': tc.get('function', {}).get('name', 'unknown'),
                                    'id': tc.get('id', '')
                                })
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Error reading {session_file}: {e}", file=sys.stderr)
        return "", []
    
    return "\n".join(assistant_text), tool_calls


def find_intents(text: str) -> List[str]:
    """Find action intent markers in text."""
    intents = []
    text_lower = text.lower()
    
    for pattern in INTENT_MARKERS:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        if matches:
            # Get the actual matched text with context
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 20)
                context = text[start:end].strip()
                
                # Check if it's a skip pattern
                skip = False
                for skip_pat in SKIP_PATTERNS:
                    if re.search(skip_pat, context, re.IGNORECASE):
                        skip = True
                        break
                
                if not skip and context not in intents:
                    intents.append(context)
    
    return intents


def find_executions(text: str, tool_calls: List[Dict]) -> List[str]:
    """Find execution evidence in text and tool calls."""
    executions = []
    
    # Tool calls are the primary evidence
    for tc in tool_calls:
        name = tc['name']
        if name not in ['session_status']:  # Skip passive tools
            executions.append(f"tool:{name}")
    
    # Also check for inline tool invocations in text
    for pattern in EXECUTION_PATTERNS:
        if re.search(pattern, text):
            match = re.search(pattern, text)
            if match:
                executions.append(f"pattern:{match.group()[:30]}")
    
    return list(set(executions))


def audit_session(session_file: Path) -> Dict:
    """Audit a single session file for say-vs-do gaps."""
    text, tool_calls = extract_assistant_content(session_file)
    
    if not text:
        return {
            'file': str(session_file),
            'status': 'empty',
            'intents': [],
            'executions': [],
            'gap': False
        }
    
    intents = find_intents(text)
    executions = find_executions(text, tool_calls)
    
    # Calculate gap: intents without corresponding actions
    gap = len(intents) > 0 and len(executions) == 0
    
    return {
        'file': str(session_file),
        'status': 'audited',
        'intents': intents,
        'executions': executions,
        'gap': gap,
        'intent_count': len(intents),
        'execution_count': len(executions)
    }


def format_report(result: Dict) -> str:
    """Format audit result as human-readable report."""
    lines = [f"\n🔍 Audit: {result['file']}\n"]
    
    if result['status'] == 'empty':
        lines.append("  (empty session)\n")
        return "".join(lines)
    
    lines.append(f"📋 Action intents ({result['intent_count']}):")
    if result['intents']:
        for intent in result['intents'][:5]:  # Limit to 5
            lines.append(f'  - "{intent}"')
    else:
        lines.append("  (none)")
    
    lines.append(f"\n✅ Execution evidence ({result['execution_count']}):")
    if result['executions']:
        for exec in result['executions'][:5]:
            lines.append(f"  - {exec}")
    else:
        lines.append("  (none)")
    
    if result['gap']:
        lines.append("\n🔴 WARNING: Action intents found but no execution evidence!")
        lines.append("   This may indicate 'completion feeling' without actual action.")
    else:
        lines.append("\n✅ OK: Intent/action balance looks reasonable.")
    
    return "\n".join(lines)


def find_session_files(directory: Path, agent_id: Optional[str] = None, limit: int = None) -> List[Path]:
    """Find session files in directory, optionally filtered by agent."""
    pattern = "*.jsonl"
    files = list(directory.glob(f"**/{pattern}"))
    
    if agent_id:
        files = [f for f in files if agent_id in str(f)]
    
    # Sort by modification time (newest first)
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    if limit:
        files = files[:limit]
    
    return files


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Say vs Do Audit")
    parser.add_argument('file', nargs='?', help='Session file to audit')
    parser.add_argument('--dir', help='Directory containing session files')
    parser.add_argument('--agent', help='Filter by agent ID')
    parser.add_argument('--recent', type=int, help='Audit N most recent sessions')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--gaps-only', action='store_true', help='Only show sessions with gaps')
    
    args = parser.parse_args()
    
    results = []
    
    if args.file:
        # Single file mode
        result = audit_session(Path(args.file))
        results.append(result)
    elif args.dir or args.recent:
        # Directory/recent mode
        search_dir = Path(args.dir) if args.dir else Path.home() / '.openclaw' / 'sessions'
        if not search_dir.exists():
            print(f"Directory not found: {search_dir}", file=sys.stderr)
            sys.exit(1)
        
        files = find_session_files(search_dir, args.agent, args.recent)
        for f in files:
            result = audit_session(f)
            results.append(result)
    else:
        parser.print_help()
        sys.exit(1)
    
    # Filter gaps only
    if args.gaps_only:
        results = [r for r in results if r.get('gap')]
    
    # Output
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            print(format_report(result))
        
        # Summary
        gaps = sum(1 for r in results if r.get('gap'))
        total = len(results)
        if total > 1:
            print(f"\n📊 Summary: {gaps}/{total} sessions have say-vs-do gaps")
            if gaps > 0:
                print("   Run with --gaps-only to see only problematic sessions")


if __name__ == '__main__':
    main()
