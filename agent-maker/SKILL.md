---
name: agent-maker
description: |
  Define custom Claude Code subagents for reuse across tasks and sessions.

  TRIGGERS: "create agent", "new agent", "define agent", "make agent",
  "I need an agent that", "I want an agent for", "build agent",
  "סוכן חדש", "יצירת סוכן", "תיצור לי סוכן"

  Saves agent definitions to ~/.claude/agents/<name>.md (Markdown + YAML frontmatter).
---

# Agent Maker

Create reusable Claude Code subagents. **A subagent is a Markdown file with YAML frontmatter** —
NOT JSON. The frontmatter is metadata; the Markdown body becomes the agent's system prompt.

> Format verified against the official Claude Code docs (code.claude.com/docs/en/sub-agents),
> 2026-06-11. The previous version of this skill emitted `.json` with an `instructions` field —
> that format does NOT load and every agent made that way silently failed to activate.

## Process

### Step 1: Understand (ask 2-3 questions MAX)
- What should this agent do, and **when should it be used** (this becomes the `description`)?
- Which tools does it need? (or omit to inherit all)
- Should it be used **proactively** (auto-delegated), or only when explicitly called?
- Does it need persistent memory across sessions?

### Step 2: Generate the file
Write to **`~/.claude/agents/<agent-name>.md`** (single Markdown file — the canonical form).
Use the Write tool.

### Step 3: Register it in the allowlist
Append the new agent's `name` to `~/.claude/agents/.known_agents.txt` (one per line). The
phantom-agent guard (`~/.claude/scripts/agent_phantom_check.py`, runs at SessionStart) warns about
any name-declaring `.md` that ISN'T on this list — so a real new agent must be added, or it will be
flagged as a false phantom.

### Step 4: Verify it loads
This is mandatory — the old skill shipped a format that never loaded. Confirm the new agent is
discoverable before declaring success:
```bash
claude -p "List your available subagents and say whether '<agent-name>' is among them." --max-turns 2
```
If it does not appear, check: file is `.md` (not `.json`), frontmatter has `name` + `description`,
and the `name` is unique (see precedence warning below).

## The canonical format

```markdown
---
name: agent-name                      # REQUIRED. kebab-case, unique across all agents
description: >                        # REQUIRED. when to delegate; add "Use proactively" for auto-use
  What this agent does and exactly when Claude should hand work to it.
  Use proactively when <trigger condition>.
tools: Read, Grep, Glob               # OPTIONAL. comma list OR YAML list. OMIT = inherit ALL tools
model: inherit                        # OPTIONAL. sonnet|opus|haiku|fable|inherit. default = inherit
memory: user                          # OPTIONAL. user|project|local — see "Memory" below. omit if none
---

You are <role>. <System prompt: how the agent behaves, its workflow, and a quality checklist.>
The Markdown body REPLACES the default Claude Code system prompt — be complete and self-contained.
```

### Field rules (from the official docs)
- **`name`, `description`** — the only required fields.
- **`description`** drives automatic delegation. To make the agent auto-used, include
  **"Use proactively"** / **"MUST BE USED"** and concrete trigger phrases.
- **`tools`** — comma-separated string OR YAML list, both valid. **Omit entirely to inherit all tools.**
  List only what's needed to restrict. (`disallowedTools` is a denylist alternative.)
- **`model`** — prefer the **alias** (`sonnet`/`opus`/`haiku`/`fable`/`inherit`). **Never pin a full
  model ID** like `claude-opus-4-6` — it breaks when that model is retired. Default is `inherit`.
- **Other optional keys** (rarely needed): `permissionMode`, `maxTurns`, `skills`, `color`,
  `background`, `effort`, `isolation`, `initialPrompt`. Unrecognized keys are ignored.

### ⚠️ Name uniqueness (silent-discard trap)
Claude Code scans `~/.claude/agents/` **recursively** and identifies an agent ONLY by its `name`
field. If two files declare the same `name` (e.g. a loose `foo.md` AND a folder `foo/AGENT.md`),
**Claude Code keeps one and discards the other with no warning.** Always pick a fresh, unique name
and check it isn't already taken (`ls ~/.claude/agents/`).

### Single file vs folder
- **Default to a single file:** `~/.claude/agents/<name>.md`.
- Folder-style (`<name>/AGENT.md` + `lessons/`, `assets/` subdirs) also works because the recursive
  scan still finds the `.md`. Use it only when the agent needs co-located assets. The folder name is
  cosmetic — discovery is by the `name` frontmatter, not the path.

## Memory (official feature — not a hack)
Set `memory: user` (cross-project, in `~/.claude/agent-memory/<name>/`), `project`
(`.claude/agent-memory/<name>/`, git-shareable), or `local` (not in git). When set, Claude Code:
- auto-creates the directory,
- injects the first 200 lines / 25 KB of its `MEMORY.md` into the agent's prompt each run,
- auto-enables Read/Write/Edit so the agent can curate its own memory.

Only add `memory:` if the agent should actually learn across sessions; otherwise omit it.

## Naming rules
- kebab-case: `code-reviewer`, not `codeReviewer` or `code reviewer`
- descriptive: `test-writer`, not `tw`

## Response format after creating
```
✅ Agent created: <agent-name>
📁 ~/.claude/agents/<agent-name>.md
🛠️ Tools: <list, or "inherits all">
🧠 Memory: <user|project|local|none>
🔎 Load check: <PASS/FAIL from the claude -p verification>
```

## Examples

### Proactive code reviewer (restricted tools, inherits model)
```markdown
---
name: code-reviewer
description: >
  Expert code-review specialist. Use proactively immediately after writing or modifying code,
  to check correctness, security, and maintainability.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer. When invoked: run `git diff` to see recent changes, then review
for bugs, edge cases, error handling, naming, and duplication. Report findings grouped by severity
(critical / warning / nit), each with a file:line and a concrete fix. Be specific, not generic.
```

### Documentation writer with persistent memory
```markdown
---
name: doc-writer
description: Creates and updates documentation for code and projects. Use when docs are requested.
tools: Read, Write, Glob, Grep
model: sonnet
memory: project
---

You write clear, concise documentation with runnable examples and consistent Markdown structure.
Record house style conventions you learn in MEMORY.md so later sessions stay consistent.
```

## Language support
Respond in the user's language (English or Hebrew) naturally.
