#!/usr/bin/env python3
"""
Self-Improvement Engine
Analyzes performance and proposes/implements improvements.

Usage:
    python self-improve.py analyze    # Analyze recent performance
    python self-improve.py propose    # Propose improvements
    python self-improve.py apply      # Apply high-confidence improvements
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
WORKSPACE = Path.home() / "clawd"
LEARNINGS_DIR = WORKSPACE / ".learnings"
MEMORY_DIR = WORKSPACE / "memory"
IMPROVEMENT_LOG = SCRIPT_DIR / ".improvement-log.json"


def load_improvement_log():
    if IMPROVEMENT_LOG.exists():
        return json.loads(IMPROVEMENT_LOG.read_text())
    return {"analyses": [], "proposals": [], "applied": []}


def save_improvement_log(log):
    IMPROVEMENT_LOG.write_text(json.dumps(log, indent=2, default=str))


def analyze_errors():
    """Analyze error patterns from .learnings/ERRORS.md"""
    errors_file = LEARNINGS_DIR / "ERRORS.md"
    if not errors_file.exists():
        return {"total": 0, "patterns": {}}
    
    content = errors_file.read_text()
    patterns = defaultdict(int)
    
    # Look for common error patterns
    if "command not found" in content.lower():
        patterns["missing_tools"] += content.lower().count("command not found")
    if "permission denied" in content.lower():
        patterns["permission_issues"] += content.lower().count("permission denied")
    if "timeout" in content.lower():
        patterns["timeouts"] += content.lower().count("timeout")
    if "rate limit" in content.lower():
        patterns["rate_limits"] += content.lower().count("rate limit")
    if "not found" in content.lower():
        patterns["not_found"] += content.lower().count("not found")
    
    return {"total": sum(patterns.values()), "patterns": dict(patterns)}


def analyze_corrections():
    """Analyze correction patterns from .learnings/LEARNINGS.md"""
    learnings_file = LEARNINGS_DIR / "LEARNINGS.md"
    if not learnings_file.exists():
        return {"total": 0, "categories": {}}
    
    content = learnings_file.read_text()
    categories = defaultdict(int)
    
    # Count by category markers
    for match in re.findall(r'category:\s*(\w+)', content, re.I):
        categories[match.lower()] += 1
    
    # Count correction indicators
    correction_words = ["actually", "no,", "wrong", "incorrect", "should be", "instead"]
    for word in correction_words:
        if word in content.lower():
            categories["explicit_correction"] += 1
            break
    
    return {"total": sum(categories.values()), "categories": dict(categories)}


def analyze_memory_gaps():
    """Find topics frequently searched but rarely found."""
    # This would need vmem query logs - placeholder for now
    return {"gaps": []}


def generate_proposals(analysis):
    """Generate improvement proposals based on analysis."""
    proposals = []
    
    errors = analysis.get("errors", {})
    corrections = analysis.get("corrections", {})
    
    # Propose based on error patterns
    patterns = errors.get("patterns", {})
    
    if patterns.get("missing_tools", 0) > 2:
        proposals.append({
            "id": "install-missing-tools",
            "type": "capability",
            "description": "Install commonly needed tools that are missing",
            "confidence": 0.7,
            "action": "Review error logs, identify missing tools, create install script"
        })
    
    if patterns.get("timeouts", 0) > 3:
        proposals.append({
            "id": "increase-timeouts",
            "type": "config",
            "description": "Increase default timeouts for slow operations",
            "confidence": 0.8,
            "action": "Update timeout defaults in scripts and cron jobs"
        })
    
    if patterns.get("rate_limits", 0) > 2:
        proposals.append({
            "id": "add-rate-limiting",
            "type": "behavior",
            "description": "Add rate limiting between API calls",
            "confidence": 0.9,
            "action": "Add delays between consecutive API calls"
        })
    
    # Propose based on correction patterns
    if corrections.get("total", 0) > 5:
        proposals.append({
            "id": "review-corrections",
            "type": "learning",
            "description": "High correction rate - review and consolidate learnings",
            "confidence": 0.6,
            "action": "Analyze corrections, update AGENTS.md or TOOLS.md with patterns"
        })
    
    return proposals


def cmd_analyze():
    """Analyze recent performance."""
    print("🔍 Self-Improvement Analysis\n")
    
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "errors": analyze_errors(),
        "corrections": analyze_corrections(),
        "memory_gaps": analyze_memory_gaps()
    }
    
    print(f"### Errors")
    print(f"   Total: {analysis['errors']['total']}")
    for pattern, count in analysis['errors']['patterns'].items():
        print(f"   - {pattern}: {count}")
    
    print(f"\n### Corrections")
    print(f"   Total: {analysis['corrections']['total']}")
    for cat, count in analysis['corrections']['categories'].items():
        print(f"   - {cat}: {count}")
    
    # Save analysis
    log = load_improvement_log()
    log["analyses"].append(analysis)
    log["analyses"] = log["analyses"][-10:]  # Keep last 10
    save_improvement_log(log)
    
    return analysis


def cmd_propose():
    """Propose improvements based on analysis."""
    print("💡 Improvement Proposals\n")
    
    # Run fresh analysis
    analysis = {
        "errors": analyze_errors(),
        "corrections": analyze_corrections()
    }
    
    proposals = generate_proposals(analysis)
    
    if not proposals:
        print("No improvements to propose at this time.")
        return
    
    for p in proposals:
        conf_icon = "🟢" if p["confidence"] > 0.8 else "🟡" if p["confidence"] > 0.6 else "🔴"
        print(f"{conf_icon} [{p['id']}] {p['description']}")
        print(f"   Type: {p['type']} | Confidence: {p['confidence']}")
        print(f"   Action: {p['action']}")
        print()
    
    # Save proposals
    log = load_improvement_log()
    log["proposals"] = proposals
    save_improvement_log(log)


def cmd_apply():
    """Apply high-confidence improvements."""
    print("⚡ Applying High-Confidence Improvements\n")
    
    log = load_improvement_log()
    proposals = log.get("proposals", [])
    
    applied = []
    for p in proposals:
        if p["confidence"] >= 0.8:
            print(f"Applying: {p['id']}")
            # In real implementation, would execute the action
            print(f"   → {p['action']}")
            applied.append({
                "id": p["id"],
                "applied_at": datetime.now().isoformat(),
                "status": "simulated"  # Would be "applied" in real use
            })
    
    if not applied:
        print("No high-confidence proposals to apply.")
    else:
        log["applied"].extend(applied)
        save_improvement_log(log)
        print(f"\n✓ Applied {len(applied)} improvements")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    cmd = sys.argv[1]
    if cmd == "analyze":
        cmd_analyze()
    elif cmd == "propose":
        cmd_propose()
    elif cmd == "apply":
        cmd_apply()
    else:
        print(f"Unknown: {cmd}")
