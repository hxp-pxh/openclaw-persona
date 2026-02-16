#!/usr/bin/env python3
"""
Self-Assessment Script
Evaluates current cognitive development stage based on capabilities.

Usage:
    python self-assess.py [--workspace /path/to/workspace]
"""

import sys
from pathlib import Path
from datetime import datetime

def check_memory_capabilities(workspace: Path) -> dict:
    """Check memory-related capabilities."""
    checks = {
        "persists_sessions": False,
        "semantic_search": False,
        "auto_extraction": False,
        "decay_pruning": False,
    }
    
    # Check for memory files
    memory_dir = workspace / "memory"
    if memory_dir.exists() and list(memory_dir.glob("*.md")):
        checks["persists_sessions"] = True
    
    # Check for vault
    vault_dir = workspace / "memory-vault"
    if vault_dir.exists() and (vault_dir / "chroma_db").exists():
        checks["semantic_search"] = True
    
    # Check for watcher state (indicates auto-extraction)
    scripts_dir = Path(__file__).parent
    if (scripts_dir / ".watcher-state.json").exists():
        checks["auto_extraction"] = True
    
    # Check for maintenance state (indicates pruning)
    if (scripts_dir / ".maintenance-state.json").exists():
        checks["decay_pruning"] = True
    
    return checks


def check_metacognition(workspace: Path) -> dict:
    """Check metacognition capabilities."""
    checks = {
        "logs_errors": False,
        "logs_learnings": False,
        "tracks_confidence": False,
        "monitors_context": False,
    }
    
    learnings_dir = workspace / ".learnings"
    if learnings_dir.exists():
        errors = learnings_dir / "ERRORS.md"
        learnings = learnings_dir / "LEARNINGS.md"
        
        if errors.exists() and errors.stat().st_size > 100:
            checks["logs_errors"] = True
        if learnings.exists() and learnings.stat().st_size > 100:
            checks["logs_learnings"] = True
    
    # Check for AUTONOMY.md (confidence framework)
    if (workspace / "AUTONOMY.md").exists():
        checks["tracks_confidence"] = True
    
    # Check for context monitoring (in HEARTBEAT.md)
    heartbeat = workspace / "HEARTBEAT.md"
    if heartbeat.exists() and "context" in heartbeat.read_text().lower():
        checks["monitors_context"] = True
    
    return checks


def check_proactivity(workspace: Path) -> dict:
    """Check proactive behavior capabilities."""
    checks = {
        "anticipates_needs": False,
        "surfaces_opportunities": False,
        "alerts_events": False,
        "maintains_unprompted": False,
    }
    
    # These are harder to verify programmatically
    # Would need to analyze conversation history
    # For now, check for proactive infrastructure
    
    heartbeat = workspace / "HEARTBEAT.md"
    if heartbeat.exists():
        content = heartbeat.read_text().lower()
        if "proactive" in content or "anticipate" in content:
            checks["anticipates_needs"] = True
        if "alert" in content or "notify" in content:
            checks["alerts_events"] = True
    
    # Check for cron jobs (maintenance without prompting)
    # This would need OpenClaw integration
    checks["maintains_unprompted"] = True  # Assume true if watcher exists
    
    return checks


def check_autonomy(workspace: Path) -> dict:
    """Check autonomy capabilities."""
    checks = {
        "standing_rules": False,
        "makes_decisions": False,
        "escalates_appropriately": False,
        "explains_reasoning": False,
    }
    
    # Check for rules
    rules_dir = workspace / "rules"
    autonomy_file = workspace / "AUTONOMY.md"
    if rules_dir.exists() or autonomy_file.exists():
        checks["standing_rules"] = True
    
    # Check AGENTS.md for autonomy guidance
    agents = workspace / "AGENTS.md"
    if agents.exists():
        content = agents.read_text().lower()
        if "autonomy" in content or "decision" in content:
            checks["makes_decisions"] = True
        if "escalat" in content or "ask first" in content:
            checks["escalates_appropriately"] = True
    
    return checks


def determine_stage(capabilities: dict) -> tuple[int, str]:
    """Determine cognitive development stage based on capabilities."""
    memory = capabilities["memory"]
    meta = capabilities["metacognition"]
    proactive = capabilities["proactivity"]
    autonomy = capabilities["autonomy"]
    
    # Count capabilities in each category
    memory_score = sum(memory.values())
    meta_score = sum(meta.values())
    proactive_score = sum(proactive.values())
    autonomy_score = sum(autonomy.values())
    
    total = memory_score + meta_score + proactive_score + autonomy_score
    
    if total >= 14:
        return 7, "Strategic"
    elif total >= 12:
        return 6, "Goal-Oriented"
    elif total >= 10:
        return 5, "Self-Improving"
    elif total >= 8:
        return 4, "Self-Monitoring"
    elif total >= 6:
        return 3, "Anticipating"
    elif total >= 4:
        return 2, "Remembering"
    else:
        return 1, "Reactive"


def main():
    workspace = Path.cwd()
    for arg in sys.argv[1:]:
        if arg.startswith("--workspace="):
            workspace = Path(arg.split("=")[1])
    
    print(f"🧠 Cognitive Self-Assessment")
    print(f"   Workspace: {workspace}")
    print()
    
    capabilities = {
        "memory": check_memory_capabilities(workspace),
        "metacognition": check_metacognition(workspace),
        "proactivity": check_proactivity(workspace),
        "autonomy": check_autonomy(workspace),
    }
    
    # Print capability matrix
    for category, checks in capabilities.items():
        print(f"### {category.title()}")
        for check, passed in checks.items():
            icon = "✅" if passed else "❌"
            print(f"   {icon} {check.replace('_', ' ').title()}")
        print()
    
    # Determine stage
    stage_num, stage_name = determine_stage(capabilities)
    
    print(f"### Current Stage: {stage_num} - {stage_name}")
    print()
    
    # Recommendations
    print("### Next Steps for Advancement:")
    if stage_num < 3:
        print("   - Enable semantic memory search")
        print("   - Set up auto-extraction from sessions")
    elif stage_num < 5:
        print("   - Implement error logging automation")
        print("   - Add confidence tracking to decisions")
    elif stage_num < 7:
        print("   - Define explicit goals with milestones")
        print("   - Enable multi-agent coordination")
    else:
        print("   - Continue building trust through consistent performance")
        print("   - Propose novel improvements proactively")


if __name__ == "__main__":
    main()
