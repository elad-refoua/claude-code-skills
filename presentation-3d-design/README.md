# presentation-3d-design

Visual direction for an immersive 3D presentation: composition, human and symbolic roles, readable charts, RTL typography, motion that means something.

## What it does

- Meaning first: subject, world, palette, light, type, reserved evidence space
- Prove the system in the browser with a representative slice, not a concept image
- Contrast checked on the rendered result (4.5:1 text), type sized for projected size
- RTL with <bdi> isolation, portrait fallback, click-to-enlarge with keyboard focus

## Requirements

None beyond Claude Code. Three.js is vendored per project by the build skill; Blender is optional.

## Usage

In Claude Code, say: “3D presentation design”, “make the journey beautiful”, “עיצוב מצגת תלת ממדית”

## How it works

Part of a five-piece stack: the `presentation-journey-architect` agent coordinates, and the four `presentation-3d-*` skills own story, design, build and review. Each skill carries `references/` (method notes) and `agents/` (sub-agent briefs). Authored with Codex in September 2026 and shared as-is; reviewed for secrets and personal data before upload.

## Install

```bash
git clone https://github.com/elad-refoua/claude-code-skills.git
cp -r claude-code-skills/presentation-3d-design ~/.claude/skills/
```
