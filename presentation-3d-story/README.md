# presentation-3d-story

Turn a slide deck into the narrative and scene plan of an interactive 3D journey: every slide becomes a stop with an audience question, evidence, meaning and a reason to move on.

## What it does

- Source contract first: the real deck (incl. notes), slide order as the spine, wording vs. factual error kept apart
- Argument map before scenes; 2-3 spatial concepts; a working slice before multiplying
- Illustrative dialogue only where it teaches, always labelled as fiction
- YAML story template + a research-narration reference for scholarly decks

## Requirements

None beyond Claude Code. Three.js is vendored per project by the build skill; Blender is optional.

## Usage

In Claude Code, say: “turn this deck into a 3D journey”, “להפוך מצגת למסע”, “slide-to-scene mapping”

## How it works

Part of a five-piece stack: the `presentation-journey-architect` agent coordinates, and the four `presentation-3d-*` skills own story, design, build and review. Each skill carries `references/` (method notes) and `agents/` (sub-agent briefs). Authored with Codex in September 2026 and shared as-is; reviewed for secrets and personal data before upload.

## Install

```bash
git clone https://github.com/elad-refoua/claude-code-skills.git
cp -r claude-code-skills/presentation-3d-story ~/.claude/skills/
```
