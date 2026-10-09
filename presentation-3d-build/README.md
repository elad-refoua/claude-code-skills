# presentation-3d-build

Build the journey in Three.js with HTML/SVG evidence panels, authored camera routes, responsive fallbacks, measured performance and a scoped static build.

## What it does

- Content / camera stops / scene modules / UI / build kept independently understandable
- HTML/SVG for exact text and charts, WebGL for the subject; CSS3D and WebGL share no depth buffer
- Authored travel paths, steady rest camera, reduced-motion and pause respected
- Budgets from measured draw calls and frame timing, not borrowed numbers

## Requirements

None beyond Claude Code. Three.js is vendored per project by the build skill; Blender is optional.

## Usage

In Claude Code, say: “3D presentation”, “Three.js presentation”, “מצגת תלת ממדית”, “camera tour”

## How it works

Part of a five-piece stack: the `presentation-journey-architect` agent coordinates, and the four `presentation-3d-*` skills own story, design, build and review. Each skill carries `references/` (method notes) and `agents/` (sub-agent briefs). Authored with Codex in September 2026 and shared as-is; reviewed for secrets and personal data before upload.

## Install

```bash
git clone https://github.com/elad-refoua/claude-code-skills.git
cp -r claude-code-skills/presentation-3d-build ~/.claude/skills/
```
