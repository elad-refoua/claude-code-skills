#!/usr/bin/env python3
"""
Organize raw mistakes into patterns and create a readable summary.
Run via: py ~/.claude/skills/mistake-analyzer/scripts/consolidate.py

IMPORTANT: This script NEVER touches LESSONS.md.
LESSONS.md is only updated by /mistake-analyzer skill (Claude AI analysis).
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

MISTAKES_DIR = Path.home() / ".claude" / "mistakes"
RAW_FILE = MISTAKES_DIR / "raw" / "pending.jsonl"
PATTERNS_FILE = MISTAKES_DIR / "patterns.json"
SUMMARY_FILE = MISTAKES_DIR / "raw" / "summary.md"
RETENTION_DAYS = 30


def categorize_error(tool: str, error: str, action: str) -> str:
    """Categorize a mistake by type."""
    error_lower = error.lower()

    if any(x in error_lower for x in ["no such file", "cannot find", "does not exist", "not found"]):
        return "path"
    if any(x in error_lower for x in ["permission denied", "access denied", "forbidden"]):
        return "permission"
    if any(x in error_lower for x in ["syntax", "unexpected token", "parse error"]):
        return "syntax"
    if "command not found" in error_lower or "is not recognized" in error_lower:
        return "tool"
    if any(x in error_lower for x in ["connection", "timeout", "network"]):
        return "external"
    return "other"


def extract_pattern_key(tool: str, error: str, category: str) -> str:
    """Create a pattern key for grouping similar mistakes."""
    error_normalized = error.lower()[:100]
    error_normalized = re.sub(r'[0-9]+', 'N', error_normalized)
    error_normalized = re.sub(r'[a-z]:\\[^\s]+', 'PATH', error_normalized, flags=re.IGNORECASE)
    error_normalized = re.sub(r'/[^\s]+', 'PATH', error_normalized)
    return f"{tool}:{category}:{error_normalized[:50]}"


def load_raw_mistakes() -> list:
    """Load raw mistakes from pending.jsonl."""
    mistakes = []
    if not RAW_FILE.exists():
        return mistakes
    with open(RAW_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    mistakes.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return mistakes


def generate_summary_md(mistakes: list, stats: dict) -> str:
    """Generate a readable summary of recent mistakes (NOT lessons)."""
    lines = [
        "# Mistake Summary (Raw Data)",
        "",
        f"*Auto-generated {datetime.now().strftime('%Y-%m-%d %H:%M')}. "
        "Run /mistake-analyzer for AI root-cause analysis.*",
        "",
        f"**Total entries:** {len(mistakes)}",
        "",
    ]

    # Stats
    if stats.get("by_tool"):
        lines.append("## By Tool")
        for tool, count in sorted(stats["by_tool"].items(), key=lambda x: -x[1]):
            lines.append(f"- {tool}: {count}")
        lines.append("")

    if stats.get("by_project"):
        lines.append("## By Project")
        for proj, count in sorted(stats["by_project"].items(), key=lambda x: -x[1]):
            lines.append(f"- {proj}: {count}")
        lines.append("")

    # Recent mistakes with errors (most useful for analysis)
    with_errors = [m for m in mistakes if m.get("err")]
    if with_errors:
        lines.append("## Recent Failures (with error messages)")
        for m in with_errors[-20:]:  # Last 20
            lines.append(f"- **[{m.get('ts', '?')}] {m.get('tool', '?')}** in {m.get('project', '?')}")
            lines.append(f"  - Input: `{m.get('input', m.get('action', '?'))[:120]}`")
            lines.append(f"  - Error: `{m.get('err', '')[:150]}`")
        lines.append("")

    # Mistakes without errors (less useful but still tracked)
    without_errors = [m for m in mistakes if not m.get("err")]
    if without_errors:
        lines.append(f"## Tool Failures Without Error Details ({len(without_errors)} entries)")
        lines.append("*These may be false positives or have missing error data.*")
        lines.append("")

    return "\n".join(lines)


def main():
    print("=== Mistake Organizer ===\n")

    raw_mistakes = load_raw_mistakes()
    print(f"Raw mistakes loaded: {len(raw_mistakes)}")

    if not raw_mistakes:
        print("No mistakes to organize.")
        return

    # Build stats
    stats = {
        "total": len(raw_mistakes),
        "by_tool": defaultdict(int),
        "by_project": defaultdict(int),
        "by_category": defaultdict(int),
        "with_errors": 0,
        "without_errors": 0,
    }

    patterns = {}
    for m in raw_mistakes:
        tool = m.get("tool", "Unknown")
        err = m.get("err", "")
        action = m.get("input", m.get("action", ""))
        project = m.get("project", "unknown")

        stats["by_tool"][tool] += 1
        stats["by_project"][project] += 1

        if err:
            stats["with_errors"] += 1
            category = categorize_error(tool, err, action)
            stats["by_category"][category] += 1
            key = extract_pattern_key(tool, err, category)
            if key in patterns:
                patterns[key]["count"] += 1
                patterns[key]["last_seen"] = m.get("ts", "")[:10]
            else:
                patterns[key] = {
                    "key": key,
                    "tool": tool,
                    "category": category,
                    "count": 1,
                    "sample_error": err[:200],
                    "sample_input": action[:150],
                    "first_seen": m.get("ts", "")[:10],
                    "last_seen": m.get("ts", "")[:10],
                }
        else:
            stats["without_errors"] += 1

    # Convert defaultdicts
    stats["by_tool"] = dict(stats["by_tool"])
    stats["by_project"] = dict(stats["by_project"])
    stats["by_category"] = dict(stats["by_category"])

    patterns_list = sorted(patterns.values(), key=lambda p: -p["count"])

    # Save patterns.json
    data = {
        "patterns": patterns_list,
        "stats": stats,
        "updated": datetime.now().isoformat(),
    }
    PATTERNS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PATTERNS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Patterns saved: {len(patterns_list)}")

    # Generate summary.md (NOT LESSONS.md!)
    summary = generate_summary_md(raw_mistakes, stats)
    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"Summary written to: {SUMMARY_FILE}")

    # Cleanup old entries
    cutoff = (datetime.now() - timedelta(days=RETENTION_DAYS)).strftime("%Y-%m-%d")
    fresh = [m for m in raw_mistakes if m.get("ts", "")[:10] >= cutoff]
    removed = len(raw_mistakes) - len(fresh)
    if removed > 0:
        with open(RAW_FILE, "w", encoding="utf-8") as f:
            for m in fresh:
                f.write(json.dumps(m, ensure_ascii=False) + "\n")
        print(f"Cleaned {removed} old entries (>{RETENTION_DAYS} days)")

    # Summary
    print(f"\n=== Summary ===")
    print(f"Total: {stats['total']} | With errors: {stats['with_errors']} | Without: {stats['without_errors']}")
    print(f"By tool: {stats['by_tool']}")
    if stats['by_category']:
        print(f"By category: {stats['by_category']}")
    print(f"\nLESSONS.md NOT modified (use /mistake-analyzer for AI analysis)")


if __name__ == "__main__":
    main()
