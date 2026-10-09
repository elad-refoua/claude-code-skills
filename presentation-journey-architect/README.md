# presentation-journey-architect

Coordinating agent that turns a source presentation into a polished, verified online 3D journey by loading the four presentation-3d-* skills phase by phase.

## What it does

- Reads the actual deck and project before touching code; preserves repository identity and canonical URL
- Story → design → build → review, with a working slice before the full deck
- Distinctions the audience must see: % of people ≠ % of messages; association ≠ efficacy; metaphor ≠ evidence
- Finishes in a real browser, then deploys to the existing destination when authorized

## Requirements

None beyond Claude Code. Three.js is vendored per project by the build skill; Blender is optional.

## Usage

In Claude Code, say: “turn this presentation into a 3D journey”, “להפוך מצגת למסע תלת ממדי”, “immersive presentation”

## How it works

Part of a five-piece stack: the `presentation-journey-architect` agent coordinates, and the four `presentation-3d-*` skills own story, design, build and review. Each skill carries `references/` (method notes) and `agents/` (sub-agent briefs). Authored with Codex in September 2026 and shared as-is; reviewed for secrets and personal data before upload.

## Install

```bash
git clone https://github.com/elad-refoua/claude-code-skills.git
cp -r claude-code-skills/presentation-journey-architect ~/.claude/agents/
```
