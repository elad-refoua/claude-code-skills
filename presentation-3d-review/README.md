# presentation-3d-review

Verify a deck-to-3D site as its audience will meet it: every number traced to its source, a real browser pass at several viewports, and publication to the existing canonical address.

## What it does

- Audit meaning and evidence: denominators, units, association vs. efficacy, publication status
- Optional structural validator: scripts/validate_journey.py over a journey manifest
- Browser pass table: arrival, travel, rest, reading, interaction, motion controls, RTL, fallback, runtime
- Publish only within authorization; verify the deployed commit at the canonical URL, no ?v= links

## Requirements

None beyond Claude Code. Three.js is vendored per project by the build skill; Blender is optional.

## Usage

In Claude Code, say: “verify 3D presentation”, “publish presentation website”, “בדיקת מסע תלת ממדי”

## How it works

Part of a five-piece stack: the `presentation-journey-architect` agent coordinates, and the four `presentation-3d-*` skills own story, design, build and review. Each skill carries `references/` (method notes) and `agents/` (sub-agent briefs). Authored with Codex in September 2026 and shared as-is; reviewed for secrets and personal data before upload.

## Scripts

`scripts/validate_journey.py` — structural validator for a journey manifest (Python 3, no dependencies).

## Install

```bash
git clone https://github.com/elad-refoua/claude-code-skills.git
cp -r claude-code-skills/presentation-3d-review ~/.claude/skills/
```
