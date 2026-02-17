# Claude Code Skills

Shareable skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI. Each folder is a self-contained skill that can be installed by copying it to `~/.claude/skills/`.

## Available Skills

| Skill | Description |
|-------|-------------|
| **[ref-check](ref-check/)** | Cross-reference in-text citations against the reference list in academic papers (.docx). Produces a color-coded Word document (green=matched, cyan=fuzzy, yellow=missing from refs, red=uncited ref). Uses Claude Code sub-agents (Sonnet + Opus) for LLM verification. |
| **[ref-context](ref-context/)** | Verify that citations contextually match the sentences where they appear. Uses web search + Sonnet/Opus sub-agents to check if each citation is relevant to its claim. |

## Architecture

These skills demonstrate the **hybrid Python + sub-agent** pattern: Python scripts handle data extraction and document processing, while Claude Code orchestrates LLM verification via sub-agents (Sonnet for extraction, Opus for verification). No API keys are needed in the scripts themselves.

## Installation

### Install a single skill

```bash
# Clone the repo
git clone https://github.com/elad-refoua/claude-code-skills.git

# Copy the skill you want
cp -r claude-code-skills/ref-check ~/.claude/skills/
```

### Install all skills

```bash
git clone https://github.com/elad-refoua/claude-code-skills.git
cp -r claude-code-skills/ref-check ~/.claude/skills/
cp -r claude-code-skills/ref-context ~/.claude/skills/
```

### Windows (PowerShell)

```powershell
git clone https://github.com/elad-refoua/claude-code-skills.git
Copy-Item -Recurse claude-code-skills\ref-check $env:USERPROFILE\.claude\skills\
Copy-Item -Recurse claude-code-skills\ref-context $env:USERPROFILE\.claude\skills\
```

## Dependencies

Each skill lists its own dependencies. Common ones:

```bash
pip install python-docx    # Required for ref-check and ref-context
```

## Usage

Once installed, skills activate automatically when you use trigger phrases in Claude Code:

- **ref-check**: "check references", "ref check", "verify references"
- **ref-context**: "check citation context", "verify citation accuracy"

Or provide a `.docx` file and ask Claude to check it.

## How Skills Work

Skills are markdown files (`SKILL.md`) that give Claude Code specialized instructions for domain-specific tasks. Some skills include Python scripts for heavy processing, with Claude Code sub-agents handling LLM verification. Claude Code automatically discovers skills in `~/.claude/skills/`.

Learn more: [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code)

## License

MIT
