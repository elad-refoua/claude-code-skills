---
name: block-files
description: |
  Block Claude from reading sensitive files using permissions.deny rules in settings.json.
  Adds deny rules that stop Claude's built-in Read tool (and, best-effort, Grep/Glob) from
  opening specified files or patterns. Shell commands run through Bash are NOT blocked by these
  rules; that needs sandboxing.

  TRIGGERS: "block files", "block reading", "deny read access", "protect files",
  "block csv", "block data files", "add deny rule", "/block-files",
  "חסום קבצים", "חסום קריאה", "חסום גישה לקבצים"
---

# Block Files

Add, view, or remove `permissions.deny` rules that block Claude's built-in Read tool from accessing sensitive files (not shell commands; see below).

## How It Works

Claude Code's `permissions.deny` in `settings.json` blocks Claude's built-in file tools (Read, and on a best-effort basis Grep and Glob) from opening matched files. It does NOT stop a shell command (`cat`, `python`, `Rscript`) run through Bash from reading them. To block those as well, enable Claude Code's sandboxing, which restricts file access at the operating-system level. Bash deny rules help only partly: they match the command text by prefix, so a different command can still read the same file. Never treat a Read deny rule as the only protection for sensitive data.

**Important:** Changes require a **session restart** to take effect.

## Parse the Arguments

The user's input after `/block-files` determines the action:

| Input | Action |
|-------|--------|
| (empty) | Show current deny rules |
| `--remove <pattern>` | Remove a deny rule |
| `--global <pattern>` | Add rule to global settings (~/.claude/settings.json) |
| `--list` | Show current deny rules (same as empty) |
| `<pattern>` | Add rule to project settings (.claude/settings.json) |

Multiple patterns can be separated by spaces.

## Execution Steps

### When ADDING a pattern:

1. Determine target file:
   - Default: `.claude/settings.json` (project-level, in current working directory)
   - With `--global`: `~/.claude/settings.json` (user-level, applies to all projects)

2. Read existing settings.json (or start with `{}` if it doesn't exist)

3. Ensure `permissions.deny` array exists in the JSON

4. For each pattern provided:
   - Prepend `/` if the pattern doesn't start with `/`, `~`, or `//` (makes it project-relative)
   - Wrap in `Read(...)` format
   - Skip if already in the deny list
   - Add to the deny array

5. Write the updated settings.json (preserve existing settings, only modify `permissions.deny`)

6. Report what was added and remind to restart the session

### When REMOVING a pattern (--remove):

1. Read the target settings.json
2. Find and remove matching `Read(...)` entries from `permissions.deny`
3. Write back
4. Report what was removed and remind to restart

### When LISTING (no args or --list):

1. Read both project `.claude/settings.json` AND global `~/.claude/settings.json`
2. Show deny rules from each, clearly labeled
3. If no rules exist, say so

## Path Format Rules

| User types | Stored as | Matches |
|-----------|-----------|---------|
| `Data/*.csv` | `Read(/Data/*.csv)` | CSVs in project's Data/ folder |
| `*.env` | `Read(/*.env)` | .env files in project root |
| `**/*.rds` | `Read(/**/*.rds)` | .rds files anywhere in project |
| `~/secrets/*` | `Read(~/secrets/*)` | Files in user's home secrets/ |
| `/absolute/path` | `Read(//absolute/path)` | Absolute filesystem path |

**Key rules:**
- Single `*` matches files in one directory
- `**` matches recursively across directories
- Paths starting with `/` in the deny rule are relative to **project root**
- Paths starting with `//` are **absolute filesystem paths**
- Paths starting with `~` are relative to **home directory**

## Example Interactions

**User:** `/block-files Data/*.csv *.sav **/*.rds`
**Action:** Add 3 deny rules to project settings:
```json
"deny": ["Read(/Data/*.csv)", "Read(/*.sav)", "Read(/**/*.rds)"]
```
**Response:** "Added 3 deny rules to .claude/settings.json. Restart session to activate. These block Claude's file tools only; a shell command (cat, python) can still read these files unless sandboxing is on."

**User:** `/block-files --global *.env *.key`
**Action:** Add to ~/.claude/settings.json
**Response:** "Added 2 global deny rules. These apply to ALL projects. Restart session to activate. These block Claude's file tools only; a shell command (cat, python) can still read these files unless sandboxing is on."

**User:** `/block-files`
**Action:** List all rules
**Response:** Show project + global rules

**User:** `/block-files --remove Data/*.csv`
**Action:** Remove that specific rule
**Response:** "Removed Read(/Data/*.csv) from project deny rules. Restart session to activate."

## Settings.json Structure

```json
{
  "permissions": {
    "deny": [
      "Read(/Data/*.csv)",
      "Read(/**/*.sav)",
      "Read(/**/*.rds)"
    ]
  }
}
```

Always preserve any existing keys in settings.json (permissions.allow, other settings). Only modify the `permissions.deny` array.
